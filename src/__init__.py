"""RAG Hackathon Starter Kit - Retrieval Augmented Generation System"""

__version__ = "1.0.0"

# Core modules
from src.config import *
from src.logging_config import logger
from src.agent import RAGAgent
from src.metrics import schema_pass_rate, latency_stats, error_analysis
from src.prompt_library import get_prompt_template, list_available_schemas

__all__ = [
    'RAGAgent',
    'logger',
    'get_prompt_template',
    'list_available_schemas',
    'schema_pass_rate',
    'latency_stats',
    'error_analysis'
]
