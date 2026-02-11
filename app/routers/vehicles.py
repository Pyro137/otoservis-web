from fastapi import APIRouter, Request, Depends, Form, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.enums import FuelType, TransmissionType
from app.services.vehicle_service import VehicleService
from app.services.customer_service import CustomerService

router = APIRouter(prefix="/vehicles", tags=["vehicles"])


@router.get("/")
async def vehicle_list(
    request: Request,
    q: str = Query(None),
    page: int = Query(1, ge=1),
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = VehicleService(db)
    per_page = 20
    skip = (page - 1) * per_page

    if q:
        vehicles = service.search(q)
        total = len(vehicles)
    else:
        vehicles = service.get_all(skip=skip, limit=per_page)
        total = service.count()

    total_pages = max(1, (total + per_page - 1) // per_page)
    return request.app.state.templates.TemplateResponse(
        "vehicles/list.html",
        {
            "request": request,
            "user": user,
            "vehicles": vehicles,
            "q": q or "",
            "page": page,
            "total_pages": total_pages,
            "total": total,
        },
    )


@router.get("/create")
async def create_form(
    request: Request,
    customer_id: int = Query(None),
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    cust_service = CustomerService(db)
    customers = cust_service.get_all(limit=500)
    return request.app.state.templates.TemplateResponse(
        "vehicles/form.html",
        {
            "request": request,
            "user": user,
            "vehicle": None,
            "customers": customers,
            "selected_customer_id": customer_id,
            "fuel_types": FuelType,
            "transmission_types": TransmissionType,
        },
    )


def _safe_int(val: str) -> int | None:
    """Parse optional int from form — empty strings become None."""
    if val and val.strip():
        try:
            return int(val)
        except ValueError:
            return None
    return None


@router.post("/create")
async def create_vehicle(
    request: Request,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
    customer_id: int = Form(...),
    plate_number: str = Form(...),
    brand: str = Form(...),
    model: str = Form(...),
    year: str = Form(""),
    fuel_type: str = Form(""),
    transmission_type: str = Form(""),
    chassis_number: str = Form(""),
    engine_number: str = Form(""),
    current_km: str = Form(""),
    notes: str = Form(""),
):
    service = VehicleService(db)
    data = {
        "customer_id": customer_id,
        "plate_number": plate_number,
        "brand": brand,
        "model": model,
        "year": _safe_int(year),
        "fuel_type": FuelType(fuel_type) if fuel_type else None,
        "transmission_type": TransmissionType(transmission_type) if transmission_type else None,
        "chassis_number": chassis_number or None,
        "engine_number": engine_number or None,
        "current_km": _safe_int(current_km),
        "notes": notes or None,
    }
    vehicle = service.create(data, user_id=user.id)
    return RedirectResponse(f"/vehicles/{vehicle.id}", status_code=303)


@router.get("/{vehicle_id}")
async def vehicle_detail(
    vehicle_id: int,
    request: Request,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = VehicleService(db)
    vehicle = service.get_by_id(vehicle_id)
    if not vehicle:
        return RedirectResponse("/vehicles", status_code=303)

    from app.services.work_order_service import WorkOrderService
    wo_service = WorkOrderService(db)

    return request.app.state.templates.TemplateResponse(
        "vehicles/detail.html",
        {
            "request": request,
            "user": user,
            "vehicle": vehicle,
            "work_orders": wo_service.get_by_vehicle(vehicle_id),
        },
    )


@router.get("/{vehicle_id}/edit")
async def edit_form(
    vehicle_id: int,
    request: Request,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = VehicleService(db)
    vehicle = service.get_by_id(vehicle_id)
    if not vehicle:
        return RedirectResponse("/vehicles", status_code=303)
    cust_service = CustomerService(db)
    customers = cust_service.get_all(limit=500)
    return request.app.state.templates.TemplateResponse(
        "vehicles/form.html",
        {
            "request": request,
            "user": user,
            "vehicle": vehicle,
            "customers": customers,
            "selected_customer_id": vehicle.customer_id,
            "fuel_types": FuelType,
            "transmission_types": TransmissionType,
        },
    )


@router.post("/{vehicle_id}/edit")
async def update_vehicle(
    vehicle_id: int,
    request: Request,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
    customer_id: int = Form(...),
    plate_number: str = Form(...),
    brand: str = Form(...),
    model: str = Form(...),
    year: str = Form(""),
    fuel_type: str = Form(""),
    transmission_type: str = Form(""),
    chassis_number: str = Form(""),
    engine_number: str = Form(""),
    current_km: str = Form(""),
    notes: str = Form(""),
):
    service = VehicleService(db)
    data = {
        "customer_id": customer_id,
        "plate_number": plate_number,
        "brand": brand,
        "model": model,
        "year": _safe_int(year),
        "fuel_type": FuelType(fuel_type) if fuel_type else None,
        "transmission_type": TransmissionType(transmission_type) if transmission_type else None,
        "chassis_number": chassis_number or None,
        "engine_number": engine_number or None,
        "current_km": _safe_int(current_km),
        "notes": notes or None,
    }
    service.update(vehicle_id, data, user_id=user.id)
    return RedirectResponse(f"/vehicles/{vehicle_id}", status_code=303)


@router.post("/{vehicle_id}/delete")
async def delete_vehicle(
    vehicle_id: int,
    request: Request,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = VehicleService(db)
    service.delete(vehicle_id, user_id=user.id)
    return RedirectResponse("/vehicles", status_code=303)
