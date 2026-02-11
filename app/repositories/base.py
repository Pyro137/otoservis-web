from typing import TypeVar, Generic, Type, Optional, List
from sqlalchemy.orm import Session
from app.core.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Generic repository with CRUD, soft-delete, pagination, and filtering."""

    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db

    def get_by_id(self, id: int) -> Optional[ModelType]:
        return self.db.query(self.model).filter(self.model.id == id).first()

    def get_active_by_id(self, id: int) -> Optional[ModelType]:
        """Get by ID, respecting soft delete if the model supports it."""
        query = self.db.query(self.model).filter(self.model.id == id)
        if hasattr(self.model, "is_deleted"):
            query = query.filter(self.model.is_deleted == False)  # noqa: E712
        return query.first()

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
    ) -> List[ModelType]:
        query = self.db.query(self.model)
        if not include_deleted and hasattr(self.model, "is_deleted"):
            query = query.filter(self.model.is_deleted == False)  # noqa: E712
        return query.order_by(self.model.id.desc()).offset(skip).limit(limit).all()

    def count(self, include_deleted: bool = False) -> int:
        query = self.db.query(self.model)
        if not include_deleted and hasattr(self.model, "is_deleted"):
            query = query.filter(self.model.is_deleted == False)  # noqa: E712
        return query.count()

    def create(self, obj_data: dict) -> ModelType:
        db_obj = self.model(**obj_data)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def update(self, db_obj: ModelType, obj_data: dict) -> ModelType:
        for key, value in obj_data.items():
            if hasattr(db_obj, key):
                setattr(db_obj, key, value)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def soft_delete(self, db_obj: ModelType) -> ModelType:
        if hasattr(db_obj, "is_deleted"):
            db_obj.is_deleted = True
            self.db.commit()
            self.db.refresh(db_obj)
        return db_obj

    def hard_delete(self, db_obj: ModelType) -> None:
        self.db.delete(db_obj)
        self.db.commit()
