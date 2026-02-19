# RAG Pipeline Architecture

## System Overview

```
┌─────────────────┐
│   Input Data    │
│ (CSV/JSON/PDF)  │
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│   Data Loader           │
│ (parse all formats)     │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│   Chunking              │
│ (900 chars, 200 overlap)│
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│   Embeddings            │
│ (gte-large via Ollama)  │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│   Vector Store          │
│ (Chroma persistent)     │
└────────┬────────────────┘
         │
    ┌────┴───────────────┐
    │ At Runtime:        │
    │ User Query         │
    └────┬───────────────┘
         │
         ▼
┌─────────────────────────┐
│   Query Embeddings      │
│ (same as KB docs)       │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│   Similarity Search     │
│ (top-k=5 retrieval)     │
└────────┬────────────────┘
         │
         ▼
┌──────────────────────────────┐
│   Context Injection          │
│ (retrieved docs + prompt)    │
└────────┬─────────────────────┘
         │
         ▼
┌──────────────────────────────┐
│   LLM (ChatOllama)           │
│ (temp=0.3, deterministic)    │
└────────┬─────────────────────┘
         │
         ▼
┌──────────────────────────────┐
│   JSON Output Parsing        │
│ (extract & validate)         │
└────────┬─────────────────────┘
         │
         ▼
┌──────────────────────────────┐
│   Schema Validation          │
│ (Pydantic models)            │
└────────┬─────────────────────┘
         │
         ▼
┌──────────────────────────────┐
│   Results                    │
│ (JSON + metrics)             │
└──────────────────────────────┘
```

## Component Details

### 1. Data Loader (`src/data_loader.py`)
- **Input Formats**: CSV, JSON, TXT, PDF
- **Output**: Standardized document objects with metadata
- **Key Function**: `load_kb_directory()` - Loads all KB files

### 2. Chunking (`src/chunking.py`)
- **Algorithm**: RecursiveCharacterTextSplitter
- **Chunk Size**: 900 characters
- **Overlap**: 200 characters
- **Separators**: Newlines → spaces → characters
- **Key Function**: `chunk_documents()` - Splits docs into overlapping chunks

### 3. Embeddings (`src/embeddings.py`)
- **Model**: gte-large (via Ollama)
- **Dimension**: 1024-d vectors
- **Purpose**: Convert text → vector space
- **Key Function**: `create_embeddings()` - Initialize embeddings

### 4. Vector Store (`src/vectorstore.py`)
- **Backend**: Chroma (persistent, local)
- **Location**: `output/chroma_db/`
- **Collection**: "knowledge_base"
- **Key Functions**:
  - `create_vector_store()` - Initialize or load
  - `add_documents_to_store()` - Index chunks
  - `retrieve_documents()` - Search similarity

### 5. LLM (`src/llm.py`)
- **Model**: llama3.2 (configurable: gemma, qwen, etc.)
- **Temperature**: 0.3 (deterministic outputs)
- **Max Tokens**: 2048
- **Key Function**: `create_llm()` - Initialize ChatOllama

### 6. Agent (`src/agent.py`)
- **Class**: `RAGAgent`
- **Methods**:
  - `run_rag()` - With context retrieval
  - `run_direct()` - Direct LLM without retrieval
  - `run_and_validate()` - With schema validation
- **Output**: Structured JSON + metadata

### 7. Schemas (`src/schemas.py`)
- **Models**: Pydantic BaseModel subclasses
- **Coverage**: 6 schema types (classification, extraction, QnA, etc.)
- **Validation**: Automatic JSON schema enforcement
- **Key Function**: `validate_output()` - Check output against schema

## Data Flow for a Single Query

### Phase 1: Indexing (One-time)
```
Knowledge Base Files (data/kb/)
    ↓
[Data Loader] Parse CSV/JSON/PDF/TXT
    ↓
[Chunking] Split with overlap (900/200)
    ↓
[Embeddings] Convert to vectors (gte-large)
    ↓
[Vector Store] Save to Chroma (output/chroma_db/)
```

