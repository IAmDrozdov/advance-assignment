from fastapi import APIRouter, Query
from app.storage import storage
from app.dependencies.payments import PaymentDep
from app.schemas.payments import PaymentWithLinksOut, PaginatedPaymentsOut

router = APIRouter(
    prefix="/payments",
    tags=["payments"],
)


@router.get("/")
def get_payments(
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
) -> PaginatedPaymentsOut:
    all_payments = storage.get_all_payments()
    total = len(all_payments)
    items = all_payments[offset:offset + limit]
    return PaginatedPaymentsOut(items=items, total=total)


@router.get("/{payment_id}")
def get_payment(payment: PaymentDep) -> PaymentWithLinksOut:
    links = storage.get_links_for_payment(payment["payment_id"])
    return {**payment, "reconciliation_links": links}
