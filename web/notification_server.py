from __future__ import annotations

import os
from typing import Any

import httpx
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field


app = FastAPI(
    title="GTI-AI-V2 Notification Gateway",
    version="1.0.0",
)


NTFY_URL = os.getenv(
    "NTFY_URL",
    "https://ntfy.sh/gti_ai_geoffrey_signals",
)
WEBHOOK_TOKEN = os.getenv("WEBHOOK_TOKEN", "")


class TestNotification(BaseModel):
    message: str = Field(
        min_length=1,
        max_length=4000,
    )
    source: str = Field(
        default="unknown",
        min_length=1,
        max_length=100,
    )


async def send_ntfy(
    title: str,
    message: str,
    priority: str = "high",
) -> None:
    headers = {
        "Title": title,
        "Priority": priority,
        "Tags": "bell",
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(
            NTFY_URL,
            content=message.encode("utf-8"),
            headers=headers,
        )

    response.raise_for_status()


def verify_token(
    authorization: str | None,
    x_webhook_token: str | None,
) -> None:
    if not WEBHOOK_TOKEN:
        raise HTTPException(
            status_code=500,
            detail="WEBHOOK_TOKEN is not configured",
        )

    bearer = ""
    if authorization and authorization.startswith("Bearer "):
        bearer = authorization.removeprefix("Bearer ").strip()

    supplied = x_webhook_token or bearer

    if supplied != WEBHOOK_TOKEN:
        raise HTTPException(
            status_code=401,
            detail="Invalid webhook token",
        )


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "service": "GTI-AI-V2 Notification Gateway",
        "status": "online",
    }


@app.get("/health")
async def health() -> dict[str, str]:
    return {
        "status": "healthy",
        "service": "notification-gateway",
    }


@app.post("/webhook/test")
async def test_notification(
    payload: TestNotification,
    authorization: str | None = Header(default=None),
    x_webhook_token: str | None = Header(default=None),
) -> dict[str, Any]:
    verify_token(
        authorization=authorization,
        x_webhook_token=x_webhook_token,
    )

    message = (
        f"GTI-AI-V2 notification test\n"
        f"Source: {payload.source}\n\n"
        f"{payload.message}"
    )

    try:
        await send_ntfy(
            title="GTI-AI-V2 TEST",
            message=message,
            priority="high",
        )
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"ntfy request failed: {exc}",
        ) from exc

    return {
        "status": "ok",
        "notification": "sent",
        "source": payload.source,
    }
