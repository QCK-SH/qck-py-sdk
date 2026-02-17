"""Manage webhook endpoints through the QCK API."""

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
    """Create, list, update, delete, and test webhook endpoints."""

    def __init__(self, client: "HttpClient") -> None:
        self._client = client

    def create(self, params: "CreateWebhookParams") -> "WebhookEndpoint":
        return self._client.post("/webhooks", dict(params))

    def list(self) -> List["WebhookEndpoint"]:
        return self._client.get("/webhooks")

    def get(self, webhook_id: str) -> "WebhookEndpoint":
        return self._client.get(f"/webhooks/{webhook_id}")

    def update(self, webhook_id: str, params: "UpdateWebhookParams") -> "WebhookEndpoint":
        return self._client.patch(f"/webhooks/{webhook_id}", dict(params))

    def delete(self, webhook_id: str) -> None:
        self._client.delete(f"/webhooks/{webhook_id}")

    def list_deliveries(
        self,
        webhook_id: str,
        params: Optional["ListWebhookDeliveriesParams"] = None,
    ) -> "PaginatedResponse":
        return self._client.get(
            f"/webhooks/{webhook_id}/deliveries",
            params=dict(params) if params else None,
        )

    def test(self, webhook_id: str) -> None:
        self._client.post(f"/webhooks/{webhook_id}/test")
