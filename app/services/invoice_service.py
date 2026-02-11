from typing import Optional
from datetime import date
from sqlalchemy.orm import Session

from app.models.invoice import Invoice
from app.repositories.invoice_repo import InvoiceRepository
from app.repositories.audit_log_repo import AuditLogRepository
from app.core.enums import AuditAction, PaymentStatus


class InvoiceService:
    def __init__(self, db: Session):
        self.repo = InvoiceRepository(db)
        self.audit = AuditLogRepository(db)

    def get_all(self, skip: int = 0, limit: int = 100):
        return self.repo.get_all(skip=skip, limit=limit)

    def get_by_id(self, invoice_id: int) -> Optional[Invoice]:
        return self.repo.get_by_id(invoice_id)

    def get_by_work_order(self, work_order_id: int) -> Optional[Invoice]:
        return self.repo.get_by_work_order(work_order_id)

    def create_for_work_order(self, work_order, user_id: int = None) -> Invoice:
        """Create an invoice from a work order."""
        invoice_number = self.repo.get_next_invoice_number()
        data = {
            "invoice_number": invoice_number,
            "work_order_id": work_order.id,
            "issue_date": date.today(),
            "due_date": date.today(),
            "payment_status": PaymentStatus.UNPAID,
            "subtotal": work_order.subtotal,
            "vat_total": work_order.vat_total,
            "grand_total": work_order.grand_total,
        }
        invoice = self.repo.create(data)
        if user_id:
            self.audit.log(user_id, "Invoice", invoice.id, AuditAction.CREATE, {"invoice_number": invoice_number})
        return invoice

    def update_payment_status(self, invoice_id: int, status: PaymentStatus, user_id: int = None) -> Optional[Invoice]:
        invoice = self.repo.get_by_id(invoice_id)
        if not invoice:
            return None
        old_status = invoice.payment_status
        invoice = self.repo.update(invoice, {"payment_status": status})
        if user_id:
            self.audit.log(
                user_id, "Invoice", invoice.id, AuditAction.UPDATE,
                {"payment_status": {"old": old_status.value, "new": status.value}},
            )
        return invoice
