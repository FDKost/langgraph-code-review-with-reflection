# LangGraph Code Review with Reflection

This project demonstrates a simple code review workflow using **LangGraph** and **LangChain**.  
The workflow:

1. **Draft Review** – Generates an initial review of a Python function.  
2. **Reflect** – A critic scores the review on four criteria.  
3. **Rewrite** – If the review is not satisfactory, the weakest part is rewritten.  
4. The process repeats until the review passes or the maximum number of rounds is reached.

## Features

- **Typed state** with `CodeReviewState` (TypedDict).  
- **Structured output parsing** for critic responses.  
- **Conditional graph flow** with a maximum of 2 rewrite rounds.  
- **CLI demo** with a sample `sort_numbers` function.

## Requirements

- Python 3.10+
- OpenAI API key (set as `OPENAI_API_KEY` environment variable)

Install dependencies:

```bash
pip install -r requirements.txt
```

## Running the Demo

```bash
export OPENAI_API_KEY="your-openai-key"
python main.py
```

You should see the final review, scores, weakest criterion, verdict, and the number of rounds completed.

## Customizing

- **Change the sample function**: Edit the `sample_code` string in `main.py`.  
- **Adjust max rounds**: Modify `max_rounds` in the initial state.  
- **Use a different LLM**: Replace the `ChatOpenAI` model name.

## License

MIT License
