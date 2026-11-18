"""Ports: what the application needs from the outside world."""

from typing import Protocol

from app.domain.campaign import Campaign


class CampaignRegistry(Protocol):
    """Our own record of the campaigns we create. Keitaro holds their real content."""

    def add(self, campaign: Campaign) -> Campaign:
        """Store a new campaign and return it with its id assigned."""
        ...

    def get(self, campaign_id: int) -> Campaign | None: ...

    def save(self, campaign: Campaign) -> None:
        """Persist changes of a stored campaign.

        Raises:
            CampaignNotFound: if the campaign is not stored.
        """
        ...

    def list_all(self) -> list[Campaign]:
        """Newest first."""
        ...
