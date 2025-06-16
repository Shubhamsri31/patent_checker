
import json
import os
from datetime import datetime
from dotenv import load_dotenv, find_dotenv
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

load_dotenv(find_dotenv())
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise ValueError("MONGO_URI not found in .env file!")

MONGO_DB_NAME = "patent_db"
MONGO_COLLECTION = "patents"
INPUT_JSON_FILE = "data_ingestion/patents.json"

def ingest_data():
    client = MongoClient(MONGO_URI)
    collection = client[MONGO_DB_NAME][MONGO_COLLECTION]
    collection.drop()

    print("Loading local AI model (all-MiniLM-L6-v2). This may take a moment...")
    model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')
    print("Model loaded.")

    docs_to_insert = []
    print(f"Reading from '{INPUT_JSON_FILE}'...")
    try:
        with open(INPUT_JSON_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        for line in tqdm(lines, desc="Processing and Embedding"):
            try:
                row = json.loads(line)
                if not row.get('abstract'): continue

                embedding_vector = model.encode(row['abstract'])
                docs_to_insert.append({
                    "publication_number": row.get('publication_number'),
                    "title": row.get('title'),
                    "abstract": row.get('abstract'),
                    "embedding": [float(x) for x in embedding_vector]
                })
            except Exception as e:
                print(f"Skipping line due to error: {e}")

        if docs_to_insert:
            print(f"Embedding complete. Inserting {len(docs_to_insert)} documents...")
            collection.insert_many(docs_to_insert, ordered=False)
            print("Data ingestion successful!")
        else:
            print("No valid documents found to ingest.")
            
    except FileNotFoundError:
        print(f"ERROR: '{INPUT_JSON_FILE}' not found. Did you run the conversion script first?")

if __name__ == "__main__":
    ingest_data()