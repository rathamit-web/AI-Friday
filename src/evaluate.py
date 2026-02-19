import json
from pathlib import Path
from typing import List, Dict, Any
from src.metrics_report import generate_metrics_report, generate_json_metrics
from src.logging_config import logger

def run_evaluation(results_path: str, output_dir: str = 'output'):
    """Run evaluation on results file."""
    
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    try:
        with open(results_path, 'r') as f:
            results = json.load(f)
    except Exception as e:
        logger.error(f"Failed to load results: {e}")
        return
    
    # Generate reports
    markdown_report = generate_metrics_report(
        results,
        output_path=f'{output_dir}/metrics_report.md'
    )
    
    json_metrics = generate_json_metrics(
        results,
        output_path=f'{output_dir}/metrics.json'
    )
    
    logger.info(f"Evaluation complete. Reports saved to {output_dir}")
    print(markdown_report)

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Evaluate results')
    parser.add_argument('--results', required=True, help='Results JSON file')
    parser.add_argument('--output-dir', default='output', help='Output directory')
    
    args = parser.parse_args()
    run_evaluation(args.results, args.output_dir)
