"""QCK Python SDK -- official client for the QCK API.

This package provides a high-level Python interface to the QCK URL shortening
and analytics platform. It exposes the :class:`QCK` client and all supporting
types, error classes, and resource modules needed to interact with every
endpoint in the QCK public API.

Typical usage::

    from qck import QCK

    client = QCK(api_key="qck_...")
    link = client.links.create({"url": "https://example.com"})
    print(link["short_url"])

Modules:
    _client: Low-level HTTP transport with retries and error mapping.
    _errors: Exception hierarchy for API error responses.
    _types: TypedDict definitions for request params and response shapes.
    resources: High-level resource classes (links, analytics, etc.).
"""

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
    DeviceAnalyticsEntry,
    DeviceAnalyticsParams,
    Domain,
    FunnelParams,
    FunnelResult,
    GeoAnalyticsEntry,
    GeoAnalyticsParams,
    HourlyAnalyticsEntry,
    HourlyAnalyticsParams,
    IngestEventsParams,
    JourneyEvent,
    JourneyLinkSummary,
    JourneyQueryParams,
    Link,
    LinkMetadata,
    LinkStats,
    ListLinksParams,
    ListWebhookDeliveriesParams,
    PaginatedResponse,
    ReferrerAnalyticsEntry,
    ReferrerAnalyticsParams,
    SessionSummary,
    TimeseriesParams,
    TimeseriesPoint,
    TimeToConvertBucket,
    TimeToConvertData,
    TrackConversionParams,
    UpdateLinkParams,
    UpdateWebhookParams,
    WEBHOOK_EVENTS,
    WEBHOOK_EVENT_CATEGORIES,
    WebhookDelivery,
    WebhookEndpoint,
    WebhookPayload,
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
    "DeviceAnalyticsEntry",
    "DeviceAnalyticsParams",
    "Domain",
    "FunnelParams",
    "FunnelResult",
    "GeoAnalyticsEntry",
    "GeoAnalyticsParams",
    "HourlyAnalyticsEntry",
    "HourlyAnalyticsParams",
    "IngestEventsParams",
    "JourneyEvent",
    "JourneyLinkSummary",
    "JourneyQueryParams",
    "Link",
    "LinkMetadata",
    "LinkStats",
    "ListLinksParams",
    "ListWebhookDeliveriesParams",
    "PaginatedResponse",
    "ReferrerAnalyticsEntry",
    "ReferrerAnalyticsParams",
    "SessionSummary",
    "TimeseriesParams",
    "TimeseriesPoint",
    "TimeToConvertBucket",
    "TimeToConvertData",
    "TrackConversionParams",
    "UpdateLinkParams",
    "UpdateWebhookParams",
    "WEBHOOK_EVENTS",
    "WEBHOOK_EVENT_CATEGORIES",
    "WebhookDelivery",
    "WebhookEndpoint",
    "WebhookPayload",
]


_DEFAULT_BASE_URL = "https://api.qck.sh/public-api/v1"


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
        """Initialise the QCK client.

        Args:
            api_key: Your QCK API key (starts with ``qck_``).
            base_url: Override the API base URL. Defaults to the QCK
                production endpoint.
            timeout: Request timeout in seconds. Defaults to 30.
            retries: Maximum number of automatic retries on transient
                failures (rate limits, timeouts, connection errors).
                Defaults to 3.

        Raises:
            ValueError: If *api_key* is empty or falsy.

        Example:
            >>> client = QCK(api_key="qck_live_abc123")
            >>> client.links.list()
        """
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
        """Enter the context manager, returning the client instance."""
        return self

    def __exit__(self, *args: object) -> None:
        """Exit the context manager, closing the HTTP session."""
        self.close()
