"""add comprehensive analysis to voice_analyses

Revision ID: add_comprehensive_fields
Revises: (check with: alembic history)
Create Date: 2025-10-03

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_comprehensive_fields'
down_revision = None  # TODO: Update this with: alembic current
branch_labels = None
depends_on = None


def upgrade():
    """Add comprehensive_analysis and comprehensive_recommendations columns to voice_analyses table"""
    
    # Add comprehensive_analysis column (TEXT) - stores Gemini's cross-validation analysis
    op.add_column('voice_analyses', 
        sa.Column('comprehensive_analysis', sa.Text(), nullable=True)
    )
    
    # Add comprehensive_recommendations column (JSON) - stores array of recommendations
    op.add_column('voice_analyses',
        sa.Column('comprehensive_recommendations', 
                  postgresql.JSON(astext_type=sa.Text()), 
                  nullable=True)
    )
    
    print("✅ Added comprehensive_analysis and comprehensive_recommendations columns to voice_analyses")


def downgrade():
    """Remove comprehensive analysis columns"""
    
    # Remove columns in reverse order
    op.drop_column('voice_analyses', 'comprehensive_recommendations')
    op.drop_column('voice_analyses', 'comprehensive_analysis')
    
    print("✅ Removed comprehensive_analysis and comprehensive_recommendations columns from voice_analyses")
