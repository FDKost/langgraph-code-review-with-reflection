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
):
    """
    Run the code review agent on the provided code snippet.
    """
    sample_code = """def sort_numbers(numbers):
    \"\"\"Sort a list of numbers in ascending order.\"\"\"
    return sorted(numbers)"""
    if code is None:
        code = sample_code

    state = CodeReviewState(code=code)
    graph = build_graph()
    # Run the graph
    final_state = graph.invoke(state)

    # Display results
    typer.echo("\nInitial draft review:")
    typer.echo(final_state["draft_review"])
    typer.echo(f"\nVerdict: {final_state['verdict']}")

    if final_state["verdict"] == "ok":
        typer.echo("\nReview accepted. No further action needed.")
    else:
        typer.echo("\nRewritten review:")
        typer.echo(final_state["draft_review"])

if __name__ == "__main__":
    app()
