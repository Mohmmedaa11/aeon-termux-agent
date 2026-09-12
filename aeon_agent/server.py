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
HTML = """<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>AEON Agent</title><style>body{font-family:system-ui;background:#101827;color:#eef2ff;max-width:850px;margin:auto;padding:20px}h1{color:#8ab4ff}#chat{min-height:55vh;background:#172235;border-radius:14px;padding:16px;overflow:auto}.m{padding:12px;margin:9px 0;border-radius:10px;white-space:pre-wrap}.u{background:#24446b}.a{background:#253044}form{display:flex;gap:8px;margin-top:12px}input,button{font:inherit;padding:13px;border:0;border-radius:9px}input{flex:1;background:#243247;color:white}button{background:#4f8cff;color:white;cursor:pointer}.key{margin-top:10px;width:100%;box-sizing:border-box}</style></head><body><h1>AEON Termux Agent</h1><div id="chat"><div class="m a">مرحبًا. أدخل مفتاح API ثم اكتب رسالتك.</div></div><input class="key" id="key" type="password" placeholder="AGENT_API_KEY"><form id="f"><input id="msg" autocomplete="off" placeholder="اكتب رسالتك هنا..."><button>إرسال</button></form><script>const c=document.querySelector('#chat'),f=document.querySelector('#f'),m=document.querySelector('#msg'),k=document.querySelector('#key');function add(t,x){let d=document.createElement('div');d.className='m '+t;d.textContent=x;c.appendChild(d);c.scrollTop=c.scrollHeight}f.onsubmit=async e=>{e.preventDefault();let q=m.value.trim();if(!q)return;add('u',q);m.value='';add('a','جاري التفكير...');let last=c.lastChild;try{let r=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json','X-API-Key':k.value},body:JSON.stringify({message:q})});let j=await r.json();last.textContent=r.ok?(j.answer||JSON.stringify(j.tool_calls||[],null,2)):('خطأ: '+(j.error||r.status))}catch(e){last.textContent='تعذر الاتصال: '+e}}</script></body></html>"""
TOOLS = [{"type":"function","function":{"name":"inspect_http_headers","description":"Read HTTP response headers for an explicitly allowed target","parameters":{"type":"object","properties":{"url":{"type":"string"}},"required":["url"]}}},{"type":"function","function":{"name":"resolve_dns","description":"Resolve DNS for an explicitly allowed hostname","parameters":{"type":"object","properties":{"host":{"type":"string"}},"required":["host"]}}}]

class Handler(BaseHTTPRequestHandler):
    def _send(self, status, payload):
        data = json.dumps(payload, ensure_ascii=False).encode()
        self.send_response(status); self.send_header("Content-Type", "application/json; charset=utf-8"); self.send_header("Content-Length", str(len(data))); self.end_headers(); self.wfile.write(data)
    def do_GET(self):
        if urlparse(self.path).path == "/":
            data = HTML.encode(); self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8"); self.send_header("Content-Length", str(len(data))); self.end_headers(); self.wfile.write(data)
        elif urlparse(self.path).path == "/health": self._send(200, {"ok": True, "model": llm.model})
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
