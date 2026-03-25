"""Query custom domains through the QCK API.

Provides the :class:`DomainsResource` class for listing custom domains
associated with an organisation.

Example::

    from qck import QCK

    client = QCK(api_key="qck_...")
    domains = client.domains.list()
    for d in domains:
        print(d["domain"], d["is_verified"])
"""

from __future__ import annotations

from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from .._client import HttpClient
    from .._types import Domain


class DomainsResource:
    """List custom domains associated with an organisation.

    Access via ``client.domains``. Currently provides a read-only
    listing of custom domains. Domain creation and verification are
    managed through the QCK dashboard.

    Attributes:
        _client: The underlying HTTP client used for API calls.
    """

    def __init__(self, client: "HttpClient") -> None:
        """Initialise the domains resource.

        Args:
            client: HTTP client instance for making API requests.
        """
        self._client = client

    def list(self) -> List["Domain"]:
        """List all custom domains for the organization associated with the API key.

        Returns:
            List of domain objects including verification status.

        Example:
            >>> domains = client.domains.list()
            >>> for d in domains:
            ...     print(d["domain"], d["is_verified"])
        """
        response = self._client.get("/domains")
        return response["domains"]
