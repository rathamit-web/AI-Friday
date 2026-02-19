# Evaluation & Metrics Guide

## Overview

The evaluation framework provides metrics to assess your RAG solution's quality across multiple dimensions:

- **Schema Validation**: % of valid JSON outputs
- **Performance**: Latency statistics
- **Accuracy**: Domain-specific metrics
- **Retrieval Quality**: RAG context coverage
- **Confidence**: Distribution of confidence levels
- **Error Analysis**: Breakdown of failures

## Running Evaluation

### Step 1: Process Your Data
```powershell
python src/main.py --process-csv data/samples/your_tasks.csv --schema classification
```

### Step 2: Generate Metrics
```powershell
python src/evaluate.py --results output/results.json --output-dir output
```

### Step 3: View Reports
```powershell
# Markdown report (human-readable)
cat output/metrics_report.md

# JSON metrics (machine-readable)
cat output/metrics.json
```

## Available Metrics

### 1. Schema Pass Rate

**Definition**: Percentage of outputs that pass Pydantic validation.

**Formula**: `(valid_outputs / total_outputs) * 100`

**Good Target**: >90%

**What it measures**: Output format correctness

**Example**:
```
Schema Pass Rate: 94.2%
- 47 of 50 outputs were valid JSON
- 3 failed due to model hallucination
```

**How to improve**:
- Lower temperature to 0.3 or below
- Simplify prompt templates
- Add example outputs to prompt
- Use smaller, more focused models

---

### 2. Latency Statistics

**Definition**: Response time metrics (min, max, mean, median)

**Good Target**: <2s per query

**What it measures**: System performance and responsiveness

**Example**:
```
Latency (seconds):
- Min: 0.8s
- Max: 4.2s
- Mean: 1.9s
- Median: 1.7s
```

**Breakdown by component** (typical for 1.9s):
- Embedding query: 50-100ms
- Vector search: 10-50ms
- LLM inference: 1.0-1.5s
- JSON parsing: 10-20ms

**How to improve**:
- Use faster LLM: `OLLAMA_MODEL=gemma`
- Reduce context: Lower RETRIEVAL_TOP_K from 5 to 3
- Smaller chunk size: Faster retrieval
- Local Ollama: Better latency than remote

---

### 3. Error Analysis

**Definition**: Breakdown of failures and error types

**What it measures**: System reliability

**Example**:
```
Error Analysis:
- Total Errors: 3 (6% error rate)
- ConnectionError: 2
- JSONDecodeError: 1
```

**Common errors and fixes**:

| Error | Cause | Fix |
|-------|-------|-----|
| ConnectionError | Ollama not running | Start Ollama: `ollama serve` |
| JSONDecodeError | Invalid JSON from model | Lower temperature, simplify prompt |
| TimeoutError | Model too slow | Switch to faster model |
| MemoryError | Out of memory | Reduce chunk size, batch size |

---

### 4. Classification Metrics

**Applicable for**: Classification schema

**Metrics Computed**:
- **Precision**: % of predicted positive that are actually positive
- **Recall**: % of actual positive that were predicted positive
- **F1 Score**: Harmonic mean of precision & recall
- **Confusion Matrix**: Detailed category breakdown

**Example**:
```
Classification Metrics:
- Precision: 0.91
- Recall: 0.89
- F1 Score: 0.90

Confusion Matrix:
           Predicted Positive  Predicted Negative
Actual Pos:      45                5
Actual Neg:      4                 46
```

**Interpretation**:
- F1 > 0.9: Excellent
- F1 > 0.8: Good
- F1 > 0.7: Acceptable
- F1 < 0.7: Needs improvement

---

### 5. Q&A Metrics (ROUGE Scores)

**Applicable for**: QnA schema

**Metrics Computed**:
- **ROUGE-1**: Overlap of unigrams (words)
- **ROUGE-L**: Overlap of longest common subsequence

**Example**:
```
Q&A Metrics:
- ROUGE-1 Mean: 0.72
- ROUGE-L Mean: 0.68

Per-query ROUGE-1: [0.65, 0.78, 0.71, ...]
```

**Interpretation**:
- 0.9+: Excellent match to reference
- 0.8-0.9: Very good
- 0.7-0.8: Good
- <0.7: Needs improvement

**Important**: ROUGE measures surface-level overlap, not semantic correctness. Manual review of samples recommended.

---

### 6. Summarization Metrics

**Applicable for**: Summarization schema

**Metrics Computed**:
- ROUGE-1, ROUGE-2, ROUGE-L
- Compression ratio
- Summary length comparison

**Example**:
```
Summarization Metrics:
- ROUGE-1: 0.81
- ROUGE-2: 0.65
- ROUGE-L: 0.75
- Compression Ratio: 0.65 (35% of original length)

Avg Summary Length: 25 words
Avg Original Length: 68 words
```

**Interpretation**:
- ROUGE-1 > 0.75: High content overlap
- Compression > 0.5: Significant reduction achieved
- ROUGE-L > 0.7: Good sentence structure match

