import os
import re
import sys
import PyPDF2
import pdfplumber
from datetime import datetime
import pickle


def merge_words(words):
    i = 0
    while i < len(words) - 1:
        if words[i].endswith('-'):
            words[i] = words[i][:-1] + words[i + 1]
            del words[i + 1]
        else:
            i += 1
    return words

"""
Process a page and return a list of bold words
Each page is divided into two columns, left and right
"""
def get_bold_words_from(page):
    words = []

    left = page.crop((0, 0.4 * float(page.height), 0.5 * float(page.width), 0.99 * float(page.height)))
    right = page.crop((0.5 * float(page.width), 0.4 * float(page.height), page.width, 0.99 * float(page.height)))
    
    # Ignore first and last lines of the document
    for side in [left, right]:
        clean_text = side.filter(lambda obj: (obj["object_type"] == "char" and "Bold" in obj["fontname"]))
        words_as_string = clean_text.extract_text()

        # split by new line and append flat to words
        words.extend(words_as_string.split("\n"))

    # Remove words that contain numbers
    words = [word for word in words if not re.search(r'\d', word)]

    # Remove words that contain more than zero lowercase letters
    words = [word for word in words if word.isupper()]

    return words

def get_text_from(page):
    page_text = page.extract_text()
    # Replace "-\n" and " -\n" with ""
    page_text = re.sub(r'-\n', '', page_text)
    page_text = re.sub(r' -\n', '', page_text)
    # Replace "\n" with " "
    page_text = re.sub(r'\n', ' ', page_text)

    # Replace more than one space with one space
    page_text = re.sub(r'\s{2,}', ' ', page_text)

    # Remove spaces before punctuation including parentheses and dash
    page_text = re.sub(r'\s([.,;!?()\-])', r'\1', page_text)

    # Remove space after "«" from text and space before "»" from text
    page_text = re.sub(r'«\s', '«', page_text)
    page_text = re.sub(r'\s»', '»', page_text)

    return page_text

def read_pdf_file(pdf_file):
    words = []

    # Check if 'words.pkl' exists if yes read it
    if os.path.exists(f'pickle/{pdf_file[:-4]}-words.pkl'):
        with open(f'pickle/{pdf_file[:-4]}-words.pkl', 'rb') as f:
            words = pickle.load(f)

    else:
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                parsed_words = get_bold_words_from(page)
                words.extend(parsed_words)
                words = merge_words(words)

                # print the progress and include number of words only when the number of words is a multiple of 100
                if page.page_number % 100 == 0:
                    print(f"Processed page {page.page_number} of {len(pdf.pages)} ({len(words)} words)")
        
        # Pickle the words so that we can use them later
        with open(f'pickle/{pdf_file[:-4]}-words.pkl', 'wb') as f:
            pickle.dump(words, f)

    # If a word contains a dash as a last character merget it with the next word
    words = merge_words(words)

    pdfFileObj = open(pdf_file, 'rb')
    pdfReader = PyPDF2.PdfReader(pdfFileObj)

    # Create a variable to store the text
    pdf_text = ''

    # Check if pdf_text.pkl exists if yes read it
    if os.path.exists(f'pickle/{pdf_file[:-4]}-pdf_text.pkl'):
        with open(f'pickle/{pdf_file[:-4]}-pdf_text.pkl', 'rb') as f:
            pdf_text = pickle.load(f)
    else:
        # Create counter to keep track of the pages
        counter = 0
        # Iterate over all the pages
        for page in pdfReader.pages:
            page_text = get_text_from(page)
            pdf_text += page_text

            # Print the progress including the possible file size in MB and percentage only when number of pages is divisible by 100
            if counter % 100 == 0:
                print(f"Processed page {counter} of {len(pdfReader.pages)} ({round(sys.getsizeof(pdf_text) / 1024 / 1024, 2)} MB, {round(counter / len(pdfReader.pages) * 100, 2)}%)")
            counter += 1

    # Close the pdf file object
    pdfFileObj.close()

    # Pickle the text so that we can use it later
    with open(f'pickle/{pdf_file[:-4]}-pdf_text.pkl', 'wb') as f:
        pickle.dump(pdf_text, f)

    return (words, pdf_text)

    
def build_dictionary(headers, text):
    # Create a dictionary to store the headers and the text between them which is the meaning of words
    dictionary = {}
    cursor = 0
    for i in range(len(headers) - 1):
        try:
            start = text[cursor:].index(headers[i]) + cursor
            cursor = start + len(headers[i])
            end = text[cursor:].index(headers[i+1]) + cursor
            
            dictionary[headers[i]] = text[cursor:end].strip()
            cursor = end
        except ValueError:
            continue  # skip to the next header if current header is not found

    # handle the last header separately
    try:
        start = text[cursor:].index(headers[-1]) + cursor
        cursor = start + len(headers[-1])
        
        dictionary[headers[-1]] = text[cursor:].strip()
    except IndexError:
        pass  # do nothing if the last header is not found

    return dictionary

def save_as_csv(dictionary, pdf_file):
    with open('csv/' + pdf_file[:-4] + '.csv', 'w') as f:
        for key in dictionary.keys():
            f.write("%s,%s\n"%(key,dictionary[key]))

def main():
    start_time = datetime.now()

    processed_files = 0
    for pdf_file in os.listdir("data"):
        
        if pdf_file.endswith(".pdf"):
            (headers, text) = read_pdf_file("data/" + pdf_file)

            dictionary = build_dictionary(headers, text)

            save_as_csv(dictionary, pdf_file)
         
        # print the progress mentioning the total number of files file name number of already processed files and percentage
        print(f"Processed file {pdf_file} ({processed_files} of {len(os.listdir('data'))}, {round(processed_files / len(os.listdir('data')) * 100, 2)}%)")
        processed_files += 1

    end_time = datetime.now()

    print('Execution time: {}'.format(end_time - start_time))

if __name__ == '__main__':
    main()

