import pytest
from code_review.graph import build_graph, CodeReviewState

def test_initial_draft_and_reflect():
    # Use a simple function for testing
    code = "def add(a, b): return a + b"
    state: CodeReviewState = {
        "code": code,
        "draft_review": "",
        "criteria_scores": {},
        "weakest_criterion": "",
        "verdict": "",
        "round": 1,
        "max_rounds": 2,
    }
    graph = build_graph()
    final_state = graph.invoke(state)
    # After one round, draft_review should not be empty
    assert final_state["draft_review"]
    # Verdict should be either ok or needs_revision
    assert final_state["verdict"] in ("ok", "needs_revision")
    # Criteria scores should be populated
    assert final_state["criteria_scores"]
    # Weakest criterion should be set
    assert final_state["weakest_criterion"]
