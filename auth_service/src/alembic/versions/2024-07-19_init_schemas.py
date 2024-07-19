"""init schemas

Revision ID: e74e9fafffaa
Revises: 
Create Date: 2024-07-19 16:46:24.306194

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e74e9fafffaa'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("create schema auth_service")
    op.execute("create schema auth_data")
    op.execute("create schema auth_secret")


def downgrade() -> None:
    op.execute("drop schema auth_service")
    op.execute("drop schema auth_data")
    op.execute("drop schema auth_secret")
