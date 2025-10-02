# Database Migration: Add Comprehensive Analysis Fields

## Problem

The `voice_analyses` table is **missing critical fields** to store Gemini's comprehensive analysis results. Currently, these fields are only returned in the API response but **NOT SAVED** to the database, causing data loss.

## Missing Fields

```sql
voice_analyses table:
  ❌ comprehensive_analysis (TEXT) - Gemini's cross-validation analysis
  ❌ comprehensive_recommendations (JSON) - Gemini's combined recommendations
```

## Impact

Without these fields:

- ❌ Cannot view comprehensive results history
- ❌ Cannot compare results over time
- ❌ Data is lost after API response
- ❌ Cannot implement History page properly
- ❌ Cannot track mental health trends with comprehensive insights

## Solution

### Step 1: Create Alembic Migration

```bash
# In ai-service directory
cd ai-service
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Generate migration
alembic revision -m "add_comprehensive_analysis_fields_to_voice_analyses"
```

### Step 2: Migration File Content

Create file: `ai-service/alembic/versions/XXXX_add_comprehensive_analysis_fields_to_voice_analyses.py`

```python
"""add comprehensive analysis fields to voice_analyses

Revision ID: XXXX
Revises: PREVIOUS_REVISION
Create Date: 2025-10-02 23:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'XXXX'
down_revision = 'PREVIOUS_REVISION'  # Get this from current head
branch_labels = None
depends_on = None


def upgrade():
    """Add comprehensive analysis fields from Gemini"""

    # Add comprehensive_analysis column (TEXT)
    op.add_column(
        'voice_analyses',
        sa.Column(
            'comprehensive_analysis',
            sa.Text(),
            nullable=True,
            comment='Cross-validation analysis from Gemini combining GAD-7 and voice data'
        )
    )

    # Add comprehensive_recommendations column (JSON)
    op.add_column(
        'voice_analyses',
        sa.Column(
            'comprehensive_recommendations',
            postgresql.JSON(astext_type=sa.Text()),
            nullable=True,
            comment='Personalized recommendations from Gemini based on combined analysis'
        )
    )


def downgrade():
    """Remove comprehensive analysis fields"""
    op.drop_column('voice_analyses', 'comprehensive_recommendations')
    op.drop_column('voice_analyses', 'comprehensive_analysis')
```

### Step 3: Update SQLAlchemy Model

File: `ai-service/app/models/voice_analysis.py`

```python
# Add after line 60 (after psychological_markers)

# Comprehensive analysis from Gemini (cross-validation with GAD-7)
comprehensive_analysis = Column(
    Text,
    nullable=True,
    comment='Cross-validation analysis combining GAD-7 (subjective) and voice (objective) data'
)
comprehensive_recommendations = Column(
    JSON,
    nullable=True,
    comment='Personalized recommendations from Gemini based on combined analysis'
)
```

### Step 4: Update Backend Endpoint

File: `ai-service/app/api/v1/endpoints/assessment_voice.py`

**Change line ~216 (VoiceAnalysis creation):**

```python
# Add these fields to the VoiceAnalysis constructor:

voice_analysis = VoiceAnalysis(
    student_id=student.id,
    assessment_id=assessment_id,

    # ... existing fields ...

    # ADD THESE TWO LINES:
    comprehensive_analysis=comprehensive_analysis,  # ← NEW
    comprehensive_recommendations=comprehensive_recommendations,  # ← NEW

    # Processing metadata
    processing_status="completed",
    processed_at=datetime.utcnow(),
    processing_time=voice_result.get("processing_time", 0.0)
)
```

### Step 5: Run Migration

```bash
# Check current revision
alembic current

# Run migration
alembic upgrade head

# Verify in database
psql -h YOUR_HOST -U YOUR_USER -d YOUR_DB
\d voice_analyses
# Should see new columns: comprehensive_analysis, comprehensive_recommendations
```

## Updated Schema

```sql
CREATE TABLE public.voice_analyses (
  -- ... existing fields ...

  -- ✅ NEW FIELDS
  comprehensive_analysis text,
  comprehensive_recommendations json,

  -- ... rest of existing fields ...
);
```

## Benefits After Migration

### 1. Data Persistence

```python
# Can query comprehensive results anytime
voice_analysis = db.query(VoiceAnalysis).filter_by(id=10).first()
print(voice_analysis.comprehensive_analysis)  # ✅ Saved in DB
```

### 2. History Page

```python
# Get all past comprehensive analyses
history = db.query(VoiceAnalysis).filter_by(
    student_id=student.id
).order_by(VoiceAnalysis.created_at.desc()).all()

for record in history:
    print(f"{record.created_at}: {record.comprehensive_analysis[:100]}...")
```

### 3. Trend Analysis

```python
# Compare comprehensive insights over time
analyses = db.query(VoiceAnalysis).filter_by(student_id=student.id).all()

# Track changes in Gemini's assessment
for i, analysis in enumerate(analyses):
    print(f"Visit {i+1}: {analysis.comprehensive_analysis}")
    # Can detect improvement or deterioration
```

### 4. API GET Endpoints

```python
# GET /api/v1/voice-analyses/{id}
# Return comprehensive analysis from DB (not recalculate)

@router.get("/{voice_analysis_id}")
async def get_voice_analysis(voice_analysis_id: int, db: Session = Depends(get_db)):
    voice = db.query(VoiceAnalysis).filter_by(id=voice_analysis_id).first()

    return {
        "id": voice.id,
        "transcription": voice.transcription,
        "comprehensive_analysis": voice.comprehensive_analysis,  # ✅ From DB
        "comprehensive_recommendations": voice.comprehensive_recommendations,  # ✅ From DB
        ...
    }
```

## Testing

### Before Migration (Current State)

```python
# Insert will ignore comprehensive fields
voice = VoiceAnalysis(comprehensive_analysis="test")
# AttributeError: 'VoiceAnalysis' object has no attribute 'comprehensive_analysis'
```

### After Migration

```python
# Insert works
voice = VoiceAnalysis(
    student_id=51,
    assessment_id=26,
    comprehensive_analysis="Dựa trên cross-validation...",
    comprehensive_recommendations=["Gặp tư vấn viên", "Thực hành thư giãn"]
)
db.add(voice)
db.commit()  # ✅ Success

# Query works
voice = db.query(VoiceAnalysis).first()
print(voice.comprehensive_analysis)  # ✅ Returns saved value
```

## Migration Commands Summary

```bash
# 1. Generate migration
cd ai-service
alembic revision -m "add_comprehensive_analysis_fields_to_voice_analyses"

# 2. Edit generated file (add upgrade/downgrade logic above)

# 3. Check migration
alembic check

# 4. Run migration
alembic upgrade head

# 5. Verify
alembic current
# Should show new revision

# 6. Test in Python
python
>>> from app.models.voice_analysis import VoiceAnalysis
>>> from app.db.session import SessionLocal
>>> db = SessionLocal()
>>> voice = db.query(VoiceAnalysis).first()
>>> print(hasattr(voice, 'comprehensive_analysis'))
True  # ✅ Field exists
```

## Rollback (if needed)

```bash
# Rollback one revision
alembic downgrade -1

# Rollback to specific revision
alembic downgrade <revision_id>
```

## Summary

**Current state:** ❌ Comprehensive analysis NOT saved (data loss)
**After migration:** ✅ Comprehensive analysis SAVED (full history)

This migration is **CRITICAL** for:

- ✅ Data persistence
- ✅ History tracking
- ✅ Trend analysis
- ✅ GET endpoints
- ✅ Complete user experience
