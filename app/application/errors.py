"""Errors exposed by outbound application ports."""


class KeitaroGatewayError(Exception):
    """The Keitaro gateway could not complete an operation."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code


class KeitaroAliasConflict(KeitaroGatewayError):
    """Keitaro rejected a campaign because its alias is already in use."""


class KeitaroResponseError(KeitaroGatewayError):
    """Keitaro returned a response outside the expected contract."""