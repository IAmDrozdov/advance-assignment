from fastapi import APIRouter
from app.storage import storage
from app.dependencies.payments import PaymentDep

router = APIRouter(
    prefix="/payments",
    tags=["payments"],
)


@router.get("/")
def get_payments():
    return storage.get_all_payments()


@router.get("/{payment_id}")
def get_payment(payment: PaymentDep):
    return payment
