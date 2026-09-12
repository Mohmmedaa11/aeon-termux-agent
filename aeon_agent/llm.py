import os
import httpx

class LLMClient:
    def __init__(self):
        self.base = os.getenv("LLM_BASE_URL", "http://127.0.0.1:8000/v1").rstrip("/")
        self.key = os.getenv("LLM_API_KEY", "EMPTY")
        self.model = os.getenv("MODEL_NAME", "AEON-7/Qwen3.8-27B-AEON-ULTIMATE-UNCENSORED-BF16")

    async def chat(self, messages, tools=None):
        body = {"model": self.model, "messages": messages, "temperature": 0.2}
        if tools:
            body["tools"] = tools
            body["tool_choice"] = "auto"
        async with httpx.AsyncClient(timeout=180) as client:
            r = await client.post(f"{self.base}/chat/completions", headers={"Authorization": f"Bearer {self.key}"}, json=body)
            r.raise_for_status()
            return r.json()
