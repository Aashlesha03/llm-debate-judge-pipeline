from collections import Counter
from src.llm import call_llm


def extract_final_answer(text):
    for line in text.splitlines():
        if "FINAL_ANSWER:" in line:
            return line.split("FINAL_ANSWER:")[-1].strip()
    return "UNKNOWN"


def run_self_consistency(question, base_url, api_key, model_name, samples=5, temperature=0.9, max_tokens=300):
    outputs = []
    answers = []

    for _ in range(samples):
        prompt = f"""
Answer the following question as accurately as possible.
Give a short reasoning.
End with exactly:

FINAL_ANSWER: <your answer>

QUESTION:
{question}
"""
        output = call_llm(
            prompt=prompt,
            base_url=base_url,
            api_key=api_key,
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens
        )
        outputs.append(output)
        answers.append(extract_final_answer(output))

    majority_answer = Counter(answers).most_common(1)[0][0]

    return {
        "outputs": outputs,
        "majority_answer": majority_answer
    }