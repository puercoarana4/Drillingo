import uuid
from datetime import datetime

from sqlalchemy import Integer, String, Text, TIMESTAMP, text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Lesson(Base):
    __tablename__ = "lessons"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    dialect_segment: Mapped[str] = mapped_column(
        SAEnum("east_coast", "midwest", name="dialect_segment_enum", create_type=False),
        nullable=False,
    )
    level_band: Mapped[str] = mapped_column(
        SAEnum("B1", "B2", "C1", name="level_band_enum", create_type=False),
        nullable=False,
    )
    day_order: Mapped[int] = mapped_column(Integer(), nullable=False)
    # Audio stored in Object Storage (S3/Supabase); only URL persisted here (Req 5.7)
    # TEXT type to support JSON payloads for exercise content
    audio_url: Mapped[str] = mapped_column(Text(), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("NOW()")
    )
