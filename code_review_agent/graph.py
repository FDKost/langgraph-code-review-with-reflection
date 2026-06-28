from langgraph.graph import StateGraph

from .models import CodeReviewState
from .nodes import draft_review, reflect, rewrite

def build_graph() -> StateGraph:
    """Build the LangGraph workflow."""
    graph = StateGraph(CodeReviewState)

    # Add nodes
    graph.add_node("draft_review", draft_review)
    graph.add_node("reflect", reflect)
    graph.add_node("rewrite", rewrite)

    # Entry point
    graph.set_entry_point("draft_review")

    # Conditional transition after reflection
    def decide_next(state: CodeReviewState):
        if state["verdict"] == "needs_revision" and state["round"] < state["max_rounds"]:
            return "rewrite"
        return "end"

    graph.add_conditional_edges("reflect", decide_next, {"rewrite": "rewrite", "end": "end"})

    # Loop back from rewrite to reflect
    graph.add_edge("rewrite", "reflect")

    # Finish point
    graph.set_finish_point("end")

    return graph
