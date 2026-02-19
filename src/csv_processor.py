import csv
import json
from typing import List, Dict, Any

def load_csv_tasks(csv_path: str) -> List[Dict[str, Any]]:
    '''Load tasks from CSV file.'''
    tasks = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            task = {
                'task_id': row.get('task_id'),
                'task_type': row.get('task_type'),
                'input': row.get('input_text'),
                'metadata': {k: v for k, v in row.items() 
                           if k not in ['task_id', 'task_type', 'input_text']}
            }
            tasks.append(task)
    return tasks

def save_results_csv(results: List[Dict[str, Any]], output_path: str):
    '''Save results to CSV.'''
    if not results:
        return
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        fieldnames = ['task_id', 'task_type', 'result_json', 'latency_s']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in results:
            writer.writerow({
                'task_id': r['task_id'],
                'task_type': r['task_type'],
                'result_json': json.dumps(r['result']),
                'latency_s': r.get('latency_s', 0)
            })
