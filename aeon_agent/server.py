import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse
from .llm import LLMClient
from tools.safe_network import inspect_http_headers, resolve_dns

def load_env_file(path=".env"):
    try:
        with open(path, encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))
    except FileNotFoundError:
        pass

load_env_file()
llm = LLMClient()
TOOLS = [{"type":"function","function":{"name":"inspect_http_headers","description":"Read HTTP response headers for an explicitly allowed target","parameters":{"type":"object","properties":{"url":{"type":"string"}},"required":["url"]}}},{"type":"function","function":{"name":"resolve_dns","description":"Resolve DNS for an explicitly allowed hostname","parameters":{"type":"object","properties":{"host":{"type":"string"}},"required":["host"]}}}]

class Handler(BaseHTTPRequestHandler):
    def _send(self, status, payload):
        data = json.dumps(payload, ensure_ascii=False).encode()
        self.send_response(status); self.send_header("Content-Type", "application/json; charset=utf-8"); self.send_header("Content-Length", str(len(data))); self.end_headers(); self.wfile.write(data)
    def do_GET(self):
        if urlparse(self.path).path == "/health": self._send(200, {"ok": True, "model": llm.model})
        else: self._send(404, {"error":"not found"})
    def do_POST(self):
        if urlparse(self.path).path != "/chat": return self._send(404, {"error":"not found"})
        expected = os.getenv("AGENT_API_KEY")
        if expected and self.headers.get("X-API-Key") != expected: return self._send(401, {"error":"invalid API key"})
        try:
            body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", "0"))))
            messages = [{"role":"system","content":"You are a helpful Termux agent. Use tools only for explicitly allowed targets. Never perform intrusion, credential attacks, exploitation, or destructive actions."},{"role":"user","content":body["message"]}]
            first = llm.chat(messages, TOOLS); msg = first["choices"][0]["message"]; results = []
            for call in msg.get("tool_calls", []):
                args = json.loads(call["function"].get("arguments", "{}")); name = call["function"]["name"]
                result = inspect_http_headers(args["url"]) if name == "inspect_http_headers" else resolve_dns(args["host"])
                results.append({"tool": name, "result": result})
            self._send(200, {"answer": msg.get("content", ""), "tool_calls": results})
        except Exception as exc: self._send(500, {"error": str(exc)})
    def log_message(self, *_): pass

def main():
    port = int(os.getenv("AGENT_PORT", "8787")); print(f"AEON agent listening on http://127.0.0.1:{port}", flush=True); ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
if __name__ == "__main__": main()
