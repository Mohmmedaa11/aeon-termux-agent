import os, socket
from urllib.parse import urlparse
import httpx


def _allowed(host: str) -> bool:
    allowed = {x.strip().lower() for x in os.getenv("ALLOWED_TARGETS", "localhost,127.0.0.1").split(",") if x.strip()}
    return host.lower() in allowed

async def inspect_http_headers(url: str) -> dict:
    p = urlparse(url)
    if p.scheme not in {"http", "https"} or not p.hostname or not _allowed(p.hostname):
        raise ValueError("Target is not in ALLOWED_TARGETS")
    async with httpx.AsyncClient(timeout=10, follow_redirects=False) as client:
        r = await client.head(url)
    return {"url": url, "status": r.status_code, "headers": dict(r.headers)}

def resolve_dns(host: str) -> dict:
    if not _allowed(host):
        raise ValueError("Target is not in ALLOWED_TARGETS")
    return {"host": host, "addresses": sorted({x[4][0] for x in socket.getaddrinfo(host, None)})}
