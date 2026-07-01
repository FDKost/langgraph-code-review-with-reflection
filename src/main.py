import os
from dotenv import load_dotenv
from src.graph import graph, CodeReviewState

load_dotenv()

def main():
    # Sample function to review
    sample_code = """
def sort_numbers(nums):
    \"\"\"Sort a list of numbers in ascending order.\"\"\"
    return sorted(nums)
"""

    initial_state: CodeReviewState = {
        "code": sample_code,
        "draft_review": "",
        "criteria_scores": {},
        "weakest_criterion": "",
        "verdict": "",
        "round": 0,  # will be set by draft node
        # max_rounds intentionally omitted to test default
    }

    final_state = graph.invoke(initial_state)

    print("\n=== Final Review ===")
    print(final_state["draft_review"])
    print("\n=== Scores ===")
    for crit, score in final_state["criteria_scores"].items():
        print(f"{crit}: {score}")
    print(f"\nWeakest criterion: {final_state['weakest_criterion']}")
    print(f"Verdict: {final_state['verdict']}")

if __name__ == "__main__":
    main()
