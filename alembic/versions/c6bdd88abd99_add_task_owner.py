"""add task owner

Revision ID: c6bdd88abd99
Revises: 36caa5653f26
Create Date: 2026-10-08 21:31:09.556547

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c6bdd88abd99'
down_revision: Union[str, Sequence[str], None] = '36caa5653f26'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        "tasks",
        sa.Column("owner_id", sa.Integer(), nullable=False),
    )

    op.create_foreign_key(
        "fk_tasks_owner_id_users",
        "tasks",
        "users",
        ["owner_id"],
        ["id"],
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_constraint(
        "fk_tasks_owner_id_users",
        "tasks",
        type_="foreignkey",
    )

    op.drop_column(
        "tasks",
        "owner_id",
    )
