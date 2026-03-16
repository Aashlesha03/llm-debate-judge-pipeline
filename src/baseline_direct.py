from src.llm import call_llm


def run_direct_qa(question, base_url, api_key, model_name, temperature=0.7, max_tokens=300):
    prompt = f"""
Answer the following question as accurately as possible.
Give a short reasoning.
End with exactly:

FINAL_ANSWER: <your answer>

QUESTION:
{question}
"""

    return call_llm(
        prompt=prompt,
        base_url=base_url,
        api_key=api_key,
        model_name=model_name,
        temperature=temperature,
        max_tokens=max_tokens
    )