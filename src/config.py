import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Ollama Configuration
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
OLLAMA_EMBEDDING_MODEL = os.getenv("OLLAMA_EMBEDDING_MODEL", "gte-large")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# LLM Parameters
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", 0.3))
LLM_TOP_P = float(os.getenv("LLM_TOP_P", 0.9))
LLM_TOP_K = int(os.getenv("LLM_TOP_K", 40))
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", 2048))

# Chunking Configuration
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 900))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 200))

# Retrieval Configuration
RETRIEVAL_TOP_K = int(os.getenv("RETRIEVAL_TOP_K", 5))
MIN_SIMILARITY_SCORE = float(os.getenv("MIN_SIMILARITY_SCORE", 0.3))

# Vector Store
VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", "output/chroma_db")
VECTOR_DB_COLLECTION = os.getenv("VECTOR_DB_COLLECTION", "knowledge_base")

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "output/app.log")

# Evaluation
EVAL_METRICS = os.getenv("EVAL_METRICS", "schema_pass_rate,latency,retrieval_accuracy").split(",")
BASELINE_MODEL = os.getenv("BASELINE_MODEL", "basic_template")

# PII Detection
ENABLE_PII_DETECTION = os.getenv("ENABLE_PII_DETECTION", "true").lower() == "true"
REDACT_EMAIL = os.getenv("REDACT_EMAIL", "true").lower() == "true"
REDACT_PHONE = os.getenv("REDACT_PHONE", "true").lower() == "true"
REDACT_SSN = os.getenv("REDACT_SSN", "true").lower() == "true"

# Ensure output directories exist
os.makedirs(os.path.dirname(VECTOR_DB_PATH), exist_ok=True)
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
