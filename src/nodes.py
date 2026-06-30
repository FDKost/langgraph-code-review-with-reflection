import os
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langgraph import node
from src.types import CodeReviewState

# Initialize LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)

# Draft review prompt
draft_prompt = PromptTemplate(
    input_variables=["code"],
    template=(
        "You are a senior Python developer. Review the following code and provide 3-6 concise points "
        "highlighting improvements in PEP8 compliance, type hints, edge case handling, and naming conventions.\n\n"
        "Code:\n{code}\n\n"
        "Review:"
    ),
)

# Reflect prompt with JSON output
scores_schema = [
    ResponseSchema(name="pep8", description="Score 0-10 for PEP8 compliance"),
    ResponseSchema(name="type_hints", description="Score 0-10 for type hints usage"),
    ResponseSchema(name="edge_cases", description="Score 0-10 for edge case handling"),
    ResponseSchema(name="naming", description="Score 0-10 for naming conventions"),
    ResponseSchema(name="weakest_criterion", description="The criterion with the lowest score"),
    ResponseSchema(name="verdict", description='Verdict "ok" or "needs_revision"'),
]
reflect_parser = StructuredOutputParser.from_response_schemas(scores_schema)

reflect_prompt = PromptTemplate(
    input_variables=["review"],
    template=(
        "Analyze the following code review. Score each of the following criteria on a scale of 0-10:\n"
        "PEP8 compliance, type hints usage, edge case handling, naming conventions.\n"
        "Identify the weakest criterion and decide if the review is satisfactory.\n\n"
        "Review:\n{review}\n\n"
        "Provide the scores and verdict in JSON format:\n{format_instructions}"
    ).format(format_instructions=reflect_parser.get_format_instructions()),
)

# Rewrite prompt
rewrite_prompt = PromptTemplate(
    input_variables=["review", "weakest_criterion"],
    template=(
        "You are a senior Python developer. Rewrite the review section that addresses the "
        "weakest criterion ({weakest_criterion}) to improve it. Keep all other points unchanged.\n\n"
        "Original Review:\n{review}\n\n"
        "Rewritten Review:"
    ),
)

# Chains
draft_chain = llm | draft_prompt
reflect_chain = llm | reflect_prompt | reflect_parser
rewrite_chain = llm | rewrite_prompt

@node
def draft_review(state: CodeReviewState) -> CodeReviewState:
    code = state["code"]
    review = draft_chain.invoke({"code": code})["output"]
    state["draft_review"] = review.strip()
    state["round"] = 1
    state.setdefault("max_rounds", 2)
    return state

@node
def reflect(state: CodeReviewState) -> CodeReviewState:
    review = state.get("draft_review") or state.get("rewritten_review")
    if not review:
        raise ValueError("No review to reflect on.")
    reflection = reflect_chain.invoke({"review": review})["output"]
    # Convert scores to int
    state["criteria_scores"] = {
        "pep8": int(reflection["pep8"]),
        "type_hints": int(reflection["type_hints"]),
        "edge_cases": int(reflection["edge_cases"]),
        "naming": int(reflection["naming"]),
    }
    state["weakest_criterion"] = reflection["weakest_criterion"]
    state["verdict"] = reflection["verdict"]
    return state

@node
def rewrite(state: CodeReviewState) -> CodeReviewState:
    review = state.get("draft_review") or state.get("rewritten_review")
    weakest = state["weakest_criterion"]
    rewritten = rewrite_chain.invoke({"review": review, "weakest_criterion": weakest})["output"]
    state["draft_review"] = rewritten.strip()
    state["round"] += 1
    return state
