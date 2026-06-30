import pytest
from unittest.mock import patch

from code_review.graph import (
    CodeReviewState,
    build_graph,
    _score_review,
    _determine_verdict,
    _weakest_criterion,
)

# Mock LLM responses for deterministic tests
@pytest.fixture
def mock_llm():
    with patch("code_review.graph.llm.invoke") as mock:
        # Return a simple review string
        mock.return_value.content = "Mock review content"
        yield mock

def test_score_review_parsing():
    # Simulate a JSON string response
    with patch("code_review.graph.llm.invoke") as mock:
        mock.return_value.content = """
{
  "clarity": 4,
  "correctness": 5,
  "style": 3,
  "completeness": 4
}
"""
        scores = _score_review("dummy")
        assert scores == {"clarity": 4, "correctness": 5, "style": 3, "completeness": 4}

def test_determine_verdict():
    assert _determine_verdict({"clarity": 4, "correctness": 5, "style": 3, "completeness": 4}) == "ok"
    assert _determine_verdict({"clarity": 2, "correctness": 5, "style": 3, "completeness": 4}) == "needs_revision"

def test_weakest_criterion():
    assert _weakest_criterion({"clarity": 4, "correctness": 5, "style": 3, "completeness": 4}) == "style"

def test_reflect_node_returns_verdict_only(mock_llm):
    state = CodeReviewState(code="def f(): pass")
    # Mock scores to trigger needs_revision
    with patch("code_review.graph._score_review") as mock_score:
        mock_score.return_value = {"clarity": 2, "correctness": 5, "style": 3, "completeness": 4}
        result = build_graph().invoke(state)
        # After graph execution, verdict should be "needs_revision"
        assert result["verdict"] == "needs_revision"
        # The state should contain weakest_criterion
        assert result["weakest_criterion"] == "clarity"

def test_graph_flow_rewrite():
    state = CodeReviewState(code="def f(): pass")
    # Mock the LLM to produce a review that needs revision
    with patch("code_review.graph.llm.invoke") as mock_llm:
        # First draft review
        mock_llm.return_value.content = "Draft review content"
        # Run graph
        final_state = build_graph().invoke(state)
        # Since the mock scores are default 3, verdict will be ok
        assert final_state["verdict"] == "ok"

if __name__ == "__main__":
    pytest.main()
