import click

from .graph import build_graph
from .models import CodeReviewState

@click.command()
@click.argument("code_path", type=click.Path(exists=True))
def main(code_path: str):
    """Run the code review agent on a Python file."""
    with open(code_path, "r", encoding="utf-8") as f:
        code = f.read()

    # Initial state
    state: CodeReviewState = {
        "code": code,
        "draft_review": "",
        "criteria_scores": {},
        "weakest_criterion": "",
        "verdict": "",
        "round": 1,
        "max_rounds": 2,
    }

    graph = build_graph()

    # Run the graph and stream events
    for event in graph.stream(state):
        node = event["name"]
        state = event["state"]

        if node == "draft_review":
            click.echo("\n=== Draft Review ===")
            click.echo(state["draft_review"])
        elif node == "reflect":
            click.echo("\n=== Reflection ===")
            click.echo(f"Scores: {state['criteria_scores']}")
            click.echo(f"Weakest Criterion: {state['weakest_criterion']}")
            click.echo(f"Verdict: {state['verdict']}")
        elif node == "rewrite":
            click.echo("\n=== Rewritten Review ===")
            click.echo(state["draft_review"])

    click.echo("\n=== Final Review ===")
    click.echo(state["draft_review"])
    click.echo("\n=== Final Scores ===")
    click.echo(state["criteria_scores"])

if __name__ == "__main__":
    main()
