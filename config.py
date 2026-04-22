import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    LM_STUDIO_URL = os.getenv("LM_STUDIO_URL", "http://localhost:1234/v1/chat/completions")
    OPENAI_MODEL = "gpt-3.5-turbo"

    NIM_API_KEY = os.getenv("NIM_API_KEY") 
    NIM_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
    NIM_MODEL = os.getenv("NIM_MODEL", "meta/llama-3.1-8b-instruct")

    DEFAULT_MODE = "auto"
    TIMEOUT = 30