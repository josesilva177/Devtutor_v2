import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    LM_STUDIO_URL = os.getenv("LM_STUDIO_URL", "http://localhost:1234/v1/chat/completions")
    OPENAI_MODEL = "gpt-3.5-turbo"
    DEFAULT_MODE = "auto"
    TIMEOUT = 30