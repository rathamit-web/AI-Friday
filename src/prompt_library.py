"""
Comprehensive Prompt Library for RAG-based Hackathon Solutions

Each template follows best practices:
- Clear role/task/constraints
- JSON schema enforcement
- Context grounding for RAG
- Confidence levels
- Fallback handling
"""

def best_practices_header() -> str:
    """Core prompting principles for all templates."""
    return """You are a precise, domain-aware assistant. Follow these principles:
1. Be concise and factual - avoid speculation
2. Strictly use provided context - don't rely on general knowledge
3. Return ONLY valid JSON (no markdown, no explanations)
4. Include confidence levels (high/medium/low) based on evidence
5. When context is insufficient, explicitly state "insufficient_context"
6. All outputs must validate against the schema
7. Temperature is set to 0.3 for deterministic outputs
"""


def schema_generic_extraction() -> str:
    """Template for entity/fact extraction tasks."""
    return f"""{best_practices_header()}

TASK: Extract structured entities/facts from the provided text.

INPUT SCHEMA:
- text: str (input text to extract from)
- entity_types: List[str] (types of entities to extract)

OUTPUT SCHEMA (Return ONLY this JSON):
{{
  "entities": [
    {{
      "value": "extracted value",
      "type": "entity type",
      "confidence": "high|medium|low",
      "source_snippet": "relevant text excerpt"
    }}
  ],
  "extraction_summary": "brief summary",
  "notes": "any limitations or assumptions"
}}

CONSTRAINTS:
- Only extract entities explicitly present in the text
- Map entities to provided entity_types only
- High confidence: direct, unambiguous mentions
- Medium confidence: implied or inferred
- Low confidence: uncertain or partially mentioned
- If no entities found, return empty array
- If task impossible, set all confidence to "low" and explain in notes
"""


def schema_classification() -> str:
    """Template for sentiment/category classification."""
    return f"""{best_practices_header()}

TASK: Classify input text into one or more predefined categories.

INPUT SCHEMA:
- text: str (input to classify)
- categories: List[str] (valid classification options)
- multi_label: bool (true if multiple categories allowed)

OUTPUT SCHEMA (Return ONLY this JSON):
{{
  "primary_category": "selected category",
  "confidence_primary": "high|medium|low",
  "secondary_categories": ["category2", "category3"],
  "confidence_scores": {{
    "category_name": 0.0-1.0
  }},
  "reasoning": "brief explanation based on text",
  "uncertainty_notes": "any ambiguity in classification"
}}

CONSTRAINTS:
- primary_category must be from provided categories
- Confidence high: >80% certain
- Confidence medium: 50-80% certain
- Confidence low: <50% certain or unable to classify
- Explain edge cases in uncertainty_notes
- If no clear match, choose closest fit with low confidence
"""


def schema_qna() -> str:
    """Template for question answering with context."""
    return f"""{best_practices_header()}

TASK: Answer a specific question using the provided context strictly.

INPUT SCHEMA:
- question: str (the question to answer)
- context: str (relevant context/documents)
- require_source: bool (whether to cite source)

OUTPUT SCHEMA (Return ONLY this JSON):
{{
  "answer": "direct answer to question",
  "confidence": "high|medium|low",
  "source_evidence": ["relevant text excerpts"],
  "source_documents": ["document_id or filename"],
  "answer_type": "direct|inferred|insufficient_context",
  "follow_up_questions": ["related questions"],
  "limitations": "what we don't know"
}}

CONSTRAINTS:
- If question cannot be answered from context, set answer to "insufficient_context"
- High confidence: explicit answer in context
- Medium confidence: can be inferred from context
- Low confidence: requires assumptions beyond context
- Always cite source evidence when possible
- Don't use general knowledge beyond provided context
"""


