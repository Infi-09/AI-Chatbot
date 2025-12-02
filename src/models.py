# src/models.py
import os

from google import genai
from dotenv import load_dotenv # type: ignore

def load_model():
    """
    Load and configure the Gemini 2.5 Flash model.
    Returns the configured model instance.
    """
    
    # Load .env
    load_dotenv(".env", override=True)
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if not GEMINI_API_KEY:
        raise RuntimeError("❌ GEMINI_API_KEY not found in .env")

    model = genai.Client(
        api_key=GEMINI_API_KEY
    )
    return model

