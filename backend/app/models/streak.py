import uuid
from datetime import date
from typing import Optional

from sqlalchemy import Date, Integer, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Streak(Base):
    __tablename__ = "streaks"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True
    )
    current_streak: Mapped[int] = mapped_column(
        Integer(), nullable=False, server_default=text("0")
    )
    longest_streak: Mapped[int] = mapped_column(
        Integer(), nullable=False, server_default=text("0")
    )
    # Stored as DATE (no time component) in the client's local timezone (Req 8.8)
    last_activity_date: Mapped[Optional[date]] = mapped_column(Date(), nullable=True)
