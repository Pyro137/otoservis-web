from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.repositories.customer_repo import CustomerRepository
from app.repositories.audit_log_repo import AuditLogRepository
from app.core.enums import AuditAction


class CustomerService:
    def __init__(self, db: Session):
        self.repo = CustomerRepository(db)
        self.audit = AuditLogRepository(db)

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Customer]:
        return self.repo.get_all(skip=skip, limit=limit)

    def count(self) -> int:
        return self.repo.count()

    def get_by_id(self, customer_id: int) -> Optional[Customer]:
        return self.repo.get_active_by_id(customer_id)

    def search(self, query: str) -> List[Customer]:
        return self.repo.search(query)

    def create(self, data: dict, user_id: int = None) -> Customer:
        customer = self.repo.create(data)
        if user_id:
            self.audit.log(user_id, "Customer", customer.id, AuditAction.CREATE, data)
        return customer

    def update(self, customer_id: int, data: dict, user_id: int = None) -> Optional[Customer]:
        customer = self.repo.get_active_by_id(customer_id)
        if not customer:
            return None
        # Track changes
        changes = {}
        for key, value in data.items():
            old_val = getattr(customer, key, None)
            if old_val != value:
                changes[key] = {"old": str(old_val), "new": str(value)}
        customer = self.repo.update(customer, data)
        if user_id and changes:
            self.audit.log(user_id, "Customer", customer.id, AuditAction.UPDATE, changes)
        return customer

    def delete(self, customer_id: int, user_id: int = None) -> bool:
        customer = self.repo.get_active_by_id(customer_id)
        if not customer:
            return False
        self.repo.soft_delete(customer)
        if user_id:
            self.audit.log(user_id, "Customer", customer_id, AuditAction.DELETE)
        return True
