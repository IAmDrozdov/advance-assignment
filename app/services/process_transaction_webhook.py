from dataclasses import dataclass
from app.schemas.webhooks import TransactionSettledWebhookIn
from app.storage import storage
from app.services.reconciler import TransactionReconciler


@dataclass
class ProcessTransactionWebhook:
    payload: TransactionSettledWebhookIn

    def __call__(self) -> bool:
        transaction_id = self.payload.transaction_id
        if storage.get_transaction(transaction_id):
            print(f"Transaction {transaction_id} already exists")
            return False
        transaction_data = {
            "transaction_id": transaction_id,
            "reference": self.payload.reference,
            "amount": str(self.payload.amount),
            "currency": self.payload.currency,
            "payer_name": self.payload.payer_name,
            "payer_account_last_four": self.payload.payer_account_last_four,
            "settled_at": self.payload.settled_at.isoformat(),
            "bank_reference": self.payload.bank_reference,
        }
        transaction_record = storage.add_transaction(transaction_data)
        is_reconciled = self._reconcile_transaction(transaction_record)
        return is_reconciled

    def _reconcile_transaction(self, transaction_record: dict) -> bool:
        is_reconciled = TransactionReconciler(transaction_record)()
        print(f"Transaction {transaction_record['transaction_id']} {'not ' if not is_reconciled else ''}reconciled")
        return is_reconciled