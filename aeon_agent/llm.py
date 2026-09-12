import json
import os
import urllib.request

class LLMClient:
    def __init__(self):
        self.base = os.getenv("LLM_BASE_URL", "http://127.0.0.1:8000/v1").rstrip("/")
        self.key = os.getenv("LLM_API_KEY", "EMPTY")
        self.model = os.getenv("MODEL_NAME", "AEON-7/Qwen3.8-27B-AEON-ULTIMATE-UNCENSORED-BF16")

    def chat(self, messages, tools=None):
        body = {"model": self.model, "messages": messages, "temperature": 0.2}
        if tools:
            body["tools"] = tools
            body["tool_choice"] = "auto"
        request = urllib.request.Request(
            f"{self.base}/chat/completions",
            data=json.dumps(body).encode(),
            headers={"Authorization": f"Bearer {self.key}", "Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=180) as response:
            return json.loads(response.read().decode())
