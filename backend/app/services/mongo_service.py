from pymongo import MongoClient
from ..core import config

# Set a reasonable score threshold to filter out truly irrelevant results
MINIMUM_RELEVANCE_SCORE = 0.5 

def vector_search(query_embedding: list[float], num_results: int = 5) -> list[dict]:
    """Performs vector search and filters out results below the relevance threshold."""
    client = MongoClient(config.MONGO_URI)
    collection = client[config.MONGO_DB_NAME]["patents"]
    
    pipeline = [
        {
            "$vectorSearch": {
                # --- THE DEFINITIVE FIX: Use the correct index name ---
                "index": "vector_index", 
                "path": "embedding",
                "queryVector": query_embedding,
                "numCandidates": 150,
                "limit": 10
            }
        },
        {"$addFields": { "score": { "$meta": "vectorSearchScore" }}},
        {"$match": { "score": { "$gte": MINIMUM_RELEVANCE_SCORE }}},
        {"$limit": num_results},
        {"$project": { "_id": 0, "publication_number": 1, "title": 1, "abstract": 1, "score": 1 }}
    ]
    results = list(collection.aggregate(pipeline))
    client.close()
    return results