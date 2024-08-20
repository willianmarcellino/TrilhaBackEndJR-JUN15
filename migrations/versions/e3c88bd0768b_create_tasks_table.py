"""create tasks table

Revision ID: e3c88bd0768b
Revises: d0c4a2c6f694
Create Date: 2024-08-14 10:04:58.377860

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e3c88bd0768b'
down_revision: Union[str, None] = 'd0c4a2c6f694'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('tasks',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('status', sa.Enum('PENDING', 'DOING', 'DONE', 'EXPIRED', name='taskstates'), nullable=False),
    sa.Column('expires_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('user_id', sa.String(), nullable=False),
    sa.Column('label_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['label_id'], ['labels.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('tasks')
