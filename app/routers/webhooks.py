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


@router.post("/payments")
@limiter.limit(settings.webhook_rate_limit)
async def handle_payment_webhook(request: Request, payload: PaymentWebhookDep):
    ProcessPaymentWebhook(payload)()


@router.post("/transactions")
@limiter.limit(settings.webhook_rate_limit)
async def handle_transaction_webhook(request: Request, payload: TransactionWebhookDep):
    ProcessTransactionWebhook(payload)()

