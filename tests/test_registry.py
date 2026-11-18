from collections.abc import Iterator
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.adapters.db.base import Base
from app.adapters.db.repository import SqlAlchemyCampaignRegistry
from app.domain.campaign import Campaign, CampaignName, CampaignStatus, GeoCodes
from app.domain.errors import CampaignNotFound


@pytest.fixture
def registry() -> Iterator[SqlAlchemyCampaignRegistry]:
    # SQLite keeps these tests fast and free of external services; the real schema is MySQL.
    engine = create_engine("sqlite+pysqlite://", poolclass=StaticPool)
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield SqlAlchemyCampaignRegistry(session)
    engine.dispose()


def make_campaign(suffix: str = "one", alias: str = "aB3dE9", **overrides: object) -> Campaign:
    campaign = Campaign(
        name=CampaignName(f"test_ivanov_{suffix}"),
        alias=alias,
        geo=GeoCodes(("MX", "AU")),
        offer_id=7,
    )
    for attribute, value in overrides.items():
        setattr(campaign, attribute, value)
    return campaign


def test_add_assigns_an_id_and_the_campaign_can_be_read_back(
    registry: SqlAlchemyCampaignRegistry,
) -> None:
    stored = registry.add(make_campaign())

    assert stored.id is not None
    assert registry.get(stored.id) == stored


def test_get_returns_none_for_an_unknown_id(registry: SqlAlchemyCampaignRegistry) -> None:
    assert registry.get(404) is None


def test_save_persists_the_new_status(registry: SqlAlchemyCampaignRegistry) -> None:
    stored = registry.add(make_campaign())
    stored.mark_active(keitaro_id=42)

    registry.save(stored)

    assert stored.id is not None
    reloaded = registry.get(stored.id)
    assert reloaded is not None
    assert reloaded.status is CampaignStatus.ACTIVE
    assert reloaded.keitaro_id == 42


def test_save_rejects_a_campaign_that_was_never_stored(
    registry: SqlAlchemyCampaignRegistry,
) -> None:
    with pytest.raises(CampaignNotFound):
        registry.save(make_campaign())


def test_list_all_returns_the_newest_first(registry: SqlAlchemyCampaignRegistry) -> None:
    now = datetime.now(UTC)
    first = registry.add(make_campaign("first", "aaaaaa", created_at=now - timedelta(hours=1)))
    second = registry.add(make_campaign("second", "bbbbbb", created_at=now))

    assert registry.list_all() == [second, first]


def test_the_campaign_name_must_be_unique(registry: SqlAlchemyCampaignRegistry) -> None:
    registry.add(make_campaign("same", "aaaaaa"))

    with pytest.raises(IntegrityError):
        registry.add(make_campaign("same", "bbbbbb"))
