"""Transaction management endpoints"""

from typing import List
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from ..core.auth import get_current_user, User
from ..core.database import Transaction, get_db

router = APIRouter()


class TransactionCreate(BaseModel):
    amount: float = Field(..., description="Positive for income, negative for expense")
    description: str
    category: str = Field(default="Uncategorized")
    date: date = Field(default_factory=date.today)


@router.post("/transactions", response_model=Transaction, status_code=status.HTTP_201_CREATED)
def create_transaction(
    txn: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new financial transaction."""
    db_txn = Transaction(user_id=current_user.id, **txn.dict())
    db.add(db_txn)
    db.commit()
    db.refresh(db_txn)
    return db_txn


@router.get("/transactions", response_model=List[Transaction])
def list_transactions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List transactions for the current user."""
    stmt = select(Transaction).where(Transaction.user_id == current_user.id).order_by(Transaction.date.desc())
    return db.exec(stmt).all()


@router.get("/transactions/{transaction_id}", response_model=Transaction)
def get_transaction(
    transaction_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve a single transaction."""
    txn = db.get(Transaction, transaction_id)
    if not txn or txn.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return txn


@router.delete("/transactions/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
    transaction_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a transaction."""
    txn = db.get(Transaction, transaction_id)
    if not txn or txn.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Transaction not found")
    db.delete(txn)
    db.commit()
    return None
