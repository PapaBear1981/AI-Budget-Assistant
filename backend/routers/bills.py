"""Bill tracking endpoints"""

from typing import List
from datetime import date

from fastapi import APIRouter, Depends, status, HTTPException
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from ..core.auth import get_current_user, User
from ..core.database import Bill, get_db

router = APIRouter()


class BillCreate(BaseModel):
    name: str
    amount: float
    due_date: date
    is_recurring: bool = Field(default=False)


@router.post("/bills", response_model=Bill, status_code=status.HTTP_201_CREATED)
def create_bill(
    bill: BillCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new bill record."""
    db_bill = Bill(user_id=current_user.id, **bill.dict())
    db.add(db_bill)
    db.commit()
    db.refresh(db_bill)
    return db_bill


@router.get("/bills", response_model=List[Bill])
def list_bills(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List bills for the current user."""
    stmt = select(Bill).where(Bill.user_id == current_user.id).order_by(Bill.due_date)
    return db.exec(stmt).all()


@router.delete("/bills/{bill_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_bill(
    bill_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a bill."""
    bill_obj = db.get(Bill, bill_id)
    if not bill_obj or bill_obj.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Bill not found")
    db.delete(bill_obj)
    db.commit()
    return None
