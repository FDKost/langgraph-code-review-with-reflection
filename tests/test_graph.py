import pytest
from unittest.mock import patch

from code_review.graph import build_graph, CodeReviewState

class DummyResponse:
    def __init__(self, content: str):
        self.content = content

def dummy_invoke_factory():
    """
    Returns a function that mimics llm.invoke.
    It returns a JSON string for scoring prompts and a simple review string otherwise.
    """
    def dummy_invoke(prompt: str) -> DummyResponse:
        if "Score the draft" in prompt:
            return DummyResponse(
                '{"pep8":8,"type_hints":9,"edge_cases":7,"naming":8}'
            )
        else:
            return DummyResponse("Initial review")
    return dummy_invoke

def test_graph_accepts_review(monkeypatch):
    """
    Test that the graph accepts a review when all scores are >= threshold.
    """
    monkeypatch.setattr("code_review.graph.llm.invoke", dummy_invoke_factory())
    graph = build_graph()
    state: CodeReviewState = {
        "code": "def add(a,b): return a+b",
        "draft_review": "",
        "criteria_scores": {},
        "weakest_criterion": "",
        "verdict": "",
        "round": 1,
        "max_rounds": 2,
    }
    final_state = graph.invoke(state)
    assert final_state["draft_review"] == "Initial review"
    assert final_state["criteria_scores"] == {"pep8": 8, "type_hints": 9, "edge_cases": 7, "naming": 8}
    assert final_state["verdict"] == "ok"
    # No rewrite should have happened
    assert final_state["round"] == 1

def test_graph_needs_revision_and_rewrites(monkeypatch):
    """
    Test that the graph rewrites the review when scores are low.
    """
    # Low scores trigger needs_revision
    def low_score_invoke(prompt: str) -> DummyResponse:
        if "Score the draft" in prompt:
            return DummyResponse('{"pep8":4,"type_hints":5,"edge_cases":3,"naming":6}')
        else:
            return DummyResponse("Initial review")
    monkeypatch.setattr("code_review.graph.llm.invoke", low_score_invoke)
    graph = build_graph()
    state: CodeReviewState = {
        "code": "def add(a,b): return a+b",
        "draft_review": "",
        "criteria_scores": {},
        "weakest_criterion": "",
        "verdict": "",
        "round": 1,
        "max_rounds": 2,
    }
    final_state = graph.invoke(state)
    # After first round, draft_review remains the same because dummy response is constant
    assert final_state["draft_review"] == "Initial review"
    # Scores should be low
    assert final_state["criteria_scores"] == {"pep8": 4, "type_hints": 5, "edge_cases": 3, "naming": 6}
    # Verdict remains needs_revision
    assert final_state["verdict"] == "needs_revision"
    # Round should have incremented to 2 after rewrite
    assert final_state["round"] == 2
    # Since round == max_rounds, graph should stop after second reflect
    # The final verdict should still be needs_revision
    assert final_state["verdict"] == "needs_revision"
