import json
from typing import List, Dict, Any
from sklearn.metrics import precision_recall_fscore_support, confusion_matrix
from rouge_score import rouge_scorer
import numpy as np
from src.logging_config import logger

def schema_pass_rate(results: List[Dict[str, Any]]) -> float:
    """Calculate percentage of valid schema outputs."""
    if not results:
        return 0.0
    valid = sum(1 for r in results if r.get('valid_output'))
    return (valid / len(results)) * 100

def latency_stats(results: List[Dict[str, Any]]) -> Dict[str, float]:
    """Calculate latency statistics."""
    latencies = [r.get('latency_s', 0) for r in results]
    if not latencies:
        return {'min': 0, 'max': 0, 'mean': 0, 'median': 0}
    
    return {
        'min': float(np.min(latencies)),
        'max': float(np.max(latencies)),
        'mean': float(np.mean(latencies)),
        'median': float(np.median(latencies))
    }

def error_analysis(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze errors in results."""
    errors = {}
    for r in results:
        if r.get('error'):
            error_type = type(r['error']).__name__
            errors[error_type] = errors.get(error_type, 0) + 1
    
    return {
        'total_errors': sum(errors.values()),
        'error_breakdown': errors,
        'error_rate': (sum(errors.values()) / len(results)) * 100 if results else 0
    }

def classification_metrics(
    predictions: List[str],
    ground_truth: List[str],
    labels: List[str]
) -> Dict[str, float]:
    """Calculate classification metrics."""
    precision, recall, f1, _ = precision_recall_fscore_support(
        ground_truth, predictions, labels=labels, average='weighted', zero_division=0
    )
    
    cm = confusion_matrix(ground_truth, predictions, labels=labels)
    
    return {
        'precision': float(precision),
        'recall': float(recall),
        'f1_score': float(f1),
        'confusion_matrix': cm.tolist()
    }

def qna_metrics(predictions: List[str], ground_truth: List[str]) -> Dict[str, float]:
    """Calculate Q&A metrics using ROUGE."""
    scorer = rouge_scorer.RougeScorer(['rouge1', 'rougeL'], use_stemmer=True)
    
    scores = {'rouge1': [], 'rougeL': []}
    for pred, gt in zip(predictions, ground_truth):
        score = scorer.score(gt, pred)
        scores['rouge1'].append(score['rouge1'].fmeasure)
        scores['rougeL'].append(score['rougeL'].fmeasure)
    
    return {
        'rouge1_mean': float(np.mean(scores['rouge1'])),
        'rougeL_mean': float(np.mean(scores['rougeL'])),
        'rouge1_scores': scores['rouge1'],
        'rougeL_scores': scores['rougeL']
    }

def summarization_metrics(summaries: List[str], references: List[str]) -> Dict[str, float]:
    """Calculate summarization metrics."""
    scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
    
    all_scores = {'rouge1': [], 'rouge2': [], 'rougeL': []}
    for summary, reference in zip(summaries, references):
        score = scorer.score(reference, summary)
        all_scores['rouge1'].append(score['rouge1'].fmeasure)
        all_scores['rouge2'].append(score['rouge2'].fmeasure)
        all_scores['rougeL'].append(score['rougeL'].fmeasure)
    
    return {
        'rouge1': float(np.mean(all_scores['rouge1'])),
        'rouge2': float(np.mean(all_scores['rouge2'])),
        'rougeL': float(np.mean(all_scores['rougeL'])),
        'summary_lengths': [len(s.split()) for s in summaries],
        'reference_lengths': [len(r.split()) for r in references]
    }

def rag_retrieval_metrics(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate RAG retrieval metrics."""
    rag_results = [r for r in results if r.get('mode') == 'rag']
    
    if not rag_results:
        return {}
    
    avg_context_coverage = {
        'high': 0,
        'medium': 0,
        'low': 0
    }
    
    for r in rag_results:
        if r.get('result'):
            coverage = r['result'].get('context_coverage', 'low')
            avg_context_coverage[coverage] += 1
    
    total = len(rag_results)
    return {
        'total_rag_queries': total,
        'context_coverage_high_pct': (avg_context_coverage['high'] / total * 100) if total else 0,
        'context_coverage_medium_pct': (avg_context_coverage['medium'] / total * 100) if total else 0,
        'context_coverage_low_pct': (avg_context_coverage['low'] / total * 100) if total else 0,
    }

def confidence_distribution(results: List[Dict[str, Any]]) -> Dict[str, float]:
    """Analyze confidence level distribution."""
    confidences = {'high': 0, 'medium': 0, 'low': 0}
    
    for r in results:
        if r.get('result'):
            conf = r['result'].get('confidence', 'low')
            if conf in confidences:
                confidences[conf] += 1
    
    total = sum(confidences.values())
    if total == 0:
        return {'high': 0, 'medium': 0, 'low': 0}
    
    return {
        'high': (confidences['high'] / total) * 100,
        'medium': (confidences['medium'] / total) * 100,
        'low': (confidences['low'] / total) * 100
    }
