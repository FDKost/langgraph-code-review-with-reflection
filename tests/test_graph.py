import pytest
from src.graph import build_graph
from src.types import CodeReviewState

def test_graph_max_rounds(monkeypatch):
    # Mock draft_chain to return a simple review
    monkeypatch.setattr("src.nodes.draft_chain.invoke", lambda x: {"output": "Review point 1.\nReview point 2."})
    # Mock reflect_chain to return dict with scores
    def mock_reflect(x):
        review = x["review"]
        if "Review point 1." in review:
            return {"output": {
                "pep8": "8",
                "type_hints": "7",
                "edge_cases": "4",
                "naming": "9",
                "weakest_criterion": "edge_cases",
                "verdict": "needs_revision",
            }}
        else:
            return {"output": {
                "pep8": "9",
                "type_hints": "9",
                "edge_cases": "9",
                "naming": "9",
                "weakest_criterion": "edge_cases",
                "verdict": "ok",
            }}
    monkeypatch.setattr("src.nodes.reflect_chain.invoke", mock_reflect)
    # Mock rewrite_chain to return rewritten review
    monkeypatch.setattr("src.nodes.rewrite_chain.invoke", lambda x: {"output": "Review point 1.\nReview point 2.\nReview point 3."})
    # Build graph
    graph = build_graph()
    # Initial state
    state: CodeReviewState = {"code": "def foo(): pass", "max_rounds": 2}
    final_state = graph.invoke(state)
    # Assertions
    assert final_state["verdict"] == "ok"
    assert final_state["round"] == 2
    assert "criteria_scores" in final_state
    assert final_state["weakest_criterion"] == "edge_cases"
    assert "draft_review" in final_state
    assert "Review point 3." in final_state["draft_review"]
