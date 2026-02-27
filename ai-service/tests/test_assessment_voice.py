"""
Tests for the async voice analysis pipeline.
  POST /{assessment_id}/add-voice          → 202 + voice_analysis_id
  GET  /{assessment_id}/voice-status/{id}  → processing / completed / failed

External dependencies (Supabase, voice-service, Gemini) are fully mocked.
SQLite in-memory + StaticPool replaces PostgreSQL.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

# NOTE: SQLiteTypeCompiler patches (UUID, ARRAY, JSONB) are applied in conftest.py
# which runs before this module, so create_all() works here.

from app.models import Base
from app.models.user import User, UserRole
from app.models.student import Student
from app.models.assessment import Assessment
from app.models.voice_analysis import VoiceAnalysis
from app.api.v1.endpoints.assessment_voice import _run_voice_pipeline
from app.core.security import get_current_active_user
from app.core.database import get_db
from app.main import app


# ── Shared SQLite helpers ──────────────────────────────────────────────────────

def _make_engine():
    """Create a fresh StaticPool in-memory SQLite engine with all tables."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    return engine


def _seed(session):
    """Insert minimal rows: user 10 → student 5 → assessment 99."""
    user = User(
        id=10, email="s@test.com", hashed_password="x",
        full_name="Test", role=UserRole.STUDENT, is_active=True,
    )
    session.add(user)
    session.flush()

    student = Student(id=5, user_id=user.id, gender="female")
    session.add(student)
    session.flush()

    assessment = Assessment(
        id=99, student_id=student.id,
        answers=[0, 1, 1, 2, 1, 1, 1], total_score=7,
        severity_level="mild", functional_impairment=0,
    )
    session.add(assessment)
    session.commit()
    return user, student, assessment


def _make_client(db_session, user_id):
    """TestClient with get_current_active_user and get_db overridden."""
    async def override_auth():
        return db_session.query(User).filter(User.id == user_id).first()

    def override_db():
        yield db_session

    app.dependency_overrides[get_current_active_user] = override_auth
    app.dependency_overrides[get_db] = override_db
    return TestClient(app, raise_server_exceptions=False)


def _clear():
    app.dependency_overrides.clear()


# ══════════════════════════════════════════════════════════════════════════════
# 1. Input validation
# ══════════════════════════════════════════════════════════════════════════════

class TestInputValidation:

    def test_empty_file_returns_400(self):
        """Empty audio file must be rejected with 400."""
        engine = _make_engine()
        Session = sessionmaker(bind=engine)
        db = Session()
        user, student, assessment = _seed(db)

        with patch("app.api.v1.endpoints.assessment_voice.storage"):
            c = _make_client(db, user.id)
            try:
                resp = c.post(
                    f"/api/v1/assessments/{assessment.id}/add-voice",
                    data={"gender": "female"},
                    files={"audio_file": ("rec.wav", b"", "audio/wav")},
                )
            finally:
                _clear()
                db.close()

        assert resp.status_code == 400
        assert "empty" in resp.json()["detail"].lower()

    def test_oversized_file_returns_413(self):
        """Files > 10 MB must be rejected with 413."""
        engine = _make_engine()
        Session = sessionmaker(bind=engine)
        db = Session()
        user, student, assessment = _seed(db)

        with patch("app.api.v1.endpoints.assessment_voice.storage"):
            c = _make_client(db, user.id)
            try:
                resp = c.post(
                    f"/api/v1/assessments/{assessment.id}/add-voice",
                    data={"gender": "male"},
                    files={"audio_file": ("rec.wav", b"x" * (11 * 1024 * 1024), "audio/wav")},
                )
            finally:
                _clear()
                db.close()

        assert resp.status_code == 413


# ══════════════════════════════════════════════════════════════════════════════
# 2. POST /{assessment_id}/add-voice  → 202
# ══════════════════════════════════════════════════════════════════════════════

