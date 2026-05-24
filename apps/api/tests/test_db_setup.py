from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.main import app


def test_settings_exposes_database_url() -> None:
    assert settings.database_url.startswith("postgresql")


def test_sqlalchemy_engine_and_session_are_configured() -> None:
    assert isinstance(engine, Engine)

    db = SessionLocal()
    try:
        assert isinstance(db, Session)
    finally:
        db.close()


def test_alembic_metadata_is_available() -> None:
    assert Base.metadata is not None


def test_app_still_boots() -> None:
    assert app.title == "AgentOps Workbench API"
