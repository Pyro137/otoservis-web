from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.part import Part
from app.repositories.base import BaseRepository


class PartRepository(BaseRepository[Part]):
    def __init__(self, db: Session):
        super().__init__(Part, db)

    def get_by_stock_code(self, stock_code: str) -> Optional[Part]:
        return self.db.query(Part).filter(Part.stock_code == stock_code).first()

    def get_low_stock(self) -> List[Part]:
        return (
            self.db.query(Part)
            .filter(Part.is_active == True, Part.stock_quantity <= Part.critical_level)  # noqa: E712
            .order_by(Part.stock_quantity)
            .all()
        )

    def search(self, query: str, skip: int = 0, limit: int = 50) -> List[Part]:
        search_term = f"%{query}%"
        return (
            self.db.query(Part)
            .filter(Part.is_active == True)  # noqa: E712
            .filter(
                or_(
                    Part.name.ilike(search_term),
                    Part.stock_code.ilike(search_term),
                    Part.category.ilike(search_term),
                )
            )
            .order_by(Part.id.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_all_active(self, skip: int = 0, limit: int = 100) -> List[Part]:
        return (
            self.db.query(Part)
            .filter(Part.is_active == True)  # noqa: E712
            .order_by(Part.name)
            .offset(skip)
            .limit(limit)
            .all()
        )
