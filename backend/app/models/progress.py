import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, Integer, TIMESTAMP, text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class LessonProgress(Base):
    __tablename__ = "lesson_progress"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    lesson_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    module_type: Mapped[str] = mapped_column(
        SAEnum(
            "reading", "listening", "writing", "speaking",
            name="module_type_enum",
            create_type=False,
        ),
        nullable=False,
    )
    score: Mapped[int] = mapped_column(
        Integer(),
        nullable=False,
    )
    completed_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("NOW()")
    )

    __table_args__ = (
        CheckConstraint("score >= 0 AND score <= 100", name="ck_lesson_progress_score"),
    )
