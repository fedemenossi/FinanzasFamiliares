from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import Transaction, User
from app.schemas import TransactionOut, TransactionUpdate

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.get("", response_model=list[TransactionOut])
def list_transactions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    category_id: int | None = None,
    q: str | None = Query(default=None),
    limit: int = Query(default=300, le=1000),
):
    stmt = (
        select(Transaction)
        .options(joinedload(Transaction.category))
        .where(Transaction.user_id == current_user.id)
        .order_by(Transaction.transaction_date.desc(), Transaction.id.desc())
        .limit(limit)
    )
    if category_id:
        stmt = stmt.where(Transaction.category_id == category_id)
    if q:
        stmt = stmt.where(Transaction.normalized_description.like(f"%{q.upper()}%"))
    return db.scalars(stmt).all()


@router.patch("/{transaction_id}", response_model=TransactionOut)
def update_transaction(
    transaction_id: int,
    payload: TransactionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    transaction = db.scalar(
        select(Transaction)
        .options(joinedload(Transaction.category))
        .where(Transaction.id == transaction_id, Transaction.user_id == current_user.id)
    )
    if not transaction:
        raise HTTPException(status_code=404, detail="Movimiento no encontrado")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(transaction, field, value)
    db.commit()
    db.refresh(transaction)
    return transaction
