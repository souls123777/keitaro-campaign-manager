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


class KeitaroGateway(Protocol):
    """Operations available from the Keitaro Admin API."""

    def create_campaign(self, payload: dict[str, object]) -> dict[str, object]:
        """Create a campaign and return the decoded JSON response."""
        ...

    def create_stream(self, payload: dict[str, object]) -> dict[str, object]:
        """Create a stream and return the decoded JSON response."""
        ...

    def delete_campaign(self, campaign_id: int) -> None:
        """Delete a campaign together with its streams."""
        ...

