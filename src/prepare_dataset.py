import json
import os
from datasets import load_dataset


def main():
    dataset = load_dataset("ChilleD/StrategyQA")
    data = dataset["train"]

    formatted = []

    # Use select() so we get row-wise examples safely
    subset = data.select(range(100))

    for item in subset:
        question = str(item["question"]).strip()
        answer = "Yes" if item["answer"] else "No"

        formatted.append({
            "question": question,
            "answer": answer
        })

    os.makedirs("data", exist_ok=True)

    with open("data/final_questions.json", "w", encoding="utf-8") as f:
        json.dump(formatted, f, indent=2)

    print("Saved 100 questions to data/final_questions.json")


if __name__ == "__main__":
    main()