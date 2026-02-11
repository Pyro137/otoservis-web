from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.payment import Payment
from app.repositories.base import BaseRepository


class PaymentRepository(BaseRepository[Payment]):
    def __init__(self, db: Session):
        super().__init__(Payment, db)

    def get_by_work_order(self, work_order_id: int) -> List[Payment]:
        return (
            self.db.query(Payment)
            .filter(Payment.work_order_id == work_order_id)
            .order_by(Payment.payment_date.desc())
            .all()
        )

    def get_total_for_work_order(self, work_order_id: int) -> float:
        result = (
            self.db.query(func.coalesce(func.sum(Payment.amount), 0))
            .filter(Payment.work_order_id == work_order_id)
            .scalar()
        )
        return float(result)
