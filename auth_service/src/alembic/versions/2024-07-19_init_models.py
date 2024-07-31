"""init models

Revision ID: 1e6216a7ff74
Revises: e74e9fafffaa
Create Date: 2024-07-19 16:59:29.096645

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '1e6216a7ff74'
down_revision: Union[str, None] = 'e74e9fafffaa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('role_table',
                    sa.Column('id', sa.String(length=36), nullable=False),
                    sa.Column('name', sa.String(length=50), nullable=False),
                    sa.PrimaryKeyConstraint('id'),
                    schema='auth_service'
                    )
    op.create_table('user_table',
                    sa.Column('id', sa.String(length=36), nullable=False),
                    sa.Column('username', sa.String(length=50), nullable=False),
                    sa.Column('email', sa.String(length=320), nullable=False),
                    sa.Column('role_id', sa.String(length=36), nullable=True),
                    sa.Column('is_superuser', sa.Boolean(), server_default='False', nullable=False),
                    sa.Column('joined_at', sa.DateTime(), nullable=False),
                    sa.Column('updated_at', sa.DateTime(), nullable=True),
                    sa.ForeignKeyConstraint(['role_id'], ['auth_service.role_table.id'], ondelete='SET NULL'),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('email'),
                    sa.UniqueConstraint('username'),
                    schema='auth_data'
                    )
    op.create_table('user_history',
                    sa.Column('id', sa.String(length=36), nullable=False),
                    sa.Column('user_id', sa.String(length=36), nullable=False),
                    sa.Column('last_logged_at', sa.DateTime(), nullable=False),
                    sa.Column('user_agent', sa.String(), nullable=False),
                    sa.ForeignKeyConstraint(['user_id'], ['auth_data.user_table.id'], ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('id'),
                    schema='auth_data'
                    )
    op.create_table('user_secrets',
                    sa.Column('id', sa.String(length=36), nullable=False),
                    sa.Column('user_id', sa.String(length=36), nullable=False),
                    sa.Column('password', sa.String(), nullable=False),
                    sa.Column('updated_at', sa.DateTime(), nullable=True),
                    sa.ForeignKeyConstraint(['user_id'], ['auth_data.user_table.id'], ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('id'),
                    schema='auth_secret'
                    )


def downgrade() -> None:
    op.drop_table('user_secrets', schema='auth_secret')
    op.drop_table('user_history', schema='auth_data')
    op.drop_table('user_table', schema='auth_data')
    op.drop_table('role_table', schema='auth_service')
