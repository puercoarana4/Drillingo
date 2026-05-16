import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Integer, String, Text, TIMESTAMP, text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class VocabularyItem(Base):
    __tablename__ = "vocabulary_items"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    term: Mapped[str] = mapped_column(String(255), nullable=False)
    definition: Mapped[str] = mapped_column(Text(), nullable=False)
    example_sentence: Mapped[Optional[str]] = mapped_column(Text(), nullable=True)
    dialect_segment: Mapped[Optional[str]] = mapped_column(
        SAEnum("east_coast", "midwest", name="dialect_segment_enum", create_type=False),
        nullable=True,
    )
    level_band: Mapped[Optional[str]] = mapped_column(
        SAEnum("B1", "B2", "C1", name="level_band_enum", create_type=False),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("NOW()")
    )


class UserVocabulary(Base):
    """Join table tracking per-user vocabulary progress."""

    __tablename__ = "user_vocabulary"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        primary_key=True,
    )
    vocabulary_item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        primary_key=True,
    )
    mastered: Mapped[bool] = mapped_column(
        Boolean(), nullable=False, server_default=text("false")
    )
    correct_count: Mapped[int] = mapped_column(
        Integer(), nullable=False, server_default=text("0")
    )
    last_reviewed_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )
