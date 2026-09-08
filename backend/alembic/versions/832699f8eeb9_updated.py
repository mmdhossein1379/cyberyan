"""updated

Revision ID: 832699f8eeb9
Revises: 0001
Create Date: 2026-09-07 09:06:51.878294
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = '832699f8eeb9'
down_revision: Union[str, None] = '0001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
