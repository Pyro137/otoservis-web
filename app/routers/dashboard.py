from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.services.work_order_service import WorkOrderService
from app.services.customer_service import CustomerService
from app.services.part_service import PartService
from app.services.payment_service import PaymentService

router = APIRouter(tags=["dashboard"])


@router.get("/")
async def dashboard(
    request: Request,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    wo_service = WorkOrderService(db)
    cust_service = CustomerService(db)
    part_service = PartService(db)

    context = {
        "request": request,
        "user": user,
        "active_orders": wo_service.count_active(),
        "revenue_today": wo_service.get_revenue_today(),
        "revenue_month": wo_service.get_revenue_month(),
        "total_customers": cust_service.count(),
        "low_stock_parts": part_service.get_low_stock(),
        "recent_completed": wo_service.get_recent_completed(5),
        "active_work_orders": wo_service.get_active_orders()[:5],
    }
    return request.app.state.templates.TemplateResponse("dashboard/index.html", context)
