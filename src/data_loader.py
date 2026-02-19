import json
import csv
from pathlib import Path
from typing import List, Dict, Any
import pdfplumber
from src.logging_config import logger

def load_json(file_path: str) -> List[Dict[str, Any]]:
    """Load data from JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading JSON from {file_path}: {e}")
        return []

def load_csv(file_path: str) -> List[Dict[str, Any]]:
    """Load data from CSV file."""
    try:
        rows = []
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(row)
        return rows
    except Exception as e:
        logger.error(f"Error loading CSV from {file_path}: {e}")
        return []

def load_txt(file_path: str) -> str:
    """Load data from text file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error loading text from {file_path}: {e}")
        return ""

def load_pdf(file_path: str) -> str:
    """Load data from PDF file."""
    try:
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        return text
    except Exception as e:
        logger.error(f"Error loading PDF from {file_path}: {e}")
        return ""

def load_kb_directory(kb_dir: str) -> List[Dict[str, str]]:
    """Load all knowledge base files from directory."""
    documents = []
    kb_path = Path(kb_dir)
    
    if not kb_path.exists():
        logger.warning(f"KB directory does not exist: {kb_dir}")
        return documents
    
    for file_path in kb_path.glob('**/*'):
        if file_path.is_file():
            doc_id = file_path.stem
            
            if file_path.suffix == '.pdf':
                content = load_pdf(str(file_path))
            elif file_path.suffix == '.txt':
                content = load_txt(str(file_path))
            elif file_path.suffix == '.json':
                data = load_json(str(file_path))
                content = json.dumps(data)
            elif file_path.suffix == '.csv':
                data = load_csv(str(file_path))
                content = json.dumps(data)
            else:
                continue
            
            if content:
                documents.append({
                    'id': doc_id,
                    'source': str(file_path),
                    'content': content
                })
    
    logger.info(f"Loaded {len(documents)} documents from {kb_dir}")
    return documents
