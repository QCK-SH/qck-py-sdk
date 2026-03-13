"""Manage webhook endpoints through the QCK API.

Provides the :class:`WebhooksResource` class for creating, listing,
updating, deleting, and testing webhook endpoints. Also supports
listing delivery history for debugging failed deliveries.

Example::

    from qck import QCK, WEBHOOK_EVENTS

    client = QCK(api_key="qck_...")

    # Create a webhook endpoint
    webhook = client.webhooks.create({
        "url": "https://example.com/webhook",
        "events": [
            WEBHOOK_EVENTS["LINK_CREATED"],
            WEBHOOK_EVENTS["LINK_DELETED"],
        ],
    })
    print(webhook["secret"])  # Save the signing secret
"""

from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from .._client import HttpClient
    from .._types import (
        CreateWebhookParams,
        ListWebhookDeliveriesParams,
        PaginatedResponse,
        UpdateWebhookParams,
        WebhookEndpoint,
    )


class WebhooksResource:
    """Create, list, update, delete, and test webhook endpoints.

    Access via ``client.webhooks``. Provides full CRUD operations on
    webhook endpoints plus delivery history and test delivery.

    Attributes:
        _client: The underlying HTTP client used for API calls.
    """

    def __init__(self, client: "HttpClient") -> None:
        """Initialise the webhooks resource.

        Args:
            client: HTTP client instance for making API requests.
        """
        self._client = client

    def create(self, params: "CreateWebhookParams") -> "WebhookEndpoint":
        """Create a new webhook endpoint.

        The response includes a ``secret`` field that should be saved
        for verifying webhook payloads. The secret is only returned
        once at creation time.

        Args:
            params: Webhook creation parameters including URL, events,
                and optional description.

        Returns:
            The newly created webhook endpoint (includes ``secret``).

        Raises:
            ValidationError: If params fail validation.

        Example:
            >>> webhook = client.webhooks.create({
            ...     "url": "https://example.com/webhook",
            ...     "events": ["link.created"],
            ... })
            >>> print(webhook["secret"])
        """
        return self._client.post("/webhooks", dict(params))

    def list(self) -> List["WebhookEndpoint"]:
        """List all webhook endpoints.

        Returns:
            List of webhook endpoint objects.

        Example:
            >>> webhooks = client.webhooks.list()
            >>> for wh in webhooks:
            ...     print(wh["url"], wh["is_active"])
        """
        return self._client.get("/webhooks")

    def get(self, webhook_id: str) -> "WebhookEndpoint":
        """Retrieve a single webhook endpoint by ID.

        Args:
            webhook_id: The unique webhook endpoint identifier.

        Returns:
            The webhook endpoint object.

        Raises:
            NotFoundError: If no webhook exists with the given ID.

        Example:
            >>> wh = client.webhooks.get("wh_abc123")
            >>> print(wh["events"])
        """
        return self._client.get(f"/webhooks/{webhook_id}")

    def update(self, webhook_id: str, params: "UpdateWebhookParams") -> "WebhookEndpoint":
        """Update an existing webhook endpoint.

        Only the fields included in *params* are modified; omitted
        fields remain unchanged.

        Args:
            webhook_id: The unique webhook endpoint identifier.
            params: Fields to update.

        Returns:
            The updated webhook endpoint object.

        Raises:
            NotFoundError: If no webhook exists with the given ID.
            ValidationError: If the update params fail validation.

        Example:
            >>> client.webhooks.update("wh_abc123", {
            ...     "is_active": False,
            ... })
        """
        return self._client.patch(f"/webhooks/{webhook_id}", dict(params))

    def delete(self, webhook_id: str) -> None:
        """Delete a webhook endpoint.

        Args:
            webhook_id: The unique webhook endpoint identifier.

        Raises:
            NotFoundError: If no webhook exists with the given ID.

        Example:
            >>> client.webhooks.delete("wh_abc123")
        """
        self._client.delete(f"/webhooks/{webhook_id}")

    def list_deliveries(
        self,
        webhook_id: str,
        params: Optional["ListWebhookDeliveriesParams"] = None,
    ) -> "PaginatedResponse":
        """List delivery attempts for a webhook endpoint.

        Useful for debugging failed deliveries and monitoring webhook
        health.

        Args:
            webhook_id: The unique webhook endpoint identifier.
            params: Pagination options. Pass ``None`` for defaults.

        Returns:
            A paginated response containing delivery attempt records.

        Raises:
            NotFoundError: If no webhook exists with the given ID.

        Example:
            >>> deliveries = client.webhooks.list_deliveries(
            ...     "wh_abc123", {"page": 1, "limit": 10}
            ... )
            >>> for d in deliveries["data"]:
            ...     print(d["event_type"], d["status"])
        """
        return self._client.get(
            f"/webhooks/{webhook_id}/deliveries",
            params=dict(params) if params else None,
        )

    def test(self, webhook_id: str) -> None:
        """Send a test delivery to a webhook endpoint.

        Fires a synthetic test event to verify that the endpoint is
        reachable and correctly processing payloads.

        Args:
            webhook_id: The unique webhook endpoint identifier.

        Raises:
            NotFoundError: If no webhook exists with the given ID.

        Example:
            >>> client.webhooks.test("wh_abc123")
        """
        self._client.post(f"/webhooks/{webhook_id}/test")
