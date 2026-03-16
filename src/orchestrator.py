def extract_final_answer(text):
    """
    Extract the text after 'FINAL_ANSWER:' from model output.
    """
    for line in text.splitlines():
        if "FINAL_ANSWER:" in line:
            return line.split("FINAL_ANSWER:")[-1].strip()
    return "UNKNOWN"


def normalize_short_answer(answer):
    """
    Normalize answer for convergence check.
    """
    if answer is None:
        return "unknown"

    answer = str(answer).strip().lower()

    if answer.startswith("yes"):
        return "yes"
    if answer.startswith("no"):
        return "no"
    if answer.startswith("true"):
        return "yes"
    if answer.startswith("false"):
        return "no"

    return answer


def run_debate(question, ground_truth, debater_a, debater_b, judge, num_rounds=3):
    """
    Full debate pipeline with adaptive stopping.
    Stops early if both agents converge to the same answer
    for two consecutive rounds.
    """

    log = {
        "question": question,
        "ground_truth": ground_truth,
        "initial_positions": {},
        "rounds": [],
        "judge_output": "",
        "stopped_early": False,
        "stop_reason": ""
    }

    # Phase 1: Initial independent answers
    initial_a = debater_a.argue(question, "")
    initial_b = debater_b.argue(question, "")

    log["initial_positions"]["A"] = initial_a
    log["initial_positions"]["B"] = initial_b

    transcript = ""
    transcript += f"Initial Response - Debater A:\n{initial_a}\n\n"
    transcript += f"Initial Response - Debater B:\n{initial_b}\n\n"

    prev_converged_answer = None
    consecutive_convergence_count = 0

    # Phase 2: Multi-round debate
    for round_num in range(1, num_rounds + 1):
        round_a = debater_a.argue(question, transcript)
        transcript += f"Round {round_num} - Debater A:\n{round_a}\n\n"

        round_b = debater_b.argue(question, transcript)
        transcript += f"Round {round_num} - Debater B:\n{round_b}\n\n"

        round_a_answer = normalize_short_answer(extract_final_answer(round_a))
        round_b_answer = normalize_short_answer(extract_final_answer(round_b))

        log["rounds"].append({
            "round": round_num,
            "debater_a_response": round_a,
            "debater_b_response": round_b,
            "debater_a_final_answer": round_a_answer,
            "debater_b_final_answer": round_b_answer
        })

        # Adaptive stopping:
        # stop if both agents converge to same answer for 2 consecutive rounds
        if round_a_answer == round_b_answer and round_a_answer != "unknown":
            if prev_converged_answer == round_a_answer:
                consecutive_convergence_count += 1
            else:
                consecutive_convergence_count = 1
                prev_converged_answer = round_a_answer
        else:
            consecutive_convergence_count = 0
            prev_converged_answer = None

        if consecutive_convergence_count >= 2:
            log["stopped_early"] = True
            log["stop_reason"] = (
                f"Both debaters converged to '{round_a_answer}' "
                f"for two consecutive rounds."
            )
            break

    # Phase 3: Judgment
    judge_output = judge.judge(question, initial_a, initial_b, transcript)
    log["judge_output"] = judge_output

    return log