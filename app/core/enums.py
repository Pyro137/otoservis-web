import enum


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    TECHNICIAN = "technician"


class CustomerType(str, enum.Enum):
    INDIVIDUAL = "individual"
    CORPORATE = "corporate"


class FuelType(str, enum.Enum):
    GASOLINE = "benzin"
    DIESEL = "dizel"
    LPG = "lpg"
    HYBRID = "hibrit"
    ELECTRIC = "elektrik"


class TransmissionType(str, enum.Enum):
    MANUAL = "manuel"
    AUTOMATIC = "otomatik"


class WorkOrderStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class WorkOrderItemType(str, enum.Enum):
    PART = "part"
    LABOR = "labor"


class PaymentMethod(str, enum.Enum):
    CASH = "cash"
    CARD = "card"
    TRANSFER = "transfer"


class PaymentStatus(str, enum.Enum):
    UNPAID = "unpaid"
    PARTIAL = "partial"
    PAID = "paid"


class AuditAction(str, enum.Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


class PhotoCategory(str, enum.Enum):
    BEFORE = "before"
    AFTER = "after"
    DAMAGE = "damage"
    OTHER = "other"
