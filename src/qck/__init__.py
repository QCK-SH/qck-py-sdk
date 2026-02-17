"""QCK Python SDK — official client for the QCK API."""

from __future__ import annotations

from ._client import HttpClient
from ._errors import (
    AuthenticationError,
    NotFoundError,
    QCKError,
    RateLimitError,
    ValidationError,
)
from ._types import (
    AnalyticsSummary,
    AnalyticsSummaryParams,
    ConversionBreakdownEntry,
    ConversionBreakdownParams,
    ConversionScopeParams,
    ConversionSummary,
    ConversionTimeseriesParams,
    ConversionTimeseriesPoint,
    CreateLinkParams,
    CreateWebhookParams,
    Domain,
    FunnelParams,
    FunnelResult,
    IngestEventsParams,
    JourneyEvent,
    JourneyLinkSummary,
    JourneyQueryParams,
    Link,
    LinkStats,
    ListLinksParams,
    ListWebhookDeliveriesParams,
    PaginatedResponse,
    SessionSummary,
    TimeseriesParams,
    TimeseriesPoint,
    TrackConversionParams,
    UpdateLinkParams,
    UpdateWebhookParams,
    WebhookDelivery,
    WebhookEndpoint,
)
from .resources import (
    AnalyticsResource,
    ConversionsResource,
    DomainsResource,
    JourneyResource,
    LinksResource,
    WebhooksResource,
)

__all__ = [
    # Main class
    "QCK",
    # Client
    "HttpClient",
    # Resources
    "AnalyticsResource",
    "ConversionsResource",
    "DomainsResource",
    "JourneyResource",
    "LinksResource",
    "WebhooksResource",
    # Errors
    "QCKError",
    "AuthenticationError",
    "RateLimitError",
    "NotFoundError",
    "ValidationError",
    # Types
    "AnalyticsSummary",
    "AnalyticsSummaryParams",
    "ConversionBreakdownEntry",
    "ConversionBreakdownParams",
    "ConversionScopeParams",
    "ConversionSummary",
    "ConversionTimeseriesParams",
    "ConversionTimeseriesPoint",
    "CreateLinkParams",
    "CreateWebhookParams",
    "Domain",
    "FunnelParams",
    "FunnelResult",
    "IngestEventsParams",
    "JourneyEvent",
    "JourneyLinkSummary",
    "JourneyQueryParams",
    "Link",
    "LinkStats",
    "ListLinksParams",
    "ListWebhookDeliveriesParams",
    "PaginatedResponse",
    "SessionSummary",
    "TimeseriesParams",
    "TimeseriesPoint",
    "TrackConversionParams",
    "UpdateLinkParams",
    "UpdateWebhookParams",
    "WebhookDelivery",
    "WebhookEndpoint",
]


_DEFAULT_BASE_URL = "https://api.qck.sh/api/v1/developer"


class QCK:
    """QCK API client.

    Usage::

        from qck import QCK

        client = QCK(api_key="qck_...")

        # Create a short link
        link = client.links.create({"url": "https://example.com"})

        # Track a conversion
        client.conversions.track({
            "link_id": link["id"],
            "visitor_id": "vis_123",
            "name": "purchase",
            "revenue": 49.99,
        })

        # Query analytics
        summary = client.analytics.summary({"days": 30})
    """

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = _DEFAULT_BASE_URL,
        timeout: int = 30,
        retries: int = 3,
    ) -> None:
        if not api_key:
            raise ValueError("api_key is required")

        self._client = HttpClient(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            retries=retries,
        )

        self.links = LinksResource(self._client)
        self.analytics = AnalyticsResource(self._client)
        self.domains = DomainsResource(self._client)
        self.webhooks = WebhooksResource(self._client)
        self.journey = JourneyResource(self._client)
        self.conversions = ConversionsResource(self._client)

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self._client.close()

    def __enter__(self) -> "QCK":
        return self

    def __exit__(self, *args: object) -> None:
        self.close()
