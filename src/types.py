from typing import TypedDict, Dict, Any

class CodeReviewState(TypedDict, total=False):
    """
    TypedDict representing the state of the code review process.
    All fields are optional to allow partial updates during the graph execution.
    """
    code: str
    draft_review: str
    rewritten_review: str
    reflection: Dict[str, Any]
    round: int
    max_rounds: int
