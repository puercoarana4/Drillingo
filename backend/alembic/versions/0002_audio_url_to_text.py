"""Change audio_url from VARCHAR(2048) to TEXT

Revision ID: 0002
Revises: 0001
Create Date: 2024-01-02 00:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '0002'
down_revision: Union[str, None] = '0001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        'lessons',
        'audio_url',
        existing_type=sa.String(2048),
        type_=sa.Text(),
        existing_nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        'lessons',
        'audio_url',
        existing_type=sa.Text(),
        type_=sa.String(2048),
        existing_nullable=False,
    )
