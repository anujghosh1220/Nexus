"""add_team_indexes_and_constraints

Revision ID: a328177511bb
Revises: 59ead14f6e62
Create Date: 2026-10-06 21:45:37.612271+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a328177511bb'
down_revision: Union[str, None] = '59ead14f6e62'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(op.f('ix_teams_organization_id'), 'teams', ['organization_id'], unique=False)
    op.create_unique_constraint('uq_teams_organization_name', 'teams', ['organization_id', 'name'])


def downgrade() -> None:
    op.drop_constraint('uq_teams_organization_name', 'teams', type_='unique')
    op.drop_index(op.f('ix_teams_organization_id'), table_name='teams')
