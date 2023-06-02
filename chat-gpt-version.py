import os
import re
import sys
import PyPDF2
import pdfplumber
from datetime import datetime
import pickle
from pathlib import Path


class PdfFile:
    def __init__(self, file_path):
        self.path = Path(file_path)
        self.name = self.path.name
        self.pickle_dir = Path('pickle')
        self.pickle_dir.mkdir(exist_ok=True)
        self.words_path = self.pickle_dir / f"{self.name}-words.pkl"
        self.text_path = self.pickle_dir / f"{self.name}-pdf_text.pkl"
        self.words = self.load_pickle(self.words_path, self.extract_words)
        self.text = self.load_pickle(self.text_path, self.extract_text)

    @staticmethod
    def load_pickle(path, fallback):
        if path.exists():
            with open(path, 'rb') as file:
                return pickle.load(file)
        else:
            data = fallback()
            with open(path, 'wb') as file:
                pickle.dump(data, file)
            return data

    @staticmethod
    def merge_words(words):
        i = 0
        while i < len(words) - 1:
            if words[i].endswith('-'):
                words[i] = words[i][:-1] + words[i + 1]
                del words[i + 1]
            else:
                i += 1
        return words

    def extract_words(self):
        words = []
        with pdfplumber.open(self.path) as pdf:
            for page in pdf.pages:
                words.extend(self.get_bold_words_from(page))
        return self.merge_words(words)

    def get_bold_words_from(self, page):
        # Rest of the code remains same here
        pass

    def extract_text(self):
        # Rest of the code remains same here
        pass

    def get_text_from(self, page):
        # Rest of the code remains same here
        pass

    def build_dictionary(self, headers):
        # Rest of the code remains same here
        pass


def save_as_csv(dictionary, path):
    with open(path, 'w') as file:
        for key, value in dictionary.items():
            file.write(f"{key},{value}\n")


def main():
    start_time = datetime.now()

    data_dir = Path('data')
    csv_dir = Path('csv')
    csv_dir.mkdir(exist_ok=True)

    pdf_files = list(data_dir.glob("*.pdf"))
    for index, pdf_path in enumerate(pdf_files, start=1):
        pdf = PdfFile(pdf_path)
        dictionary = pdf.build_dictionary(pdf.words)
        save_as_csv(dictionary, csv_dir / f"{pdf.name}.csv")
        print(f"Processed file {pdf.name} ({index} of {len(pdf_files)}, {round(index / len(pdf_files) * 100, 2)}%)")

    print('Execution time:', datetime.now() - start_time)


if __name__ == '__main__':
    main()
