from typing import Annotated
from fastapi import Depends, HTTPException, Path
from app.storage import storage


def get_payment(payment_id: str = Path(...)) -> dict:
    payment = storage.get_payment(payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment


PaymentDep = Annotated[dict, Depends(get_payment)]
