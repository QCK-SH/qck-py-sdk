"""Manage short links through the QCK API."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from .._client import HttpClient
    from .._types import (
        CreateLinkParams,
        Link,
        LinkStats,
        ListLinksParams,
        PaginatedResponse,
        UpdateLinkParams,
    )


class LinksResource:
    """Create, list, update, and delete short links."""

    def __init__(self, client: "HttpClient") -> None:
        self._client = client

    def create(self, params: "CreateLinkParams") -> "Link":
        return self._client.post("/links", dict(params))

    def list(self, params: Optional["ListLinksParams"] = None) -> "PaginatedResponse":
        return self._client.get("/links", params=dict(params) if params else None)

    def get(self, link_id: str) -> "Link":
        return self._client.get(f"/links/{link_id}")

    def update(self, link_id: str, params: "UpdateLinkParams") -> "Link":
        return self._client.patch(f"/links/{link_id}", dict(params))

    def delete(self, link_id: str) -> None:
        self._client.delete(f"/links/{link_id}")

    def bulk_create(self, links: List["CreateLinkParams"]) -> List["Link"]:
        return self._client.post("/links/bulk", [dict(l) for l in links])

    def get_stats(self, link_id: str) -> "LinkStats":
        return self._client.get(f"/links/{link_id}/stats")
