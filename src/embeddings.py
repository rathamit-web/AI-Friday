from langchain_community.embeddings import OllamaEmbeddings
from src.config import OLLAMA_BASE_URL, OLLAMA_EMBEDDING_MODEL
from src.logging_config import logger

def create_embeddings():
    """Create and return Ollama embeddings model."""
    try:
        embeddings = OllamaEmbeddings(
            base_url=OLLAMA_BASE_URL,
            model=OLLAMA_EMBEDDING_MODEL
        )
        logger.info(f"Initialized Ollama embeddings: {OLLAMA_EMBEDDING_MODEL}")
        return embeddings
    except Exception as e:
        logger.error(f"Failed to initialize embeddings: {e}")
        raise
