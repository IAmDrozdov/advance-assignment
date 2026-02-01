from fastapi import APIRouter
from app.storage import storage
from app.dependencies.payments import PaymentDep
from app.schemas.payments import PaymentOut, PaymentWithLinksOut

router = APIRouter(
    prefix="/payments",
    tags=["payments"],
)


@router.get("/")
def get_payments() -> list[PaymentOut]:
    return storage.get_all_payments()


@router.get("/{payment_id}")
def get_payment(payment: PaymentDep) -> PaymentWithLinksOut:
    links = storage.get_links_for_payment(payment["payment_id"])
    return {**payment, "reconciliation_links": links}
