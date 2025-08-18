"""Budget management endpoints"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from ..core.auth import get_current_user, User
from ..core.database import Budget, get_db

router = APIRouter()


class BudgetCreate(BaseModel):
    category: str
    limit: float = Field(..., description="Spending limit for the period")
    period: str = Field(default="monthly")


@router.post("/budgets", response_model=Budget, status_code=status.HTTP_201_CREATED)
def create_budget(
    budget: BudgetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new budget entry."""
    db_budget = Budget(user_id=current_user.id, **budget.dict())
    db.add(db_budget)
    db.commit()
    db.refresh(db_budget)
    return db_budget


@router.get("/budgets", response_model=List[Budget])
def list_budgets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List budgets for the current user."""
    stmt = select(Budget).where(Budget.user_id == current_user.id)
    return db.exec(stmt).all()
