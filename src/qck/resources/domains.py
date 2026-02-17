"""Query custom domains through the QCK API."""

from __future__ import annotations

from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from .._client import HttpClient
    from .._types import Domain


class DomainsResource:
    """List domains associated with an organization."""

    def __init__(self, client: "HttpClient") -> None:
        self._client = client

    def list(self, organization_id: str) -> List["Domain"]:
        return self._client.get("/domains", params={"organizationId": organization_id})
