import typer
import os
from pathlib import Path
from dotenv import load_dotenv
from src.graph import build_graph
from src.types import CodeReviewState

app = typer.Typer()

def read_code(path: str) -> str:
    return Path(path).read_text()

@app.command()
def review(
    file: str = typer.Option(..., help="Path to the Python file to review"),
    max_rounds: int = typer.Option(2, help="Maximum number of revision rounds"),
):
    """
    Run the LangGraph code review on the specified Python file.
    """
    load_dotenv()
    code = read_code(file)
    state: CodeReviewState = {"code": code, "max_rounds": max_rounds}
    graph = build_graph()
    final_state = graph.invoke(state)

    typer.echo("\n=== Draft Review ===")
    typer.echo(final_state.get("draft_review", "No draft review."))
    typer.echo("\n=== Reflection ===")
    reflection = final_state.get("reflection", {})
    for key, value in reflection.items():
        typer.echo(f"{key}: {value}")
    if "rewritten_review" in final_state:
        typer.echo("\n=== Rewritten Review ===")
        typer.echo(final_state["rewritten_review"])
    else:
        typer.echo("\nNo rewriting was necessary.")

if __name__ == "__main__":
    app()
