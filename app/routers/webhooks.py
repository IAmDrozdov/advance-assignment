from typing import Annotated
from fastapi import APIRouter, Depends, Request
from app.dependencies.webhooks import validated_webhook_dep
from app.schemas.webhooks import PaymentCreateWebhookIn, TransactionSettledWebhookIn
from app.services.process_payment_webhook import ProcessPaymentWebhook
from app.services.process_transaction_webhook import ProcessTransactionWebhook
from app.middleware.rate_limiter import limiter
from app.config import settings

router = APIRouter(
    prefix="/webhooks",
    tags=["webhooks"],
)

PaymentWebhookDep = Annotated[PaymentCreateWebhookIn, Depends(validated_webhook_dep(PaymentCreateWebhookIn))]
TransactionWebhookDep = Annotated[TransactionSettledWebhookIn, Depends(validated_webhook_dep(TransactionSettledWebhookIn))]


@router.post(
    "/payments",
    summary="Receive Payment Created Webhook",
    description="Handles incoming payment.created webhook events from the payment provider. Creates a new payment record and triggers automatic reconciliation with existing transactions.",
    response_description="Empty response on successful processing",
    status_code=200,
)
@limiter.limit(settings.webhook_rate_limit)
async def handle_payment_webhook(request: Request, payload: PaymentWebhookDep):
    ProcessPaymentWebhook(payload)()


@router.post(
    "/transactions",
    summary="Receive Transaction Settled Webhook",
    description="Handles incoming transaction.settled webhook events from the bank. Creates a new transaction record and triggers automatic reconciliation with existing payments.",
    response_description="Empty response on successful processing",
    status_code=200,
)
@limiter.limit(settings.webhook_rate_limit)
async def handle_transaction_webhook(request: Request, payload: TransactionWebhookDep):
    ProcessTransactionWebhook(payload)()

