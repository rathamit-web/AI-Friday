# Prompt Library & Best Practices

## Overview

The prompt library contains 6 specialized templates for different tasks. All templates follow these core principles:

- **Deterministic outputs**: Temperature = 0.3 for consistent JSON
- **Strict context grounding**: Don't use general knowledge, only provided context
- **Schema enforcement**: Always return valid JSON matching Pydantic models
- **Confidence assessment**: High/Medium/Low based on evidence strength
- **Graceful degradation**: Fallback to "insufficient_context" when needed

## Schema Types

### 1. Generic Extraction

**Use For**: Extracting entities, facts, or structured data from text.

**Example Use Cases**:
- Extract product names, prices, dates from e-commerce data
- Pull out technical specifications from documents
- Identify people, organizations, locations

**Input**:
```json
{
  "text": "Apple Inc. announced $120B revenue for Q4 2024.",
  "entity_types": ["organization", "money", "date"]
}
```

**Output**:
```json
{
  "entities": [
    {
      "value": "Apple Inc.",
      "type": "organization",
      "confidence": "high",
      "source_snippet": "Apple Inc. announced"
    },
    {
      "value": "$120B",
      "type": "money",
      "confidence": "high",
      "source_snippet": "$120B revenue for Q4 2024"
    },
    {
      "value": "Q4 2024",
      "type": "date",
      "confidence": "high",
      "source_snippet": "Q4 2024"
    }
  ],
  "extraction_summary": "Extracted company, revenue amount, and time period",
  "notes": null
}
```

**Customization Tips**:
- Add domain-specific entity types in the prompt
- Request extraction of relationships between entities
- Ask for normalized formats (e.g., dates in YYYY-MM-DD)

---

### 2. Classification

**Use For**: Categorizing text into predefined classes or detecting sentiment.

**Example Use Cases**:
- Sentiment analysis (positive/negative/neutral)
- Intent classification (question, complaint, suggestion)
- Content categorization (product type, risk level, priority)
- Ticket routing (support, sales, billing)

**Input**:
```json
{
  "text": "This product is amazing! Highly recommend to everyone.",
  "categories": ["positive", "negative", "neutral"],
  "multi_label": false
}
```

**Output**:
```json
{
  "primary_category": "positive",
  "confidence_primary": "high",
  "secondary_categories": [],
  "confidence_scores": {
    "positive": 0.98,
    "negative": 0.01,
    "neutral": 0.01
  },
  "reasoning": "Text contains explicitly positive words (amazing, recommend) and exclamation marks indicating enthusiasm",
  "uncertainty_notes": null
}
```

**Customization Tips**:
- Add custom categories relevant to your domain
- Set `multi_label: true` if text can belong to multiple classes
- Request score calibration for threshold tuning

---

### 3. Question Answering

**Use For**: Answering specific questions using provided context.

**Example Use Cases**:
- FAQ automation
- Policy lookup
- Technical documentation Q&A
- Knowledge base search

**Input**:
```json
{
  "question": "What is the API rate limit?",
  "context": "REST API rate limit is 1000 requests per minute per API key.",
  "require_source": true
}
```

**Output**:
```json
{
  "answer": "The REST API rate limit is 1000 requests per minute per API key.",
  "confidence": "high",
  "source_evidence": ["REST API rate limit is 1000 requests per minute per API key"],
  "source_documents": ["api_documentation.txt"],
  "answer_type": "direct",
  "follow_up_questions": [
    "What about burst limits?",
    "How do I increase my rate limit?"
  ],
  "limitations": null
}
```

**Customization Tips**:
- Request references to specific documents or sections
- Ask for follow-up questions to guide users
- Set `answer_type` to "insufficient_context" when KB doesn't have answer
- Request related questions for better UX

---

### 4. Summarization

**Use For**: Creating concise summaries of longer text.

**Example Use Cases**:
- News article summarization
- Meeting notes condensing
- Document abstract generation
- Report highlights

**Input**:
```json
{
  "text": "Q4 results exceeded expectations with 25% revenue growth. We expanded into 3 new markets: Europe, Asia-Pacific, and South America. Employee headcount increased from 500 to 750 (+50%).",
  "summary_length": "short",
  "focus_areas": ["revenue", "expansion", "hiring"]
}
```

**Output**:
```json
{
  "summary": "Q4 exceeded expectations with 25% revenue growth, expanded to 3 new markets, and hired 250 new employees.",
  "key_points": [
    "Revenue exceeded expectations",
    "25% growth achieved",
    "Expanded to Europe, Asia-Pacific, South America",
    "Increased headcount by 50% (500→750)"
  ],
  "entities_mentioned": ["Europe", "Asia-Pacific", "South America"],
  "topics": ["financial_performance", "market_expansion", "hiring"],
  "tone": "formal",
  "compression_ratio": 0.75,
  "completeness": "high"
}
```

**Customization Tips**:
- Control length: short (1-2 sentences), medium (3-5), long (6+)
- Highlight key metrics and entities
- Preserve important dates and numbers
- Extract topic tags for categorization

---

### 5. Action Plan

**Use For**: Generating step-by-step procedures or implementation plans.

**Example Use Cases**:
- Deployment procedures
- Incident response playbooks
- Onboarding workflows
- Process documentation

**Input**:
```json
{
  "objective": "Deploy application to production",
  "context": "Using Kubernetes cluster, 3 replicas needed",
  "resource_constraints": ["no downtime", "max 30 min duration"]
}
```

