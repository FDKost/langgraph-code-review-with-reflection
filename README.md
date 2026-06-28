# Code Review Agent

This project implements a simple code review agent using **LangGraph** and **OpenAI**.  
The agent:

1. Generates an initial review of a Python function.  
2. Critiques the review, scoring it on four criteria.  
3. If the review is not good enough, rewrites the weakest part and repeats.  
4. Stops after a maximum number of rounds (default 2).

## Features

- **Typed state** with `CodeReviewState` (TypedDict).  
- **Draft review** node – generates a concise review.  
- **Reflect** node – scores the review and picks the weakest criterion.  
- **Rewrite** node – improves the weak part of the review.  
- **LangGraph workflow** – loops until the review is satisfactory or the round limit is reached.  
- **CLI demo** – run the agent on any Python file.  

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/code-review-agent.git
cd code-review-agent

# Create a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

Set your OpenAI API key:

```bash
export OPENAI_API_KEY="sk-..."
```

Run the CLI on a Python file:

```bash
python -m code_review_agent.cli demo/sample.py
```

You should see the draft review, the reflection scores, any rewritten sections, and the final review.

## Extending the Agent

- **Add more criteria** – update the `REFLECT_PROMPT` and the logic in `nodes.py`.  
- **Change the LLM** – swap `ChatOpenAI` for another provider.  
- **Adjust thresholds** – modify the `verdict` logic in `reflect`.  

## Testing

Run the unit tests with:

```bash
pytest tests/
```

## License

MIT License
