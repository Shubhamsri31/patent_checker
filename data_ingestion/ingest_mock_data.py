import os
from dotenv import load_dotenv
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

load_dotenv() 

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")
MONGO_COLLECTION = "patents"

if not MONGO_URI or not MONGO_DB_NAME:
    raise ValueError("MONGO_URI and MONGO_DB_NAME must be set in the .env file")

mock_patents = [
    {"publication_number": "MOCK-001","title": "Low impact footrope and methods","abstract": "A footrope for a bottom trawl that has markedly reduced carbon footprint and dust cloud formation compared to known footropes, thereby conserving sequestered carbon in the seafloor. The footrope has a plurality of footrope unit bodies."},
    {"publication_number": "MOCK-002","title": "Breathing control using high flow respiration assistance","abstract": "High flow therapy is used to treat Cheyne-Stokes respiration and other types of periodic respiration disorders by periodic application of high flow therapy, adjustment of high flow therapy flow rates and/or periodic additions of CO2 or O2 into the air flow provided to the patient."},
    {"publication_number": "MOCK-003","title": "Wearable Gaming Device and Method Thereof","abstract": "A gaming wearable device directed to be worn by a player whilst playing a videogame is provided. The gaming wearable device of the invention hereby disclosed allows the user to feel the sensations currently suffered by a character of a video game, in such a way a deeply immersive gaming experience is provided."},
    {"publication_number": "MOCK-004","title": "Oral care compositions comprising prenylated flavonoids","abstract": "Oral care compositions that include prenylated flavonoid and metal ion. Oral care compositions that include prenylated flavonoid and calcium. Anticavity oral care compositions that comprise prenylated flavonoid. Anticavity oral care compositions that comprise prenylated flavonoid and are free of fluoride."},
    {"publication_number": "MOCK-005","title": "Proximity detection for a surgical light","abstract": "A surgical light head and proximity detection method includes a housing, a plurality of light emitting elements arranged in the housing and configured to direct light at a target region of interest, and a plurality of distance sensors arranged in the housing."}
]

def ingest_mock_data():
    print("Connecting to MongoDB Atlas...")
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB_NAME]
    collection = db[MONGO_COLLECTION]
    print("Connection successful.")

    collection.drop()
    print(f"Dropped existing collection '{MONGO_COLLECTION}'.")

    print("Loading local embedding model (all-MiniLM-L6-v2)...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print("Model loaded.")

    documents_to_insert = []
    
    print("Generating embeddings for mock data...")
    for patent in tqdm(mock_patents, desc="Embedding Mock Data"):
        # The .tolist() method returns numpy floats, which can cause issues.
        raw_embedding = model.encode(patent['abstract']).tolist()

        # --- THIS IS THE FIX ---
        # We explicitly cast every number in the vector to a standard Python float.
        # This ensures the data is stored in the correct BSON Double format.
        clean_embedding = [float(x) for x in raw_embedding]
        # --------------------

        patent_document = {
            "publication_number": patent['publication_number'],
            "title": patent['title'],
            "abstract": patent['abstract'],
            "embedding": clean_embedding, # Use the cleaned vector
        }
        documents_to_insert.append(patent_document)

    collection.insert_many(documents_to_insert)
    print("\nMock data ingestion complete!")
    print(f"Total documents in '{MONGO_COLLECTION}': {collection.count_documents({})}")

if __name__ == "__main__":
    ingest_mock_data()