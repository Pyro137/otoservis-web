from typing import List
from sqlalchemy.orm import Session

from app.models.work_order_photo import WorkOrderPhoto
from app.repositories.base import BaseRepository


class WorkOrderPhotoRepository(BaseRepository[WorkOrderPhoto]):
    def __init__(self, db: Session):
        super().__init__(WorkOrderPhoto, db)

    def get_by_work_order(self, work_order_id: int) -> List[WorkOrderPhoto]:
        return (
            self.db.query(WorkOrderPhoto)
            .filter(WorkOrderPhoto.work_order_id == work_order_id)
            .order_by(WorkOrderPhoto.id.desc())
            .all()
        )

    def count_for_work_order(self, work_order_id: int) -> int:
        return (
            self.db.query(WorkOrderPhoto)
            .filter(WorkOrderPhoto.work_order_id == work_order_id)
            .count()
        )
