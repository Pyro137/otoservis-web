from fastapi import APIRouter, Request, Depends, Form, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.enums import WorkOrderStatus, WorkOrderItemType
from app.services.work_order_service import WorkOrderService
from app.services.customer_service import CustomerService
from app.services.vehicle_service import VehicleService
from app.services.part_service import PartService
from app.services.auth_service import AuthService
from app.services.payment_service import PaymentService
from app.services.invoice_service import InvoiceService

router = APIRouter(prefix="/work-orders", tags=["work_orders"])


@router.get("/")
async def work_order_list(
    request: Request,
    status: str = Query(None),
    page: int = Query(1, ge=1),
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = WorkOrderService(db)
    per_page = 20
    skip = (page - 1) * per_page

    if status:
        work_orders = service.get_by_status(WorkOrderStatus(status))
        total = len(work_orders)
    else:
        work_orders = service.get_all(skip=skip, limit=per_page)
        total = service.count()

    total_pages = max(1, (total + per_page - 1) // per_page)
    return request.app.state.templates.TemplateResponse(
        "work_orders/list.html",
        {
            "request": request,
            "user": user,
            "work_orders": work_orders,
            "statuses": WorkOrderStatus,
            "current_status": status,
            "page": page,
            "total_pages": total_pages,
            "total": total,
        },
    )


@router.get("/create")
async def create_form(
    request: Request,
    vehicle_id: int = Query(None),
    customer_id: int = Query(None),
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    cust_service = CustomerService(db)
    v_service = VehicleService(db)
    auth_service = AuthService(db)

    customers = cust_service.get_all(limit=500)
    vehicles = v_service.get_all(limit=500)
    technicians = auth_service.get_technicians()

    return request.app.state.templates.TemplateResponse(
        "work_orders/form.html",
        {
            "request": request,
            "user": user,
            "work_order": None,
            "customers": customers,
            "vehicles": vehicles,
            "technicians": technicians,
            "selected_vehicle_id": vehicle_id,
            "selected_customer_id": customer_id,
            "statuses": WorkOrderStatus,
        },
    )


def _safe_int(val: str) -> int | None:
    if val and val.strip():
        try:
            return int(val)
        except ValueError:
            return None
    return None


@router.post("/create")
async def create_work_order(
    request: Request,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
    vehicle_id: int = Form(...),
    customer_id: int = Form(...),
    technician_id: str = Form(""),
    complaint_description: str = Form(""),
    internal_notes: str = Form(""),
    km_in: str = Form(""),
    fuel_level: str = Form(""),
):
    service = WorkOrderService(db)
    data = {
        "vehicle_id": vehicle_id,
        "customer_id": customer_id,
        "technician_id": _safe_int(technician_id),
        "complaint_description": complaint_description or None,
        "internal_notes": internal_notes or None,
        "km_in": _safe_int(km_in),
        "fuel_level": fuel_level or None,
    }
    wo = service.create(data, user_id=user.id)
    return RedirectResponse(f"/work-orders/{wo.id}", status_code=303)


@router.get("/{wo_id}")
async def work_order_detail(
    wo_id: int,
    request: Request,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = WorkOrderService(db)
    wo = service.get_by_id(wo_id)
    if not wo:
        return RedirectResponse("/work-orders", status_code=303)

    pay_service = PaymentService(db)
    inv_service = InvoiceService(db)
    part_service = PartService(db)

    from app.services.work_order_service import VALID_TRANSITIONS
    allowed_transitions = VALID_TRANSITIONS.get(wo.status, [])
    payments = pay_service.get_by_work_order(wo_id)
    total_paid = pay_service.get_total_for_work_order(wo_id)
    invoice = inv_service.get_by_work_order(wo_id)
    parts = part_service.get_all(limit=500)

    return request.app.state.templates.TemplateResponse(
        "work_orders/detail.html",
        {
            "request": request,
            "user": user,
            "wo": wo,
            "allowed_transitions": allowed_transitions,
            "payments": payments,
            "total_paid": total_paid,
            "remaining": float(wo.grand_total) - total_paid,
            "invoice": invoice,
            "parts": parts,
            "item_types": WorkOrderItemType,
            "statuses": WorkOrderStatus,
        },
    )


@router.get("/{wo_id}/edit")
async def edit_form(
    wo_id: int,
    request: Request,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = WorkOrderService(db)
    wo = service.get_by_id(wo_id)
    if not wo:
        return RedirectResponse("/work-orders", status_code=303)

    cust_service = CustomerService(db)
    v_service = VehicleService(db)
    auth_service = AuthService(db)

    return request.app.state.templates.TemplateResponse(
        "work_orders/form.html",
        {
            "request": request,
            "user": user,
            "work_order": wo,
            "customers": cust_service.get_all(limit=500),
            "vehicles": v_service.get_all(limit=500),
            "technicians": auth_service.get_technicians(),
            "selected_vehicle_id": wo.vehicle_id,
            "selected_customer_id": wo.customer_id,
            "statuses": WorkOrderStatus,
        },
    )


@router.post("/{wo_id}/edit")
async def update_work_order(
    wo_id: int,
    request: Request,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
    vehicle_id: int = Form(...),
    customer_id: int = Form(...),
    technician_id: str = Form(""),
    complaint_description: str = Form(""),
    internal_notes: str = Form(""),
    km_in: str = Form(""),
    km_out: str = Form(""),
    fuel_level: str = Form(""),
):
    service = WorkOrderService(db)
    data = {
        "vehicle_id": vehicle_id,
        "customer_id": customer_id,
        "technician_id": _safe_int(technician_id),
        "complaint_description": complaint_description or None,
        "internal_notes": internal_notes or None,
        "km_in": _safe_int(km_in),
        "km_out": _safe_int(km_out),
        "fuel_level": fuel_level or None,
    }
    service.update(wo_id, data, user_id=user.id)
    return RedirectResponse(f"/work-orders/{wo_id}", status_code=303)


@router.post("/{wo_id}/status")
async def change_status(
    wo_id: int,
    request: Request,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
    new_status: str = Form(...),
):
    service = WorkOrderService(db)
    try:
        service.change_status(wo_id, WorkOrderStatus(new_status), user_id=user.id)
    except ValueError:
        pass
    return RedirectResponse(f"/work-orders/{wo_id}", status_code=303)


@router.post("/{wo_id}/add-item")
async def add_item(
    wo_id: int,
    request: Request,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
    type: str = Form(...),
    description: str = Form(...),
    quantity: str = Form("1"),
    unit_price: str = Form("0"),
    discount: str = Form("0"),
    part_id: str = Form(""),
):
    service = WorkOrderService(db)
    # Safe parsing — prevent empty string → int errors
    try:
        qty = float(quantity) if quantity else 1
    except ValueError:
        qty = 1
    try:
        price = float(unit_price) if unit_price else 0
    except ValueError:
        price = 0
    try:
        disc = float(discount) if discount else 0
    except ValueError:
        disc = 0

    parsed_part_id = None
    if part_id and part_id.strip():
        try:
            parsed_part_id = int(part_id)
        except ValueError:
            parsed_part_id = None

    item_data = {
        "type": WorkOrderItemType(type),
        "description": description,
        "quantity": qty,
        "unit_price": price,
        "discount": disc,
        "part_id": parsed_part_id,
    }
    service.add_item(wo_id, item_data, user_id=user.id)
    return RedirectResponse(f"/work-orders/{wo_id}", status_code=303)


@router.post("/{wo_id}/remove-item/{item_id}")
async def remove_item(
    wo_id: int,
    item_id: int,
    request: Request,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = WorkOrderService(db)
    service.remove_item(item_id, user_id=user.id)
    return RedirectResponse(f"/work-orders/{wo_id}", status_code=303)


@router.post("/{wo_id}/delete")
async def delete_work_order(
    wo_id: int,
    request: Request,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = WorkOrderService(db)
    service.delete(wo_id, user_id=user.id)
    return RedirectResponse("/work-orders", status_code=303)
