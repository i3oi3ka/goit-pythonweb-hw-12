"""add roles for user

Revision ID: d518a89babb6
Revises: 31f96756bad4
Create Date: 2025-09-17 19:29:05.743394

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d518a89babb6"
down_revision: Union[str, Sequence[str], None] = "31f96756bad4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    role_enum = sa.Enum("admin", "moderator", "user", name="role_enum")
    role_enum.create(op.get_bind())  # створюємо тип у БД

    op.add_column(
        "users", sa.Column("roles", role_enum, nullable=False, server_default="user")
    )
    op.alter_column("users", "roles", server_default=None)  # прибираємо default із DDL


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("users", "roles")
    sa.Enum("admin", "moderator", "user", name="role_enum").drop(op.get_bind())
