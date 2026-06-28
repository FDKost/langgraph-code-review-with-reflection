import pytest
from code_review_agent.nodes import draft_review, reflect, rewrite
from code_review_agent.models import CodeReviewState

@pytest.fixture
def sample_state():
    return {
        "code": "def add(a: int, b: int) -> int:\n    return a + b",
        "draft_review": "",
        "criteria_scores": {},
        "weakest_criterion": "",
        "verdict": "",
        "round": 1,
        "max_rounds": 2,
    }

def test_draft_review(sample_state):
    state = draft_review(sample_state)
    assert state["draft_review"] != ""

def test_reflect(sample_state):
    sample_state["draft_review"] = "Good code."
    state = reflect(sample_state)
    assert "criteria_scores" in state
    assert "weakest_criterion" in state
    assert state["verdict"] in ("ok", "needs_revision")

def test_rewrite(sample_state):
    sample_state["draft_review"] = "Good code."
    sample_state["weakest_criterion"] = "PEP8 compliance"
    state = rewrite(sample_state)
    assert state["round"] == 2
    assert state["draft_review"] != "Good code."
