"""add_files_table

Revision ID: 20261006_2320_d4e5f6a7b8c9
Revises: 20261006_2310_c3d4e5f6a7b8
Create Date: 2026-10-06 23:20:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = "20261006_2320_d4e5f6a7b8c9"
down_revision: Union[str, None] = "20261006_2310_c3d4e5f6a7b8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "files",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("organization_id", sa.String(), nullable=False),
        sa.Column("uploaded_by", sa.String(), nullable=False),
        sa.Column("filename", sa.String(), nullable=False),
        sa.Column("storage_key", sa.String(), nullable=False),
        sa.Column("content_type", sa.String(), nullable=False),
        sa.Column("size", sa.Integer(), nullable=False),
        sa.Column("checksum", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["uploaded_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_files_storage_key"), "files", ["storage_key"], unique=True)
    op.create_index(op.f("ix_files_organization_id"), "files", ["organization_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_files_organization_id"), table_name="files")
    op.drop_index(op.f("ix_files_storage_key"), table_name="files")
    op.drop_table("files")
