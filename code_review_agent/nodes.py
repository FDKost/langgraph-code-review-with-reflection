import json
from typing import Dict

from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

from .models import CodeReviewState

# Initialize the LLM
llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")

# Prompt templates
DRAFT_REVIEW_PROMPT = PromptTemplate.from_template(
    """You are a senior software engineer. Review the following Python code:

{code}

Provide a concise review with 3-6 points. Each point should be a short sentence."""
)

REFLECT_PROMPT = PromptTemplate.from_template(
    """You are a code review critic. Evaluate the following review:

Review:
{review}

Code:
{code}

Score each of the following criteria on a scale from 0 to 10 (0 = poor, 10 = excellent). Return a JSON object with the following structure:

{{
  "scores": {{
    "PEP8 compliance": int,
    "Type hints": int,
    "Edge case handling": int,
    "Naming conventions": int
  }},
  "weakest_criterion": string
}}

Only output the JSON object."""
)

REWRITE_PROMPT = PromptTemplate.from_template(
    """You are a code review critic. Rewrite the review to improve the section related to the criterion: {criterion}. The rest of the review should remain unchanged. Provide only the updated review text."""
)

def draft_review(state: CodeReviewState) -> CodeReviewState:
    """Generate the initial code review."""
    review = llm.invoke(DRAFT_REVIEW_PROMPT.format(code=state["code"]))
    state["draft_review"] = review
    return state

def reflect(state: CodeReviewState) -> CodeReviewState:
    """Score the review and determine the weakest criterion."""
    response = llm.invoke(
        REFLECT_PROMPT.format(review=state["draft_review"], code=state["code"])
    )
    try:
        data = json.loads(response)
    except json.JSONDecodeError:
        # Fallback in case the LLM does not return valid JSON
        data = {
            "scores": {
                "PEP8 compliance": 0,
                "Type hints": 0,
                "Edge case handling": 0,
                "Naming conventions": 0,
            },
            "weakest_criterion": "PEP8 compliance",
        }
    state["criteria_scores"] = data["scores"]
    state["weakest_criterion"] = data["weakest_criterion"]
    weakest_score = data["scores"][data["weakest_criterion"]]
    state["verdict"] = "ok" if weakest_score >= 8 else "needs_revision"
    return state

def rewrite(state: CodeReviewState) -> CodeReviewState:
    """Rewrite the review section for the weakest criterion."""
    criterion = state["weakest_criterion"]
    updated_review = llm.invoke(
        REWRITE_PROMPT.format(criterion=criterion, review=state["draft_review"])
    )
    state["draft_review"] = updated_review
    state["round"] += 1
    return state