class TestAddVoiceEndpoint:

    def _post(self, client, assessment_id):
        return client.post(
            f"/api/v1/assessments/{assessment_id}/add-voice",
            data={"gender": "female"},
            files={"audio_file": ("rec.wav", b"RIFF" + b"\x00" * 100, "audio/wav")},
        )

    @patch("app.api.v1.endpoints.assessment_voice._run_voice_pipeline")
    @patch("app.api.v1.endpoints.assessment_voice.storage")
    def test_returns_202_with_voice_analysis_id(self, mock_storage, mock_bg):
        """POST must respond 202 immediately and return voice_analysis_id."""
        engine = _make_engine()
        Session = sessionmaker(bind=engine)
        db = Session()
        user, student, assessment = _seed(db)
        mock_storage.save_audio.return_value = {"path": "5/rec.wav"}

        c = _make_client(db, user.id)
        try:
            resp = self._post(c, assessment.id)
        finally:
            _clear()
            db.close()

        assert resp.status_code == 202, resp.text
        body = resp.json()
        assert "voice_analysis_id" in body
        assert body["processing_status"] == "processing"
        assert isinstance(body["voice_analysis_id"], int)

    @patch("app.api.v1.endpoints.assessment_voice._run_voice_pipeline")
    @patch("app.api.v1.endpoints.assessment_voice.storage")
    def test_assessment_not_found_returns_404(self, mock_storage, mock_bg):
        """POST with non-existent assessment_id must return 404."""
        engine = _make_engine()
        Session = sessionmaker(bind=engine)
        db = Session()
        user, student, _ = _seed(db)

        c = _make_client(db, user.id)
        try:
            resp = self._post(c, 9999)
        finally:
            _clear()
            db.close()

        assert resp.status_code == 404

    @patch("app.api.v1.endpoints.assessment_voice._run_voice_pipeline")
    @patch("app.api.v1.endpoints.assessment_voice.storage")
    def test_stub_record_created_with_processing_status(self, mock_storage, mock_bg):
        """After 202, a VoiceAnalysis stub with status='processing' must exist in DB."""
        engine = _make_engine()
        Session = sessionmaker(bind=engine)
        db = Session()
        user, student, assessment = _seed(db)
        mock_storage.save_audio.return_value = {"path": "5/rec.wav"}

        c = _make_client(db, user.id)
        try:
            resp = self._post(c, assessment.id)
        finally:
            _clear()

        assert resp.status_code == 202
        va_id = resp.json()["voice_analysis_id"]

        db.expire_all()
        va = db.query(VoiceAnalysis).filter(VoiceAnalysis.id == va_id).first()
        assert va is not None
        assert va.processing_status == "processing"
        assert va.assessment_id == assessment.id
        assert va.student_id == student.id
        db.close()


# ══════════════════════════════════════════════════════════════════════════════
# 3. GET /{assessment_id}/voice-status/{id}  →  polling
# ══════════════════════════════════════════════════════════════════════════════

class TestVoiceStatusEndpoint:

    def _setup(self, proc_status="processing", error_msg=None):
        engine = _make_engine()
        Session = sessionmaker(bind=engine)
        db = Session()
        user, student, assessment = _seed(db)

        va = VoiceAnalysis(
            id=77,
            student_id=student.id,
            assessment_id=assessment.id,
            audio_file_path="5/rec.wav",
            processing_status=proc_status,
            has_error=1 if proc_status == "failed" else 0,
            error_message=error_msg,
            transcription="Test text" if proc_status == "completed" else None,
            dominant_emotion="neutral" if proc_status == "completed" else None,
            comprehensive_analysis="Analysis" if proc_status == "completed" else None,
        )
        db.add(va)
        db.commit()
        return db, user, student, assessment, va

    def test_status_processing_returns_processing(self):
        db, user, student, assessment, va = self._setup("processing")
        c = _make_client(db, user.id)
        try:
            resp = c.get(f"/api/v1/assessments/{assessment.id}/voice-status/{va.id}")
        finally:
            _clear()
            db.close()

        assert resp.status_code == 200
        assert resp.json()["processing_status"] == "processing"

    def test_status_completed_returns_full_result(self):
        db, user, student, assessment, va = self._setup("completed")
        c = _make_client(db, user.id)
        try:
            resp = c.get(f"/api/v1/assessments/{assessment.id}/voice-status/{va.id}")
        finally:
            _clear()
            db.close()

        assert resp.status_code == 200
        body = resp.json()
        assert body["processing_status"] == "completed"
        assert "transcription" in body
        assert body["gad7_score"] == 7
        assert body["gad7_severity"] == "mild"

    def test_status_failed_returns_error(self):
        db, user, student, assessment, va = self._setup("failed", error_msg="Deepgram timeout")
        c = _make_client(db, user.id)
        try:
            resp = c.get(f"/api/v1/assessments/{assessment.id}/voice-status/{va.id}")
        finally:
            _clear()
            db.close()

        assert resp.status_code == 200
        body = resp.json()
        assert body["processing_status"] == "failed"
        assert "Deepgram timeout" in body["error_message"]

    def test_wrong_voice_id_returns_404(self):
        db, user, student, assessment, _ = self._setup("processing")
        c = _make_client(db, user.id)
        try:
            resp = c.get(f"/api/v1/assessments/{assessment.id}/voice-status/9999")
        finally:
            _clear()
            db.close()

        assert resp.status_code == 404


# ══════════════════════════════════════════════════════════════════════════════
# 4. Background pipeline unit tests (_run_voice_pipeline)
# ══════════════════════════════════════════════════════════════════════════════

