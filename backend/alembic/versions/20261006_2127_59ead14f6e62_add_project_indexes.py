"""add_project_indexes

Revision ID: 59ead14f6e62
Revises: 001
Create Date: 2026-10-06 21:27:35.509685+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '59ead14f6e62'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(op.f('ix_projects_key'), 'projects', ['key'], unique=False)
    op.create_index(op.f('ix_projects_organization_id'), 'projects', ['organization_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_projects_organization_id'), table_name='projects')
    op.drop_index(op.f('ix_projects_key'), table_name='projects')
