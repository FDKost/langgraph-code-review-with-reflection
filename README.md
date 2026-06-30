# LangGraph Code Review

A lightweight tool that uses **LangGraph** and **LangChain** to perform an automated code review.  
The workflow:

1. **Draft Review** – An LLM generates an initial review of the supplied code.  
2. **Reflect** – The LLM scores the review on four criteria (PEP8, type hints, edge cases, naming).  
3. **Rewrite** – If the review is not satisfactory, the LLM rewrites the weakest part of the review.  
4. **Loop** – The process repeats until the review passes or the maximum number of rounds is reached.

## Features

- Uses the latest LangChain and LangGraph APIs.  
- Supports OpenAI models via `langchain-openai`.  
- CLI powered by Typer.  
- Structured output for easy parsing.  

## Installation

```bash
# Create a virtual environment
python -m venv .venv
source .venv/bin/activate   # On Windows use `.venv\Scripts\activate`

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
# Run the demo on a sample file
python -m src.main review --file sample.py
```

### Sample `sample.py`

```python
def sort_numbers(numbers: list[int]) -> list[int]:
    """Sort a list of numbers in ascending order."""
    return sorted(numbers)
```

### Expected Output

```
=== Draft Review ===
- The function name is clear but could be more descriptive.
- The type hints are missing for the return value.
- No edge case handling for empty lists.
- PEP8 compliance is good.

=== Reflection ===
pep8: 9
type_hints: 5
edge_cases: 4
naming: 8
weakest_criterion: edge_cases
verdict: needs_revision

=== Rewritten Review ===
- The function name is clear but could be more descriptive.
- The type hints are missing for the return value.
- The function should handle empty lists gracefully.
- PEP8 compliance is good.
```

## Project Structure

```
src/
├── main.py          # CLI entry point
├── graph.py         # LangGraph definition
├── nodes.py         # Node implementations
├── types.py         # TypedDict for state
└── __init__.py
```

## Extending

- Replace the OpenAI model with another provider by editing `src/nodes.py`.  
- Add more criteria to the reflection step by updating the prompt and parser.  
- Adjust `max_rounds` via the CLI option.

## License

MIT License
