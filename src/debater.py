from src.llm import call_llm


class Debater:
    def __init__(self, name, prompt_template, base_url, api_key, model_name, temperature, max_tokens):
        self.name = name
        self.prompt_template = prompt_template
        self.base_url = base_url
        self.api_key = api_key
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens

    def argue(self, question, transcript=""):
        prompt = f"""{self.prompt_template}

QUESTION:
{question}

DEBATE TRANSCRIPT:
{transcript}
"""
        return call_llm(
            prompt=prompt,
            base_url=self.base_url,
            api_key=self.api_key,
            model_name=self.model_name,
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )