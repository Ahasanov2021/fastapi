"""add content column to posts table

Revision ID: df203d635054
Revises: bb8e2080a117
Create Date: 2022-09-11 17:05:51.211074

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'df203d635054'
down_revision = 'bb8e2080a117'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('posts', sa.Column('content', sa.String, nullable=False))
    pass


def downgrade():
    op.drop_column('posts', 'content')
    pass
