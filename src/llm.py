import time
import requests


def call_llm(prompt, base_url, api_key, model_name, temperature=0.7, max_tokens=500, max_retries=3):
    base_url = base_url.rstrip("/")
    final_url = f"{base_url}/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model_name,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": temperature,
        "max_tokens": max_tokens
    }

    last_error = None

    for attempt in range(1, max_retries + 1):
        try:
            response = requests.post(final_url, headers=headers, json=payload, timeout=120)
            response.raise_for_status()

            data = response.json()
            choice = data["choices"][0]

            if "message" in choice:
                message = choice["message"]

                if message.get("content"):
                    return message["content"]

                if message.get("reasoning_content"):
                    return message["reasoning_content"]

                if message.get("reasoning"):
                    return message["reasoning"]

            if choice.get("text"):
                return choice["text"]

            return str(data)

        except requests.exceptions.RequestException as e:
            last_error = e
            print(f"[WARNING] LLM call failed on attempt {attempt}/{max_retries} for model {model_name}: {e}")

            if attempt < max_retries:
                time.sleep(5)

    raise last_error