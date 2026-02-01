from dataclasses import dataclass
from app.schemas.webhooks import PaymentCreateWebhookIn
from app.storage import storage
from app.services.reconciler import PaymentReconciler


@dataclass
class ProcessPaymentWebhook:
    payload: PaymentCreateWebhookIn

    def __call__(self):
        payment_id = self.payload.payment_id
        if storage.get_payment(payment_id):
            print(f"Payment {payment_id} already exists")
            return
        payment_data = {
            "payment_id": payment_id,
            "reference": self.payload.reference,
            "expected_amount": str(self.payload.expected_amount),
            "currency": self.payload.currency,
            "payer_name": self.payload.payer_name,
            "payer_email": self.payload.payer_email,
            "due_date": self.payload.due_date,
            "description": self.payload.description,
        }
        payment_record = storage.add_payment(payment_data)
        self._reconcile_unmatched_transactions(payment_record)

    def _reconcile_unmatched_transactions(self, payment: dict) -> None:
        matched_count = PaymentReconciler(payment)()
        if matched_count > 0:
            print(f"Payment {payment['payment_id']}: retroactively matched {matched_count} transaction(s)")
