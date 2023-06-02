import csv
import sqlite3
import os

def read_csv(file_path):
    with open(file_path, newline='') as file:
        reader = csv.reader(file, delimiter='~')
        data = []
        for row in reader:
            # If row has more than one column and the second column is not empty
            if len(row) > 1 and row[1]:
                data.append((row[0], row[1]))
        return data

def prepare_database(cursor):
    # Drop the 'words' table if it exists
    cursor.execute('''
        DROP TABLE IF EXISTS words
    ''')

    # Create the 'words' table with three columns: id, word, meaning
    cursor.execute('''
        CREATE TABLE words (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            word TEXT,
            meaning TEXT
        )
    ''')

    # Drop the 'words_fts' table if it exists
    cursor.execute('''
        DROP TABLE IF EXISTS words_fts
    ''')
            
    # Create a virtual table 'words_fts' for full-text search
    cursor.execute('''
        CREATE VIRTUAL TABLE words_fts USING fts5(word, meaning)
    ''')

def insert_rows_into_both_tables(rows):
    # Insert data into both tables
    for row in rows:
        c.execute('''
            INSERT INTO words (word, meaning)
            VALUES (?, ?)
        ''', (row[0], row[1]))
        c.execute('''
            INSERT INTO words_fts (word, meaning)
            VALUES (?, ?)
        ''', (row[0], row[1]))

def process_file(filepath):
    # Open the file and do something with it
    csv_data = read_csv(filepath)
    insert_rows_into_both_tables(csv_data)

def iterate_files(directory, callback):
    # Get number of files in the directory
    num_files = len([filename for filename in os.listdir(directory) if filename.endswith(".csv")])
    # Create a variable to count the number of processed files
    processed_files = 0
    # Use os.listdir to get all files in the directory
    for filename in os.listdir(directory):
        # Check if the file is a .csv file
        if filename.endswith(".csv"):
            # Concatenate the directory path with the filename to get the full path to the file
            filepath = os.path.join(directory, filename)
            
            # Call the callback function with the file path
            callback(filepath)

            # Print the progress
            print(f"Processed file {processed_files} of {num_files} ({round(processed_files / num_files * 100, 2)}%)")

            # Increment the number of processed files
            processed_files += 1


# Create a new database
conn = sqlite3.connect('words.db')
# Create a new Cursor object
c = conn.cursor()
prepare_database(c)

# Specify the directory you want to iterate over
directory = 'csv'

iterate_files(directory, process_file)

# Commit the transaction and close the connection
conn.commit()
conn.close()



