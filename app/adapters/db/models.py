from datetime import datetime

from sqlalchemy import JSON, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app import constants
from app.adapters.db.base import Base


class CampaignRecord(Base):
    __tablename__ = constants.CAMPAIGNS_TABLE

    id: Mapped[int] = mapped_column(primary_key=True)
    # Empty until Keitaro has created the campaign. MySQL allows many NULLs in a unique index.
    keitaro_id: Mapped[int | None] = mapped_column(unique=True)
    alias: Mapped[str] = mapped_column(String(constants.CAMPAIGN_ALIAS_MAX_LENGTH), unique=True)
    name: Mapped[str] = mapped_column(String(constants.CAMPAIGN_NAME_MAX_LENGTH), unique=True)
    geo: Mapped[list[str]] = mapped_column(JSON)
    offer_id: Mapped[int]
    status: Mapped[str] = mapped_column(String(constants.CAMPAIGN_STATUS_MAX_LENGTH), index=True)
    error: Mapped[str | None] = mapped_column(Text)
    # MySQL DATETIME has no time zone: values are stored as UTC and read back as UTC.
    created_at: Mapped[datetime] = mapped_column(DateTime)
