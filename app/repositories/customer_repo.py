from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.customer import Customer
from app.repositories.base import BaseRepository


class CustomerRepository(BaseRepository[Customer]):
    def __init__(self, db: Session):
        super().__init__(Customer, db)

    def search(self, query: str, skip: int = 0, limit: int = 50) -> List[Customer]:
        search_term = f"%{query}%"
        return (
            self.db.query(Customer)
            .filter(Customer.is_deleted == False)  # noqa: E712
            .filter(
                or_(
                    Customer.full_name.ilike(search_term),
                    Customer.phone.ilike(search_term),
                    Customer.company_name.ilike(search_term),
                    Customer.tax_number.ilike(search_term),
                )
            )
            .order_by(Customer.id.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_phone(self, phone: str) -> Optional[Customer]:
        return (
            self.db.query(Customer)
            .filter(Customer.phone == phone, Customer.is_deleted == False)  # noqa: E712
            .first()
        )
