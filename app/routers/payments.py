from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse, StreamingResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.enums import PaymentMethod, PaymentStatus
from app.services.payment_service import PaymentService
from app.services.invoice_service import InvoiceService
from app.services.work_order_service import WorkOrderService
from app.utils.pdf_generator import generate_invoice_pdf, generate_proposal_pdf

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/work-order/{wo_id}/pay")
async def add_payment(
    wo_id: int,
    request: Request,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
    amount: float = Form(...),
    payment_method: str = Form(...),
    reference_number: str = Form(None),
):
    pay_service = PaymentService(db)
    data = {
        "work_order_id": wo_id,
        "amount": amount,
        "payment_method": PaymentMethod(payment_method),
        "reference_number": reference_number,
    }
    pay_service.create(data, user_id=user.id)

    # Update invoice payment status if exists
    inv_service = InvoiceService(db)
    wo_service = WorkOrderService(db)
    invoice = inv_service.get_by_work_order(wo_id)
    wo = wo_service.get_by_id(wo_id)
    if invoice and wo:
        total_paid = pay_service.get_total_for_work_order(wo_id)
        if total_paid >= float(wo.grand_total):
            inv_service.update_payment_status(invoice.id, PaymentStatus.PAID, user_id=user.id)
        elif total_paid > 0:
            inv_service.update_payment_status(invoice.id, PaymentStatus.PARTIAL, user_id=user.id)

    return RedirectResponse(f"/work-orders/{wo_id}", status_code=303)


@router.post("/work-order/{wo_id}/invoice")
async def create_invoice(
    wo_id: int,
    request: Request,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    inv_service = InvoiceService(db)
    wo_service = WorkOrderService(db)

    wo = wo_service.get_by_id(wo_id)
    if not wo:
        return RedirectResponse("/work-orders", status_code=303)

    # Check if invoice already exists
    existing = inv_service.get_by_work_order(wo_id)
    if not existing:
        inv_service.create_for_work_order(wo, user_id=user.id)

    return RedirectResponse(f"/work-orders/{wo_id}", status_code=303)


@router.get("/work-order/{wo_id}/invoice/pdf")
async def download_invoice_pdf(
    wo_id: int,
    request: Request,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    wo_service = WorkOrderService(db)
    inv_service = InvoiceService(db)

    wo = wo_service.get_by_id(wo_id)
    invoice = inv_service.get_by_work_order(wo_id)
    if not wo or not invoice:
        return RedirectResponse(f"/work-orders/{wo_id}", status_code=303)

    pdf_buffer = generate_invoice_pdf(wo, invoice)
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename=fatura_{invoice.invoice_number}.pdf"},
    )


@router.get("/work-order/{wo_id}/proposal/pdf")
async def download_proposal_pdf(
    wo_id: int,
    request: Request,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    wo_service = WorkOrderService(db)
    wo = wo_service.get_by_id(wo_id)
    if not wo:
        return RedirectResponse(f"/work-orders/{wo_id}", status_code=303)

    pdf_buffer = generate_proposal_pdf(wo)
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename=teklif_{wo.work_order_number}.pdf"},
    )


@router.post("/{payment_id}/delete")
async def delete_payment(
    payment_id: int,
    request: Request,
    wo_id: int,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    pay_service = PaymentService(db)
    pay_service.delete(payment_id, user_id=user.id)
    return RedirectResponse(f"/work-orders/{wo_id}", status_code=303)
