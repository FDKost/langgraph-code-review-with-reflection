import os
import pytest
from dotenv import load_dotenv
from src.graph import graph, CodeReviewState

load_dotenv()

@pytest.fixture
def sample_state() -> CodeReviewState:
    return {
        "code": """
def add(a, b):
    return a + b
""",
        "draft_review": "",
        "criteria_scores": {},
        "weakest_criterion": "",
        "verdict": "",
        "round": 0,
    }

def test_draft_creates_points(sample_state):
    state = graph.invoke({"code": sample_state["code"], "draft_review":"", "criteria_scores":{}, "weakest_criterion":"","verdict":"","round":0})
    assert isinstance(state["draft_review"], str)
    points = [p for p in state["draft_review"].splitlines() if p.strip().startswith("-")]
    assert 3 <= len(points) <= 6

def test_reflect_scores(sample_state):
    # First draft
    state = graph.invoke({"code": sample_state["code"], "draft_review":"", "criteria_scores":{}, "weakest_criterion":"","verdict":"","round":0})
    # Reflect node will be called automatically
    assert isinstance(state["criteria_scores"], dict)
    for key in ["pep8","type_hints","edge_cases","naming"]:
        assert key in state["criteria_scores"]
        assert 0 <= state["criteria_scores"][key] <= 10

def test_max_rounds_logic(sample_state):
    # Set max_rounds to 1 to force early stop
    state = graph.invoke({
        "code": sample_state["code"],
        "draft_review":"",
        "criteria_scores":{},
        "weakest_criterion":"",
        "verdict":"",
        "round":0,
        "max_rounds":1
    })
    # After one round, verdict should be final (either ok or needs_revision)
    assert state["round"] <= 1

def test_final_verdict(sample_state):
    state = graph.invoke({
        "code": sample_state["code"],
        "draft_review":"",
        "criteria_scores":{},
        "weakest_criterion":"",
        "verdict":"",
        "round":0
    })
    assert state["verdict"] in ("ok", "needs_revision")
