import pytest

from code_review.graph import CodeReviewGraph, CodeReviewState

SAMPLE_CODE = """
def add(a, b):
    \"\"\"Return the sum of two numbers.\"\"\"
    return a + b
"""

def test_code_review_graph_runs():
    graph = CodeReviewGraph(max_rounds=3)
    result: CodeReviewState = graph.run(SAMPLE_CODE)

    # Basic structure checks
    assert isinstance(result, dict)
    assert "draft_review" in result
    assert "criteria_scores" in result
    assert "verdict" in result
    assert "round" in result
    assert "max_rounds" in result

    # Scores should be integers between 0 and 10
    for score in result["criteria_scores"].values():
        assert isinstance(score, int)
        assert 0 <= score <= 10

    # Round should not exceed max_rounds
    assert result["round"] <= result["max_rounds"]

    # Verdict should be either "ok" or "needs_revision"
    assert result["verdict"] in ("ok", "needs_revision")

    # Draft review should contain at least one bullet point
    assert result["draft_review"].strip().startswith("-") or result["draft_review"].strip().startswith("•")

if __name__ == "__main__":
    pytest.main()
