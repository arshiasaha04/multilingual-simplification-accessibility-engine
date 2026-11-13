from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import DateTime, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

from app.config import get_settings


class Base(DeclarativeBase):
    pass


class TelemetryEvent(Base):
    __tablename__ = "telemetry_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    event_type: Mapped[str] = mapped_column(String(80), index=True)
    language: Mapped[str | None] = mapped_column(String(12), nullable=True)
    details: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True
    )


def _create_engine():
    url = get_settings().database_url
    if url.startswith("sqlite:///"):
        database_path = Path(url.removeprefix("sqlite:///"))
        if str(database_path) != ":memory:":
            database_path.parent.mkdir(parents=True, exist_ok=True)
        return create_engine(url, connect_args={"check_same_thread": False})
    return create_engine(url)


engine = _create_engine()
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def log_event(event_type: str, language: str | None = None, details: str | None = None) -> None:
    with SessionLocal() as session:
        session.add(
            TelemetryEvent(event_type=event_type, language=language, details=details)
        )
        session.commit()
