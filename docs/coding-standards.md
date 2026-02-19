# Python Coding Standards

## Project Standards

This project follows PEP 8 with these specifics:

### Formatting
- **Indentation**: 4 spaces (no tabs)
- **Line Length**: 100 characters max (hard limit)
- **Imports**: Group in order: stdlib, third-party, local
- **Docstrings**: Google-style or triple-quoted

### Naming Conventions

| Type | Convention | Example |
|------|-----------|---------|
| Constants | UPPER_SNAKE_CASE | `CHUNK_SIZE`, `OLLAMA_MODEL` |
| Functions | lower_snake_case | `load_csv_tasks()`, `run_rag()` |
| Classes | PascalCase | `RAGAgent`, `ClassificationOutput` |
| Variables | lower_snake_case | `vectorstore`, `result_dict` |
| Privates | _leading_underscore | `_internal_helper()` |

### Code Organization

#### Imports
```python
# Standard library
import json
import os
from pathlib import Path

# Third-party
from pydantic import BaseModel
from langchain_community.llms import ChatOllama

# Local imports
from src.config import CHUNK_SIZE
from src.logging_config import logger
```

#### Functions
```python
def load_csv_tasks(csv_path: str) -> List[Dict[str, Any]]:
    """Load and parse CSV task file.
    
    Args:
        csv_path: Path to CSV file
        
    Returns:
        List of task dictionaries
        
    Raises:
        FileNotFoundError: If csv_path doesn't exist
    """
```

#### Classes
```python
class RAGAgent:
    """Manages RAG and direct LLM pipelines."""
    
    def __init__(self, vectorstore=None):
        """Initialize agent with optional vectorstore."""
        self.vectorstore = vectorstore
        self.llm = create_llm()
    
    def run_rag(self, query: str, schema_type: str) -> Dict[str, Any]:
        """Run RAG pipeline with context retrieval."""
```

## Type Hints

Always use type hints:

```python
# ✅ Good
def process_results(results: List[Dict[str, Any]]) -> float:
    """Calculate average latency."""
    return sum(r['latency'] for r in results) / len(results)

# ❌ Bad
def process_results(results):
    """Calculate average latency."""
    return sum(r['latency'] for r in results) / len(results)
```

## Error Handling

```python
# ✅ Good - Specific exceptions
try:
    with open(file_path, 'r') as f:
        data = json.load(f)
except FileNotFoundError:
    logger.error(f"File not found: {file_path}")
    return []
except json.JSONDecodeError:
    logger.error(f"Invalid JSON in {file_path}")
    return []

# ❌ Bad - Bare exception
try:
    with open(file_path, 'r') as f:
        data = json.load(f)
except:
    return []
```

## Logging

Use structured logging:

```python
from src.logging_config import logger

# ✅ Good
logger.info(f"Loaded {len(documents)} documents from {kb_dir}")
logger.warning(f"Failed to parse JSON: {response_text[:100]}")
logger.error(f"Error in RAG pipeline: {e}", exc_info=True)

# ❌ Bad
print("Done loading")
print(f"Error: {e}")
```

## Configuration

```python
# ✅ Good - Use config module
from src.config import CHUNK_SIZE, LLM_TEMPERATURE

chunk_size = CHUNK_SIZE
temperature = LLM_TEMPERATURE

# ❌ Bad - Hardcoded values
chunk_size = 900
temperature = 0.3
```

## Testing Standards

All modules should have basic smoke tests:

```python
# tests/test_module.py
import pytest
from src.module_name import function_name

class TestModuleName:
    """Test module_name.py"""
    
    def test_function_basic(self):
        """Test basic functionality."""
        result = function_name("test")
        assert result is not None
    
    def test_function_edge_case(self):
        """Test edge case."""
        result = function_name("")
        assert result == []

def test_imports():
    """Verify all imports work."""
    from src import config, agent, metrics
    assert config is not None
```

Run tests:
```powershell
python -m pytest tests/ -v
```

## Documentation

### Module Docstrings
```python
"""
Module for loading and parsing various data formats.

Supports CSV, JSON, TXT, and PDF files.
Uses appropriate parsers for each format and normalizes output.
"""
```

### Function Docstrings
```python
def load_kb_directory(kb_dir: str) -> List[Dict[str, str]]:
    """Load all knowledge base files from directory.
    
    Scans kb_dir recursively for PDF, TXT, JSON, and CSV files.
    Returns normalized document objects with metadata.
    
    Args:
        kb_dir: Path to knowledge base directory
        
    Returns:
        List of dicts with keys: id, source, content
        
    Raises:
        FileNotFoundError: If kb_dir doesn't exist
    """
```

