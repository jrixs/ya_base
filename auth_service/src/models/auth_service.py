from datetime import datetime

from sqlalchemy import String, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Role(Base):
    __tablename__ = "role_table"
    __table_args__ = {"schema": "auth_service"}

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    create_access: Mapped[bool] = mapped_column(Boolean, server_default="False")
    update_access: Mapped[bool] = mapped_column(Boolean, server_default="False")
    view_access: Mapped[bool] = mapped_column(Boolean, server_default="False")
    delete_access: Mapped[bool] = mapped_column(Boolean, server_default="False")

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, onupdate=datetime.utcnow)

    user: Mapped[list["User"]] = relationship(back_populates="role")

    def __repr__(self):
        return f"<Role {self.name}>"
