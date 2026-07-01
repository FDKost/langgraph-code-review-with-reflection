import typer
from typing import Optional

from .graph import CodeReviewState, build_graph

app = typer.Typer(help="LangGraph Code Review Agent")


@app.command()
def run(
    code: Optional[str] = typer.Option(
        None,
        help="Python code snippet to review. If omitted, a sample function is used.",
    ),
    max_rounds: int = typer.Option(
        2,
        help="Maximum number of rewrite attempts allowed.",
    ),
):
    """
    Run the code review agent on the provided code snippet.
    """
    sample_code = """def sort_numbers(numbers):
    \"\"\"Sort a list of numbers in ascending order.\"\"\"
    return sorted(numbers)"""
    if code is None:
        code = sample_code

    # Initialize state with defaults
    state: CodeReviewState = {
        "code": code,
        "draft_review": "",
        "criteria_scores": {},
        "weakest_criterion": "",
        "verdict": "",
        "round": 1,
        "max_rounds": max_rounds,
    }

    graph = build_graph()
    # Run the graph
    final_state = graph.invoke(state)

    # Display results
    typer.echo("\nFinal review:")
    typer.echo(final_state["draft_review"])
    typer.echo(f"\nVerdict: {final_state['verdict']}")

    if final_state["verdict"] == "ok":
        typer.echo("\nReview accepted. No further action needed.")
    else:
        typer.echo("\nReview needs revision. Rewritten review shown above.")

    # Optionally display scores
    if final_state["criteria_scores"]:
        typer.echo("\nScores:")
        for k, v in final_state["criteria_scores"].items():
            typer.echo(f"  {k}: {v}")

    if final_state["weakest_criterion"]:
        typer.echo(f"\nWeakest criterion: {final_state['weakest_criterion']}")

    if final_state["round"] > 1:
        typer.echo(f"\nTotal rounds performed: {final_state['round']}")


if __name__ == "__main__":
    app()
