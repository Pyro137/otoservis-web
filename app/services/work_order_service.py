from typing import List, Optional
from decimal import Decimal
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.work_order import WorkOrder
from app.models.work_order_item import WorkOrderItem
from app.core.enums import WorkOrderStatus, WorkOrderItemType, AuditAction
from app.repositories.work_order_repo import WorkOrderRepository
from app.repositories.work_order_item_repo import WorkOrderItemRepository
from app.repositories.part_repo import PartRepository
from app.repositories.audit_log_repo import AuditLogRepository
from app.core.config import settings


# Valid status transitions
VALID_TRANSITIONS = {
    WorkOrderStatus.PENDING: [WorkOrderStatus.APPROVED, WorkOrderStatus.CANCELLED],
    WorkOrderStatus.APPROVED: [WorkOrderStatus.IN_PROGRESS, WorkOrderStatus.CANCELLED],
    WorkOrderStatus.IN_PROGRESS: [WorkOrderStatus.COMPLETED, WorkOrderStatus.CANCELLED],
    WorkOrderStatus.COMPLETED: [WorkOrderStatus.DELIVERED],
    WorkOrderStatus.DELIVERED: [],
    WorkOrderStatus.CANCELLED: [],
}


class WorkOrderService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = WorkOrderRepository(db)
        self.item_repo = WorkOrderItemRepository(db)
        self.part_repo = PartRepository(db)
        self.audit = AuditLogRepository(db)

    def get_all(self, skip: int = 0, limit: int = 100) -> List[WorkOrder]:
        return self.repo.get_all(skip=skip, limit=limit)

    def count(self) -> int:
        return self.repo.count()

    def get_by_id(self, work_order_id: int) -> Optional[WorkOrder]:
        return self.repo.get_active_by_id(work_order_id)

    def get_active_orders(self) -> List[WorkOrder]:
        return self.repo.get_active_orders()

    def get_by_status(self, status: WorkOrderStatus) -> List[WorkOrder]:
        return self.repo.get_by_status(status)

    def get_by_vehicle(self, vehicle_id: int) -> List[WorkOrder]:
        return self.repo.get_by_vehicle(vehicle_id)

    def get_by_customer(self, customer_id: int) -> List[WorkOrder]:
        return self.repo.get_by_customer(customer_id)

    def create(self, data: dict, user_id: int = None) -> WorkOrder:
        data["work_order_number"] = self.repo.get_next_order_number()
        data["vat_rate"] = data.get("vat_rate", settings.DEFAULT_VAT_RATE)
        work_order = self.repo.create(data)
        if user_id:
            self.audit.log(user_id, "WorkOrder", work_order.id, AuditAction.CREATE, data)
        return work_order

    def update(self, work_order_id: int, data: dict, user_id: int = None) -> Optional[WorkOrder]:
        work_order = self.repo.get_active_by_id(work_order_id)
        if not work_order:
            return None
        changes = {}
        for key, value in data.items():
            old_val = getattr(work_order, key, None)
            if str(old_val) != str(value):
                changes[key] = {"old": str(old_val), "new": str(value)}
        work_order = self.repo.update(work_order, data)
        if user_id and changes:
            self.audit.log(user_id, "WorkOrder", work_order.id, AuditAction.UPDATE, changes)
        return work_order

    def change_status(self, work_order_id: int, new_status: WorkOrderStatus, user_id: int = None) -> Optional[WorkOrder]:
        work_order = self.repo.get_active_by_id(work_order_id)
        if not work_order:
            return None

        # Validate transition
        allowed = VALID_TRANSITIONS.get(work_order.status, [])
        if new_status not in allowed:
            raise ValueError(
                f"'{work_order.status.value}' durumundan '{new_status.value}' durumuna geçiş yapılamaz."
            )

        old_status = work_order.status
        work_order.status = new_status

        if new_status == WorkOrderStatus.COMPLETED:
            work_order.completed_at = datetime.now()
            # Decrease stock for parts
            self._decrease_stock_for_items(work_order)

        self.db.commit()
        self.db.refresh(work_order)

        if user_id:
            self.audit.log(
                user_id, "WorkOrder", work_order.id, AuditAction.UPDATE,
                {"status": {"old": old_status.value, "new": new_status.value}},
            )
        return work_order

    def _decrease_stock_for_items(self, work_order: WorkOrder):
        """Decrement stock quantity for all part items in the work order."""
        for item in work_order.items:
            if item.type == WorkOrderItemType.PART and item.part_id:
                part = self.part_repo.get_by_id(item.part_id)
                if part:
                    new_qty = part.stock_quantity - int(item.quantity)
                    if new_qty < 0:
                        new_qty = 0
                    self.part_repo.update(part, {"stock_quantity": new_qty})

    def add_item(self, work_order_id: int, item_data: dict, user_id: int = None) -> Optional[WorkOrderItem]:
        work_order = self.repo.get_active_by_id(work_order_id)
        if not work_order:
            return None

        # Calculate line total
        item_data["work_order_id"] = work_order_id
        item_data = self._calculate_item_total(item_data)
        item = self.item_repo.create(item_data)

        # Recalculate work order totals
        self._recalculate_totals(work_order)
        return item

    def remove_item(self, item_id: int, user_id: int = None) -> bool:
        item = self.item_repo.get_by_id(item_id)
        if not item:
            return False
        work_order = self.repo.get_by_id(item.work_order_id)
        self.item_repo.hard_delete(item)
        if work_order:
            self._recalculate_totals(work_order)
        return True

    def _calculate_item_total(self, item_data: dict) -> dict:
        """Calculate line item total: (qty * unit_price) - discount."""
        qty = Decimal(str(item_data.get("quantity", 1)))
        unit_price = Decimal(str(item_data.get("unit_price", 0)))
        discount = Decimal(str(item_data.get("discount", 0)))
        total = (qty * unit_price) - discount
        item_data["total_price"] = max(total, Decimal("0"))
        # Ensure vat_rate has a default
        if "vat_rate" not in item_data:
            item_data["vat_rate"] = settings.DEFAULT_VAT_RATE
        return item_data

    def _recalculate_totals(self, work_order: WorkOrder):
        """Recalculate work order financial totals from items (per-item VAT)."""
        items = self.item_repo.get_by_work_order(work_order.id)

        labor_total = Decimal("0")
        parts_total = Decimal("0")
        discount_total = Decimal("0")
        vat_total = Decimal("0")

        for item in items:
            if item.type == WorkOrderItemType.LABOR:
                labor_total += item.total_price
            else:
                parts_total += item.total_price
            discount_total += item.discount
            # Per-item VAT calculation
            item_vat_rate = Decimal(str(item.vat_rate)) if item.vat_rate is not None else Decimal("20")
            vat_total += item.total_price * item_vat_rate / Decimal("100")

        subtotal = labor_total + parts_total
        grand_total = subtotal + vat_total

        self.repo.update(work_order, {
            "labor_total": labor_total,
            "parts_total": parts_total,
            "discount_total": discount_total,
            "subtotal": subtotal,
            "vat_total": vat_total,
            "grand_total": grand_total,
        })

    def delete(self, work_order_id: int, user_id: int = None) -> bool:
        work_order = self.repo.get_active_by_id(work_order_id)
        if not work_order:
            return False
        self.repo.soft_delete(work_order)
        if user_id:
            self.audit.log(user_id, "WorkOrder", work_order_id, AuditAction.DELETE)
        return True

    # Dashboard queries
    def count_active(self) -> int:
        return self.repo.count_active()

    def get_revenue_today(self) -> float:
        return self.repo.get_revenue_today()

    def get_revenue_month(self) -> float:
        return self.repo.get_revenue_month()

    def get_recent_completed(self, limit: int = 10) -> List[WorkOrder]:
        return self.repo.get_recent_completed(limit)