### Phase 2: Query Processing (Per query)
```
User Query
    ↓
[Embeddings] Convert query to vector
    ↓
[Vector Store] Find top-5 similar chunks
    ↓
[Prompt Library] Get template for schema
    ↓
[Context Injection] Add context to prompt
    ↓
[LLM] Call ChatOllama with context
    ↓
[JSON Parser] Extract JSON from response
    ↓
[Schema Validator] Validate against Pydantic
    ↓
[Metrics] Calculate latency, confidence, etc.
    ↓
Result JSON + Metadata
```

## Configuration

All configuration via `.env`:

```env
# Model Selection
OLLAMA_MODEL=llama3.2              # LLM model
OLLAMA_EMBEDDING_MODEL=gte-large   # Embedding model
OLLAMA_BASE_URL=http://localhost:11434

# LLM Parameters
LLM_TEMPERATURE=0.3                # Low for determinism
LLM_MAX_TOKENS=2048                # Response length
LLM_TOP_P=0.9                       # Nucleus sampling
LLM_TOP_K=40                        # Token filter

# Chunking
CHUNK_SIZE=900                      # Characters per chunk
CHUNK_OVERLAP=200                   # Overlap between chunks

# Retrieval
RETRIEVAL_TOP_K=5                   # Docs to retrieve
MIN_SIMILARITY_SCORE=0.3            # Score threshold

# Storage
VECTOR_DB_PATH=output/chroma_db     # Chroma location
VECTOR_DB_COLLECTION=knowledge_base
```

## Performance Characteristics

| Component | Time (approx) | Bottleneck |
|-----------|---------------|-----------|
| Embedding query | 50-100ms | Ollama network |
| Vector search | 10-50ms | Index size |
| LLM inference | 1-5s | Model size, context length |
| JSON parsing | 1-10ms | Response complexity |
| **Total** | **~2-6s per query** | LLM inference |

## Key Design Decisions

1. **Local Models Only**: No API calls, full privacy, offline capable
2. **Temperature=0.3**: Ensures consistent, valid JSON outputs
3. **Persistent Chroma**: Fast re-initialization for rapid iteration
4. **Pydantic Validation**: Strong output typing, automatic schema enforcement
5. **Modular Architecture**: Easy to swap components (models, schemas, etc.)
6. **Context Grounding**: RAG prompt explicitly forces use of provided context
7. **Confidence Levels**: High/Medium/Low assessment in every response
8. **Error Handling**: Graceful degradation with fallback to "insufficient_context"

## Extending the Pipeline

### Add New Schema Type
1. Create Pydantic model in `src/schemas.py`
2. Add prompt template in `src/prompt_library.py`
3. Register in `SCHEMA_MODELS` dict
4. Add metrics in `src/metrics.py`

### Switch LLM Model
Change in `.env`:
```env
OLLAMA_MODEL=gemma          # Faster, 2B params
OLLAMA_MODEL=qwen           # Multilingual, 7B params
OLLAMA_MODEL=llama2:70b     # More capable, slower
```

### Adjust Chunking Strategy
Edit `src/chunking.py`:
```python
CHUNK_SIZE = 500            # Smaller chunks for retrieval
CHUNK_OVERLAP = 100         # Less overlap, faster processing
```

### Use Different Vector Store
Swap in `src/vectorstore.py`:
```python
# Replace Chroma with FAISS for scalability
from langchain_community.vectorstores import FAISS
```

## Troubleshooting

**Issue**: Slow queries
- **Fix**: Use gte-large embeddings, keep CHUNK_SIZE reasonable (~900)

**Issue**: Low accuracy
- **Fix**: Improve KB quality, increase RETRIEVAL_TOP_K to 7-10

**Issue**: Inconsistent outputs
- **Fix**: Lower LLM_TEMPERATURE below 0.5, check for floating-point randomness

**Issue**: Memory issues
- **Fix**: Reduce CHUNK_SIZE, use smaller LLM, batch process
