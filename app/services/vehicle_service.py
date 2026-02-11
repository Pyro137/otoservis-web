from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.vehicle import Vehicle
from app.repositories.vehicle_repo import VehicleRepository
from app.repositories.audit_log_repo import AuditLogRepository
from app.core.enums import AuditAction


class VehicleService:
    def __init__(self, db: Session):
        self.repo = VehicleRepository(db)
        self.audit = AuditLogRepository(db)

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Vehicle]:
        return self.repo.get_all(skip=skip, limit=limit)

    def count(self) -> int:
        return self.repo.count()

    def get_by_id(self, vehicle_id: int) -> Optional[Vehicle]:
        return self.repo.get_active_by_id(vehicle_id)

    def get_by_customer(self, customer_id: int) -> List[Vehicle]:
        return self.repo.get_by_customer(customer_id)

    def search(self, query: str) -> List[Vehicle]:
        return self.repo.search(query)

    def create(self, data: dict, user_id: int = None) -> Vehicle:
        # Normalize plate number
        if "plate_number" in data:
            data["plate_number"] = data["plate_number"].upper().strip()
        vehicle = self.repo.create(data)
        if user_id:
            self.audit.log(user_id, "Vehicle", vehicle.id, AuditAction.CREATE, data)
        return vehicle

    def update(self, vehicle_id: int, data: dict, user_id: int = None) -> Optional[Vehicle]:
        vehicle = self.repo.get_active_by_id(vehicle_id)
        if not vehicle:
            return None
        if "plate_number" in data:
            data["plate_number"] = data["plate_number"].upper().strip()
        changes = {}
        for key, value in data.items():
            old_val = getattr(vehicle, key, None)
            if old_val != value:
                changes[key] = {"old": str(old_val), "new": str(value)}
        vehicle = self.repo.update(vehicle, data)
        if user_id and changes:
            self.audit.log(user_id, "Vehicle", vehicle.id, AuditAction.UPDATE, changes)
        return vehicle

    def delete(self, vehicle_id: int, user_id: int = None) -> bool:
        vehicle = self.repo.get_active_by_id(vehicle_id)
        if not vehicle:
            return False
        self.repo.soft_delete(vehicle)
        if user_id:
            self.audit.log(user_id, "Vehicle", vehicle_id, AuditAction.DELETE)
        return True
