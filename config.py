"""Load config from environment."""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
TOPICS_EXCEL = DATA_DIR / "topics.xlsx"
OUTPUT_DIR = BASE_DIR / "output"

# API keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "").strip()

# OpenAI
OPENAI_CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")
DALLE_MODEL = "dall-e-3"
DALLE_SIZE = "1792x1024"  # landscape, good for LinkedIn
DALLE_QUALITY = "standard"


def ensure_dirs():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
