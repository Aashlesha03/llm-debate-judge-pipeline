import json
import os
import pandas as pd
import numpy as np


def extract_final_answer(text):
    if not isinstance(text, str):
        return "UNKNOWN"

    for line in text.splitlines():
        line = line.strip()
        if "FINAL_ANSWER:" in line:
            return line.split("FINAL_ANSWER:", 1)[1].strip()

    # fallback: search whole text in case formatting is weird
    text_lower = text.lower()
    if "final_answer:" in text_lower:
        idx = text_lower.rfind("final_answer:")
        return text[idx + len("FINAL_ANSWER:"):].strip().splitlines()[0].strip()

    return "UNKNOWN"


def normalize_answer(ans):
    if ans is None:
        return "unknown"

    ans = str(ans).strip().lower()

    if ans.startswith("yes"):
        return "yes"

    if ans.startswith("no"):
        return "no"

    if ans.startswith("true"):
        return "yes"

    if ans.startswith("false"):
        return "no"

    return ans


def confidence_interval(values):
    """
    95% confidence interval using normal approximation.
    """
    values = np.array(values, dtype=float)
    mean = values.mean()
    std = values.std(ddof=1) if len(values) > 1 else 0.0
    ci = 1.96 * std / np.sqrt(len(values)) if len(values) > 1 else 0.0
    return mean, ci


def main():
    with open("logs/debate_runs.json", "r", encoding="utf-8") as file:
        logs = json.load(file)

    rows = []

    for item in logs:
        ground_truth = normalize_answer(item["ground_truth"])

        debate_answer = extract_final_answer(
            item["debate_result"]["judge_output"]
        )
        direct_answer = extract_final_answer(
            item["direct_qa_result"]
        )
        sc_answer = item["self_consistency_result"]["majority_answer"]

        debate_correct = int(normalize_answer(debate_answer) == ground_truth)
        direct_correct = int(normalize_answer(direct_answer) == ground_truth)
        sc_correct = int(normalize_answer(sc_answer) == ground_truth)

        rows.append({
            "question": item["question"],
            "ground_truth": item["ground_truth"],
            "debate_answer": debate_answer,
            "direct_answer": direct_answer,
            "self_consistency_answer": sc_answer,
            "debate_correct": debate_correct,
            "direct_correct": direct_correct,
            "self_consistency_correct": sc_correct
        })

    df = pd.DataFrame(rows)

    debate_mean, debate_ci = confidence_interval(df["debate_correct"])
    direct_mean, direct_ci = confidence_interval(df["direct_correct"])
    sc_mean, sc_ci = confidence_interval(df["self_consistency_correct"])

    summary = pd.DataFrame([{
        "debate_accuracy": debate_mean,
        "debate_ci_95": debate_ci,
        "direct_qa_accuracy": direct_mean,
        "direct_qa_ci_95": direct_ci,
        "self_consistency_accuracy": sc_mean,
        "self_consistency_ci_95": sc_ci
    }])

    os.makedirs("results", exist_ok=True)

    df.to_csv("results/detailed_results.csv", index=False)
    summary.to_csv("results/summary.csv", index=False)

    print("\nDetailed results saved to results/detailed_results.csv")
    print("Summary saved to results/summary.csv")
    print("\nSummary:")
    print(summary)

    print("\n95% Confidence Intervals:")
    print(f"Debate Accuracy: {debate_mean:.2f} ± {debate_ci:.2f}")
    print(f"Direct QA Accuracy: {direct_mean:.2f} ± {direct_ci:.2f}")
    print(f"Self-Consistency Accuracy: {sc_mean:.2f} ± {sc_ci:.2f}")


if __name__ == "__main__":
    main()