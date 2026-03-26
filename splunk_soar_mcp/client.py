from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any

import httpx

from .config import SOAR_HOST, SOAR_PASS, SOAR_TOKEN, SOAR_USER, SOAR_VERIFY_SSL


@asynccontextmanager
async def app_lifespan(server):
    kwargs: dict[str, Any] = {
        "base_url": SOAR_HOST,
        "verify": SOAR_VERIFY_SSL,
        "timeout": 30.0,
    }
    if SOAR_USER and SOAR_PASS:
        kwargs["auth"] = httpx.BasicAuth(SOAR_USER, SOAR_PASS)
    else:
        kwargs["headers"] = {"ph-auth-token": SOAR_TOKEN}

    async with httpx.AsyncClient(**kwargs) as client:
        yield {"client": client}


def _err(e: Exception) -> str:
    if isinstance(e, httpx.HTTPStatusError):
        code = e.response.status_code
        if code == 401:
            return f"Authentication failed (401). Verify SOAR_TOKEN is valid and the automation user is active."
        if code == 403:
            return f"Permission denied (403). The automation user lacks required permissions for this operation."
        if code == 404:
            return f"Not found (404). Verify the resource ID exists. Detail: {e.response.text}"
        if code == 429:
            return "Rate limited (429). SOAR is throttling requests — wait and retry."
        return f"HTTP {code}: {e.response.text}"
    if isinstance(e, httpx.ConnectError):
        return f"Connection failed. Verify SOAR_HOST ({SOAR_HOST}) is reachable."
    if isinstance(e, httpx.TimeoutException):
        return "Request timed out. SOAR may be under heavy load — retry shortly."
    return f"Unexpected error: {e}"


def _pagination_params(limit: int, page: int) -> dict[str, int]:
    return {"page_size": limit, "page": page}


def _filter(field: str, value: str | int) -> dict[str, str]:
    if isinstance(value, int):
        return {f"_filter_{field}": str(value)}
    return {f"_filter_{field}": f'"{value}"'}
