import os
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain.chains import LLMChain
from langgraph.prebuilt import create_react_agent
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

draft_chain = LLMChain(llm=llm, prompt=draft_prompt)

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

reflect_chain = LLMChain(llm=llm, prompt=reflect_prompt, output_parser=reflect_parser)

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

rewrite_chain = LLMChain(llm=llm, prompt=rewrite_prompt)

def draft_review(state: CodeReviewState) -> CodeReviewState:
    code = state["code"]
    review = draft_chain.run({"code": code})
    state["draft_review"] = review.strip()
    state["round"] = 1
    state.setdefault("max_rounds", 2)
    return state

def reflect(state: CodeReviewState) -> CodeReviewState:
    review = state.get("draft_review") or state.get("rewritten_review")
    if not review:
        raise ValueError("No review to reflect on.")
    reflection = reflect_chain.run({"review": review})
    # reflection is a dict from parser
    state["reflection"] = reflection
    return state

def rewrite(state: CodeReviewState) -> CodeReviewState:
    review = state.get("draft_review") or state.get("rewritten_review")
    weakest = state["reflection"]["weakest_criterion"]
    rewritten = rewrite_chain.run({"review": review, "weakest_criterion": weakest})
    state["rewritten_review"] = rewritten.strip()
    state["round"] += 1
    return state
