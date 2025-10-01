"""add_gender_to_students

Revision ID: f8596d68f891
Revises: 
Create Date: 2025-10-01 18:51:58.140485

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f8596d68f891'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add gender column to students table
    op.add_column('students', 
        sa.Column('gender', sa.String(length=20), nullable=True, server_default='prefer_not_to_say')
    )
    
    # Add check constraint for valid gender values
    op.create_check_constraint(
        'check_gender_values',
        'students',
        "gender IN ('male', 'female', 'other', 'prefer_not_to_say')"
    )


def downgrade() -> None:
    # Remove check constraint first
    op.drop_constraint('check_gender_values', 'students', type_='check')
    
    # Remove gender column
    op.drop_column('students', 'gender')
