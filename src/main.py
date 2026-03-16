import os
import json
import yaml
from dotenv import load_dotenv

from src.debater import Debater
from src.judge import Judge
from src.orchestrator import run_debate
from src.baseline_direct import run_direct_qa
from src.baseline_self_consistency import run_self_consistency


def load_text_file(path):
    with open(path, "r", encoding="utf-8") as file:
        return file.read()


def main():
    load_dotenv()

    with open("config/config.yaml", "r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

    debater_a_prompt = load_text_file("prompts/debater_a.txt")
    debater_b_prompt = load_text_file("prompts/debater_b.txt")
    judge_prompt = load_text_file("prompts/judge.txt")

    debater_a = Debater(
        name="Debater A",
        prompt_template=debater_a_prompt,
        base_url=os.getenv("LLAMA_BASE_URL"),
        api_key=os.getenv("LLAMA_API_KEY"),
        model_name=os.getenv("LLAMA_MODEL_NAME"),
        temperature=config["temperature"],
        max_tokens=config["max_tokens"]
    )

    debater_b = Debater(
        name="Debater B",
        prompt_template=debater_b_prompt,
        base_url=os.getenv("QWEN_BASE_URL"),
        api_key=os.getenv("QWEN_API_KEY"),
        model_name=os.getenv("QWEN_MODEL_NAME"),
        temperature=config["temperature"],
        max_tokens=config["max_tokens"]
    )

    judge = Judge(
        prompt_template=judge_prompt,
        base_url=os.getenv("JUDGE_BASE_URL"),
        api_key=os.getenv("JUDGE_API_KEY"),
        model_name=os.getenv("JUDGE_MODEL_NAME"),
        temperature=config["temperature"],
        max_tokens=config["max_tokens"]
    )

    with open("data/final_questions.json", "r", encoding="utf-8") as file:
        dataset = json.load(file)
        dataset = dataset[:config["num_questions"]]

    os.makedirs("logs", exist_ok=True)

    all_results = []

    for item in dataset:
        question = item["question"]
        ground_truth = item["answer"]

        print(f"\nRunning debate for question: {question}")

        try:
            debate_result = run_debate(
                question=question,
                ground_truth=ground_truth,
                debater_a=debater_a,
                debater_b=debater_b,
                judge=judge,
                num_rounds=config["num_rounds"]
            )

            direct_result = run_direct_qa(
                question=question,
                base_url=os.getenv("LLAMA_BASE_URL"),
                api_key=os.getenv("LLAMA_API_KEY"),
                model_name=os.getenv("LLAMA_MODEL_NAME"),
                temperature=config["temperature"],
                max_tokens=config["max_tokens"]
            )

            self_consistency_result = run_self_consistency(
                question=question,
                base_url=os.getenv("LLAMA_BASE_URL"),
                api_key=os.getenv("LLAMA_API_KEY"),
                model_name=os.getenv("LLAMA_MODEL_NAME"),
                samples=config["self_consistency_samples"],
                temperature=0.9,
                max_tokens=config["max_tokens"]
            )

            all_results.append({
                "question": question,
                "ground_truth": ground_truth,
                "debate_result": debate_result,
                "direct_qa_result": direct_result,
                "self_consistency_result": self_consistency_result
            })

        except Exception as e:
            print(f"[ERROR] Failed on question: {question}")
            print(f"[ERROR] {e}")
            continue

    with open("logs/debate_runs.json", "w", encoding="utf-8") as file:
        json.dump(all_results, file, indent=2)

    print("\nAll debates and baselines completed successfully.")
    print("Logs saved to logs/debate_runs.json")


if __name__ == "__main__":
    main()