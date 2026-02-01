import hmac
import hashlib
import json
from typing import Annotated
from fastapi import Depends, HTTPException, Header, Request
from app.config import settings


async def verify_webhook_signature(
    request: Request,
    x_webhook_signature: str = Header(...)
) -> dict:
    body = await request.body()
    payload = json.loads(body)

    payload_for_signature = {k: v for k, v in payload.items() if k != "sandbox_id"}
    canonical_json = json.dumps(payload_for_signature, sort_keys=True, separators=(',', ':'))

    expected_signature = "sha256=" + hmac.new(
        settings.webhook_secret.encode(),
        canonical_json.encode(),
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(expected_signature, x_webhook_signature):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    return payload


WebhookPayloadDep = Annotated[dict, Depends(verify_webhook_signature)]
