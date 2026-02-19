from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.config import CHUNK_SIZE, CHUNK_OVERLAP
from src.logging_config import logger

def create_chunker():
    """Create and return a text splitter with configured parameters."""
    return RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", " ", ""]
    )

def chunk_documents(documents: list, splitter=None) -> list:
    """Chunk documents using recursive character splitter."""
    if splitter is None:
        splitter = create_chunker()
    
    chunks = []
    for doc in documents:
        doc_chunks = splitter.split_text(doc.get('content', ''))
        for i, chunk in enumerate(doc_chunks):
            chunks.append({
                'id': f"{doc.get('id', 'unknown')}_{i}",
                'source': doc.get('source', 'unknown'),
                'content': chunk,
                'chunk_index': i
            })
    
    logger.info(f"Created {len(chunks)} chunks from {len(documents)} documents")
    return chunks
