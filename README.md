# LLM Debate + Judge Pipeline

> **Known issues (fix in progress): **Debater A's prompt file says "Debater B", and the judge's answer can be misread when the reasoning model runs out of tokens before writing FINAL_ANSWER. Treat the accuracy numbers below as preliminary until the fix is published.

## Overview

This project implements a multi-agent LLM debate system.

Two LLM agents debate a question over multiple rounds, and a third LLM acts as a judge to determine the final answer.

The debate system is evaluated against two baseline approaches:

- Direct QA
- Self-Consistency

The goal is to investigate whether structured adversarial debate between two LLMs can produce more accurate answers than a single model answering directly.

---

## Models Used

Debater A: Llama-3.1-8B  
Debater B: Qwen3-8B  
Judge: GPT-OSS-20B

These models were accessed through API endpoints provided for the course.

---

## Dataset

The experiments use the StrategyQA dataset, which contains commonsense reasoning questions with yes/no answers.

For evaluation, 100 questions were sampled.

Example:

Question:  
Can penguins fly?

Ground Truth Answer:  
No

---

## System Architecture

The system follows four phases.

### Phase 1 — Initialization

1. The question is sent independently to both debaters.
2. Each debater generates an initial answer and reasoning.
3. The debaters do not see each other's responses in this phase.

---

### Phase 2 — Multi-Round Debate

The debate runs for 3 rounds.

Each round:

1. Debater A presents an argument.
2. Debater B responds with a counterargument.
3. Both agents receive the full debate transcript as context.

Adaptive stopping rule:

If both agents converge to the same answer for two consecutive rounds, the debate stops early.

---

### Phase 3 — Judgment

The judge receives:

- the original question
- both initial answers
- the full debate transcript

The judge outputs:

- reasoning analysis
- strongest and weakest arguments from each debater
- winner of the debate
- final answer
- confidence score (1–5)

---

### Phase 4 — Evaluation

The judge's final answer is compared with the ground truth answer.

All intermediate data is logged, including:

- initial responses
- debate rounds
- judge reasoning
- final verdict

---

## Baseline Methods

Two baseline methods were implemented.

### Direct QA

A single model answers the question directly using chain-of-thought prompting.

### Self-Consistency

The model generates multiple sampled answers and selects the majority vote.

---

## Results

Example evaluation results:

Debate Accuracy: 0.45 ± 0.10  
Direct QA Accuracy: 0.72 ± 0.09  
Self-Consistency Accuracy: 0.68 ± 0.09


## Project Structure

llm-debate-judge-pipeline

src
- main.py
- evaluate.py
- debater.py
- judge.py
- orchestrator.py
- baseline_direct.py
- baseline_self_consistency.py
- prepare_dataset.py

prompts
- debater_a.txt
- debater_b.txt
- judge.txt

config
- config.yaml

data
- final_questions.json

ui
- app.py

logs

results

README.md

report.md

requirements.txt


## Installation

Create a virtual environment:

python -m venv .venv
.venv\Scripts\Activate.ps1


Install dependencies:

pip install -r requirements.txt


## Environment Variables

Create a .env file in the project root.

Example:

LLAMA_BASE_URL=YOUR_URL
LLAMA_API_KEY=YOUR_KEY
LLAMA_MODEL_NAME=meta-llama/Llama-3.1-8B-Instruct

QWEN_BASE_URL=YOUR_URL
QWEN_API_KEY=YOUR_KEY
QWEN_MODEL_NAME=Qwen/Qwen3-8B

JUDGE_BASE_URL=YOUR_URL
JUDGE_API_KEY=YOUR_KEY
JUDGE_MODEL_NAME=openai/gpt-oss-20b


## Run the Debate Pipeline

python -m src.main

This runs the debate experiments and saves logs.


## Run Evaluation

python -m src.evaluate

Results are saved in:

results/detailed_results.csv  
results/summary.csv

These files contain experiment results and accuracy statistics.

---

## Running the Web Interface

A simple Streamlit interface is included.

Run:
streamlit run ui/app.py



The interface allows users to:

- enter a question
- observe debate rounds
- view judge reasoning
- see the final verdict

---

## Logging

All debate transcripts are saved as JSON logs containing:

- question
- ground truth
- initial positions
- debate rounds
- judge reasoning
- final verdict

This enables reproducibility and detailed analysis of debate behavior.

---

## LLM Assistance Disclosure

LLM tools such as ChatGPT were used for coding assistance and debugging during development.

All experiments, system configuration, and final report writing were completed independently.

---


## Notes

.env file should not be uploaded to GitHub.

API keys must be kept private.

Logs and results folders can be ignored using .gitignore.



