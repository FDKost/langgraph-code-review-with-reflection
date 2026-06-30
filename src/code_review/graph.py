import os
from typing import Dict, Any

from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

# --------------------------------------------------------------------------- #
# State definition
# --------------------------------------------------------------------------- #
class CodeReviewState(BaseModel):
    """
    The state that flows through the LangGraph.

    Attributes
    ----------
    code : str
        The source code to be reviewed.
    draft_review : str
        The current draft review text.
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
    draft_review: str = Field(default_factory=str)
    weakest_criterion: str = Field(default_factory=str)
    verdict: str = Field(default_factory=str)
    round: int = 1
    max_rounds: int = 2

# --------------------------------------------------------------------------- #
# LLM setup
# --------------------------------------------------------------------------- #
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

    Returns a dictionary with integer scores (1‑5) for each criterion.
    """
    prompt = f"""
You are a senior software engineer reviewing a code review draft.  
Score the draft on the following criteria on a scale of 1 (poor) to 5 (excellent):

1. Clarity
2. Correctness
3. Style
4. Completeness

Return a JSON object with keys "clarity", "correctness", "style", "completeness".
Example:
{{
  "clarity": 4,
  "correctness": 5,
  "style": 3,
  "completeness": 4
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
        # Fallback: assign random scores if parsing fails
        return {"clarity": 3, "correctness": 3, "style": 3, "completeness": 3}

def _determine_verdict(scores: Dict[str, int], threshold: int = 3) -> str:
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
{state.code}
"""
    response = llm.invoke(prompt)
    state.draft_review = response.content.strip()
    return {"draft_review": state.draft_review}

def reflect_node(state: CodeReviewState) -> Dict[str, Any]:
    """
    Reflect on the draft review, compute scores, and produce a verdict.
    The weakest criterion is stored in the state but not returned.
    """
    scores = _score_review(state.draft_review)
    state.weakest_criterion = _weakest_criterion(scores)
    state.verdict = _determine_verdict(scores)
    # Only expose the verdict in the node output
    return {"verdict": state.verdict}

def rewrite_node(state: CodeReviewState) -> Dict[str, Any]:
    """
    Rewrite the review focusing on the weakest criterion.
    Increment the round counter.
    """
    prompt = f"""
You are a senior software engineer.  
The current draft review is:

{state.draft_review}

The weakest criterion identified was: {state.weakest_criterion}.  
Rewrite the review to improve this aspect.  
Provide a new draft review (3–6 bullet points) without any additional commentary.

New draft review:
"""
    response = llm.invoke(prompt)
    state.draft_review = response.content.strip()
    state.round += 1
    # After rewriting, we consider the review acceptable
    state.verdict = "ok"
    return {"draft_review": state.draft_review, "verdict": state.verdict}

# --------------------------------------------------------------------------- #
# Graph construction
# --------------------------------------------------------------------------- #
def build_graph() -> StateGraph[CodeReviewState]:
    """
    Build and return the LangGraph for the code review agent.
    """
    graph = StateGraph(CodeReviewState)

    graph.add_node("draft_review", draft_review_node)
    graph.add_node("reflect", reflect_node)
    graph.add_node("rewrite", rewrite_node)

    # Entry point
    graph.set_entry_point("draft_review")

    # Transitions
    graph.add_edge("draft_review", "reflect")
    graph.add_conditional_edges(
        "reflect",
        lambda state: state.verdict,
        {
            "ok": END,
            "needs_revision": "rewrite_check",
        },
    )
    # Check if we can rewrite
    graph.add_node("rewrite_check", lambda state: "rewrite" if state.round < state.max_rounds else END)
    graph.add_edge("rewrite_check", "rewrite")
    graph.add_edge("rewrite", "reflect")

    return graph

# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #
__all__ = ["CodeReviewState", "build_graph"]
