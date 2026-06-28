from typing import TypedDict, Dict

class CodeReviewState(TypedDict):
    code: str
    draft_review: str
    criteria_scores: Dict[str, int]
    weakest_criterion: str
    verdict: str  # "ok" or "needs_revision"
    round: int
    max_rounds: int
