from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column


class Base(DeclarativeBase):
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False
    )


class BaseDocument(Base):
    __abstract__ = True
    name: Mapped[str] = mapped_column(nullable=False)
    url: Mapped[str] = mapped_column(nullable=False)

    @declared_attr
    def owner_id(self) -> Mapped[UUID]:
        return mapped_column(ForeignKey("users.id"), nullable=True)


class ProjectUser(Base):
    __tablename__ = "m2m_projects_users"
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), primary_key=True)
    project_id: Mapped[UUID] = mapped_column(
        ForeignKey("projects.id"), primary_key=True
    )
