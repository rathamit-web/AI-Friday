import json
import time
from typing import Dict, Any, Optional, List
from src.prompt_library import get_prompt_template
from src.llm import create_llm
from src.vectorstore import retrieve_documents
from src.schemas import validate_output, SCHEMA_MODELS
from src.security import redact_pii
from src.logging_config import logger
from src.config import RETRIEVAL_TOP_K

class RAGAgent:
    """Agent for running RAG and direct LLM pipelines."""
    
    def __init__(self, vectorstore=None):
        self.vectorstore = vectorstore
        self.llm = create_llm()
    
    def run_rag(
        self,
        query: str,
        schema_type: str,
        use_rag: bool = True,
        num_context: int = RETRIEVAL_TOP_K
    ) -> Dict[str, Any]:
        """Run RAG pipeline with context retrieval."""
        start_time = time.time()
        result = {
            'query': query,
            'schema_type': schema_type,
            'mode': 'rag' if use_rag else 'direct',
            'result': None,
            'context_used': [],
            'valid_output': False,
            'latency_s': 0,
            'error': None
        }
        
        try:
            # Retrieve context
            context_docs = []
            if use_rag and self.vectorstore:
                context_docs = retrieve_documents(self.vectorstore, query, k=num_context)
                result['context_used'] = [
                    {
                        'content': doc['content'][:200],
                        'source': doc['metadata'].get('source', 'unknown'),
                        'score': doc['score']
                    }
                    for doc in context_docs
                ]
            
            # Format context
            context_text = "\n".join([doc['content'] for doc in context_docs])
            
            # Get prompt template
            prompt_template = get_prompt_template(schema_type)
            
            # Build full prompt
            if use_rag and context_text:
                full_prompt = prompt_template.replace("{{context}}", context_text)
                full_prompt += f"\n\nQUERY: {query}"
            else:
                full_prompt = prompt_template + f"\n\nQUERY: {query}"
            
            # Call LLM
            response = self.llm.invoke(full_prompt)
            response_text = response.content if hasattr(response, 'content') else str(response)
            
            # Parse JSON output
            try:
                # Extract JSON from response
                json_str = response_text.strip()
                if json_str.startswith('```json'):
                    json_str = json_str[7:-3]
                elif json_str.startswith('```'):
                    json_str = json_str[3:-3]
                
                result['result'] = json.loads(json_str)
                result['valid_output'] = validate_output(result['result'], schema_type)
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse JSON from LLM response: {response_text[:100]}")
                result['error'] = "Failed to parse JSON from LLM response"
        
        except Exception as e:
            logger.error(f"Error in RAG pipeline: {e}")
            result['error'] = str(e)
        
        result['latency_s'] = time.time() - start_time
        return result
    
    def run_direct(
        self,
        query: str,
        schema_type: str,
        input_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Run direct LLM without retrieval."""
        start_time = time.time()
        result = {
            'query': query,
            'schema_type': schema_type,
            'mode': 'direct',
            'result': None,
            'valid_output': False,
            'latency_s': 0,
            'error': None
        }
        
        try:
            prompt_template = get_prompt_template(schema_type)
            full_prompt = prompt_template + f"\n\nINPUT: {json.dumps(input_data or {'text': query})}"
            
            response = self.llm.invoke(full_prompt)
            response_text = response.content if hasattr(response, 'content') else str(response)
            
            try:
                json_str = response_text.strip()
                if json_str.startswith('```json'):
                    json_str = json_str[7:-3]
                elif json_str.startswith('```'):
                    json_str = json_str[3:-3]
                
                result['result'] = json.loads(json_str)
                result['valid_output'] = validate_output(result['result'], schema_type)
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse JSON: {response_text[:100]}")
                result['error'] = "Failed to parse JSON"
        
        except Exception as e:
            logger.error(f"Error in direct pipeline: {e}")
            result['error'] = str(e)
        
        result['latency_s'] = time.time() - start_time
        return result
    
    def run_and_validate(
        self,
        query: str,
        schema_type: str,
        use_rag: bool = True
    ) -> Dict[str, Any]:
        """Run pipeline and validate output."""
        if use_rag and self.vectorstore:
            result = self.run_rag(query, schema_type, use_rag=True)
        else:
            result = self.run_direct(query, schema_type)
        
        if not result['valid_output'] and result['result']:
            logger.warning(f"Output failed validation for schema {schema_type}")
        
        return result
