from fastapi import APIRouter, Request, Depends, Form, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.enums import CustomerType
from app.services.customer_service import CustomerService

router = APIRouter(prefix="/customers", tags=["customers"])


@router.get("/")
async def customer_list(
    request: Request,
    q: str = Query(None),
    page: int = Query(1, ge=1),
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = CustomerService(db)
    per_page = 20
    skip = (page - 1) * per_page

    if q:
        customers = service.search(q)
        total = len(customers)
    else:
        customers = service.get_all(skip=skip, limit=per_page)
        total = service.count()

    total_pages = max(1, (total + per_page - 1) // per_page)
    return request.app.state.templates.TemplateResponse(
        "customers/list.html",
        {
            "request": request,
            "user": user,
            "customers": customers,
            "q": q or "",
            "page": page,
            "total_pages": total_pages,
            "total": total,
            "customer_types": CustomerType,
        },
    )


@router.get("/create")
async def create_form(request: Request, user=Depends(get_current_user)):
    return request.app.state.templates.TemplateResponse(
        "customers/form.html",
        {"request": request, "user": user, "customer": None, "customer_types": CustomerType},
    )


@router.post("/create")
async def create_customer(
    request: Request,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
    full_name: str = Form(...),
    phone: str = Form(...),
    type: str = Form("individual"),
    company_name: str = Form(""),
    tax_number: str = Form(""),
    tax_office: str = Form(""),
    email: str = Form(""),
    address: str = Form(""),
    city: str = Form(""),
    notes: str = Form(""),
):
    service = CustomerService(db)
    data = {
        "full_name": full_name,
        "phone": phone,
        "type": CustomerType(type),
        "company_name": company_name or None,
        "tax_number": tax_number or None,
        "tax_office": tax_office or None,
        "email": email or None,
        "address": address or None,
        "city": city or None,
        "notes": notes or None,
    }
    service.create(data, user_id=user.id)
    return RedirectResponse("/customers", status_code=303)


@router.get("/{customer_id}")
async def customer_detail(
    customer_id: int,
    request: Request,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = CustomerService(db)
    customer = service.get_by_id(customer_id)
    if not customer:
        return RedirectResponse("/customers", status_code=303)

    from app.services.vehicle_service import VehicleService
    from app.services.work_order_service import WorkOrderService
    v_service = VehicleService(db)
    wo_service = WorkOrderService(db)

    return request.app.state.templates.TemplateResponse(
        "customers/detail.html",
        {
            "request": request,
            "user": user,
            "customer": customer,
            "vehicles": v_service.get_by_customer(customer_id),
            "work_orders": wo_service.get_by_customer(customer_id),
        },
    )


@router.get("/{customer_id}/edit")
async def edit_form(
    customer_id: int,
    request: Request,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = CustomerService(db)
    customer = service.get_by_id(customer_id)
    if not customer:
        return RedirectResponse("/customers", status_code=303)
    return request.app.state.templates.TemplateResponse(
        "customers/form.html",
        {"request": request, "user": user, "customer": customer, "customer_types": CustomerType},
    )


@router.post("/{customer_id}/edit")
async def update_customer(
    customer_id: int,
    request: Request,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
    full_name: str = Form(...),
    phone: str = Form(...),
    type: str = Form("individual"),
    company_name: str = Form(""),
    tax_number: str = Form(""),
    tax_office: str = Form(""),
    email: str = Form(""),
    address: str = Form(""),
    city: str = Form(""),
    notes: str = Form(""),
):
    service = CustomerService(db)
    data = {
        "full_name": full_name,
        "phone": phone,
        "type": CustomerType(type),
        "company_name": company_name or None,
        "tax_number": tax_number or None,
        "tax_office": tax_office or None,
        "email": email or None,
        "address": address or None,
        "city": city or None,
        "notes": notes or None,
    }
    service.update(customer_id, data, user_id=user.id)
    return RedirectResponse(f"/customers/{customer_id}", status_code=303)


@router.post("/{customer_id}/delete")
async def delete_customer(
    customer_id: int,
    request: Request,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = CustomerService(db)
    service.delete(customer_id, user_id=user.id)
    return RedirectResponse("/customers", status_code=303)
