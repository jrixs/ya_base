"""add roles settings

Revision ID: d4a9b602325a
Revises: 1e6216a7ff74
Create Date: 2024-07-24 19:53:18.469350

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'd4a9b602325a'
down_revision: Union[str, None] = '1e6216a7ff74'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('auth_service.role_table',
                  sa.Column('create_access', sa.Boolean(), server_default='False', nullable=True))
    op.add_column('auth_service.role_table',
                  sa.Column('update_access', sa.Boolean(), server_default='False', nullable=True))
    op.add_column('auth_service.role_table',
                  sa.Column('view_access', sa.Boolean(), server_default='False', nullable=True))
    op.add_column('auth_service.role_table',
                  sa.Column('delete_access', sa.Boolean(), server_default='False', nullable=True))
    op.add_column('auth_service.role_table',
                  sa.Column('updated_at', sa.DateTime(), nullable=False))
    op.add_column('auth_service.role_table',
                  sa.Column('created_at', sa.DateTime(), nullable=False))


def downgrade() -> None:
    op.drop_column('auth_service.role_table', 'create_access')
    op.drop_column('auth_service.role_table', 'update_access')
    op.drop_column('auth_service.role_table', 'view_access')
    op.drop_column('auth_service.role_table', 'delete_access')
    op.drop_column('auth_service.role_table', 'updated_at')
    op.drop_column('auth_service.role_table', 'created_at')
