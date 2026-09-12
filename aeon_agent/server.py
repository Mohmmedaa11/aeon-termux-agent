import os
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from .llm import LLMClient
from tools.safe_network import inspect_http_headers, resolve_dns

load_dotenv()
app = FastAPI(title="AEON Termux Agent", version="0.1.0")
llm = LLMClient()
TOOLS = [
 {"type":"function","function":{"name":"inspect_http_headers","description":"Read HTTP response headers for an explicitly allowed target","parameters":{"type":"object","properties":{"url":{"type":"string"}},"required":["url"]}}},
 {"type":"function","function":{"name":"resolve_dns","description":"Resolve DNS for an explicitly allowed hostname","parameters":{"type":"object","properties":{"host":{"type":"string"}},"required":["host"]}}}
]
class ChatIn(BaseModel):
    message: str

def auth(x_api_key: str | None):
    expected = os.getenv("AGENT_API_KEY")
    if expected and x_api_key != expected:
        raise HTTPException(401, "Invalid API key")

@app.get("/health")
def health(): return {"ok": True, "model": llm.model}

@app.post("/chat")
async def chat(body: ChatIn, x_api_key: str | None = Header(default=None)):
    auth(x_api_key)
    messages = [{"role":"system","content":"You are a helpful Termux agent. Use tools only for targets explicitly allowed by configuration. Never perform intrusion, credential attacks, exploitation, or destructive actions."},{"role":"user","content":body.message}]
    first = await llm.chat(messages, TOOLS)
    msg = first["choices"][0]["message"]
    calls = msg.get("tool_calls", [])
    if not calls: return {"answer": msg.get("content", ""), "tool_calls": []}
    results = []
    for call in calls:
        name, args = call["function"]["name"], call["function"].get("arguments", "{}")
        import json
        args = json.loads(args)
        if name == "inspect_http_headers": result = await inspect_http_headers(args["url"])
        elif name == "resolve_dns": result = resolve_dns(args["host"])
        else: raise HTTPException(400, "Tool not allowed")
        results.append({"tool": name, "result": result})
    return {"answer": msg.get("content", ""), "tool_calls": results}
