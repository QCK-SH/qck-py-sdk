"""Manage short links through the QCK API."""

from __future__ import annotations

import mimetypes
from pathlib import Path
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

    def upload_og_image(self, link_id: str, file_path: str) -> Dict[str, Any]:
        """Upload an OG image for a link.

        Reads the file at *file_path*, detects its content type, and sends
        the binary body via ``PUT /links/{link_id}/og-image``.

        Supported formats: JPEG, PNG, WebP, and GIF.
        """
        _ALLOWED_CONTENT_TYPES = {
            "image/jpeg",
            "image/png",
            "image/webp",
            "image/gif",
        }

        path = Path(file_path)
        content_type, _ = mimetypes.guess_type(str(path))
        if content_type not in _ALLOWED_CONTENT_TYPES:
            raise ValueError(
                f"Unsupported image type '{content_type}'. "
                f"Allowed: {', '.join(sorted(_ALLOWED_CONTENT_TYPES))}"
            )

        data = path.read_bytes()
        return self._client.put(
            f"/links/{link_id}/og-image",
            content=data,
            headers={"Content-Type": content_type},
        )

    def delete_og_image(self, link_id: str) -> None:
        """Delete the OG image for a link."""
        self._client.delete(f"/links/{link_id}/og-image")
