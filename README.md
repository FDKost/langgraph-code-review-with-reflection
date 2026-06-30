# LangGraph Code Review with Reflection – Revision

## Requirements
- [high] State Definition: Define CodeReviewState with fields: code (str), draft_review (str), criteria_scores (dict[str,int]), weakest_criterion (str), verdict (str: "ok" or "needs_revision"), round (int), max_rounds (int, default 2).
- [high] Draft Review Node: Create a node that generates an initial review (3–6 points) for the provided code.
- [high] Reflect Node: Implement a node that uses an LLM to score the draft review on four criteria (PEP8, type-hints, edge cases, naming), returns a structured output with scores, determines weakest_criterion, and sets verdict. Store scores in criteria_scores.
- [high] Rewrite Node: Create a node that rewrites the review section corresponding to weakest_criterion, increments round, and updates draft_review.
- [high] Graph Flow: Build a LangGraph flow: START → draft_review → reflect → (if verdict ok → END; else if round < max_rounds → rewrite → reflect; else → END).
- [normal] CLI Demo: Provide a command-line interface that accepts a Python function, runs the graph, and prints the draft review, scores, weakest criterion, and any rewritten review.
- [normal] Documentation: Add a README explaining usage, dependencies, and example output.
