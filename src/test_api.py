import os
from dotenv import load_dotenv
from src.llm import call_llm

load_dotenv()

prompt = "Say hello in one line."

output = call_llm(
    prompt=prompt,
    base_url=os.getenv("JUDGE_BASE_URL"),
    api_key=os.getenv("JUDGE_API_KEY"),
    model_name=os.getenv("JUDGE_MODEL_NAME"),
    temperature=0.7,
    max_tokens=200
)

print("MODEL OUTPUT:")
print(output)