import csv
import json
import os

# Define file paths relative to the project root
CSV_FILE_PATH = os.path.join('data_ingestion', 'datamain.csv')
JSON_FILE_PATH = os.path.join('data_ingestion', 'patents.json')

def convert_csv_to_jsonl():
    """
    Reads the downloaded patents.csv and converts it to patents.json,
    where each line is a valid JSON object (JSON Lines format).
    """
    try:
        print(f"Opening CSV file: {CSV_FILE_PATH}")
        patent_data = []
        with open(CSV_FILE_PATH, mode='r', encoding='utf-8') as csv_file:
            # Use DictReader to easily access columns by name
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                patent_data.append(row)
        
        print(f"Read {len(patent_data)} rows from CSV. Writing to JSON Lines file...")
        with open(JSON_FILE_PATH, mode='w', encoding='utf-8') as json_file:
            for entry in patent_data:
                # Write each row as a new line in the JSON file
                json.dump(entry, json_file)
                json_file.write('\n')

        print(f"Conversion complete. Data saved to: {JSON_FILE_PATH}")

    except FileNotFoundError:
        print(f"ERROR: Could not find '{CSV_FILE_PATH}'.")
        print("Please ensure you have downloaded the CSV and placed it in the 'data_ingestion' folder.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == '__main__':
    convert_csv_to_jsonl()