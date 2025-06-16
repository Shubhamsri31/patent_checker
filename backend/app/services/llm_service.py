import json
import traceback
import re
from openai import OpenAI
import google.generativeai as genai
from ..core import config
from ..models.patent import HolisticAnalysis, MatchedPatent, PointOfAnalysis
from typing import List

# --- REWRITTEN AND REINFORCED PROMPT TEMPLATE ---
PROMPT_TEMPLATE = """
You are a meticulous, evidence-based Patent Analyst AI. Your credibility depends on precision. Your task is to analyze a "User's Idea" against a "List of Prior Art Patents" and produce a verifiable, structured report.

**CRITICAL INSTRUCTIONS:**
1.  **No Generic Statements:** Do not provide vague or non-specific analysis. Every point you make in "keySimilarities" and "keyDifferences" MUST be directly supported by evidence from the provided patents.
2.  **Mandatory Citations:** For every point of analysis, you MUST cite the `publication_number` of the patent(s) that justify your claim in the `cited_patents` field.
3.  **Strict JSON Output:** Your entire output must be a single, valid JSON object that strictly adheres to the format defined below.

**JSON OUTPUT FORMAT:**
{{
  "noveltyScore": <An integer from 1 (highly derivative) to 10 (highly novel)>,
  "synthesisOfPriorArt": "A dense paragraph summarizing the collective technology described across all provided patent abstracts. What is the current state-of-the-art according to this data?",
  "keySimilarities": [
    {{
      "description": "A specific point of overlap between the user's idea and the prior art.",
      "cited_patents": ["<publication_number_of_relevant_patent_1>", "..."]
    }}
  ],
  "keyDifferences": [
    {{
      "description": "A specific point of novelty in the user's idea when contrasted with the prior art.",
      "cited_patents": ["<publication_number_of_patent_being_contrasted>", "..."]
    }}
  ],
  "expertRecommendation": "A final, concise paragraph of strategic advice. Summarize patentability, highlight the strongest novel aspects to pursue, and warn about the most significant challenges based on your analysis."
}}

---
**DATA FOR ANALYSIS:**

<USER_IDEA>
{user_idea}
</USER_IDEA>

<PRIOR_ART_PATENTS>
{formatted_patents}
</PRIOR_ART_PATENTS>
"""

# --- UTILITIES (Unchanged) ---
def _clean_and_parse_json(text: str) -> dict:
    match = re.search(r'```(json)?(.*)```', text, re.DOTALL)
    if match: json_str = match.group(2).strip()
    else: json_str = text.strip()
    return json.loads(json_str)

def _format_patents_for_prompt(patents: List[MatchedPatent]) -> str:
    formatted_list = [
        f"<PATENT>\nPublication Number: {p.publication_number}\nTitle: {p.title}\nAbstract: {p.abstract}\n</PATENT>"
        for p in patents
    ]
    return "\n\n".join(formatted_list)

# --- NEW: POST-PROCESSING QUALITY VALIDATION ---
def _validate_analysis_quality(analysis: HolisticAnalysis):
    """
    Performs semantic checks on the AI's output.
    Raises ValueError if the quality is too low.
    """
    if len(analysis.synthesisOfPriorArt.split()) < 15:
        raise ValueError("AI analysis failed quality check: 'synthesisOfPriorArt' is too short or empty.")
    
    if len(analysis.expertRecommendation.split()) < 20:
        raise ValueError("AI analysis failed quality check: 'expertRecommendation' is too short or empty.")
        
    # An analysis MUST find some similarities and differences to be useful.
    # If either list is empty, the AI was lazy or couldn't perform the task.
    if not analysis.keySimilarities:
        raise ValueError("AI analysis failed quality check: 'keySimilarities' list is empty.")
    
    if not analysis.keyDifferences:
        raise ValueError("AI analysis failed quality check: 'keyDifferences' list is empty.")
    
    print("✅ AI response passed quality validation.")


# --- AI IMPLEMENTATIONS (Unchanged function signatures) ---
def _get_gemini_analysis(user_idea: str, patents: List[MatchedPatent]) -> dict:
    # (Implementation is the same as before, just uses the new prompt)
    if not config.GOOGLE_API_KEY: raise ConnectionRefusedError("Google API Key not configured.")
    genai.configure(api_key=config.GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash-latest', generation_config={"response_mime_type": "application/json"})
    prompt = PROMPT_TEMPLATE.format(user_idea=user_idea, formatted_patents=_format_patents_for_prompt(patents))
    print("-----> Sending new landscape analysis request to Primary AI (Gemini 1.5 Flash)...")
    response = model.generate_content(prompt)
    print("<----- Successfully received response from Primary AI.")
    return _clean_and_parse_json(response.text)

def _get_togetherai_analysis(user_idea: str, patents: List[MatchedPatent]) -> dict:
    # (Implementation is the same as before, just uses the new prompt)
    if not config.TOGETHER_API_KEY: raise ConnectionRefusedError("Together AI API Key not configured.")
    client = OpenAI(api_key=config.TOGETHER_API_KEY, base_url='https://api.together.xyz/v1', timeout=45.0)
    prompt = PROMPT_TEMPLATE.format(user_idea=user_idea, formatted_patents=_format_patents_for_prompt(patents))
    print("-----> Sending new landscape analysis request to Fallback AI (Together AI)...")
    chat_completion = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="mistralai/Mixtral-8x7B-Instruct-v0.1", temperature=0.7, response_format={"type": "json_object"})
    print("<----- Successfully received response from Fallback AI.")
    return _clean_and_parse_json(chat_completion.choices[0].message.content)


# --- UPDATED PUBLIC ORCHESTRATOR FUNCTION ---
def get_holistic_analysis(user_idea: str, matched_patents: List[MatchedPatent]) -> HolisticAnalysis:
    """
    Orchestrates the AI landscape analysis with a primary/fallback system
    and now includes a post-processing quality validation step.
    """
    try:
        # --- ATTEMPT 1: PRIMARY AI (GEMINI) ---
        print("\n--- Attempting Primary AI: Gemini ---")
        analysis_dict = _get_gemini_analysis(user_idea, matched_patents)
        analysis = HolisticAnalysis(**analysis_dict)
        _validate_analysis_quality(analysis) # <-- NEW QUALITY CHECK
        print("✅ Primary AI (Gemini) Succeeded with High Quality.")
        return analysis

    except Exception as gemini_error:
        # --- PRIMARY AI FAILED (API Error, JSON Error, OR Quality Error) ---
        print("\n" + "!"*25 + " PRIMARY AI FAILED " + "!"*25)
        print(f"Reason: {type(gemini_error).__name__} - {gemini_error}")
        print("Attempting fallback...")
        print("!"*70 + "\n")
        
        try:
            # --- ATTEMPT 2: FALLBACK AI (TOGETHER AI) ---
            print("\n--- Attempting Fallback AI: Together AI ---")
            analysis_dict = _get_togetherai_analysis(user_idea, matched_patents)
            analysis = HolisticAnalysis(**analysis_dict)
            _validate_analysis_quality(analysis) # <-- NEW QUALITY CHECK
            print("✅ Fallback AI (Together AI) Succeeded with High Quality.")
            return analysis
            
        except Exception as fallback_error:
            # --- FALLBACK AI ALSO FAILED ---
            print("\n" + "="*25 + " FALLBACK AI FAILED " + "="*25)
            print(f"Reason: {type(fallback_error).__name__} - {fallback_error}")
            traceback.print_exc()
            print("="*70 + "\n")
            raise Exception("Both primary and fallback AIs failed to produce a quality analysis.") from fallback_error