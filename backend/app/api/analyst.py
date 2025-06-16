from fastapi import APIRouter, HTTPException
from ..models.patent import InitialIdeaRequest, StartChatResponse, LandscapeAnalysisRequest, HolisticAnalysis
from ..services import local_embedding_service, mongo_service, llm_service

router = APIRouter()

@router.post("/find-similar", response_model=StartChatResponse)
async def find_similar_patents(request: InitialIdeaRequest):
    """
    Step 1: Takes a user's idea and finds a list of similar patents from the database.
    This endpoint remains unchanged and works as intended.
    """
    try:
        embedding = local_embedding_service.create_embedding(request.idea_text)
        patents = mongo_service.vector_search(embedding)
        return StartChatResponse(matched_patents=patents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error finding similar patents: {str(e)}")

# --- THIS IS THE NEW, CORRECTED ANALYSIS ENDPOINT ---
@router.post("/analyze-landscape", response_model=HolisticAnalysis)
async def analyze_patent_landscape(request: LandscapeAnalysisRequest):
    """
    Step 2: Takes the user's idea AND the list of patents found in step 1,
    and returns a deep, holistic analysis of the idea's novelty and patentability.
    """
    if not request.matched_patents:
        raise HTTPException(status_code=400, detail="Cannot perform analysis with an empty list of matched patents.")

    try:
        # This now calls our new, more powerful orchestrator function
        analysis = llm_service.get_holistic_analysis(
            user_idea=request.user_idea,
            matched_patents=request.matched_patents
        )
        return analysis
    except Exception as e:
        # The service layer's final error is passed cleanly to the frontend.
        raise HTTPException(status_code=500, detail=f"AI Landscape Analysis Failed: {str(e)}")