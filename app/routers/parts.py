from fastapi import APIRouter, Request, Depends, Form, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.services.part_service import PartService

router = APIRouter(prefix="/parts", tags=["parts"])


@router.get("/")
async def part_list(
    request: Request,
    q: str = Query(None),
    page: int = Query(1, ge=1),
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = PartService(db)
    per_page = 20
    skip = (page - 1) * per_page

    if q:
        parts = service.search(q)
        total = len(parts)
    else:
        parts = service.get_all(skip=skip, limit=per_page)
        total = service.count()

    total_pages = max(1, (total + per_page - 1) // per_page)
    return request.app.state.templates.TemplateResponse(
        "parts/list.html",
        {
            "request": request,
            "user": user,
            "parts": parts,
            "q": q or "",
            "page": page,
            "total_pages": total_pages,
            "total": total,
        },
    )


@router.get("/create")
async def create_form(request: Request, user=Depends(get_current_user)):
    return request.app.state.templates.TemplateResponse(
        "parts/form.html",
        {"request": request, "user": user, "part": None},
    )


def _safe_int(val: str) -> int | None:
    if val and val.strip():
        try:
            return int(val)
        except ValueError:
            return None
    return None


def _safe_float(val: str) -> float:
    if val and val.strip():
        try:
            return float(val)
        except ValueError:
            return 0
    return 0


@router.post("/create")
async def create_part(
    request: Request,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
    stock_code: str = Form(...),
    name: str = Form(...),
    category: str = Form(""),
    purchase_price: str = Form("0"),
    sale_price: str = Form("0"),
    stock_quantity: str = Form("0"),
    critical_level: str = Form("5"),
    supplier_name: str = Form(""),
):
    service = PartService(db)
    data = {
        "stock_code": stock_code,
        "name": name,
        "category": category or None,
        "purchase_price": _safe_float(purchase_price),
        "sale_price": _safe_float(sale_price),
        "stock_quantity": _safe_int(stock_quantity) or 0,
        "critical_level": _safe_int(critical_level) or 5,
        "supplier_name": supplier_name or None,
    }
    service.create(data, user_id=user.id)
    return RedirectResponse("/parts", status_code=303)


@router.get("/{part_id}/edit")
async def edit_form(
    part_id: int,
    request: Request,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = PartService(db)
    part = service.get_by_id(part_id)
    if not part:
        return RedirectResponse("/parts", status_code=303)
    return request.app.state.templates.TemplateResponse(
        "parts/form.html",
        {"request": request, "user": user, "part": part},
    )


@router.post("/{part_id}/edit")
async def update_part(
    part_id: int,
    request: Request,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
    stock_code: str = Form(...),
    name: str = Form(...),
    category: str = Form(""),
    purchase_price: str = Form("0"),
    sale_price: str = Form("0"),
    stock_quantity: str = Form("0"),
    critical_level: str = Form("5"),
    supplier_name: str = Form(""),
):
    service = PartService(db)
    data = {
        "stock_code": stock_code,
        "name": name,
        "category": category or None,
        "purchase_price": _safe_float(purchase_price),
        "sale_price": _safe_float(sale_price),
        "stock_quantity": _safe_int(stock_quantity) or 0,
        "critical_level": _safe_int(critical_level) or 5,
        "supplier_name": supplier_name or None,
    }
    service.update(part_id, data, user_id=user.id)
    return RedirectResponse("/parts", status_code=303)


@router.post("/{part_id}/delete")
async def delete_part(
    part_id: int,
    request: Request,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = PartService(db)
    service.delete(part_id, user_id=user.id)
    return RedirectResponse("/parts", status_code=303)
