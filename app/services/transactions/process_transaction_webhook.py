from dataclasses import dataclass
from app.schemas.webhooks import TransactionSettledWebhookIn
from app.storage import storage


@dataclass
class ProcessTransactionWebhook:
    payload: TransactionSettledWebhookIn

    def __call__(self) -> dict:
        transaction_data = {
            "transaction_id": self.payload.transaction_id,
            "reference": self.payload.reference,
            "amount": str(self.payload.amount),
            "currency": self.payload.currency,
            "payer_name": self.payload.payer_name,
            "payer_account_last_four": self.payload.payer_account_last_four,
            "settled_at": self.payload.settled_at.isoformat(),
            "bank_reference": self.payload.bank_reference,
        }
        storage.add_transaction(transaction_data)
