import hmac
import hashlib
import json
from pathlib import Path
from typing import Annotated, TypeVar
from fastapi import Depends, HTTPException, Header, Request
from pydantic import BaseModel
from app.config import settings

WEBHOOK_PAYLOADS_FILE = Path("webhook_payloads.json")

T = TypeVar("T", bound=BaseModel)


def dump_payload_to_file(payload: dict) -> None:
    payloads = []
    if WEBHOOK_PAYLOADS_FILE.exists():
        with open(WEBHOOK_PAYLOADS_FILE, "r") as f:
            payloads = json.load(f)
    payloads.append(payload)
    with open(WEBHOOK_PAYLOADS_FILE, "w") as f:
        json.dump(payloads, f, indent=2)


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
        print("=== WEBHOOK VALIDATION FAILED (401) ===")
        print(f"Raw body bytes: {body}")
        print(f"Raw payload: {payload}")
        print(f"Payload for signature (excluding sandbox_id): {payload_for_signature}")
        print(f"Canonical JSON: {canonical_json}")
        print(f"Expected signature: {expected_signature}")
        print(f"Received signature: {x_webhook_signature}")
        print(f"Webhook secret used: {settings.webhook_secret[:4]}...{settings.webhook_secret[-4:]}")
        print("========================================")
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    dump_payload_to_file(payload)
    return payload


WebhookPayloadDep = Annotated[dict, Depends(verify_webhook_signature)]


def validated_webhook_dep(model: type[T]):
    async def dependency(payload: WebhookPayloadDep) -> T:
        return model.model_validate(payload)
    return dependency
