from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.vehicle import Vehicle
from app.repositories.base import BaseRepository


class VehicleRepository(BaseRepository[Vehicle]):
    def __init__(self, db: Session):
        super().__init__(Vehicle, db)

    def get_by_plate(self, plate_number: str) -> Optional[Vehicle]:
        return (
            self.db.query(Vehicle)
            .filter(Vehicle.plate_number == plate_number.upper(), Vehicle.is_deleted == False)  # noqa: E712
            .first()
        )

    def get_by_customer(self, customer_id: int) -> List[Vehicle]:
        return (
            self.db.query(Vehicle)
            .filter(Vehicle.customer_id == customer_id, Vehicle.is_deleted == False)  # noqa: E712
            .order_by(Vehicle.id.desc())
            .all()
        )

    def search(self, query: str, skip: int = 0, limit: int = 50) -> List[Vehicle]:
        search_term = f"%{query}%"
        return (
            self.db.query(Vehicle)
            .filter(Vehicle.is_deleted == False)  # noqa: E712
            .filter(
                Vehicle.plate_number.ilike(search_term)
                | Vehicle.brand.ilike(search_term)
                | Vehicle.model.ilike(search_term)
            )
            .order_by(Vehicle.id.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
