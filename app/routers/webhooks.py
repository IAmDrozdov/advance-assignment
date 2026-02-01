from fastapi import APIRouter
from app.dependencies.webhooks import WebhookPayloadDep

router = APIRouter(
    prefix="/webhooks",
    tags=["webhooks"],
)


@router.post("/payments")
async def handle_payment_webhook(payload: WebhookPayloadDep):
    print(payload)
    return len(payload)


@router.post("/transactions")
async def handle_transaction_webhook(payload: WebhookPayloadDep):
    print(payload)
    return len(payload)
