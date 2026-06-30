import os
from typing import TypedDict, Dict, Any

from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

# --------------------------------------------------------------------------- #
# State definition
# --------------------------------------------------------------------------- #
class CodeReviewState(TypedDict):
    """
    The state that flows through the LangGraph.

    Attributes
    ----------
    code : str
        The source code to be reviewed.
    draft_review : str
        The current draft review text.
    criteria_scores : dict[str, int]
        Scores for each review criterion.
    weakest_criterion : str
        The criterion with the lowest score (used for rewriting).
    verdict : str
        The overall verdict of the review: "ok" or "needs_revision".
    round : int
        The current round number (starting at 1).
    max_rounds : int
        The maximum number of rewrite attempts allowed.
    """
    code: str
    draft_review: str
    criteria_scores: Dict[str, int]
    weakest_criterion: str
    verdict: str
    round: int
    max_rounds: int

# --------------------------------------------------------------------------- #
# LLM setup
# --------------------------------------------------------------------------- #
if not os.getenv("OPENAI_API_KEY"):
    raise RuntimeError(
        "OPENAI_API_KEY not set. Please set it in your .env file."
    )

llm = ChatOpenAI(
    temperature=0,
    model="gpt-4o-mini",
)

# --------------------------------------------------------------------------- #
# Helper functions
# --------------------------------------------------------------------------- #
def _score_review(review: str) -> Dict[str, int]:
    """
    Use the LLM to score the review on four criteria.

    Returns a dictionary with integer scores (0‑10) for each criterion.
    """
    prompt = f"""
You are a senior software engineer reviewing a code review draft.  
Score the draft on the following criteria on a scale of 0 (poor) to 10 (excellent):

1. PEP8 compliance
2. Type hints
3. Edge case handling
4. Naming conventions

Return a JSON object with keys "pep8", "type_hints", "edge_cases", "naming".
Example:
{{
  "pep8": 8,
  "type_hints": 9,
  "edge_cases": 7,
  "naming": 8
}}

Draft review:
{review}
"""
    response = llm.invoke(prompt)
    try:
        scores = response.content
        import json

        return json.loads(scores)
    except Exception:
        # Fallback: assign neutral scores if parsing fails
        return {"pep8": 5, "type_hints": 5, "edge_cases": 5, "naming": 5}


def _determine_verdict(scores: Dict[str, int], threshold: int = 6) -> str:
    """
    Determine the overall verdict based on individual scores.
    If all scores are >= threshold, verdict is "ok".
    Otherwise, "needs_revision".
    """
    return "ok" if all(v >= threshold for v in scores.values()) else "needs_revision"


def _weakest_criterion(scores: Dict[str, int]) -> str:
    """
    Return the criterion with the lowest score.
    """
    return min(scores, key=scores.get)

# --------------------------------------------------------------------------- #
# Node implementations
# --------------------------------------------------------------------------- #
def draft_review_node(state: CodeReviewState) -> Dict[str, Any]:
    """
    Generate an initial draft review for the provided code.
    """
    prompt = f"""
You are a senior software engineer.  
Write a concise code review (3–6 bullet points) for the following Python function.  
Do not include any explanations, just the review points.

Function:
{state["code"]}
"""
    response = llm.invoke(prompt)
    state["draft_review"] = response.content.strip()
    return {"draft_review": state["draft_review"]}


def reflect_node(state: CodeReviewState) -> Dict[str, Any]:
    """
    Reflect on the draft review, compute scores, and produce a verdict.
    """
    scores = _score_review(state["draft_review"])
    state["criteria_scores"] = scores
    state["weakest_criterion"] = _weakest_criterion(scores)
    state["verdict"] = _determine_verdict(scores)
    return {"verdict": state["verdict"]}


def rewrite_node(state: CodeReviewState) -> Dict[str, Any]:
    """
    Rewrite the review focusing on the weakest criterion.
    Increment the round counter.
    """
    prompt = f"""
You are a senior software engineer.  
The current draft review is:

{state["draft_review"]}

The weakest criterion identified was: {state["weakest_criterion"]}.  
Rewrite the review to improve this aspect.  
Provide a new draft review (3–6 bullet points) without any additional commentary.

New draft review:
"""
    response = llm.invoke(prompt)
    state["draft_review"] = response.content.strip()
    state["round"] += 1
    return {"draft_review": state["draft_review"]}

# --------------------------------------------------------------------------- #
# Graph construction
# --------------------------------------------------------------------------- #
def build_graph() -> StateGraph[CodeReviewState]:
    """
    Build and return the LangGraph for the code review agent.
    """
    graph = StateGraph[CodeReviewState]()

    graph.add_node("draft_review", draft_review_node)
    graph.add_node("reflect", reflect_node)
    graph.add_node("rewrite", rewrite_node)

    graph.set_entry_point("draft_review")

    graph.add_edge("draft_review", "reflect")

    # After reflection, decide next step
    def decide_next(state: CodeReviewState):
        verdict = state.get("verdict", "")
        round_num = state.get("round", 1)
        max_rounds = state.get("max_rounds", 2)
        if verdict == "needs_revision" and round_num < max_rounds:
            return "rewrite"
        return END

    graph.add_conditional_edges("reflect", decide_next)

    graph.add_edge("rewrite", "reflect")

    return graph

# --------------------------------------------------------------------------- #
# Wrapper class for tests and convenience
# --------------------------------------------------------------------------- #
class CodeReviewGraph:
    """
    Convenience wrapper around the LangGraph that exposes a simple run method.
    """

    def __init__(self, max_rounds: int = 2):
        self.max_rounds = max_rounds
        self.graph = build_graph()

    def run(self, code: str) -> CodeReviewState:
        """
        Run the graph on the provided code snippet.

        Parameters
        ----------
        code : str
            The Python code to review.

        Returns
        -------
        CodeReviewState
            The final state after the graph execution.
        """
        state: CodeReviewState = {
            "code": code,
            "draft_review": "",
            "criteria_scores": {},
            "weakest_criterion": "",
            "verdict": "",
            "round": 1,
            "max_rounds": self.max_rounds,
        }
        return self.graph.invoke(state)

# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #
__all__ = ["CodeReviewState", "CodeReviewGraph", "build_graph"]
