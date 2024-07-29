from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Role(Base):
    __tablename__ = "role_table"
    __table_args__ = {"schema": "auth_service"}

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(50))

    user: Mapped[list["User"]] = relationship(back_populates="role")

    def __repr__(self):
        return f"<Role {self.name}>"
