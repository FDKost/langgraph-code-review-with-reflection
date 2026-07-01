import pytest
from code_review.graph import CodeReviewGraph

def test_basic_flow():
    """
    Test that the graph runs without errors and produces a verdict.
    """
    graph = CodeReviewGraph(max_rounds=2)
    result = graph.run("def foo(): pass")
    assert isinstance(result, dict)
    assert "verdict" in result
    assert result["verdict"] in ("ok", "needs_revision")
    assert "draft_review" in result
    assert isinstance(result["draft_review"], str)
    assert isinstance(result["criteria_scores"], dict)
    assert isinstance(result["weakest_criterion"], str)
    assert result["round"] <= 2
