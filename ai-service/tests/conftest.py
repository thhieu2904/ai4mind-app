"""
Test configuration and shared fixtures.
Uses SQLite in-memory so no real DB connection is needed.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy.dialects.sqlite import base as sqlite_base

# ── Patch SQLite to handle PostgreSQL-specific types ──────────────────────────
# These types are not natively supported by SQLite; map them to simple equivalents.
def _visit_UUID(self, type_, **kw):          # noqa: N802
    return "VARCHAR(36)"

def _visit_ARRAY(self, type_, **kw):         # noqa: N802
    return "TEXT"  # store as JSON string in tests

def _visit_JSONB(self, type_, **kw):         # noqa: N802
    return "TEXT"

for _name, _fn in [("visit_UUID", _visit_UUID), ("visit_ARRAY", _visit_ARRAY), ("visit_JSONB", _visit_JSONB)]:
    if not hasattr(sqlite_base.SQLiteTypeCompiler, _name):
        setattr(sqlite_base.SQLiteTypeCompiler, _name, _fn)


from app.core.database import get_db
from app.models import Base          # models register on THIS Base, not core.database.Base
from app.main import app
from app.models.user import User, UserRole
from app.models.student import Student
from app.models.assessment import Assessment
from app.models.voice_analysis import VoiceAnalysis

# ── In-memory SQLite DB ────────────────────────────────────────────────────────
# StaticPool forces all connections to reuse the same underlying SQLite connection,
# so tables created by create_all() are visible to the session.
SQLALCHEMY_TEST_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_TEST_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """Fresh in-memory DB per test function."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_with_data(db):
    """DB pre-populated with a student, user, and assessment."""
    user = User(
        id=1,
        email="test@student.com",
        hashed_password="hashed",
        full_name="Test Student",
        role=UserRole.STUDENT,
        is_active=True,
    )
    db.add(user)
    db.flush()

    student = Student(id=1, user_id=user.id, gender="male")
    db.add(student)
    db.flush()

    assessment = Assessment(
        id=1,
        student_id=student.id,
        answers=[1, 1, 1, 1, 1, 1, 1],
        total_score=7,
        severity_level="mild",
        functional_impairment=0,
    )
    db.add(assessment)
    db.commit()

    return {"user": user, "student": student, "assessment": assessment}


@pytest.fixture(scope="function")
def client(db):
    """TestClient with DB dependency overridden."""
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c
    app.dependency_overrides.clear()
