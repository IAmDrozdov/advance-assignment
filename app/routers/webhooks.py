from typing import Annotated
from fastapi import APIRouter, Depends
from app.dependencies.webhooks import validated_webhook_dep
from app.schemas.webhooks import PaymentCreateWebhookIn, TransactionSettledWebhookIn
from app.services.payments.process_payment_webhook import ProcessPaymentWebhook
from app.services.transactions.process_transaction_webhook import ProcessTransactionWebhook

router = APIRouter(
    prefix="/webhooks",
    tags=["webhooks"],
)

PaymentWebhookDep = Annotated[PaymentCreateWebhookIn, Depends(validated_webhook_dep(PaymentCreateWebhookIn))]
TransactionWebhookDep = Annotated[TransactionSettledWebhookIn, Depends(validated_webhook_dep(TransactionSettledWebhookIn))]


@router.post("/payments")
async def handle_payment_webhook(payload: PaymentWebhookDep):
    return ProcessPaymentWebhook(payload)()


@router.post("/transactions")
async def handle_transaction_webhook(payload: TransactionWebhookDep):
    return ProcessTransactionWebhook(payload)()