**Output**:
```json
{
  "objective": "Deploy application to production",
  "steps": [
    {
      "step_number": 1,
      "action": "Build Docker image",
      "details": "Run 'docker build -t myapp:v1.0 .'",
      "time_estimate": "5 min",
      "dependencies": [],
      "success_criteria": "Image built without errors"
    },
    {
      "step_number": 2,
      "action": "Push to registry",
      "details": "Run 'docker push myregistry/myapp:v1.0'",
      "time_estimate": "3 min",
      "dependencies": [1],
      "success_criteria": "Image appears in registry"
    },
    {
      "step_number": 3,
      "action": "Update Kubernetes deployment",
      "details": "kubectl set image deployment/myapp myapp=myregistry/myapp:v1.0",
      "time_estimate": "2 min",
      "dependencies": [2],
      "success_criteria": "All 3 replicas running new version"
    }
  ],
  "total_duration": "10 minutes",
  "risks": [
    "Deployment failure if resources exhausted",
    "Connection issues during registry push"
  ],
  "success_rate": "high"
}
```

**Customization Tips**:
- Include time estimates for each step
- Specify dependencies between steps
- Add rollback procedures for critical steps
- Include troubleshooting tips for common failures

---

### 6. RAG (Question + Context)

**Use For**: Answering queries specifically grounded in provided documents.

**Example Use Cases**:
- Document-aware Q&A
- Support ticket auto-response
- Compliance verification
- Training material lookup

**Input**:
```json
{
  "question": "What is the backup schedule?",
  "context": "Daily backups run at 2 AM UTC. Full backup on Sunday, incremental on weekdays."
}
```

**Output**:
```json
{
  "answer": "Backups run daily at 2 AM UTC. Full backups run on Sundays, with incremental backups on weekdays.",
  "confidence": "high",
  "evidence_used": [
    "Daily backups run at 2 AM UTC",
    "Full backup on Sunday, incremental on weekdays"
  ],
  "context_coverage": "high",
  "answer_status": "answered"
}
```

**Customization Tips**:
- Inject multiple document chunks as context
- Use context_coverage to indicate retrieval quality
- Request citations to specific sections
- Fallback to "unable_to_answer" if context insufficient

---

## Confidence Levels

All templates use three confidence levels:

| Level | Threshold | Action | Example |
|-------|-----------|--------|---------|
| **High** | >80% certain | Use directly | Text explicitly contains "urgent" for urgent classification |
| **Medium** | 50-80% certain | Use with review | Some keywords match but tone is ambiguous |
| **Low** | <50% certain | Flag for review | Minimal matching context or requires assumptions |

## Best Practices

### 1. Context Grounding
Always use provided context, never general knowledge:

❌ **Bad**:
```
Q: What is the backup schedule?
A: Typically backups run nightly...
```

✅ **Good**:
```
Q: What is the backup schedule?
Context: Daily backups run at 2 AM UTC. Full backup on Sunday.
A: According to the provided context, backups run daily at 2 AM UTC...
```

### 2. Schema Enforcement
Always return valid JSON matching the schema:

❌ **Bad**:
```
The answer is "yes" and I'm pretty confident about it.
```

✅ **Good**:
```json
{
  "answer": "yes",
  "confidence": "high"
}
```

### 3. Insufficient Context Handling
Explicitly state when context is missing:

❌ **Bad**:
```
The answer probably exists somewhere...
```

✅ **Good**:
```json
{
  "answer": "insufficient_context",
  "confidence": "low",
  "limitations": "Knowledge base does not contain information about weekly schedules"
}
```

### 4. Structured Output
Break down complex responses:

❌ **Bad**:
```
Extract: Apple Inc (organization), $120B (money)
```

✅ **Good**:
```json
{
  "entities": [
    {"value": "Apple Inc.", "type": "organization", "confidence": "high"},
    {"value": "$120B", "type": "money", "confidence": "high"}
  ]
}
```

### 5. Evidence Citation
Always include source snippets:

❌ **Bad**:
```
Apple revenue was $120B
```

✅ **Good**:
```json
{
  "entities": [{
    "value": "$120B",
    "source_snippet": "Apple announced $120B revenue for Q4"
  }]
}
```

## Prompt Customization for Your Domain

### Step 1: Identify Your Schema Type
Match your use case to a schema (classification, extraction, QnA, etc.)

### Step 2: Add Domain Context
```python
# In src/prompt_library.py
def schema_classification_insurance():
    return f"""{best_practices_header()}
    
    TASK: Classify insurance claims by urgency level
    
    VALID CATEGORIES:
    - critical_injury: Any injury requiring hospitalization
    - major_property: >$10K property damage
    - minor_property: <$10K property damage
    - auto_only: Vehicle damage without injury
    
    {schema_classification()}  # Base template
    """
```

### Step 3: Update Temperature if Needed
- For extraction/classification: Keep at 0.3 (deterministic)
- For creative tasks: Increase to 0.7
- Always test with your specific data!

### Step 4: Test and Iterate
```powershell
python src/main.py --text "your test input" --schema your_schema
```

## Performance Tips

| Goal | Action |
|------|--------|
| Faster responses | Use smaller model (gemma), smaller chunk size |
| Better accuracy | Increase RETRIEVAL_TOP_K to 7-10, improve KB quality |
| More deterministic | Lower temperature to 0.1 |
| Broader responses | Increase LLM_MAX_TOKENS, raise temperature to 0.5 |
| Reduced hallucination | Tighten context grounding in prompt |
| Multi-language support | Use qwen or multilingual-e5 embeddings |

## Testing Your Prompts

Create test cases in `data/eval/`:

```jsonl
{"input": "test query", "expected_output": {...}, "schema": "classification"}
```

Then run evaluation:
```powershell
python src/evaluate.py --results output/results.json
```

Check `output/metrics_report.md` for results.
