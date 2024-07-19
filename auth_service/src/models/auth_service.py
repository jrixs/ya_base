from enum import Enum

from sqlalchemy import String, Integer
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


class TokenType(str, Enum):
    access = "access_token"
    refresh = "refresh_token"


class TokenSettings(Base):
    __tablename__ = "token_settings"
    __table_args__ = {"schema": "auth_service"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    token: Mapped[TokenType]
    time_alive: Mapped[int] = mapped_column(Integer)

    def __repr__(self):
        return f"TokenSettings {self.token}: {self.time_alive}"
