import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import streamlit as st
import os
import yaml
from dotenv import load_dotenv

from src.debater import Debater
from src.judge import Judge
from src.orchestrator import run_debate


def load_text_file(path):
    with open(path, "r", encoding="utf-8") as file:
        return file.read()


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

st.title("LLM Debate + Judge System")

question = st.text_area("Enter your question")

if st.button("Run Debate"):
    if question.strip():
        result = run_debate(
            question=question,
            ground_truth="N/A",
            debater_a=debater_a,
            debater_b=debater_b,
            judge=judge,
            num_rounds=config["num_rounds"]
        )

        st.subheader("Debater A Initial Answer")
        st.write(result["initial_positions"]["A"])

        st.subheader("Debater B Initial Answer")
        st.write(result["initial_positions"]["B"])

        for r in result["rounds"]:
            st.subheader(f"Round {r['round']}")
            st.write("Debater A:")
            st.write(r["debater_a_response"])
            st.write("Debater B:")
            st.write(r["debater_b_response"])

        st.subheader("Judge Decision")
        st.write(result["judge_output"])