import os
from src.llm import call_llm


class Judge:
    def __init__(self, prompt_template, base_url, api_key, model_name, temperature, max_tokens):
        self.prompt_template = prompt_template
        self.base_url = base_url
        self.api_key = api_key
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens

    def judge(self, question, initial_a, initial_b, transcript):
        prompt = f"""{self.prompt_template}

QUESTION:
{question}

INITIAL_ANSWER_A:
{initial_a}

INITIAL_ANSWER_B:
{initial_b}

FULL_TRANSCRIPT:
{transcript}
"""

        try:
            return call_llm(
                prompt=prompt,
                base_url=self.base_url,
                api_key=self.api_key,
                model_name=self.model_name,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
        except Exception as e:
            print(f"[WARNING] Primary judge failed: {e}")
            print("[INFO] Falling back to Llama model as judge.")

            return call_llm(
                prompt=prompt,
                base_url=os.getenv("LLAMA_BASE_URL"),
                api_key=os.getenv("LLAMA_API_KEY"),
                model_name=os.getenv("LLAMA_MODEL_NAME"),
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )