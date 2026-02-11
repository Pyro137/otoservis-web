from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.payment import Payment
from app.repositories.payment_repo import PaymentRepository
from app.repositories.audit_log_repo import AuditLogRepository
from app.core.enums import AuditAction


class PaymentService:
    def __init__(self, db: Session):
        self.repo = PaymentRepository(db)
        self.audit = AuditLogRepository(db)

    def get_by_work_order(self, work_order_id: int) -> List[Payment]:
        return self.repo.get_by_work_order(work_order_id)

    def get_total_for_work_order(self, work_order_id: int) -> float:
        return self.repo.get_total_for_work_order(work_order_id)

    def create(self, data: dict, user_id: int = None) -> Payment:
        payment = self.repo.create(data)
        if user_id:
            self.audit.log(user_id, "Payment", payment.id, AuditAction.CREATE, data)
        return payment

    def delete(self, payment_id: int, user_id: int = None) -> bool:
        payment = self.repo.get_by_id(payment_id)
        if not payment:
            return False
        self.repo.hard_delete(payment)
        if user_id:
            self.audit.log(user_id, "Payment", payment_id, AuditAction.DELETE)
        return True
