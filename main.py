import os
from typing import TypedDict, Dict

from langchain.chat_models import ChatOpenAI
from langchain.output_parsers import StructuredOutputParser
from langgraph.graph import StateGraph, END

# Ensure the OpenAI API key is set
if "OPENAI_API_KEY" not in os.environ:
    raise RuntimeError("Please set the OPENAI_API_KEY environment variable.")

# Define the state schema
class CodeReviewState(TypedDict):
    code: str
    draft_review: str
    criteria_scores: Dict[str, int]
    weakest_criterion: str
    verdict: str  # "ok" or "needs_revision"
    round: int
    max_rounds: int

# LLM instance
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

# Structured output parser for the critic response
critic_schema = {
    "criteria_scores": {
        "type": "dict",
        "description": "Scores for each criterion (0-10)",
    },
    "weakest_criterion": {
        "type": "string",
        "description": "Criterion with the lowest score",
    },
    "verdict": {
        "type": "string",
        "description": "ok or needs_revision",
    },
}
critic_parser = StructuredOutputParser.from_response_schema(critic_schema)

# Node: Draft Review
def draft_review(state: CodeReviewState) -> Dict[str, str]:
    prompt = f"""You are a code reviewer. Provide a concise review (3-6 bullet points) for the following Python function code:

{state["code"]}

Review:"""
    review = llm.invoke(prompt)
    return {"draft_review": review.strip()}

# Node: Reflect
def reflect(state: CodeReviewState) -> Dict[str, object]:
    prompt = f"""You are a critic. Score the following review on four criteria: PEP8 compliance, type hints, edge case handling, naming conventions. Each score is an integer from 0 to 10. The verdict is "ok" if all scores are >= 7, otherwise "needs_revision". Respond with JSON only.

Review:
{state["draft_review"]}

Code:
{state["code"]}

Response:"""
    response = llm.invoke(prompt)
    parsed = critic_parser.parse(response)
    # Ensure scores are integers
    scores = {k: int(v) for k, v in parsed["criteria_scores"].items()}
    return {
        "criteria_scores": scores,
        "weakest_criterion": parsed["weakest_criterion"],
        "verdict": parsed["verdict"],
    }

# Node: Rewrite
def rewrite(state: CodeReviewState) -> Dict[str, object]:
    prompt = f"""You are a code reviewer. Rewrite the part of the review that addresses the weakest criterion ({state["weakest_criterion"]}). Keep all other parts of the review unchanged. The review should still be concise (3-6 points).

Original review:
{state["draft_review"]}

Code:
{state["code"]}

Rewritten review:"""
    new_review = llm.invoke(prompt)
    return {
        "draft_review": new_review.strip(),
        "round": state["round"] + 1,
    }

# Decision function for conditional edges
def decide_next(state: CodeReviewState) -> str:
    if state["verdict"] == "ok":
        return "END"
    elif state["round"] < state["max_rounds"]:
        return "rewrite"
    else:
        return "END"

# Build the graph
graph_builder = StateGraph(CodeReviewState)

graph_builder.add_node("draft_review", draft_review)
graph_builder.add_node("reflect", reflect)
graph_builder.add_node("rewrite", rewrite)

# Start from draft_review
graph_builder.set_entry_point("draft_review")

# After reflect, decide next step
graph_builder.add_conditional_edges("reflect", decide_next, {"rewrite": "rewrite", "END": END})

# After rewrite, always go back to reflect
graph_builder.add_conditional_edges("rewrite", lambda _: "reflect", {"reflect": "reflect"})

graph = graph_builder.compile()

# CLI Demo
def main():
    sample_code = '''
def sort_numbers(numbers: list[int]) -> list[int]:
    """Sort a list of numbers in ascending order."""
    return sorted(numbers)
'''
    initial_state: CodeReviewState = {
        "code": sample_code.strip(),
        "draft_review": "",
        "criteria_scores": {},
        "weakest_criterion": "",
        "verdict": "",
        "round": 1,
        "max_rounds": 2,
    }

    final_state = graph.invoke(initial_state)

    print("\n=== Final Review ===")
    print(final_state["draft_review"])
    print("\n=== Scores ===")
    for crit, score in final_state["criteria_scores"].items():
        print(f"{crit}: {score}")
    print(f"\nWeakest criterion: {final_state['weakest_criterion']}")
    print(f"Verdict: {final_state['verdict']}")
    print(f"Rounds completed: {final_state['round']}")

if __name__ == "__main__":
    main()
