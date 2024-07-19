from datetime import datetime
from sqlalchemy import ForeignKey, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Secret(Base):
    __tablename__ = "user_secrets"
    __table_args__ = {"schema": "auth_secret"}

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("auth_data.user_table.id", ondelete="CASCADE"))
    password: Mapped[str] = mapped_column(String)
    updated_at: Mapped[datetime] = mapped_column(DateTime, onupdate=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="secret")

    def __repr__(self):
        return f"<Secret {self.user_id}>"
