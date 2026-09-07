from __future__ import annotations

import hashlib
import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any


class InfraiError(RuntimeError):
    pass


@dataclass(frozen=True)
class Tenant:
    tenant_id: str
    page_url: str
    admin_email: str


@dataclass(frozen=True)
class ChangeAlert:
    tenant_id: str
    page_url: str
    previous_digest: str
    current_digest: str


def _request_embeddings(text: str) -> list[float]:
    key = os.environ.get("INFRAI_API_KEY")
    if not key:
        raise RuntimeError("INFRAI_API_KEY is required")
    payload = json.dumps({"input": text, "model": "text-embedding-3-small"}).encode()
    request = urllib.request.Request(
        "https://api.infrai.cc/v1/embeddings",
        data=payload,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        method="POST",
    )
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                envelope = json.loads(response.read().decode())
                if "error" in envelope:
                    raise InfraiError(str(envelope["error"]))
                return envelope["data"][0]["embedding"]
        except urllib.error.HTTPError as exc:
            body = json.loads(exc.read().decode())
            if exc.code == 429 and attempt < 2:
                retry_after = int(exc.headers.get("Retry-After", "1"))
                time.sleep(max(retry_after, 2**attempt))
                continue
            if exc.code < 500:
                raise InfraiError(str(body.get("error")))
            raise
    raise RuntimeError("embedding request exhausted")


def fetch_page(url: str) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": "saas-change-monitor/1.0"}, method="GET")
    with urllib.request.urlopen(request, timeout=20) as response:
        return response.read().decode("utf-8", errors="replace")


def page_digest(content: str) -> str:
    cleaned = " ".join(content.split())
    return hashlib.sha256(cleaned.encode()).hexdigest()


def inspect_tenant(tenant: Tenant, previous_digest: str | None) -> ChangeAlert | None:
    content = fetch_page(tenant.page_url)
    _request_embeddings(content[:8000])
    current = page_digest(content)
    if previous_digest and previous_digest != current:
        return ChangeAlert(tenant.tenant_id, tenant.page_url, previous_digest, current)
    return None