### Class Docstrings
```python
class RAGAgent:
    """Agent for running RAG and direct LLM pipelines.
    
    Manages vector store retrieval, context injection, and LLM calls.
    Supports both RAG mode (with context) and direct mode.
    
    Attributes:
        vectorstore: Chroma vector store instance
        llm: ChatOllama LLM instance
    """
```

## Common Patterns

### Data Processing Pipeline
```python
def process_documents(raw_docs: List[str]) -> List[Dict[str, Any]]:
    """Process documents through the full pipeline."""
    # 1. Normalize
    docs = [normalize(d) for d in raw_docs]
    
    # 2. Chunk
    chunks = chunk_documents(docs)
    
    # 3. Validate
    valid_chunks = [c for c in chunks if len(c['content']) > 0]
    
    # 4. Log progress
    logger.info(f"Processed {len(valid_chunks)} chunks from {len(raw_docs)} docs")
    
    return valid_chunks
```

### Context Manager for Resources
```python
from contextlib import contextmanager

@contextmanager
def timer(name: str):
    """Context manager to measure execution time."""
    import time
    start = time.time()
    try:
        yield
    finally:
        elapsed = time.time() - start
        logger.info(f"{name} took {elapsed:.2f}s")

# Usage:
with timer("data loading"):
    data = load_kb_directory("data/kb")
```

### Pydantic Model Validation
```python
from pydantic import BaseModel, Field, validator

class TaskInput(BaseModel):
    """Validated task input."""
    query: str = Field(..., min_length=1, max_length=500)
    schema_type: str = Field(..., regex="^(classification|extraction|qna)$")
    top_k: int = Field(default=5, ge=1, le=20)
    
    @validator('schema_type')
    def validate_schema(cls, v):
        if v not in ['classification', 'extraction', 'qna']:
            raise ValueError(f"Unknown schema: {v}")
        return v
```

## Performance Considerations

### Avoid
```python
# ❌ N+1 queries
for doc in documents:
    metadata = retrieve_metadata(doc['id'])

# ❌ Creating new objects in loops
results = []
for item in large_list:
    results.append(dict(item))  # Slow for large lists

# ❌ String concatenation in loops
text = ""
for chunk in chunks:
    text += chunk  # O(n²) complexity
```

### Use Instead
```python
# ✅ Batch operations
metadatas = retrieve_metadata([d['id'] for d in documents])

# ✅ List comprehensions
results = [dict(item) for item in large_list]

# ✅ String joining
text = "".join(chunks)  # O(n) complexity
```

## Debugging Tips

### Use Logger Strategically
```python
logger.debug(f"Processing chunk {i}/{total}")  # Verbose
logger.info(f"Loaded {n} documents")            # Normal
logger.warning(f"Low confidence: {score}")     # Attention
logger.error(f"Failed: {e}")                   # Problem
```

### Enable Debug Logging
```powershell
# In .env
LOG_LEVEL=DEBUG

# Or in code
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Use Breakpoints
```python
# In code:
import pdb; pdb.set_trace()  # Pauses execution

# Or:
breakpoint()  # Python 3.7+
```

## CI/CD Checklist

Before committing:

```powershell
# 1. Format code
python -m black src/ tests/

# 2. Lint
python -m pylint src/

# 3. Type check
python -m mypy src/

# 4. Run tests
python -m pytest tests/ -v

# 5. Verify imports
python -c "from src import config, agent, metrics; print('✅')"
```

## File Organization

```
src/
├── __init__.py           # Empty or imports
├── config.py             # Configuration
├── logging_config.py     # Logging setup
├── security.py           # PII handling
├── data_loader.py        # Data loading
├── chunking.py           # Document chunking
├── embeddings.py         # Embedding models
├── vectorstore.py        # Vector DB
├── llm.py                # LLM wrapper
├── agent.py              # RAG agent
├── prompt_library.py     # Prompt templates
├── schemas.py            # Pydantic models
├── metrics.py            # Evaluation metrics
├── metrics_report.py     # Report generation
├── main.py               # CLI entry point
└── evaluate.py           # Evaluation runner

tests/
├── test_basic.py         # Smoke tests
└── test_integration.py   # Integration tests
```

## Review Checklist

- [ ] Type hints on all functions
- [ ] Docstrings for all public functions/classes
- [ ] Error handling with specific exceptions
- [ ] Logging at appropriate levels
- [ ] No hardcoded values (use config)
- [ ] Tests pass: `pytest tests/`
- [ ] Imports organized and clean
- [ ] No unused imports
- [ ] Line length <100 chars
- [ ] Meaningful variable names