---

### 7. RAG Retrieval Metrics

**Applicable for**: RAG mode (when context is retrieved)

**Metrics Computed**:
- Context coverage distribution (high/medium/low)
- Retrieval success rate

**Example**:
```
RAG Retrieval Metrics:
- Total RAG Queries: 30
- High Context Coverage: 85.0%
- Medium Context Coverage: 12.0%
- Low Context Coverage: 3.0%
```

**Interpretation**:
- High coverage >80%: KB is comprehensive
- Medium coverage 10-30%: KB needs expansion
- Low coverage >10%: KB is missing key topics

**How to improve high coverage**:
1. Add more domain documents to KB
2. Ensure documents contain specific facts
3. Increase RETRIEVAL_TOP_K to 7-10
4. Use better embeddings

---

### 8. Confidence Distribution

**Definition**: How model distributes confidence across responses

**Example**:
```
Confidence Distribution:
- High: 72.0%
- Medium: 20.0%
- Low: 8.0%
```

**Interpretation**:
- High >70%: Model is confident (good)
- Medium 20-40%: Mixed signals (watch)
- Low >10%: Many uncertain answers (investigate)

**Healthy pattern**:
- Most answers (70%+) should be high confidence
- Some (10-20%) medium confidence
- Few (<10%) low confidence

---

## Interpreting the Report

### Sample Report Structure

```markdown
# Evaluation Report
Generated: 2024-02-19 10:30:15

## Executive Summary
- Total Queries: 100
- Valid Schema Outputs: 94.0%
- Error Rate: 2.0%
- Average Latency: 1.8s

## Detailed Metrics
### Schema Validation
- Valid outputs: 94.0%
- Invalid outputs: 6.0%

### Performance
- Latency: Min 0.9s, Max 3.2s, Mean 1.8s, Median 1.7s

### By Schema Type
- classification: 25/25 valid (100%)
- qna: 22/25 valid (88%)
- extraction: 47/50 valid (94%)

## Recommendations
- Context expansion recommended (Low coverage: 12%)
```

### What Each Section Tells You

1. **Executive Summary**: Quick health check - aim for >90% valid, <5% errors
2. **Schema Validation**: Format quality - all should be valid JSON
3. **Performance**: Response time - under 3s is good
4. **Error Analysis**: Where to debug
5. **Domain Metrics**: Accuracy for specific schemas
6. **Recommendations**: Specific actions to improve

## Benchmarking

Create baseline with sample data:

```powershell
# Process with baseline model
python src/main.py --process-csv data/samples/sample_input.csv --schema classification
python src/evaluate.py --results output/results.json
cat output/metrics.json > output/baseline_metrics.json
```

Then compare improvements:

```powershell
# After making changes
python src/main.py --process-csv data/samples/sample_input.csv --schema classification
python src/evaluate.py --results output/results.json

# Compare: are metrics better than baseline?
```

## Common Improvement Strategies

### ✅ If Schema Pass Rate <90%
1. Reduce temperature: 0.3 → 0.1
2. Check error logs: Look for patterns
3. Simplify output format: Fewer fields
4. Add output examples to prompt

### ✅ If Latency >3 seconds
1. Switch model: llama3.2 → gemma
2. Reduce context: top_k 5 → 3
3. Reduce chunk size: 900 → 500
4. Cache embeddings

### ✅ If Low Context Coverage <70%
1. Expand KB: Add more documents
2. Improve document quality: Clearer, more structured
3. Adjust chunking: Smaller chunks might help retrieval
4. Increase top_k: 5 → 7-10

### ✅ If Classification F1 <0.85
1. Improve training data: More examples per class
2. Balance classes: Similar count per category
3. Adjust prompts: More specific category definitions
4. Add examples to prompt

## Automated Comparison

Create comparison script:

```python
# compare_runs.py
import json

baseline = json.load(open('output/baseline_metrics.json'))
current = json.load(open('output/metrics.json'))

improvements = {
    'schema_pass_rate': current['schema_pass_rate'] - baseline['schema_pass_rate'],
    'avg_latency': baseline['latency_stats']['mean'] - current['latency_stats']['mean'],
    'error_rate': baseline['error_analysis']['error_rate'] - current['error_analysis']['error_rate']
}

for metric, delta in improvements.items():
    print(f"{metric}: {delta:+.1f}")
```

## Metrics for Hackathon Presentation

When presenting, highlight these 3 metrics:

1. **Schema Pass Rate**: "94% valid JSON outputs"
2. **Latency**: "Average response time: 1.8 seconds"
3. **Domain Accuracy**: "Classification F1: 0.92"

Bonus metrics:
- Context coverage (for RAG systems)
- Confidence distribution
- Error rate

## Further Reading

- ROUGE scores: https://en.wikipedia.org/wiki/ROUGE_(metric)
- Precision/Recall: https://en.wikipedia.org/wiki/Precision_and_recall
- F1 Score: https://en.wikipedia.org/wiki/F-score
