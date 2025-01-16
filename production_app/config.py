import os
from dotenv import load_dotenv

# Load environment variables from .env if available
load_dotenv()

class Config:
    # Example: set your API key for Gemini
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY_HERE")

    # Database settings (you can adjust as needed)
    DB_URL = os.getenv("DB_URL", "sqlite:///./orders.db")
