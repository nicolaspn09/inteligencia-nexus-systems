import os
from dotenv import load_dotenv


load_dotenv()

EVOLUTION_API_URL = os.getenv("EVOLUTION_API_URL")
EVOLUTION_INSTANCE_NAME = os.getenv("EVOLUTION_INSTANCE_NAME")
EVOLUTION_API_KEY = os.getenv("EVOLUTION_API_KEY")
VECTOR_STORE_PATH = os.getenv("VECTOR_STORE_PATH") # Caminho para criar o banco de dados vector store
RAG_FILES_DIR = os.getenv("RAG_FILES_DIR") # Local onde ficam os arquivos para o RAG
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY") # Chave da API do HuggingFace
GROQ_API_KEY = os.getenv("GROQ_API_KEY") # Chave da API do Groq
GROQ_MODEL = os.getenv("GROQ_MODEL") # Nome do modelo do Groq
GROQ_TEMPERATURE = os.getenv("GROQ_TEMPERATURE") # Temperatura do modelo do Groq
AI_CONTEXTUALIZE_PROMPT = os.getenv("AI_CONTEXTUALIZE_PROMPT") # Prompt para contextualizar a resposta do AI
AI_SYSTEM_PROMPT = os.getenv("AI_SYSTEM_PROMPT") # Prompt para o sistema do AI
REDIS_URL = os.getenv("CACHE_REDIS_URI") # URL do Redis
BUFFER_KEY_SUFIX = os.getenv("BUFFER_KEY_SUFIX")
DEBOUNCE_SECONDS = os.getenv("DEBOUNCE_SECONDS")
BUFFER_TTL = os.getenv("BUFFER_TTL")