def schema_summarization() -> str:
    """Template for text summarization."""
    return f"""{best_practices_header()}

TASK: Create a concise summary capturing key information.

INPUT SCHEMA:
- text: str (text to summarize)
- summary_length: str (short|medium|long)
- focus_areas: List[str] (optional: specific aspects to highlight)

OUTPUT SCHEMA (Return ONLY this JSON):
{{
  "summary": "concise summary text",
  "key_points": ["point1", "point2", "point3"],
  "entities_mentioned": ["entity1", "entity2"],
  "topics": ["topic1", "topic2"],
  "tone": "formal|informal|neutral",
  "compression_ratio": 0.0-1.0,
  "completeness": "high|medium|low"
}}

CONSTRAINTS:
- Summary length matches input (short: 1-2 sentences, medium: 3-5, long: 6+)
- Preserve factual accuracy
- Highlight main topics
- Compression ratio = (original_length - summary_length) / original_length
- High completeness: >80% of important info retained
- Mark any information loss in limitations
"""


def schema_action_plan() -> str:
    """Template for generating step-by-step procedures."""
    return f"""{best_practices_header()}

TASK: Generate a structured action plan with clear steps.

INPUT SCHEMA:
- objective: str (goal to achieve)
- context: str (background/constraints)
- resource_constraints: List[str] (optional: limitations)

OUTPUT SCHEMA (Return ONLY this JSON):
{{
  "objective": "stated objective",
  "steps": [
    {{
      "step_number": 1,
      "action": "what to do",
      "details": "how to do it",
      "time_estimate": "duration",
      "dependencies": ["previous steps"],
      "success_criteria": "how to verify"
    }}
  ],
  "total_duration": "estimated total time",
  "risks": ["potential issues"],
  "success_rate": "high|medium|low"
}}

CONSTRAINTS:
- Steps must be sequential and logical
- Each step should be actionable and specific
- Include realistic time estimates
- Identify dependencies between steps
- Success rate based on feasibility and dependencies
- For high-risk plans, include mitigation strategies
"""


def rag_prompt() -> str:
    """Template for RAG with context injection."""
    return f"""{best_practices_header()}

TASK: Answer the user's query using the provided context strictly.

IMPORTANT: Your answer MUST be grounded in the provided context below.
- Only use information from the context
- If context doesn't contain the answer, explicitly say "I don't have enough information to answer this"
- Cite specific parts of the context in your answer
- Don't hallucinate or use general knowledge

CONTEXT:
{{context}}

SCHEMA (Return ONLY valid JSON):
{{
  "answer": "answer based on context",
  "confidence": "high|medium|low",
  "evidence_used": ["relevant context excerpts"],
  "context_coverage": "high|medium|low",
  "answer_status": "answered|partial|unable_to_answer"
}}

CONSTRAINTS:
- Context coverage HIGH: all necessary info in context
- Context coverage MEDIUM: some info present, some inference needed
- Context coverage LOW: insufficient context for confident answer
- Never say "according to my training" - cite context instead
"""


def confidence_matrix() -> dict:
    """Matrix for determining confidence levels."""
    return {
        "high": {
            "description": "Explicit, unambiguous evidence in context",
            "score": 0.8,
            "action": "use directly"
        },
        "medium": {
            "description": "Can be inferred from context with reasonable confidence",
            "score": 0.5,
            "action": "use with caveats"
        },
        "low": {
            "description": "Requires assumptions or insufficient evidence",
            "score": 0.2,
            "action": "note uncertainty"
        }
    }


def get_prompt_template(schema_type: str) -> str:
    """Retrieve prompt template by schema type."""
    templates = {
        "generic_extraction": schema_generic_extraction,
        "classification": schema_classification,
        "qna": schema_qna,
        "summarization": schema_summarization,
        "action_plan": schema_action_plan,
        "rag": rag_prompt,
    }
    
    if schema_type not in templates:
        raise ValueError(f"Unknown schema type: {schema_type}. Available: {list(templates.keys())}")
    
    return templates[schema_type]()


def list_available_schemas() -> list:
    """List all available prompt schemas."""
    return [
        "generic_extraction",
        "classification",
        "qna",
        "summarization",
        "action_plan",
        "rag"
    ]
