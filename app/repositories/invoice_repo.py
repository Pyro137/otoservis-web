from typing import Optional
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.invoice import Invoice
from app.repositories.base import BaseRepository


class InvoiceRepository(BaseRepository[Invoice]):
    def __init__(self, db: Session):
        super().__init__(Invoice, db)

    def get_by_work_order(self, work_order_id: int) -> Optional[Invoice]:
        return (
            self.db.query(Invoice)
            .filter(Invoice.work_order_id == work_order_id)
            .first()
        )

    def get_next_invoice_number(self) -> str:
        now = datetime.now()
        prefix = f"FTR-{now.strftime('%Y%m')}"
        last_invoice = (
            self.db.query(Invoice)
            .filter(Invoice.invoice_number.like(f"{prefix}%"))
            .order_by(Invoice.id.desc())
            .first()
        )
        if last_invoice:
            last_num = int(last_invoice.invoice_number.split("-")[-1])
            next_num = last_num + 1
        else:
            next_num = 1
        return f"{prefix}-{next_num:04d}"
