OPENAI_API_KEY = "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" 

# Configurações do sistema
SYSTEM_CONFIG = {
    "modes": {
        "local": " IA Local (LM Studio)",
        "online": " IA Online (OpenAI GPT-3.5)"
    },
    "default_mode": "auto",
    "openai_model": "gpt-3.5-turbo",
    "openai_timeout": 30,
    "lm_studio_url": "http://localhost:1234/v1/chat/completions",
    "lm_model": "deepseek-coder"
}