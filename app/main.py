"""
Payment Reconciliation Service

Build your API here!
"""

from fastapi import FastAPI
from app.routers import webhooks, payments
app = FastAPI(
    title="Payment Reconciliation Service",
    description="Your reconciliation service goes here.",
    version="1.0.0",
)



@app.get("/")
def root():
    """Health check"""
    return {"status": "healthy", "service": "reconciliation-service"}


app.include_router(webhooks.router)
app.include_router(payments.router)

# app.include_router(payments.router)
