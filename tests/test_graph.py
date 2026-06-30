import pytest
from src import graph, nodes

def test_graph_loop(monkeypatch):
    # Mock the LLM chains to avoid external API calls
    monkeypatch.setattr(nodes.draft_chain, "run", lambda x: "Draft review")
    monkeypatch.setattr(
        nodes.reflect_chain,
        "run",
        lambda x: {
            "pep8": 9,
            "type_hints": 5,
            "edge_cases": 4,
            "naming": 8,
            "weakest_criterion": "edge_cases",
            "verdict": "needs_revision",
        },
    )
    monkeypatch.setattr(nodes.rewrite_chain, "run", lambda x: "Rewritten review")

    g = graph.build_graph()
    state = {"code": "def f(): pass", "max_rounds": 2}
    final_state = g.invoke(state)

    # The loop should have run twice (draft + rewrite) and stopped
    assert final_state["round"] <= 2
    assert final_state["rewritten_review"] == "Rewritten review"
    assert final_state["reflection"]["verdict"] in ("ok", "needs_revision")
    assert final_state["reflection"]["weakest_criterion"] == "edge_cases"
