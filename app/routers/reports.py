from fastapi import APIRouter, Request, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import datetime, date, timedelta

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.work_order import WorkOrder
from app.models.work_order_item import WorkOrderItem
from app.models.customer import Customer
from app.models.vehicle import Vehicle
from app.models.payment import Payment
from app.core.enums import WorkOrderStatus, WorkOrderItemType

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/")
async def reports_page(
    request: Request,
    report_type: str = Query("revenue"),
    start_date: str = Query(None),
    end_date: str = Query(None),
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    today = date.today()
    start = datetime.strptime(start_date, "%Y-%m-%d").date() if start_date else today.replace(day=1)
    end = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else today

    report_data = {}

    if report_type == "revenue":
        # Revenue by date range
        orders = (
            db.query(WorkOrder)
            .filter(
                WorkOrder.status.in_([WorkOrderStatus.COMPLETED, WorkOrderStatus.DELIVERED]),
                WorkOrder.is_deleted == False,  # noqa: E712
                func.date(WorkOrder.completed_at) >= start,
                func.date(WorkOrder.completed_at) <= end,
            )
            .order_by(WorkOrder.completed_at.desc())
            .all()
        )
        total_revenue = sum(float(o.grand_total) for o in orders)
        report_data = {"orders": orders, "total_revenue": total_revenue}

    elif report_type == "technician":
        # Technician performance
        from app.models.user import User
        techs = db.query(User).filter(User.is_active == True).all()  # noqa: E712
        tech_stats = []
        for tech in techs:
            count = (
                db.query(WorkOrder)
                .filter(
                    WorkOrder.technician_id == tech.id,
                    WorkOrder.status.in_([WorkOrderStatus.COMPLETED, WorkOrderStatus.DELIVERED]),
                    WorkOrder.is_deleted == False,  # noqa: E712
                    func.date(WorkOrder.completed_at) >= start,
                    func.date(WorkOrder.completed_at) <= end,
                )
                .count()
            )
            revenue = (
                db.query(func.coalesce(func.sum(WorkOrder.grand_total), 0))
                .filter(
                    WorkOrder.technician_id == tech.id,
                    WorkOrder.status.in_([WorkOrderStatus.COMPLETED, WorkOrderStatus.DELIVERED]),
                    WorkOrder.is_deleted == False,  # noqa: E712
                    func.date(WorkOrder.completed_at) >= start,
                    func.date(WorkOrder.completed_at) <= end,
                )
                .scalar()
            )
            tech_stats.append({"tech": tech, "count": count, "revenue": float(revenue)})
        report_data = {"tech_stats": tech_stats}

    elif report_type == "vehicles":
        # Most serviced vehicles
        vehicle_stats = (
            db.query(
                Vehicle,
                func.count(WorkOrder.id).label("order_count"),
            )
            .join(WorkOrder, WorkOrder.vehicle_id == Vehicle.id)
            .filter(WorkOrder.is_deleted == False, Vehicle.is_deleted == False)  # noqa: E712
            .group_by(Vehicle.id)
            .order_by(func.count(WorkOrder.id).desc())
            .limit(20)
            .all()
        )
        report_data = {"vehicle_stats": vehicle_stats}

    elif report_type == "parts":
        # Most used parts
        from app.models.part import Part
        part_stats = (
            db.query(
                Part.name,
                Part.stock_code,
                func.sum(WorkOrderItem.quantity).label("total_used"),
            )
            .join(WorkOrderItem, WorkOrderItem.part_id == Part.id)
            .group_by(Part.id)
            .order_by(func.sum(WorkOrderItem.quantity).desc())
            .limit(20)
            .all()
        )
        report_data = {"part_stats": part_stats}

    elif report_type == "debt":
        # Customer debt summary
        customers_with_debt = (
            db.query(Customer)
            .filter(Customer.is_deleted == False, Customer.total_debt > 0)  # noqa: E712
            .order_by(Customer.total_debt.desc())
            .all()
        )
        report_data = {"customers_with_debt": customers_with_debt}

    return request.app.state.templates.TemplateResponse(
        "reports/index.html",
        {
            "request": request,
            "user": user,
            "report_type": report_type,
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            **report_data,
        },
    )
