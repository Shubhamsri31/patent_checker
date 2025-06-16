import os
import sys
from dotenv import load_dotenv
from pymongo import MongoClient
from google.cloud import bigquery
from google.cloud import aiplatform
from tqdm import tqdm

load_dotenv(dotenv_path='../.env')

# --- Configuration ---
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")
GOOGLE_CLOUD_PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT_ID")
GOOGLE_CLOUD_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION")
EMBEDDING_MODEL_NAME = "text-embedding-004" # Use the latest Google model
MONGO_COLLECTION = "patents"

if not all([MONGO_URI, MONGO_DB_NAME, GOOGLE_CLOUD_PROJECT_ID, GOOGLE_CLOUD_LOCATION]):
    raise ValueError("All credentials (Mongo and Google Cloud) must be set in .env file.")

def get_mongodb_collection():
    print("Connecting to MongoDB Atlas...")
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB_NAME]
    return db[MONGO_COLLECTION]

def get_text_embedding(client, text: str) -> list[float]:
    response = client.get_embeddings(
        texts=[text],
        output_dimensionality=768 # Standard for this model
    )
    return response.embeddings[0].values

def ingest_data():
    collection = get_mongodb_collection()
    collection.drop()
    print(f"Dropped existing collection '{MONGO_COLLECTION}'.")

    print("Connecting to Google BigQuery...")
    bq_client = bigquery.Client(project=GOOGLE_CLOUD_PROJECT_ID)
    print("Initializing Google AI Platform TextEmbeddingModel...")
    embedding_client = aiplatform.TextEmbeddingModel.from_pretrained(EMBEDDING_MODEL_NAME)

    # Note: Increase LIMIT for a real dataset (e.g., 50000).
    # Be mindful of costs, although this will be covered by free credits.
    sql_query = """
        SELECT
          publication_number,
          (SELECT text FROM UNNEST(title_localized) WHERE language = 'en' LIMIT 1) AS title,
          (SELECT text FROM UNNEST(abstract_localized) WHERE language = 'en' LIMIT 1) AS abstract
        FROM `patents-public-data.patents.publications`
        WHERE EXISTS(SELECT 1 FROM UNNEST(abstract_localized) WHERE language = 'en')
        ORDER BY publication_date DESC
        LIMIT 2000;
    """
    
    print("Executing BigQuery query...")
    query_job = bq_client.query(sql_query)
    total_rows = query_job.result().total_rows
    print(f"Found {total_rows} patents to ingest.")

    batch = []
    batch_size = 100
    
    for row in tqdm(query_job.result(), total=total_rows, desc="Processing patents"):
        if not row.abstract or not row.title:
            continue
        try:
            embedding_vector = get_text_embedding(embedding_client, row.abstract)
            patent_document = {
                "publication_number": row.publication_number,
                "title": row.title,
                "abstract": row.abstract,
                "embedding": embedding_vector,
            }
            batch.append(patent_document)

            if len(batch) >= batch_size:
                collection.insert_many(batch)
                batch = []
        except Exception as e:
            print(f"\nAn error occurred for {row.publication_number}: {e}")

    if batch:
        collection.insert_many(batch)
    
    print("\nData ingestion complete!")

if __name__ == "__main__":
    aiplatform.init(project=GOOGLE_CLOUD_PROJECT_ID, location=GOOGLE_CLOUD_LOCATION)
    ingest_data()