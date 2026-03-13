"""Manage short links through the QCK API.

Provides the :class:`LinksResource` class for creating, listing,
updating, deleting, and bulk-creating short links. Also supports
per-link statistics and OG image upload/deletion.

Example::

    from qck import QCK

    client = QCK(api_key="qck_...")

    # Create a link
    link = client.links.create({"url": "https://example.com"})

    # List links with filtering
    page = client.links.list({"tags": ["marketing"], "per_page": 10})
"""

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
    """Create, list, update, and delete short links.

    Access via ``client.links``. Provides CRUD operations on short
    links, bulk creation, per-link statistics, and OG image management.

    Attributes:
        _client: The underlying HTTP client used for API calls.
    """

    def __init__(self, client: "HttpClient") -> None:
        """Initialise the links resource.

        Args:
            client: HTTP client instance for making API requests.
        """
        self._client = client

    def create(self, params: "CreateLinkParams") -> "Link":
        """Create a new short link.

        Args:
            params: Link creation parameters. Only ``url`` is required.

        Returns:
            The newly created link object.

        Raises:
            ValidationError: If the URL is invalid or params fail
                validation.

        Example:
            >>> link = client.links.create({
            ...     "url": "https://example.com",
            ...     "custom_alias": "my-link",
            ...     "tags": ["marketing"],
            ... })
            >>> print(link["short_url"])
        """
        return self._client.post("/links", dict(params))

    def list(self, params: Optional["ListLinksParams"] = None) -> "PaginatedResponse":
        """List links with optional filtering and pagination.

        Args:
            params: Query filters and pagination options. Pass ``None``
                to retrieve the first page with default settings.

        Returns:
            A paginated response containing a list of links and
            pagination metadata.

        Example:
            >>> page = client.links.list({"page": 1, "per_page": 10})
            >>> for link in page["data"]:
            ...     print(link["short_url"])
        """
        return self._client.get("/links", params=dict(params) if params else None)

    def get(self, link_id: str) -> "Link":
        """Retrieve a single link by ID.

        Args:
            link_id: The unique link identifier.

        Returns:
            The link object.

        Raises:
            NotFoundError: If no link exists with the given ID.

        Example:
            >>> link = client.links.get("lnk_abc123")
            >>> print(link["original_url"])
        """
        return self._client.get(f"/links/{link_id}")

    def update(self, link_id: str, params: "UpdateLinkParams") -> "Link":
        """Update an existing link.

        Only the fields included in *params* are modified; omitted
        fields remain unchanged.

        Args:
            link_id: The unique link identifier.
            params: Fields to update.

        Returns:
            The updated link object.

        Raises:
            NotFoundError: If no link exists with the given ID.
            ValidationError: If the update params fail validation.

        Example:
            >>> updated = client.links.update("lnk_abc123", {
            ...     "title": "New Title",
            ...     "is_active": False,
            ... })
        """
        return self._client.patch(f"/links/{link_id}", dict(params))

    def delete(self, link_id: str) -> None:
        """Delete a link.

        Args:
            link_id: The unique link identifier.

        Raises:
            NotFoundError: If no link exists with the given ID.

        Example:
            >>> client.links.delete("lnk_abc123")
        """
        self._client.delete(f"/links/{link_id}")

    def bulk_create(self, links: List["CreateLinkParams"]) -> List["Link"]:
        """Create multiple links in a single request.

        The maximum batch size depends on your subscription tier.

        Args:
            links: List of link creation parameter objects.

        Returns:
            List of newly created link objects.

        Raises:
            ValidationError: If any link params fail validation or
                the batch exceeds your tier's bulk import limit.

        Example:
            >>> links = client.links.bulk_create([
            ...     {"url": "https://example.com/a"},
            ...     {"url": "https://example.com/b"},
            ... ])
        """
        return self._client.post("/links/bulk", [dict(l) for l in links])

    def get_stats(self, link_id: str) -> "LinkStats":
        """Retrieve click statistics for a single link.

        Args:
            link_id: The unique link identifier.

        Returns:
            Aggregated click statistics including breakdowns by
            country, device, and referrer.

        Raises:
            NotFoundError: If no link exists with the given ID.

        Example:
            >>> stats = client.links.get_stats("lnk_abc123")
            >>> print(stats["total_clicks"])
        """
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
