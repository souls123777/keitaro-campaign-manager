"""Domain errors. The message of each one is meant to be shown to the user."""


class DomainError(Exception):
    """Base class for every business-rule violation."""


class InvalidCampaignName(DomainError):
    pass


class InvalidGeoCodes(DomainError):
    pass


class InvalidOfferId(DomainError):
    pass


class InvalidStatusTransition(DomainError):
    pass


class CampaignNotFound(DomainError):
    pass


class CampaignAlreadyExists(DomainError):
    pass


class OfferAlreadyInCampaign(DomainError):
    pass


class OfferNotInCampaign(DomainError):
    pass
