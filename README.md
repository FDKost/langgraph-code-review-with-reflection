# LangGraph Code Review Agent with Reflection

## Requirements
- [high] Define State: Create CodeReviewState TypedDict with fields: code (str), draft_review (str), criteria_scores (dict[str,int]), weakest_criterion (str), verdict ('ok'|'needs_revision'), round (int), max_rounds (int, default 2).
- [high] Draft Review Node: Implement a node that generates an initial review of 3–6 points for the provided code using LLM. Store result in draft_review.
- [high] Reflect Node: Implement a critic node that receives draft_review and assigns scores (0‑10) for PEP8, type_hints, edge_cases, naming. Determine weakest_criterion and verdict ('ok' if all >=7 else 'needs_revision'). Store scores in criteria_scores.
- [high] Rewrite Node: Implement a rewrite node that, given the current state and weakest_criterion, rewrites only that section of the review to improve it. Increment round counter.
- [high] Graph Flow: Build LangGraph with flow: START → draft_review → reflect. If verdict is 'ok' end; if 'needs_revision' and round < max_rounds go to rewrite → reflect; otherwise end.
- [normal] CLI Demo: Provide a command‑line demo that accepts a Python function (e.g., def sort_numbers(arr): return sorted(arr)), runs the graph, and prints draft review, scores, any rewrites, and final verdict.
