from langgraph.graph import StateGraph
from src.types import CodeReviewState
from src.nodes import draft_review, reflect, rewrite

def build_graph() -> StateGraph[CodeReviewState]:
    graph = StateGraph[CodeReviewState]()

    graph.add_node("draft_review", draft_review)
    graph.add_node("reflect", reflect)
    graph.add_node("rewrite", rewrite)

    graph.set_entry_point("draft_review")
    graph.add_edge("draft_review", "reflect")

    def condition(state: CodeReviewState):
        verdict = state.get("verdict")
        round_ = state.get("round", 0)
        max_rounds = state.get("max_rounds", 2)
        if verdict == "needs_revision" and round_ < max_rounds:
            return "rewrite"
        return "__end__"

    graph.add_conditional_edges("reflect", condition, {"rewrite": "rewrite", "__end__": "__end__"})
    graph.add_edge("rewrite", "reflect")

    return graph
