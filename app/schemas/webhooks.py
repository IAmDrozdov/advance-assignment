from datetime import datetime
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel


class PaymentCreateWebhookIn(BaseModel):
    event_type: Literal["payment.created"]
    payment_id: str
    reference: str
    expected_amount: Decimal
    currency: str
    payer_name: str
    payer_email: str
    due_date: str
    description: str | None = None
    timestamp: datetime
    sandbox_id: str


class TransactionSettledWebhookIn(BaseModel):
    event_type: Literal["transaction.settled"]
    transaction_id: str
    reference: str | None
    amount: Decimal
    currency: str
    payer_name: str
    payer_account_last_four: str
    settled_at: datetime
    bank_reference: str
    timestamp: datetime
    sandbox_id: str
