from typing import List
from sqlalchemy.orm import Session

from app.models.work_order_item import WorkOrderItem
from app.repositories.base import BaseRepository


class WorkOrderItemRepository(BaseRepository[WorkOrderItem]):
    def __init__(self, db: Session):
        super().__init__(WorkOrderItem, db)

    def get_by_work_order(self, work_order_id: int) -> List[WorkOrderItem]:
        return (
            self.db.query(WorkOrderItem)
            .filter(WorkOrderItem.work_order_id == work_order_id)
            .order_by(WorkOrderItem.id)
            .all()
        )

    def delete_by_work_order(self, work_order_id: int) -> None:
        self.db.query(WorkOrderItem).filter(
            WorkOrderItem.work_order_id == work_order_id
        ).delete()
        self.db.commit()
