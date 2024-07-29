from datetime import datetime
from sqlalchemy import ForeignKey, String, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

from models.auth_secret import Secret
from models.auth_service import Role


class User(Base):
    __tablename__ = "user_table"
    __table_args__ = {"schema": "auth_data"}

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    username: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(320), unique=True)
    role_id: Mapped[str] = mapped_column(String(36), ForeignKey("auth_service.role_table.id", ondelete="SET NULL"),
                                         nullable=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, server_default="False")
    joined_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, onupdate=datetime.utcnow, nullable=True)

    secret: Mapped["Secret"] = relationship(back_populates="user")
    role: Mapped["Role"] = relationship(back_populates="user")
    history: Mapped[list["History"]] = relationship(back_populates="user", uselist=True)

    def __repr__(self):
        return f"<User {self.email}>"


class History(Base):
    __tablename__ = "user_history"
    __table_args__ = {"schema": "auth_data"}

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("auth_data.user_table.id", ondelete="CASCADE"))
    last_logged_at: Mapped[datetime] = mapped_column(DateTime)
    user_agent: Mapped[str] = mapped_column(String)

    user: Mapped["User"] = relationship(back_populates="history")

    def __repr__(self):
        return f"<History {self.user_id}>"
