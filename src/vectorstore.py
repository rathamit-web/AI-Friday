from langchain_community.vectorstores import Chroma
from src.embeddings import create_embeddings
from src.config import VECTOR_DB_PATH, VECTOR_DB_COLLECTION
from src.logging_config import logger
from pathlib import Path

def create_vector_store(embeddings=None, persist_directory=None):
    """Create or load Chroma vector store."""
    if embeddings is None:
        embeddings = create_embeddings()
    if persist_directory is None:
        persist_directory = VECTOR_DB_PATH
    
    Path(persist_directory).mkdir(parents=True, exist_ok=True)
    
    vectorstore = Chroma(
        collection_name=VECTOR_DB_COLLECTION,
        embedding_function=embeddings,
        persist_directory=persist_directory
    )
    
    logger.info(f"Initialized Chroma vector store at {persist_directory}")
    return vectorstore

def add_documents_to_store(vectorstore, chunks: list):
    """Add chunked documents to vector store."""
    try:
        texts = [chunk['content'] for chunk in chunks]
        metadatas = [
            {
                'source': chunk['source'],
                'chunk_index': chunk.get('chunk_index', 0)
            }
            for chunk in chunks
        ]
        ids = [chunk['id'] for chunk in chunks]
        
        vectorstore.add_texts(texts=texts, metadatas=metadatas, ids=ids)
        logger.info(f"Added {len(chunks)} chunks to vector store")
        return vectorstore
    except Exception as e:
        logger.error(f"Error adding documents to store: {e}")
        raise

def retrieve_documents(vectorstore, query: str, k: int = 5) -> list:
    """Retrieve top-k documents from vector store."""
    try:
        results = vectorstore.similarity_search_with_score(query, k=k)
        documents = [
            {
                'content': doc.page_content,
                'metadata': doc.metadata,
                'score': score
            }
            for doc, score in results
        ]
        return documents
    except Exception as e:
        logger.error(f"Error retrieving documents: {e}")
        return []
