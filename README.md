# LangGraph Code Review with Reflection

## Overview

This project demonstrates how to build a simple code‑review agent using **LangGraph** and **LangChain**.  
The agent:

1. Generates an initial draft review of a code snippet.  
2. Reflects on the draft, scoring it on four criteria and producing a single verdict (`ok` or `needs_revision`).  
3. If the verdict is `needs_revision` and the maximum number of rounds has not been reached, it rewrites the review.  
4. The process repeats until the review is accepted or the maximum rounds are exhausted.

The agent is intentionally simple and can be extended with more sophisticated scoring or rewriting logic.

## Installation

```bash
# Clone the repository
git clone https://github.com/your-username/langgraph-code-review.git
cd langgraph-code-review

# Create a virtual environment (optional but recommended)
python -m venv .venv
source .venv/bin/activate   # On Windows use `.venv\\Scripts\\activate`

# Install dependencies
pip install -r requirements.txt

# Copy the example environment file and add your OpenAI key
cp .env.example .env
# Edit .env and replace YOUR_OPENAI_API_KEY with your key
```

## Usage

```bash
# Run the demo on a sample function
python -m code_review.cli
```

The CLI will output:

```
Initial draft review:
- ...

Verdict: needs_revision

Rewritten review:
- ...
```

You can also feed your own code snippet by passing it as an argument:

```bash
python -m code_review.cli --code "def add(a, b): return a + b"
```

## Project Structure

```
code_review/
├── __init__.py
├── graph.py          # LangGraph definition
└── cli.py            # Command‑line interface
tests/
├── __init__.py
└── test_graph.py     # Unit tests
.env.example
requirements.txt
```

## Extending the Agent

- **Scoring**: Replace the simple threshold logic in `reflect_node` with a more advanced LLM prompt or a custom scoring function.  
- **Rewrite**: Modify the prompt in `rewrite_node` to target specific sections or to incorporate additional context.  
- **State**: Add more fields to `CodeReviewState` if you need to keep track of additional metadata.

## License

MIT License
