from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, date

from app.models.work_order import WorkOrder
from app.core.enums import WorkOrderStatus
from app.repositories.base import BaseRepository


class WorkOrderRepository(BaseRepository[WorkOrder]):
    def __init__(self, db: Session):
        super().__init__(WorkOrder, db)

    def get_by_status(self, status: WorkOrderStatus, skip: int = 0, limit: int = 50) -> List[WorkOrder]:
        return (
            self.db.query(WorkOrder)
            .filter(WorkOrder.status == status, WorkOrder.is_deleted == False)  # noqa: E712
            .order_by(WorkOrder.id.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_active_orders(self) -> List[WorkOrder]:
        active_statuses = [
            WorkOrderStatus.PENDING,
            WorkOrderStatus.APPROVED,
            WorkOrderStatus.IN_PROGRESS,
        ]
        return (
            self.db.query(WorkOrder)
            .filter(WorkOrder.status.in_(active_statuses), WorkOrder.is_deleted == False)  # noqa: E712
            .order_by(WorkOrder.id.desc())
            .all()
        )

    def count_active(self) -> int:
        active_statuses = [
            WorkOrderStatus.PENDING,
            WorkOrderStatus.APPROVED,
            WorkOrderStatus.IN_PROGRESS,
        ]
        return (
            self.db.query(WorkOrder)
            .filter(WorkOrder.status.in_(active_statuses), WorkOrder.is_deleted == False)  # noqa: E712
            .count()
        )

    def get_revenue_today(self) -> float:
        today = date.today()
        result = (
            self.db.query(func.coalesce(func.sum(WorkOrder.grand_total), 0))
            .filter(
                WorkOrder.status == WorkOrderStatus.COMPLETED,
                func.date(WorkOrder.completed_at) == today,
                WorkOrder.is_deleted == False,  # noqa: E712
            )
            .scalar()
        )
        return float(result)

    def get_revenue_month(self, year: int = None, month: int = None) -> float:
        now = datetime.now()
        year = year or now.year
        month = month or now.month
        result = (
            self.db.query(func.coalesce(func.sum(WorkOrder.grand_total), 0))
            .filter(
                WorkOrder.status.in_([WorkOrderStatus.COMPLETED, WorkOrderStatus.DELIVERED]),
                func.extract("year", WorkOrder.completed_at) == year,
                func.extract("month", WorkOrder.completed_at) == month,
                WorkOrder.is_deleted == False,  # noqa: E712
            )
            .scalar()
        )
        return float(result)

    def get_recent_completed(self, limit: int = 10) -> List[WorkOrder]:
        return (
            self.db.query(WorkOrder)
            .filter(
                WorkOrder.status.in_([WorkOrderStatus.COMPLETED, WorkOrderStatus.DELIVERED]),
                WorkOrder.is_deleted == False,  # noqa: E712
            )
            .order_by(WorkOrder.completed_at.desc())
            .limit(limit)
            .all()
        )

    def get_next_order_number(self) -> str:
        now = datetime.now()
        prefix = f"IS-{now.strftime('%Y%m')}"
        last_order = (
            self.db.query(WorkOrder)
            .filter(WorkOrder.work_order_number.like(f"{prefix}%"))
            .order_by(WorkOrder.id.desc())
            .first()
        )
        if last_order:
            last_num = int(last_order.work_order_number.split("-")[-1])
            next_num = last_num + 1
        else:
            next_num = 1
        return f"{prefix}-{next_num:04d}"

    def get_by_vehicle(self, vehicle_id: int) -> List[WorkOrder]:
        return (
            self.db.query(WorkOrder)
            .filter(WorkOrder.vehicle_id == vehicle_id, WorkOrder.is_deleted == False)  # noqa: E712
            .order_by(WorkOrder.id.desc())
            .all()
        )

    def get_by_customer(self, customer_id: int) -> List[WorkOrder]:
        return (
            self.db.query(WorkOrder)
            .filter(WorkOrder.customer_id == customer_id, WorkOrder.is_deleted == False)  # noqa: E712
            .order_by(WorkOrder.id.desc())
            .all()
        )
