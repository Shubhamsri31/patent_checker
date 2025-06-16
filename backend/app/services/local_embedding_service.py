from sentence_transformers import SentenceTransformer
from functools import lru_cache

@lru_cache(maxsize=1)
def get_embedding_model():
    print("Loading local AI model for vector search embeddings...")
    model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')
    print("Local AI model loaded.")
    return model

def create_embedding(text: str) -> list[float]:
    model = get_embedding_model()
    return model.encode(text).tolist()