from langchain_community.chat_models import ChatOllama
from src.config import OLLAMA_BASE_URL, OLLAMA_MODEL, LLM_TEMPERATURE, LLM_MAX_TOKENS
from src.logging_config import logger

def create_llm():
    """Create and return ChatOllama LLM instance."""
    try:
        llm = ChatOllama(
            base_url=OLLAMA_BASE_URL,
            model=OLLAMA_MODEL,
            temperature=LLM_TEMPERATURE,
            num_ctx=4096,
            top_k=40,
            top_p=0.9,
        )
        logger.info(f"Initialized ChatOllama: {OLLAMA_MODEL} (temp={LLM_TEMPERATURE})")
        return llm
    except Exception as e:
        logger.error(f"Failed to initialize LLM: {e}")
        raise