class TestRunVoicePipeline:
    """
    Calls _run_voice_pipeline() directly.
    SessionLocal is patched with the test sessionmaker CLASS (not an instance)
    so the pipeline opens+closes its own session on the StaticPool test DB.
    Verification uses a fresh session from the same sessionmaker.
    """

    def _setup(self):
        engine = _make_engine()
        PipelineSession = sessionmaker(bind=engine)

        seed_db = PipelineSession()
        user, student, assessment = _seed(seed_db)
        va = VoiceAnalysis(
            student_id=student.id,
            assessment_id=assessment.id,
            audio_file_path="5/rec.wav",
            processing_status="processing",
        )
        seed_db.add(va)
        seed_db.commit()
        seed_db.refresh(va)
        va_id = va.id
        a_id = assessment.id
        seed_db.close()
        return PipelineSession, va_id, a_id

    def _fake_voice(self, transcript="Hi"):
        return {
            "transcript": {"transcript": transcript, "language": "vi",
                           "word_count": 1, "confidence": 0.9, "duration": 5.0},
            "emotion_result": {"primary_emotion": "neutral", "confidence": 0.8},
            "text_analysis": {"sentiment_score": 0.1, "keywords": [],
                              "psychological_markers": {}},
            "audio_features": {}, "normalized_features": {},
            "audio_duration": 5.0, "processing_time": 2.0,
        }

    def _mock_ctx(self, return_value=None, side_effect=None):
        mock_resp = MagicMock()
        mock_resp.json.return_value = return_value
        mock_resp.raise_for_status = MagicMock()
        ctx = AsyncMock()
        ctx.__aenter__ = AsyncMock(return_value=ctx)
        ctx.__aexit__ = AsyncMock(return_value=False)
        ctx.post = AsyncMock(return_value=mock_resp) if not side_effect else AsyncMock(side_effect=side_effect)
        return ctx

    @pytest.mark.asyncio
    async def test_pipeline_updates_to_completed_on_success(self):
        """Happy path: voice-service + Gemini succeed → status='completed'."""
        PipelineSession, va_id, a_id = self._setup()

        import app.api.v1.endpoints.assessment_voice as av
        with patch.object(av, "SessionLocal", PipelineSession), \
             patch("httpx.AsyncClient", return_value=self._mock_ctx(self._fake_voice("Hello"))), \
             patch.object(av.gemini_service, "analyze_combined",
                          new=AsyncMock(return_value={"analysis": "summary", "recommendations": ["r1"]})):
            await _run_voice_pipeline(
                voice_analysis_id=va_id, audio_bytes=b"RIFF\x00",
                audio_filename="rec.wav", audio_content_type="audio/wav",
                gender_for_voice_service="female", assessment_id=a_id,
                prompt_text="prompt", file_size=5,
            )

        verify = PipelineSession()
        updated = verify.query(VoiceAnalysis).filter(VoiceAnalysis.id == va_id).first()
        assert updated.processing_status == "completed"
        assert updated.transcription == "Hello"
        assert updated.dominant_emotion == "neutral"
        assert updated.comprehensive_analysis == "summary"
        verify.close()

    @pytest.mark.asyncio
    async def test_pipeline_marks_failed_on_voice_service_error(self):
        """If voice-service request throws, VA must be marked 'failed'."""
        PipelineSession, va_id, a_id = self._setup()

        import app.api.v1.endpoints.assessment_voice as av
        with patch.object(av, "SessionLocal", PipelineSession), \
             patch("httpx.AsyncClient", return_value=self._mock_ctx(side_effect=Exception("voice-service down"))):
            await _run_voice_pipeline(
                voice_analysis_id=va_id, audio_bytes=b"RIFF",
                audio_filename="rec.wav", audio_content_type="audio/wav",
                gender_for_voice_service="male", assessment_id=a_id,
                prompt_text="prompt", file_size=4,
            )

        verify = PipelineSession()
        updated = verify.query(VoiceAnalysis).filter(VoiceAnalysis.id == va_id).first()
        assert updated.processing_status == "failed"
        assert updated.has_error == 1
        assert "voice-service down" in (updated.error_message or "")
        verify.close()

    @pytest.mark.asyncio
    async def test_pipeline_gemini_fallback_still_completes(self):
        """If Gemini fails, fallback text is used and status is still 'completed'."""
        PipelineSession, va_id, a_id = self._setup()

        import app.api.v1.endpoints.assessment_voice as av
        with patch.object(av, "SessionLocal", PipelineSession), \
             patch("httpx.AsyncClient", return_value=self._mock_ctx(self._fake_voice("Fallback"))), \
             patch.object(av.gemini_service, "analyze_combined",
                          new=AsyncMock(side_effect=Exception("Gemini quota"))):
            await _run_voice_pipeline(
                voice_analysis_id=va_id, audio_bytes=b"RIFF",
                audio_filename="rec.wav", audio_content_type="audio/wav",
                gender_for_voice_service="female", assessment_id=a_id,
                prompt_text="prompt", file_size=4,
            )

        verify = PipelineSession()
        updated = verify.query(VoiceAnalysis).filter(VoiceAnalysis.id == va_id).first()
        # Gemini fails → fallback text used, still completes
        assert updated.processing_status == "completed"
        assert updated.transcription == "Fallback"
        verify.close()
