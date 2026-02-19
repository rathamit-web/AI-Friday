import pytest
import json
from pathlib import Path
from src.config import OLLAMA_BASE_URL
from src.data_loader import load_csv, load_txt, load_kb_directory
from src.chunking import chunk_documents
from src.schemas import validate_output, SCHEMA_MODELS
from src.prompt_library import get_prompt_template, list_available_schemas

class TestConfig:
    """Test configuration loading."""
    def test_ollama_url(self):
        assert OLLAMA_BASE_URL is not None
        assert 'localhost' in OLLAMA_BASE_URL or '127.0.0.1' in OLLAMA_BASE_URL

class TestDataLoading:
    """Test data loading functionality."""
    def test_load_csv(self):
        csv_path = 'data/kb/sample_kb.csv'
        if Path(csv_path).exists():
            data = load_csv(csv_path)
            assert isinstance(data, list)
            assert len(data) > 0

    def test_load_txt(self):
        txt_path = 'data/kb/sample_kb.txt'
        if Path(txt_path).exists():
            data = load_txt(txt_path)
            assert isinstance(data, str)

class TestPromptLibrary:
    """Test prompt library functionality."""
    def test_available_schemas(self):
        schemas = list_available_schemas()
        assert len(schemas) > 0
        assert 'classification' in schemas
        assert 'generic_extraction' in schemas

    def test_get_prompt_template(self):
        for schema in list_available_schemas():
            template = get_prompt_template(schema)
            assert isinstance(template, str)
            assert len(template) > 0

class TestSchemas:
    """Test schema validation."""
    def test_classification_schema(self):
        output = {
            "primary_category": "positive",
            "confidence_primary": "high",
            "secondary_categories": [],
            "confidence_scores": {"positive": 0.95},
            "reasoning": "Text contains positive words",
            "uncertainty_notes": None
        }
        assert validate_output(output, "classification")

    def test_extraction_schema(self):
        output = {
            "entities": [
                {"value": "Test", "type": "name", "confidence": "high", "source_snippet": "Test entity"}
            ],
            "extraction_summary": "Extracted test entity",
            "notes": None
        }
        assert validate_output(output, "generic_extraction")

    def test_invalid_schema(self):
        output = {"invalid": "data"}
        assert not validate_output(output, "classification")

class TestChunking:
    """Test document chunking."""
    def test_chunk_documents(self):
        documents = [
            {
                'id': 'test',
                'source': 'test.txt',
                'content': 'A' * 5000  # Large content
            }
        ]
        chunks = chunk_documents(documents)
        assert len(chunks) > 1
        assert all('content' in chunk for chunk in chunks)

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
