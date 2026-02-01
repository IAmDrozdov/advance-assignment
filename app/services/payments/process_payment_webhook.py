from dataclasses import dataclass
from app.schemas.webhooks import PaymentCreateWebhookIn
from app.storage import storage


@dataclass
class ProcessPaymentWebhook:
    payload: PaymentCreateWebhookIn

    def __call__(self) -> dict:
        payment_data = {
            "payment_id": self.payload.payment_id,
            "reference": self.payload.reference,
            "expected_amount": str(self.payload.expected_amount),
            "currency": self.payload.currency,
            "payer_name": self.payload.payer_name,
            "payer_email": self.payload.payer_email,
            "due_date": self.payload.due_date,
            "description": self.payload.description,
        }
        storage.add_payment(payment_data)
