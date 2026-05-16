import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import CheckConstraint, Integer, TIMESTAMP, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class OralReport(Base):
    __tablename__ = "oral_reports"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    # JSONB — not TEXT/VARCHAR — enables direct SQL queries on the JSON (Req 2.6, 2.9)
    raw_json: Mapped[dict] = mapped_column(JSONB(), nullable=False)
    fluency_score: Mapped[int] = mapped_column(Integer(), nullable=False)
    pronunciation_score: Mapped[int] = mapped_column(Integer(), nullable=False)
    session_duration_seconds: Mapped[Optional[int]] = mapped_column(
        Integer(), nullable=True
    )
    submitted_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("NOW()")
    )

    __table_args__ = (
        CheckConstraint(
            "fluency_score >= 0 AND fluency_score <= 100",
            name="ck_oral_fluency_score",
        ),
        CheckConstraint(
            "pronunciation_score >= 0 AND pronunciation_score <= 100",
            name="ck_oral_pronunciation_score",
        ),
    )
