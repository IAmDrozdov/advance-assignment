from enum import Enum


class PaymentStatus(str, Enum):
    PENDING = "PENDING"
    PARTIALLY_PAID = "PARTIALLY_PAID"
    FULLY_PAID = "FULLY_PAID"
    OVERPAID = "OVERPAID"


class MatchType(str, Enum):
    EXACT = "EXACT"
    FUZZY_REF = "FUZZY_REF"
    AMOUNT_ONLY = "AMOUNT_ONLY"
