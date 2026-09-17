"""initial schema: users, artists, albums

Revision ID: 0001
Revises:
Create Date: 2026-09-17

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _timestamps() -> list[sa.Column[sa.DateTime]]:
    return [
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    ]


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("username", sa.String(30), nullable=False),
        sa.Column("display_name", sa.String(80), nullable=True),
        sa.Column("bio", sa.Text(), nullable=True),
        sa.Column("avatar_url", sa.String(500), nullable=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        *_timestamps(),
        sa.PrimaryKeyConstraint("id", name="pk_users"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_username", "users", ["username"], unique=True)

    op.create_table(
        "artists",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("apple_id", sa.BigInteger(), nullable=True),
        *_timestamps(),
        sa.PrimaryKeyConstraint("id", name="pk_artists"),
        sa.UniqueConstraint("apple_id", name="uq_artists_apple_id"),
    )
    op.create_index("ix_artists_name", "artists", ["name"])
    op.create_index(
        "ix_artists_name_trgm",
        "artists",
        ["name"],
        postgresql_using="gin",
        postgresql_ops={"name": "gin_trgm_ops"},
    )

    op.create_table(
        "albums",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("artist_id", sa.Uuid(), nullable=False),
        sa.Column("apple_id", sa.BigInteger(), nullable=True),
        sa.Column("upc", sa.String(32), nullable=True),
        sa.Column("release_date", sa.Date(), nullable=True),
        sa.Column("artwork_url", sa.String(500), nullable=True),
        sa.Column("genre", sa.String(100), nullable=True),
        sa.Column("track_count", sa.Integer(), nullable=True),
        *_timestamps(),
        sa.PrimaryKeyConstraint("id", name="pk_albums"),
        sa.ForeignKeyConstraint(
            ["artist_id"], ["artists.id"], name="fk_albums_artist_id_artists", ondelete="RESTRICT"
        ),
        sa.UniqueConstraint("apple_id", name="uq_albums_apple_id"),
        sa.UniqueConstraint("upc", name="uq_albums_upc"),
    )
    op.create_index("ix_albums_title", "albums", ["title"])
    op.create_index("ix_albums_artist_id", "albums", ["artist_id"])
    op.create_index(
        "ix_albums_title_trgm",
        "albums",
        ["title"],
        postgresql_using="gin",
        postgresql_ops={"title": "gin_trgm_ops"},
    )


def downgrade() -> None:
    op.drop_table("albums")
    op.drop_table("artists")
    op.drop_table("users")
