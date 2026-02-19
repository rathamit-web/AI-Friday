import logging
import os
from src.config import LOG_LEVEL, LOG_FILE

# Configure logging
os.makedirs(os.path.dirname(LOG_FILE) if LOG_FILE else "output", exist_ok=True)

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE) if LOG_FILE else logging.NullHandler(),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
