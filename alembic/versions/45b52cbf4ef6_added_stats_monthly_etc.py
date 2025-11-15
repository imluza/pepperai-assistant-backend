"""added stats monthly etc

Revision ID: 45b52cbf4ef6
Revises: ecfedd08d14e
Create Date: 2025-11-10 22:18:35.670067

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '45b52cbf4ef6'
down_revision: Union[str, None] = 'ecfedd08d14e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Добавляем колонки с дефолтом и значением по умолчанию
    op.add_column('user_stats', sa.Column('hourly_requests', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('user_stats', sa.Column('daily_requests', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('user_stats', sa.Column('weekly_requests', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('user_stats', sa.Column('monthly_requests', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('user_stats', sa.Column('hourly_tokens', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('user_stats', sa.Column('daily_tokens', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('user_stats', sa.Column('weekly_tokens', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('user_stats', sa.Column('monthly_tokens', sa.Integer(), nullable=False, server_default='0'))


def downgrade() -> None:
    op.drop_column('user_stats', 'monthly_tokens')
    op.drop_column('user_stats', 'weekly_tokens')
    op.drop_column('user_stats', 'daily_tokens')
    op.drop_column('user_stats', 'hourly_tokens')
    op.drop_column('user_stats', 'monthly_requests')
    op.drop_column('user_stats', 'weekly_requests')
    op.drop_column('user_stats', 'daily_requests')
    op.drop_column('user_stats', 'hourly_requests')
