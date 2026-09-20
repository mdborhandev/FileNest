"""add reset-token and refresh-token columns

Revision ID: 7c8294d5dcf2
Revises: 7697cdbf4561
Create Date: 2026-09-20 23:16:05.112850
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '7c8294d5dcf2'
down_revision: Union[str, None] = '7697cdbf4561'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- users: enforce case-insensitive uniqueness via lower(email) index ---
    op.drop_constraint('uq_users_email', 'users', type_='unique')
    op.create_index('uq_users_email_lower', 'users', [sa.text('lower(email)')], unique=True)

    # --- password_resets: add expires_at (30-min expiry) + index ---
    op.add_column(
        'password_resets',
        sa.Column(
            'expires_at',
            sa.DateTime(timezone=True),
            server_default=sa.text("now() + interval '30 minutes'"),
            nullable=False,
        ),
    )
    op.create_index(
        op.f('ix_password_resets_expires_at'),
        'password_resets',
        ['expires_at'],
        unique=False,
    )

    # --- refresh_tokens: add replaced_by_id (self-FK) + expires_at index ---
    op.add_column(
        'refresh_tokens',
        sa.Column('replaced_by_id', sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        'fk_refresh_tokens_replaced_by_id_refresh_tokens',
        'refresh_tokens',
        'refresh_tokens',
        ['replaced_by_id'],
        ['id'],
        ondelete='SET NULL',
    )
    op.create_index(
        op.f('ix_refresh_tokens_expires_at'),
        'refresh_tokens',
        ['expires_at'],
        unique=False,
    )


def downgrade() -> None:
    # --- refresh_tokens ---
    op.drop_index(op.f('ix_refresh_tokens_expires_at'), table_name='refresh_tokens')
    op.drop_constraint(
        'fk_refresh_tokens_replaced_by_id_refresh_tokens',
        'refresh_tokens',
        type_='foreignkey',
    )
    op.drop_column('refresh_tokens', 'replaced_by_id')

    # --- password_resets ---
    op.drop_index(op.f('ix_password_resets_expires_at'), table_name='password_resets')
    op.drop_column('password_resets', 'expires_at')

    # --- users: restore the old unique constraint on email ---
    op.drop_index('uq_users_email_lower', table_name='users')
    op.create_unique_constraint('uq_users_email', 'users', ['email'])