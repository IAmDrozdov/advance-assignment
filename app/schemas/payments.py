from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel
from app.services.payments.constants import PaymentStatus, MatchType


class ReconciliationLinkOut(BaseModel):
    link_id: str
    payment_id: str
    transaction_id: str
    match_type: MatchType | None
    amount: Decimal | None
    notes: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class PaymentOut(BaseModel):
    payment_id: str
    reference: str | None
    expected_amount: Decimal
    currency: str
    payer_name: str | None
    payer_email: str | None
    due_date: str | None
    description: str | None
    status: PaymentStatus
    received_amount: Decimal
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PaymentWithLinksOut(PaymentOut):
    reconciliation_links: list[ReconciliationLinkOut]


class PaginatedPaymentsOut(BaseModel):
    items: list[PaymentOut]
    total: int
