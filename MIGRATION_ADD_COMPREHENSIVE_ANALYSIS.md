# Migration: Add Comprehensive Analysis to voice_analyses

## 🎯 Purpose

Store Gemini's comprehensive analysis (cross-validation of GAD-7 + Voice) in the database for:

- History viewing
- Progress tracking
- Avoiding re-computation with Gemini API

## 🗄️ Changes

### Database Schema

**Table**: `voice_analyses`

**Add 2 columns:**

```sql
ALTER TABLE voice_analyses
ADD COLUMN comprehensive_analysis TEXT,
ADD COLUMN comprehensive_recommendations JSON;
```

**Rationale:**

- `comprehensive_analysis` (TEXT) - Stores Gemini's comprehensive analysis text
- `comprehensive_recommendations` (JSON) - Stores array of recommendation strings
- Placed in `voice_analyses` because it represents the FINAL step (GAD-7 + Voice combined)

## 📦 Implementation Steps

### 1. Create Alembic Migration

```bash
cd ai-service
alembic revision -m "add_comprehensive_analysis_to_voice_analyses"
```

### 2. Edit Migration File

**File**: `ai-service/alembic/versions/XXXX_add_comprehensive_analysis_to_voice_analyses.py`

```python
"""add comprehensive analysis to voice_analyses

Revision ID: XXXX
Revises: YYYY
Create Date: 2025-10-03

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'XXXX'
down_revision = 'YYYY'  # Get this from: alembic history
branch_labels = None
depends_on = None


def upgrade():
    # Add comprehensive_analysis column (TEXT)
    op.add_column('voice_analyses',
        sa.Column('comprehensive_analysis', sa.Text(), nullable=True)
    )

    # Add comprehensive_recommendations column (JSON)
    op.add_column('voice_analyses',
        sa.Column('comprehensive_recommendations',
                  postgresql.JSON(astext_type=sa.Text()),
                  nullable=True)
    )


def downgrade():
    # Remove columns in reverse order
    op.drop_column('voice_analyses', 'comprehensive_recommendations')
    op.drop_column('voice_analyses', 'comprehensive_analysis')
```

### 3. Update SQLAlchemy Model

**File**: `ai-service/app/models/voice_analysis.py`

```python
class VoiceAnalysis(Base):
    __tablename__ = "voice_analyses"

    # ... existing columns ...

    transcription = Column(Text)
    detected_emotions = Column(JSON)
    sentiment_score = Column(Float)

    # 🆕 ADD THESE TWO LINES:
    comprehensive_analysis = Column(Text, nullable=True)
    comprehensive_recommendations = Column(JSON, nullable=True)

    # Relationships
    student = relationship("Student", back_populates="voice_analyses")
    assessment = relationship("Assessment", back_populates="voice_analyses")
```

### 4. Update Pydantic Schema

**File**: `ai-service/app/schemas/voice_analysis.py`

```python
class VoiceAnalysisResponse(BaseModel):
    id: int
    student_id: int
    assessment_id: int

    # ... existing fields ...

    transcription: Optional[str]
    detected_emotions: Optional[List[Dict]]
    sentiment_score: Optional[float]

    # 🆕 ADD THESE TWO LINES:
    comprehensive_analysis: Optional[str] = None
    comprehensive_recommendations: Optional[List[str]] = None

    class Config:
        from_attributes = True
```

### 5. Update API Endpoint

**File**: `ai-service/app/api/v1/endpoints/assessment_voice.py`

**Line ~216** (VoiceAnalysis creation):

```python
# Create VoiceAnalysis record
voice_analysis = VoiceAnalysis(
    student_id=assessment.student_id,
    assessment_id=assessment_id,
    audio_file_path=audio_path,
    audio_duration=voice_data.get("duration"),
    transcription=voice_data.get("transcript", ""),
    detected_emotions=emotions,
    dominant_emotion=dominant_emotion,
    sentiment_score=voice_data.get("sentiment_score"),
    audio_features=voice_data.get("audio_features"),
    psychological_markers=voice_data.get("psychological_markers"),
    # ... other existing fields ...

    # 🆕 ADD THESE TWO LINES:
    comprehensive_analysis=comprehensive_analysis,
    comprehensive_recommendations=comprehensive_recommendations,
)

db.add(voice_analysis)
db.commit()
db.refresh(voice_analysis)
```

**Line ~266** (Response - REMOVE these lines):

```python
# ❌ DELETE THIS BLOCK (no longer needed):
# return VoiceAnalysisResponse(
#     **voice_analysis.__dict__,
#     comprehensive_analysis=comprehensive_analysis,  # ❌ Remove
#     comprehensive_recommendations=comprehensive_recommendations,  # ❌ Remove
# )

# ✅ REPLACE WITH:
return voice_analysis  # Now includes comprehensive fields from DB
```

### 6. Run Migration

```bash
cd ai-service
alembic upgrade head
```

Verify:

```bash
alembic current
# Should show: XXXX (head)
```

### 7. Test

```bash
# Test endpoint
curl -X POST "http://localhost:8000/api/v1/assessments/123/add-voice" \
  -H "Authorization: Bearer TOKEN" \
  -F "audio_file=@test.wav"

# Check database
psql -d ai4mind -c "SELECT id, comprehensive_analysis FROM voice_analyses LIMIT 1;"
```

## 🧪 Testing Checklist

- [ ] Migration runs without errors
- [ ] `voice_analyses` table has new columns
- [ ] POST `/assessments/{id}/add-voice` saves comprehensive data
- [ ] ComprehensiveResultsPage displays saved data
- [ ] History page can load old comprehensive results
- [ ] Rollback works: `alembic downgrade -1`

## 📊 Impact Assessment

### ✅ Benefits

- **History feature enabled** - Users can view past comprehensive analyses
- **No API cost** - Don't need to call Gemini again for old results
- **Consistent results** - Analysis doesn't change on re-view
- **Simple structure** - No new tables, just 2 columns

### ⚠️ Considerations

- **Storage**: ~2KB per record (TEXT + JSON)
- **Nullable**: Existing records will have NULL (backward compatible)
- **Migration time**: < 1 second (add columns is fast)

## 🔄 Backward Compatibility

**Existing records**: Will have `NULL` in new columns

- ✅ No impact on existing queries
- ✅ Frontend handles missing data gracefully
- ✅ New recordings will populate fields

**Frontend compatibility**:

```tsx
// ComprehensiveResultsPage already checks:
if (!state.comprehensiveAnalysis) {
  navigate("/dashboard");
  return null;
}
```

## 📱 Frontend Changes

**No changes needed!** ComprehensiveResultsPage already uses `comprehensiveAnalysis` and `comprehensiveRecommendations` from location state, which now come from DB instead of memory.

## 🚀 Deployment

### Development

```bash
cd ai-service
alembic upgrade head
# Restart ai-service
```

### Production

```bash
# Backup database first!
pg_dump ai4mind > backup_$(date +%Y%m%d).sql

# Run migration
cd ai-service
alembic upgrade head

# Restart services
systemctl restart ai-service
```

## 🔙 Rollback Plan

If issues occur:

```bash
cd ai-service
alembic downgrade -1
```

This removes the two columns without data loss (other columns unaffected).

---

**Status**: ⏳ Ready to implement  
**Complexity**: 🟢 Low (simple column addition)  
**Risk**: 🟢 Low (backward compatible, nullable)  
**Recommendation**: ✅ **DO IT** - Needed for History feature
