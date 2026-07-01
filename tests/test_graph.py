import os
from unittest.mock import patch, MagicMock
import json

import pytest

from src.graph import graph, CodeReviewState, llm

# Helper to mock LLM responses
def mock_llm_response(text):
    mock = MagicMock()
    mock.content = text
    return mock

@pytest.fixture(autouse=True)
def set_env():
    os.environ["OPENAI_MODEL"] = "gpt-4o-mini"
    yield

def test_round_limit_and_state_updates(monkeypatch):
    # Mock draft review response
    monkeypatch.setattr(llm, "invoke", lambda prompt: mock_llm_response(" - point 1\n - point 2"))
    
    # Mock reflect response with low scores to trigger rewrite
    def reflect_mock(prompt):
        data = {
            "pep8": 5,
            "type_hints": 4,
            "edge_cases": 6,
            "naming": 7,
            "weakest_criterion": "type_hints",
            "verdict": "needs_revision"
        }
        return mock_llm_response(json.dumps(data))
    monkeypatch.setattr(llm, "invoke", reflect_mock)
    
    # Mock rewrite response
    def rewrite_mock(prompt):
        return mock_llm_response(" - updated point 1\n - updated point 2")
    monkeypatch.setattr(llm, "invoke", rewrite_mock)

    initial_state: CodeReviewState = {
        "code": "def f(): pass",
        "draft_review": "",
        "criteria_scores": {},
        "weakest_criterion": "",
        "verdict": "",
        "round": 0,
    }

    final_state = graph.invoke(initial_state)

    # After two rewrites (max_rounds=2) should end with verdict 'needs_revision'
    assert final_state["verdict"] == "needs_revision"
    assert final_state["round"] == 2
    assert final_state["draft_review"].startswith("- updated")

def test_rewrite_modifies_only_weak_section(monkeypatch):
    # Draft review contains two distinct sections
    draft_text = "- Good naming\n- Missing type hints"
    monkeypatch.setattr(llm, "invoke", lambda prompt: mock_llm_response(draft_text))
    
    # Reflect scores with weakest 'type_hints'
    def reflect_mock(prompt):
        data = {
            "pep8": 9,
            "type_hints": 3,
            "edge_cases": 8,
            "naming": 10,
            "weakest_criterion": "type_hints",
            "verdict": "needs_revision"
        }
        return mock_llm_response(json.dumps(data))
    monkeypatch.setattr(llm, "invoke", reflect_mock)
    
    # Rewrite only updates the type hints section
    def rewrite_mock(prompt):
        updated = "- Good naming\n- Added type hints for clarity"
        return mock_llm_response(updated)
    monkeypatch.setattr(llm, "invoke", rewrite_mock)

    initial_state: CodeReviewState = {
        "code": "def f(x): pass",
        "draft_review": "",
        "criteria_scores": {},
        "weakest_criterion": "",
        "verdict": "",
        "round": 0,
    }

    final_state = graph.invoke(initial_state)
    assert "- Added type hints" in final_state["draft_review"]
    assert "- Good naming" in final_state["draft_review"]

if __name__ == "__main__":
    pytest.main()
