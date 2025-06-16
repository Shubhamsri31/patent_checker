from pydantic import BaseModel, Field
from typing import List

# --- API Request Models ---
class InitialIdeaRequest(BaseModel):
    idea_text: str

class LandscapeAnalysisRequest(BaseModel):
    user_idea: str
    matched_patents: List['MatchedPatent'] 

# --- API Response & Data Models ---
class MatchedPatent(BaseModel):
    publication_number: str
    title: str
    abstract: str
    score: float

class StartChatResponse(BaseModel):
    matched_patents: List[MatchedPatent]

# --- NEW: A sub-model to enforce evidence-based analysis ---
class PointOfAnalysis(BaseModel):
    description: str = Field(..., description="A specific, detailed point of similarity or difference.")
    # This field FORCES the AI to cite its sources from the provided data.
    cited_patents: List[str] = Field(..., description="List of publication numbers (e.g., 'US-12345-B2') that support this point of analysis.")

# --- UPDATED: The main response model with stronger requirements ---
class HolisticAnalysis(BaseModel):
    # This ensures the score is always within the 1-10 range.
    noveltyScore: int = Field(..., ge=1, le=10, description="An integer from 1 (highly derivative) to 10 (highly novel) based on the provided prior art.")
    
    synthesisOfPriorArt: str = Field(..., description="A summary of the existing technology landscape as described by the provided patents.")
    
    # These fields now use the new, more demanding sub-model.
    keySimilarities: List[PointOfAnalysis] = Field(..., description="A list of specific areas where the user's idea overlaps with the prior art, with citations.")
    keyDifferences: List[PointOfAnalysis] = Field(..., description="A list of specific, unique aspects of the user's idea, with citations for contrast.")
    
    expertRecommendation: str = Field(..., description="A concluding paragraph offering strategic advice for a non-expert on how to proceed, focusing on patentability.")