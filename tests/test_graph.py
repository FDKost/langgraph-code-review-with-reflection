import sys
import os
import pytest

# Ensure the src directory is importable
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from code_review import graph

# Dummy LLM response object
class DummyResponse:
    def __init__(self, content: str):
        self.content = content

@pytest.fixture
def dummy_review():
    return "• Point 1\n• Point 2\n• Point 3"

@pytest.fixture
def dummy_scores():
    return {"pep8": 8, "type_hints": 9, "edge_cases": 7, "naming": 8}

@pytest.fixture
def dummy_scores_needs_revision():
    return {"pep8": 5, "type_hints": 6, "edge_cases": 4, "naming": 7}

def test_state_initialization():
    state = {
        "code": "def foo(): pass",
        "draft_review": "",
        "criteria_scores": {},
        "weakest_criterion": "",
        "verdict": "",
        "round": 1,
        "max_rounds": 2,
    }
    assert state["code"] == "def foo(): pass"
    assert state["round"] == 1
    assert state["max_rounds"] == 2

def test_draft_review_node(monkeypatch, dummy_review):
    monkeypatch.setattr(graph.llm, "invoke", lambda prompt: DummyResponse(dummy_review))
    state = {
        "code": "def foo(): pass",
        "draft_review": "",
        "criteria_scores": {},
        "weakest_criterion": "",
        "verdict": "",
        "round": 1,
        "max_rounds": 2,
    }
    graph.draft_review_node(state)
    assert state["draft_review"] == dummy_review

def test_reflect_node(monkeypatch, dummy_scores_needs_revision):
    monkeypatch.setattr(graph, "_score_review", lambda review: dummy_scores_needs_revision)
    state = {
        "code": "def foo(): pass",
        "draft_review": "• Point 1\n• Point 2",
        "criteria_scores": {},
        "weakest_criterion": "",
        "verdict": "",
        "round": 1,
        "max_rounds": 2,
    }
    graph.reflect_node(state)
    assert state["criteria_scores"] == dummy_scores_needs_revision
    assert state["weakest_criterion"] == "edge_cases"
    assert state["verdict"] == "needs_revision"

def test_rewrite_node(monkeypatch, dummy_review):
    monkeypatch.setattr(graph.llm, "invoke", lambda prompt: DummyResponse(dummy_review))
    state = {
        "code": "def foo(): pass",
        "draft_review": "• Old point",
        "criteria_scores": {},
        "weakest_criterion": "edge_cases",
        "verdict": "needs_revision",
        "round": 1,
        "max_rounds": 2,
    }
    graph.rewrite_node(state)
    assert state["draft_review"] == dummy_review
    assert state["round"] == 2

def test_graph_termination(monkeypatch):
    # Mock LLM responses for draft and rewrite
    dummy_review_text = "• Point 1\n• Point 2"
    monkeypatch.setattr(graph.llm, "invoke", lambda prompt: DummyResponse(dummy_review_text))

    # Mock scoring: first round needs_revision, second round ok
    def mock_score(review: str):
        if graph_state["round"] == 1:
            return {"pep8": 5, "type_hints": 6, "edge_cases": 4, "naming": 7}
        else:
            return {"pep8": 8, "type_hints": 9, "edge_cases": 7, "naming": 8}

    monkeypatch.setattr(graph, "_score_review", mock_score)

    # Initialize state
    graph_state = {
        "code": "def foo(): pass",
        "draft_review": "",
        "criteria_scores": {},
        "weakest_criterion": "",
        "verdict": "",
        "round": 1,
        "max_rounds": 2,
    }

    graph_obj = graph.build_graph()
    final_state = graph_obj.invoke(graph_state)

    assert final_state["verdict"] == "ok"
    assert final_state["round"] == 2
    assert final_state["draft_review"] == dummy_review_text
