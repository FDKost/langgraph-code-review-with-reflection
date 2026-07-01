from typing import TypedDict, Dict, Any
import os

from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv

load_dotenv()

# Define the state structure
class CodeReviewState(TypedDict):
    code: str
    draft_review: str
    criteria_scores: Dict[str, int]
    weakest_criterion: str
    verdict: str  # "ok" | "needs_revision"
    round: int
    max_rounds: int

# LLM model (OpenAI or Ollama)
llm = ChatOpenAI(
    temperature=0.2,
    model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
)

def draft_review(state: CodeReviewState) -> CodeReviewState:
    # Ensure max_rounds defaults to 2 if not provided
    if state.get("max_rounds") is None:
        state["max_rounds"] = 2

    prompt = f"""
You are a senior software engineer. Read the following Python function and write a concise code review with 3–6 bullet points. Focus on style, correctness, edge cases, and naming.

Function:
{state['code']}

Your review should be in plain text, each point starting with a dash.
"""
    response = llm.invoke(prompt)
    state["draft_review"] = response.content.strip()
    state["round"] = 0
    return state

def reflect(state: CodeReviewState) -> CodeReviewState:
    prompt = f"""
You are an automated code review critic. Evaluate the draft review below on four criteria (PEP8, type hints, edge cases, naming). Assign each a score from 0 to 10 (integer). Identify the weakest criterion and set verdict to 'ok' if all scores >=7, otherwise 'needs_revision'.

Draft Review:
{state['draft_review']}

Respond in JSON with keys: pep8, type_hints, edge_cases, naming, weakest_criterion, verdict.
"""
    response = llm.invoke(prompt)
    import json
    data = json.loads(response.content.strip())
    state["criteria_scores"] = {
        "pep8": int(data["pep8"]),
        "type_hints": int(data["type_hints"]),
        "edge_cases": int(data["edge_cases"]),
        "naming": int(data["naming"]),
    }
    state["weakest_criterion"] = data["weakest_criterion"]
    state["verdict"] = data["verdict"]
    return state

def rewrite(state: CodeReviewState) -> CodeReviewState:
    prompt = f"""
You are a senior software engineer. The draft review below has been flagged as needing revision, specifically the section on '{state['weakest_criterion']}'. Rewrite or strengthen that part of the review to improve it.

Draft Review:
{state['draft_review']}

Provide only the updated review (no explanations). Ensure the review still contains 3–6 bullet points.
"""
    response = llm.invoke(prompt)
    state["draft_review"] = response.content.strip()
    state["round"] += 1
    return state

def build_graph() -> StateGraph:
    graph = StateGraph(CodeReviewState)

    graph.add_node("draft", draft_review)
    graph.add_node("reflect", reflect)
    graph.add_node("rewrite", rewrite)

    # Entry point
    graph.set_entry_point("draft")

    # Transition from draft to reflect
    graph.add_edge("draft", "reflect")

    # Conditional transition after reflect
    def decide_next(state: CodeReviewState):
        if state["verdict"] == "needs_revision" and state["round"] < state["max_rounds"]:
            return "rewrite"
        else:
            return END

    graph.add_conditional_edges("reflect", decide_next, {"rewrite": "rewrite", END: END})

    # After rewrite go back to reflect
    graph.add_edge("rewrite", "reflect")

    return graph

# Export the graph instance
graph = build_graph()
