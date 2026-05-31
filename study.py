from utils.ai_helper import ask_ai

def study_module(query, task):

    prompts = {
        "Summary": f"Summarize:\n{query}",

        "Questions": f"""
Generate:
1. 5 questions with answers
2. 5 MCQs with answers
Content:
{query}
""",

        "Concept": f"Explain:\n{query}",
        "Revision": f"Give revision points:\n{query}",
        "Definitions": f"Give definitions:\n{query}",
        "Examples": f"Give examples:\n{query}"
    }

    return ask_ai(prompts.get(task, query))