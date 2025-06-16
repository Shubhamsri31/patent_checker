from fastapi import APIRouter, HTTPException
from typing import List, Optional
from ..models.patent import SearchRequest, PatentResult
from ..services import mongo_service
from ..core import config

if config.EMBEDDING_PROVIDER == 'google':
    from ..services import google_ai_service as embedding_service
    from ..services.google_ai_service import summarize_with_gemini # Import the new function
    print("API is running in GOOGLE mode.")
else:
    # Fallback for local mode (won't have summarization)
    from ..services import local_embedding_service as embedding_service
    summarize_with_gemini = None
    print("API is running in LOCAL mode.")

router = APIRouter()

# NEW: Define a response model that includes the summary
class SearchResponse(BaseModel):
    summary: Optional[str] = None
    results: List[PatentResult]

@router.post("/search", response_model=SearchResponse)
async def search_patents(request: SearchRequest):
    try:
        query_embedding = embedding_service.create_embedding(request.query)
        search_results = mongo_service.vector_search(query_embedding)
        
        ai_summary = None
        # Only try to summarize if in Google mode and results were found
        if summarize_with_gemini and search_results:
            print("Generating AI summary...")
            # Combine the abstracts into a single context
            context = "\n\n---\n\n".join([result['abstract'] for result in search_results])
            ai_summary = summarize_with_gemini(request.query, context)

        return SearchResponse(summary=ai_summary, results=search_results)

    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail=str(e))