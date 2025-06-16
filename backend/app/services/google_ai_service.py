import json
import re
from functools import lru_cache
from vertexai.generative_models import GenerativeModel
from vertexai.language_models import TextEmbeddingModel

@lru_cache(maxsize=1)
def get_embedding_model():
    return TextEmbeddingModel.from_pretrained("text-embedding-004")

@lru_cache(maxsize=1)
def get_generative_model():
    return GenerativeModel("gemini-1.0-pro")

def create_embedding(text: str) -> list[float]:
    model = get_embedding_model()
    response = model.get_embeddings([text])
    return response[0].values

def get_comparison_from_gemini(user_idea: str, patent_abstract: str) -> dict:
    model = get_generative_model()
    prompt = f"""
    You are an impartial technical analyst. Your task is to compare a "User's New Idea" with an "Existing Patent Abstract".
    Analyze the texts and identify key points of similarity and dissimilarity.
    Do not offer opinions or judgments. Focus only on factual comparisons based on the text.
    Your response must be a JSON object with two keys: "similarities" and "dissimilarities". Each key must hold a list of strings, with each string being a specific point.

    Example Response Format:
    ```json
    {{
      "similarities": ["Both systems involve a method for regulating temperature.", "Both mention a rechargeable power source."],
      "dissimilarities": ["The user's idea specifies an LED screen, which is not mentioned in the patent.", "The patent describes using phase-change materials, while the user's idea implies an active heating element."]
    }}
    ```
    ---
    DATA FOR ANALYSIS:
    ---
    User's New Idea: "{user_idea}"
    Existing Patent Abstract: "{patent_abstract}"
    """
    try:
        response = model.generate_content([prompt])
        json_str_match = re.search(r'```json\s*(\{.*?\})\s*```', response.text, re.DOTALL)
        json_str = json_str_match.group(1) if json_str_match else response.text
        return json.loads(json_str)
    except Exception as e:
        print(f"CRITICAL: Gemini response parsing failed. Raw text: {response.text}. Error: {e}")
        return {"similarities": ["Error: The AI analysis could not be parsed."], "dissimilarities": ["Please try selecting the patent again."]}