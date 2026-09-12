import os, socket, urllib.request, urllib.error
from urllib.parse import urlparse


def _allowed(host: str) -> bool:
    allowed = {x.strip().lower() for x in os.getenv("ALLOWED_TARGETS", "localhost,127.0.0.1").split(",") if x.strip()}
    return host.lower() in allowed


def inspect_http_headers(url: str) -> dict:
    p = urlparse(url)
    if p.scheme not in {"http", "https"} or not p.hostname or not _allowed(p.hostname):
        raise ValueError("Target is not in ALLOWED_TARGETS")
    request = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "AEON-Termux-Agent/0.1"})
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            headers = dict(response.headers.items())
            status = response.status
    except urllib.error.HTTPError as error:
        headers = dict(error.headers.items())
        status = error.code
    return {"url": url, "status": status, "headers": headers}


def resolve_dns(host: str) -> dict:
    if not _allowed(host):
        raise ValueError("Target is not in ALLOWED_TARGETS")
    return {"host": host, "addresses": sorted({x[4][0] for x in socket.getaddrinfo(host, None)})}
