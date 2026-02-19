import json
import argparse
from pathlib import Path
from src.data_loader import load_json, load_kb_directory
from src.chunking import chunk_documents
from src.vectorstore import create_vector_store, add_documents_to_store
from src.agent import RAGAgent
from src.csv_processor import load_csv_tasks, save_results_csv
from src.logging_config import logger
from src.config import VECTOR_DB_PATH

def main():
    parser = argparse.ArgumentParser(description="RAG-based hackathon solution runner")
    parser.add_argument('--index', action='store_true', help='Index knowledge base')
    parser.add_argument('--kb-dir', type=str, default='data/kb', help='Knowledge base directory')
    parser.add_argument('--process', type=str, help='Process single JSON task')
    parser.add_argument('--process-csv', type=str, help='Process CSV batch tasks')
    parser.add_argument('--schema', type=str, default='generic_extraction', help='Schema type')
    parser.add_argument('--text', type=str, help='Direct text query')
    parser.add_argument('--no-rag', action='store_true', help='Run without RAG')
    parser.add_argument('--output', type=str, default='output/results.json', help='Output file path')
    
    args = parser.parse_args()
    
    # Index knowledge base
    if args.index:
        logger.info(f"Indexing knowledge base from {args.kb_dir}")
        documents = load_kb_directory(args.kb_dir)
        chunks = chunk_documents(documents)
        
        vectorstore = create_vector_store()
        add_documents_to_store(vectorstore, chunks)
        
        logger.info(f"Successfully indexed {len(chunks)} chunks")
        return
    
    # Initialize agent
    vectorstore = create_vector_store() if not args.no_rag else None
    agent = RAGAgent(vectorstore=vectorstore)
    
    results = []
    
    # Process single task
    if args.process:
        logger.info(f"Processing single task from {args.process}")
        task = load_json(args.process)
        if isinstance(task, list):
            task = task[0]
        
        query = task.get('input') or task.get('text')
        result = agent.run_and_validate(query, args.schema, use_rag=not args.no_rag)
        results.append(result)
    
    # Process CSV batch
    if args.process_csv:
        logger.info(f"Processing CSV batch from {args.process_csv}")
        tasks = load_csv_tasks(args.process_csv)
        
        for task in tasks:
            query = task.get('input_text')
            schema = task.get('task_type', args.schema)
            result = agent.run_and_validate(query, schema, use_rag=not args.no_rag)
            result['task_id'] = task.get('task_id')
            results.append(result)
        
        # Save results as CSV
        output_path = args.output if args.output.endswith('.csv') else args.output.replace('.json', '.csv')
        save_results_csv(results, output_path)
        logger.info(f"Saved results to {output_path}")
        return
    
    # Process text query
    if args.text:
        logger.info(f"Processing text query")
        result = agent.run_and_validate(args.text, args.schema, use_rag=not args.no_rag)
        results.append(result)
    
    # Save results
    if results:
        output_dir = Path(args.output).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"Saved results to {args.output}")
        
        # Print summary
        valid_count = sum(1 for r in results if r.get('valid_output'))
        print(f"\n=== Results Summary ===")
        print(f"Total tasks: {len(results)}")
        print(f"Valid outputs: {valid_count}/{len(results)}")
        print(f"Avg latency: {sum(r.get('latency_s', 0) for r in results) / len(results):.2f}s")

if __name__ == '__main__':
    main()
