import os
import json
from typing import TypedDict, Dict

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
    if "max_rounds" not in state or state.get("max_rounds") is None:
        state["max_rounds"] = 2

    prompt = f"""You are a code reviewer. Provide 3–6 concise points about the following Python function that improve its quality, style, or correctness.

```python
{state['code']}
```

Respond with each point on a new line prefixed by "-". Do not add any additional text."""
    response = llm.invoke(prompt)
    state["draft_review"] = response.content.strip()
    state["round"] = 0
    return state

def reflect(state: CodeReviewState) -> CodeReviewState:
    prompt = f"""You are a senior developer. Evaluate the following review points against these criteria:

- pep8 (style)
- type_hints (type annotations)
- edge_cases (handling of edge cases)
- naming (variable/function names)

For each criterion, assign an integer score from 0 to 10. Identify the weakest criterion and decide if the review is satisfactory.

Review:
{state['draft_review']}

Respond with a JSON object containing keys: pep8, type_hints, edge_cases, naming, weakest_criterion, verdict (either "ok" or "needs_revision")."""
    response = llm.invoke(prompt)
    data = json.loads(response.content.strip())
    state["criteria_scores"] = {
        k: int(v) for k, v in data.items() if k in ["pep8", "type_hints", "edge_cases", "naming"]
    }
    state["weakest_criterion"] = data.get("weakest_criterion", "")
    state["verdict"] = data.get("verdict", "needs_revision")
    return state

def rewrite(state: CodeReviewState) -> CodeReviewState:
    prompt = f"""You are a code reviewer. The current review points are:

{state['draft_review']}

The weakest criterion is '{state['weakest_criterion']}'. Rewrite only the part of the review that addresses this criterion to improve it, keeping all other points unchanged.

Respond with the updated review in the same format (each point on its own line prefixed by "-")."""
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
