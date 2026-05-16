from datetime import date
from typing import Optional

from pydantic import BaseModel, field_validator


class CheckinRequest(BaseModel):
    """
    Client sends its local IANA timezone so the Streak Engine uses the correct
    midnight boundary — not the server's UTC clock (Req 8.5, 8.9).
    """

    timezone: str

    @field_validator("timezone")
    @classmethod
    def validate_iana_timezone(cls, v: str) -> str:
        import pytz

        try:
            pytz.timezone(v)
        except pytz.exceptions.UnknownTimeZoneError:
            raise ValueError(f"Invalid timezone: {v}")
        return v


class StreakResponse(BaseModel):
    current_streak: int
    longest_streak: int
    last_activity_date: Optional[date] = None
