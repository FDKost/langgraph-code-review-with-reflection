from typing import TypedDict, Optional, Dict, Any

class CodeReviewState(TypedDict, total=False):
    """
    State dictionary used throughout the LangGraph workflow.
    """
    code: str
    draft_review: str
    reflection: Dict[str, Any]
    rewritten_review: str
    round: int
    max_rounds: int
