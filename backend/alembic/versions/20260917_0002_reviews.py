"""reviews table

Revision ID: 0002
Revises: 0001
Create Date: 2026-09-17

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "reviews",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("album_id", sa.Uuid(), nullable=False),
        sa.Column("rating_half_stars", sa.SmallInteger(), nullable=False),
        sa.Column("body", sa.Text(), nullable=True),
        sa.Column("listened_at", sa.Date(), nullable=True),
        sa.Column(
            "contains_spoilers", sa.Boolean(), server_default=sa.text("false"), nullable=False
        ),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id", name="pk_reviews"),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name="fk_reviews_user_id_users", ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["album_id"], ["albums.id"], name="fk_reviews_album_id_albums", ondelete="CASCADE"
        ),
        sa.UniqueConstraint("user_id", "album_id", name="uq_reviews_user_id_album_id"),
        sa.CheckConstraint(
            "rating_half_stars BETWEEN 1 AND 10", name="ck_reviews_rating_half_stars_range"
        ),
    )
    op.create_index(
        "ix_reviews_album_id_created_at", "reviews", ["album_id", sa.text("created_at DESC")]
    )
    op.create_index(
        "ix_reviews_user_id_created_at", "reviews", ["user_id", sa.text("created_at DESC")]
    )


def downgrade() -> None:
    op.drop_table("reviews")
