import json
import traceback
from openai import OpenAI
from ..core import config

if not config.TOGETHER_API_KEY:
    raise ValueError("FATAL ERROR: TOGETHER_API_KEY is not defined in your .env file. The application cannot start.")

client = OpenAI(
  api_key=config.TOGETHER_API_KEY,
  base_url='https://api.together.xyz/v1',
  timeout=30.0, # Add a timeout to prevent hanging
)

def get_comparison(user_idea: str, patent_abstract: str) -> dict:
    prompt = f"""
    You are a meticulous Patent Analyst AI. Your sole task is to provide a detailed, logical, and factual comparative analysis between a "User's New Idea" and an "Existing Patent Abstract". Your language must be professional, clear, and grammatically perfect. Your entire output MUST be a single, valid JSON object following this exact format:
    {{
      "noveltyScore": <A number from 1 (very similar) to 10 (highly distinct)>,
      "keySimilarities": ["A list of strings detailing similarities."],
      "keyDifferences": ["A list of strings detailing differences."],
      "expertOpinion": "A concluding paragraph for a non-expert, summarizing your findings."
    }}
    ---
    DATA FOR ANALYSIS:
    <USER_IDEA>{user_idea}</USER_IDEA>
    <PATENT_ABSTRACT>{patent_abstract}</PATENT_ABSTRACT>
    """

    try:
        print("-----> Sending new analysis request to Together AI...")
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            temperature=0.7,
            response_format={"type": "json_object"},
        )
        print("<----- Successfully received response from Together AI.")
        response_text = chat_completion.choices[0].message.content
        return json.loads(response_text)
    except Exception as e:
        print("\n" + "="*80)
        print("!!!!!!!!!   CRITICAL ERROR DURING TOGETHER AI API CALL   !!!!!!!!!")
        print(f"This is the definitive point of failure. The issue is likely with your API Key, network connection, or an outage at Together AI.")
        print(f"Error Type:    {type(e).__name__}")
        print(f"Error Details: {e}")
        traceback.print_exc()
        print("="*80 + "\n")
        # Re-raise the exception to send a 500 error back to the frontend
        raise e