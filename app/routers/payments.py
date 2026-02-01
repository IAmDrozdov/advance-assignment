from fastapi import APIRouter, Query
from app.storage import storage
from app.dependencies.payments import PaymentDep
from app.schemas.payments import PaymentWithLinksOut, PaginatedPaymentsOut

router = APIRouter(
    prefix="/payments",
    tags=["payments"],
)


@router.get(
    "/",
    summary="List All Payments",
    description="Retrieves a paginated list of all payments in the system. Supports pagination via offset and limit parameters.",
    response_description="Paginated list of payments with total count",
)
def get_payments(
    offset: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of records to return"),
) -> PaginatedPaymentsOut:
    all_payments = storage.get_all_payments()
    total = len(all_payments)
    items = all_payments[offset:offset + limit]
    return PaginatedPaymentsOut(items=items, total=total)


@router.get(
    "/{payment_id}",
    summary="Get Payment Details",
    description="Retrieves a single payment by its ID, including all reconciliation links to associated transactions.",
    response_description="Payment details with reconciliation links",
)
def get_payment(payment: PaymentDep) -> PaymentWithLinksOut:
    links = storage.get_links_for_payment(payment["payment_id"])
    return {**payment, "reconciliation_links": links}
