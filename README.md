# LangGraph Code Review with Reflection

## Requirements
- [high] Add requirements.txt: Create a requirements.txt file listing all necessary packages: langgraph, langchain-openai or langchain-ollama, python-dotenv, and any other dependencies used in the project.
- [high] Define CodeReviewState: Implement the TypedDict CodeReviewState with fields: code, draft_review, criteria_scores (dict of 4 criteria), weakest_criterion, verdict, round, max_rounds (default 2).
- [normal] Implement draft_review node: Create a LangGraph node that generates an initial code review (3–6 points) for the provided code.
- [normal] Implement reflect node: Create a LangGraph node that uses an LLM to score the draft review on the four criteria, determine the weakest criterion, and set the verdict ("ok" or "needs_revision"). Use structured output for scores and verdict.
- [normal] Implement rewrite node: Create a LangGraph node that rewrites the review section corresponding to the weakest criterion, increments the round counter, and updates the state.
- [normal] Build the graph flow: Set up the LangGraph flow: START → draft_review → reflect → (if ok → END; if needs_revision & round < max_rounds → rewrite → reflect; else → END). Ensure max_rounds default is 2.
- [normal] Create CLI demo: Provide a command-line interface that accepts a sample function (e.g., sort_numbers), runs the graph, and prints the draft review, scores, and any rewritten sections.
- [normal] Add README: Document the project, installation steps, usage, and example output.
