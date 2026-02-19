import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
from src.metrics import (
    schema_pass_rate, latency_stats, error_analysis,
    rag_retrieval_metrics, confidence_distribution
)

def generate_metrics_report(results: List[Dict[str, Any]], output_path: str = 'output/metrics_report.md') -> str:
    """Generate comprehensive metrics report in Markdown."""
    
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    # Calculate metrics
    pass_rate = schema_pass_rate(results)
    latency = latency_stats(results)
    errors = error_analysis(results)
    rag_metrics = rag_retrieval_metrics(results)
    confidence = confidence_distribution(results)
    
    # Generate report
    report = f"""# Evaluation Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary
- **Total Queries**: {len(results)}
- **Valid Schema Outputs**: {pass_rate:.1f}%
- **Error Rate**: {errors['error_rate']:.1f}%
- **Average Latency**: {latency['mean']:.2f}s

## Detailed Metrics

### Schema Validation
- Valid outputs: {pass_rate:.1f}%
- Invalid outputs: {100 - pass_rate:.1f}%

### Performance
- **Latency Statistics** (seconds):
  - Min: {latency['min']:.2f}s
  - Max: {latency['max']:.2f}s
  - Mean: {latency['mean']:.2f}s
  - Median: {latency['median']:.2f}s

### Errors
- **Total Errors**: {errors['total_errors']}
- **Error Rate**: {errors['error_rate']:.1f}%
- **Error Breakdown**:
"""
    
    for error_type, count in errors['error_breakdown'].items():
        report += f"  - {error_type}: {count}\n"
    
    # RAG metrics if available
    if rag_metrics:
        report += f"\n### RAG Retrieval\n"
        report += f"- High Context Coverage: {rag_metrics.get('context_coverage_high_pct', 0):.1f}%\n"
        report += f"- Medium Context Coverage: {rag_metrics.get('context_coverage_medium_pct', 0):.1f}%\n"
        report += f"- Low Context Coverage: {rag_metrics.get('context_coverage_low_pct', 0):.1f}%\n"
    
    # Confidence distribution
    report += f"\n### Confidence Distribution\n"
    report += f"- High Confidence: {confidence['high']:.1f}%\n"
    report += f"- Medium Confidence: {confidence['medium']:.1f}%\n"
    report += f"- Low Confidence: {confidence['low']:.1f}%\n"
    
    # Schema breakdown
    schema_breakdown = {}
    for r in results:
        schema = r.get('schema_type', 'unknown')
        if schema not in schema_breakdown:
            schema_breakdown[schema] = {'total': 0, 'valid': 0}
        schema_breakdown[schema]['total'] += 1
        if r.get('valid_output'):
            schema_breakdown[schema]['valid'] += 1
    
    report += f"\n### By Schema Type\n"
    for schema, counts in schema_breakdown.items():
        valid_pct = (counts['valid'] / counts['total'] * 100) if counts['total'] > 0 else 0
        report += f"- **{schema}**: {counts['valid']}/{counts['total']} valid ({valid_pct:.1f}%)\n"
    
    # Recommendations
    report += f"\n## Recommendations\n"
    if pass_rate < 80:
        report += f"- ⚠️ Schema validation pass rate is {pass_rate:.1f}%. Review prompt templates and output formats.\n"
    if errors['error_rate'] > 5:
        report += f"- ⚠️ Error rate is {errors['error_rate']:.1f}%. Check error logs for details.\n"
    if rag_metrics and rag_metrics.get('context_coverage_low_pct', 0) > 30:
        report += f"- ⚠️ Low context coverage at {rag_metrics.get('context_coverage_low_pct', 0):.1f}%. Consider expanding knowledge base.\n"
    if latency['mean'] > 5:
        report += f"- ⚠️ Average latency is {latency['mean']:.2f}s. Consider optimizing retrieval or model selection.\n"
    
    if pass_rate >= 90 and errors['error_rate'] < 2:
        report += f"- ✅ System performance is excellent!\n"
    
    # Save report
    with open(output_path, 'w') as f:
        f.write(report)
    
    return report

def generate_json_metrics(results: List[Dict[str, Any]], output_path: str = 'output/metrics.json') -> Dict[str, Any]:
    """Generate metrics in JSON format."""
    
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    metrics_data = {
        'timestamp': datetime.now().isoformat(),
        'total_queries': len(results),
        'schema_pass_rate': schema_pass_rate(results),
        'latency_stats': latency_stats(results),
        'error_analysis': error_analysis(results),
        'rag_metrics': rag_retrieval_metrics(results),
        'confidence_distribution': confidence_distribution(results)
    }
    
    with open(output_path, 'w') as f:
        json.dump(metrics_data, f, indent=2)
    
    return metrics_data
