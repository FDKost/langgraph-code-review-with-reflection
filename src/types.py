from typing import TypedDict, Dict, Any

class CodeReviewState(TypedDict, total=False):
    code: str
    draft_review: str
    reflection: Dict[str, Any]
    rewritten_review: str
    round: int
    max_rounds: int
