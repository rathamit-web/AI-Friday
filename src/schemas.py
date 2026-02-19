from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class Entity(BaseModel):
    """Extracted entity with confidence."""
    value: str
    type: str
    confidence: str = Field(..., pattern="^(high|medium|low)$")
    source_snippet: Optional[str] = None

class GenericExtractionOutput(BaseModel):
    """Output schema for generic extraction."""
    entities: List[Entity]
    extraction_summary: str
    notes: Optional[str] = None

class ClassificationOutput(BaseModel):
    """Output schema for classification."""
    primary_category: str
    confidence_primary: str = Field(..., pattern="^(high|medium|low)$")
    secondary_categories: List[str] = []
    confidence_scores: Dict[str, float]
    reasoning: str
    uncertainty_notes: Optional[str] = None

class QnAOutput(BaseModel):
    """Output schema for question answering."""
    answer: str
    confidence: str = Field(..., pattern="^(high|medium|low)$")
    source_evidence: List[str] = []
    source_documents: List[str] = []
    answer_type: str = Field(..., pattern="^(direct|inferred|insufficient_context)$")
    follow_up_questions: List[str] = []
    limitations: Optional[str] = None

class KeyPoint(BaseModel):
    """Key point in summary."""
    text: str

class SummarizationOutput(BaseModel):
    """Output schema for summarization."""
    summary: str
    key_points: List[str]
    entities_mentioned: List[str] = []
    topics: List[str] = []
    tone: str = Field(..., pattern="^(formal|informal|neutral)$")
    compression_ratio: float
    completeness: str = Field(..., pattern="^(high|medium|low)$")

class ActionStep(BaseModel):
    """Step in an action plan."""
    step_number: int
    action: str
    details: str
    time_estimate: str
    dependencies: List[int] = []
    success_criteria: str

class ActionPlanOutput(BaseModel):
    """Output schema for action plans."""
    objective: str
    steps: List[ActionStep]
    total_duration: str
    risks: List[str] = []
    success_rate: str = Field(..., pattern="^(high|medium|low)$")

class RAGOutput(BaseModel):
    """Output schema for RAG queries."""
    answer: str
    confidence: str = Field(..., pattern="^(high|medium|low)$")
    evidence_used: List[str] = []
    context_coverage: str = Field(..., pattern="^(high|medium|low)$")
    answer_status: str = Field(..., pattern="^(answered|partial|unable_to_answer)$")

# Mapping for easy access
SCHEMA_MODELS = {
    "generic_extraction": GenericExtractionOutput,
    "classification": ClassificationOutput,
    "qna": QnAOutput,
    "summarization": SummarizationOutput,
    "action_plan": ActionPlanOutput,
    "rag": RAGOutput,
}

def validate_output(output_dict: Dict[str, Any], schema_type: str) -> bool:
    """Validate output against schema."""
    if schema_type not in SCHEMA_MODELS:
        return False
    
    try:
        SCHEMA_MODELS[schema_type](**output_dict)
        return True
    except Exception:
        return False

def get_schema_model(schema_type: str):
    """Get Pydantic model for schema type."""
    return SCHEMA_MODELS.get(schema_type)
