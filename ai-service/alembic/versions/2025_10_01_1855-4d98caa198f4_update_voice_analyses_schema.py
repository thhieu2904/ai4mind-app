"""update_voice_analyses_schema

Revision ID: 4d98caa198f4
Revises: f8596d68f891
Create Date: 2025-10-01 18:55:05.745882

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4d98caa198f4'
down_revision: Union[str, None] = 'f8596d68f891'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new columns to voice_analyses table (skip if exists)
    with op.batch_alter_table('voice_analyses', schema=None) as batch_op:
        batch_op.add_column(sa.Column('assessment_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('file_size_bytes', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('audio_format', sa.String(length=10), nullable=True))
        batch_op.add_column(sa.Column('prompt_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('prompt_text', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('word_count', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('audio_features', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('sentiment_score', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('keywords', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('psychological_markers', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('gender_used', sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column('normalized_features', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))
        batch_op.add_column(sa.Column('processing_status', sa.String(length=20), server_default='pending', nullable=False))
        
        # Make transcription nullable
        batch_op.alter_column('transcription', nullable=True)
        batch_op.alter_column('transcription_language', server_default='vi')
        
        # Add foreign key
        batch_op.create_foreign_key('fk_voice_analyses_assessment_id', 'assessments', ['assessment_id'], ['id'], ondelete='SET NULL')
        
        # Add indexes
        batch_op.create_index('ix_voice_analyses_student_id', ['student_id'])
        batch_op.create_index('ix_voice_analyses_assessment_id', ['assessment_id'])
        batch_op.create_index('ix_voice_analyses_created_at', ['created_at'])
        batch_op.create_index('ix_voice_analyses_dominant_emotion', ['dominant_emotion'])


def downgrade() -> None:
    # Remove indexes
    op.drop_index('ix_voice_analyses_dominant_emotion', 'voice_analyses')
    op.drop_index('ix_voice_analyses_created_at', 'voice_analyses')
    op.drop_index('ix_voice_analyses_assessment_id', 'voice_analyses')
    op.drop_index('ix_voice_analyses_student_id', 'voice_analyses')
    
    # Remove foreign key
    op.drop_constraint('fk_voice_analyses_assessment_id', 'voice_analyses', type_='foreignkey')
    
    # Remove columns
    op.drop_column('voice_analyses', 'processing_status')
    op.drop_column('voice_analyses', 'created_at')
    op.drop_column('voice_analyses', 'normalized_features')
    op.drop_column('voice_analyses', 'gender_used')
    op.drop_column('voice_analyses', 'psychological_markers')
    op.drop_column('voice_analyses', 'keywords')
    op.drop_column('voice_analyses', 'sentiment_score')
    op.drop_column('voice_analyses', 'audio_features')
    op.drop_column('voice_analyses', 'word_count')
    op.drop_column('voice_analyses', 'prompt_text')
    op.drop_column('voice_analyses', 'prompt_id')
    op.drop_column('voice_analyses', 'audio_format')
    op.drop_column('voice_analyses', 'file_size_bytes')
    op.drop_column('voice_analyses', 'assessment_id')
