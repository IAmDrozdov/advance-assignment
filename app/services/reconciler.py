from dataclasses import dataclass
from decimal import Decimal
from app.services.constants import PaymentStatus, MatchType
from app.storage import storage
from app.config import settings


def to_decimal(value) -> Decimal:
    return Decimal(str(value)) if value else Decimal("0")


def get_tolerance(amount: Decimal) -> Decimal:
    return amount * to_decimal(settings.fee_tolerance_percent) / Decimal("100")


def normalize_ref(ref: str | None) -> str:
    if not ref: return ""
    return ref.lower().strip().replace("-", "")


def payer_matches(payer1: str | None, payer2: str | None) -> bool:
    if not payer1 or not payer2:
        return False
    p1, p2 = payer1.lower(), payer2.lower()
    return p1 == p2 or p1 in p2 or p2 in p1


def match_reference(txn_ref: str | None, payment_ref: str | None) -> MatchType | None:
    if not txn_ref or not payment_ref:
        return None
    if txn_ref.strip() == payment_ref.strip():
        return MatchType.EXACT
    if normalize_ref(txn_ref) == normalize_ref(payment_ref):
        return MatchType.FUZZY_REF
    return None


def calculate_payment_status(expected: Decimal, received: Decimal) -> PaymentStatus:
    if received <= 0:
        return PaymentStatus.PENDING
    if received > expected:
        return PaymentStatus.OVERPAID
    if received >= expected - get_tolerance(expected):
        return PaymentStatus.FULLY_PAID
    return PaymentStatus.PARTIALLY_PAID


def amount_matches_remaining(txn_amount: Decimal, payment: dict) -> bool:
    remaining = to_decimal(payment.get("expected_amount")) - to_decimal(payment.get("received_amount"))
    return txn_amount <= remaining or txn_amount >= remaining - get_tolerance(remaining)


def create_reconciliation_link(payment: dict, txn: dict, match_type: MatchType) -> None:
    txn_amount = to_decimal(txn.get("amount"))
    
    storage.add_reconciliation_link({
        "payment_id": payment["payment_id"],
        "transaction_id": txn["transaction_id"],
        "match_type": match_type.value,
        "amount": txn_amount,
        "notes": "Refund" if txn_amount < 0 else None,
    })
    storage.update_transaction(txn["transaction_id"], {
        "matched": True,
        "matched_to_payment_id": payment["payment_id"],
    })


def update_payment_received(payment_id: str, txn_amount: Decimal) -> None:
    payment = storage.get_payment(payment_id)
    if not payment:
        return
    
    expected = to_decimal(payment["expected_amount"])
    new_received = to_decimal(payment.get("received_amount")) + txn_amount
    status = calculate_payment_status(expected, new_received)
    
    storage.update_payment(payment_id, {
        "received_amount": str(new_received),
        "status": status.value,
    })


@dataclass
class TransactionReconciler:
    transaction: dict

    @property
    def amount(self) -> Decimal:
        return to_decimal(self.transaction.get("amount"))

    @property
    def currency(self) -> str:
        return self.transaction.get("currency", "USD")

    @property
    def reference(self) -> str | None:
        return self.transaction.get("reference")

    @property
    def payer(self) -> str | None:
        return self.transaction.get("payer_name")

    def __call__(self) -> bool:
        payment, match_type = self._find_payment()
        if not payment:
            return False
        create_reconciliation_link(payment, self.transaction, match_type)
        update_payment_received(payment["payment_id"], self.amount)
        return True

    def _find_payment(self) -> tuple[dict | None, MatchType | None]:
        if match := self._match_by_reference():
            return match
        if not self.reference and (match := self._match_by_payer_amount()):
            return match
        if self.amount < 0 and (match := self._match_refund_by_payer()):
            return match
        return None, None

    def _match_by_reference(self) -> tuple[dict, MatchType] | None:
        if not self.reference:
            return None
        for p in storage.get_all_payments(currency=self.currency):
            if match_type := match_reference(self.reference, p.get("reference")):
                return p, match_type
        return None

    def _match_by_payer_amount(self) -> tuple[dict, MatchType] | None:
        if not self.payer:
            return None
        candidates = storage.get_all_payments(
            currency=self.currency,
            status__in=[PaymentStatus.PENDING.value, PaymentStatus.PARTIALLY_PAID.value]
        )
        for p in candidates:
            if not payer_matches(self.payer, p.get("payer_name")):
                continue
            if amount_matches_remaining(abs(self.amount), p):
                return p, MatchType.AMOUNT_ONLY
        return None

    def _match_refund_by_payer(self) -> tuple[dict, MatchType] | None:
        if not self.payer:
            return None
        for link in storage.get_all_reconciliation_links():
            p = storage.get_payment(link.get("payment_id"))
            if not p or p.get("currency") != self.currency:
                continue
            if payer_matches(self.payer, p.get("payer_name")):
                return p, MatchType.EXACT
        return None


@dataclass
class PaymentReconciler:
    payment: dict

    @property
    def currency(self) -> str:
        return self.payment.get("currency", "USD")

    @property
    def reference(self) -> str | None:
        return self.payment.get("reference")

    @property
    def payer(self) -> str | None:
        return self.payment.get("payer_name")

    def __call__(self) -> int:
        matched_count = 0
        for txn in storage.get_unmatched_transactions():
            if txn.get("currency") != self.currency:
                continue
            if match_type := self._check_match(txn):
                create_reconciliation_link(self.payment, txn, match_type)
                update_payment_received(self.payment["payment_id"], to_decimal(txn.get("amount")))
                matched_count += 1
        return matched_count

    def _check_match(self, txn: dict) -> MatchType | None:
        if match_type := match_reference(txn.get("reference"), self.reference):
            return match_type
        if not txn.get("reference") and to_decimal(txn.get("amount")) > 0:
            if self._matches_by_payer_amount(txn):
                return MatchType.AMOUNT_ONLY
        return None

    def _matches_by_payer_amount(self, txn: dict) -> bool:
        if not payer_matches(txn.get("payer_name"), self.payer):
            return False
        payment = storage.get_payment(self.payment["payment_id"])
        if not payment or payment.get("status") not in [PaymentStatus.PENDING.value, PaymentStatus.PARTIALLY_PAID.value]:
            return False
        return amount_matches_remaining(abs(to_decimal(txn.get("amount"))), payment)
