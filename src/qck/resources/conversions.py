"""Track and query conversion analytics through the QCK API.

Provides the :class:`ConversionsResource` class for recording conversion
events and querying conversion metrics including summaries, timeseries,
breakdowns by dimension, and time-to-convert distributions.

Example::

    from qck import QCK

    client = QCK(api_key="qck_...")

    # Track a purchase conversion
    client.conversions.track({
        "link_id": "abc123",
        "visitor_id": "vis_xyz",
        "session_id": "sess_456",
        "name": "purchase",
        "revenue": 49.99,
    })

    # Get conversion summary
    summary = client.conversions.summary({"period": "30d"})
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from .._client import HttpClient
    from .._types import (
        ConversionBreakdownEntry,
        ConversionBreakdownParams,
        ConversionScopeParams,
        ConversionSummary,
        ConversionTimeseriesParams,
        ConversionTimeseriesPoint,
        TimeToConvertData,
        TrackConversionParams,
    )


class ConversionsResource:
    """Track conversion events and query conversion analytics.

    Access via ``client.conversions``. Provides methods to record
    conversion events server-side and to query conversion metrics.

    Attributes:
        _client: The underlying HTTP client used for API calls.
    """

    def __init__(self, client: "HttpClient") -> None:
        """Initialise the conversions resource.

        Args:
            client: HTTP client instance for making API requests.
        """
        self._client = client

    def track(self, params: "TrackConversionParams") -> None:
        """Track a conversion event.

        Use this from server-side code, mobile apps, or any HTTP client.
        """
        event = {
            "link_id": params["link_id"],
            "visitor_id": params["visitor_id"],
            "session_id": params.get("session_id", ""),
            "event_type": "conversion",
            "event_name": params["name"],
            "page_url": params.get("page_url", ""),
            "conversion_name": params["name"],
            "revenue_cents": round((params.get("revenue", 0) or 0) * 100),
            "currency": params.get("currency", "USD"),
            "properties": params.get("properties") or {},
        }

        self._client.post("/journey/events", {"events": [event]})

    def summary(
        self, params: Optional["ConversionScopeParams"] = None
    ) -> "ConversionSummary":
        """Get an aggregated conversion summary.

        Args:
            params: Scope filters (period, domain, or link). Pass
                ``None`` to use the API default period.

        Returns:
            A summary with total conversions, unique converters,
            revenue, average order value, and conversion rate.

        Example:
            >>> summary = client.conversions.summary({"period": "30d"})
            >>> print(summary["total_revenue"])
        """
        return self._client.get(
            "/conversions/summary", params=dict(params) if params else None
        )

    def timeseries(
        self, params: Optional["ConversionTimeseriesParams"] = None
    ) -> List["ConversionTimeseriesPoint"]:
        """Get conversion timeseries data.

        Returns time-bucketed conversion counts and revenue, suitable
        for charting trends over time.

        Args:
            params: Period, interval, and scope filters. Pass ``None``
                to use the API defaults.

        Returns:
            List of timeseries data points ordered chronologically.

        Example:
            >>> points = client.conversions.timeseries({
            ...     "period": "30d",
            ...     "interval": "day",
            ... })
        """
        return self._client.get(
            "/conversions/timeseries", params=dict(params) if params else None
        )

    def breakdown(
        self, params: "ConversionBreakdownParams"
    ) -> List["ConversionBreakdownEntry"]:
        """Get conversions broken down by a dimension.

        Args:
            params: Must include a ``dimension`` (``"device"``,
                ``"country"``, ``"link"``, or ``"name"``).
                Optional period and scope filters.

        Returns:
            List of breakdown entries sorted by conversions descending.

        Example:
            >>> by_country = client.conversions.breakdown({
            ...     "dimension": "country",
            ...     "period": "30d",
            ... })
        """
        return self._client.get("/conversions/breakdown", params=dict(params))

    def time_to_convert(
        self, params: Optional["ConversionScopeParams"] = None
    ) -> "TimeToConvertData":
        """Get time-to-convert distribution.

        Shows how long visitors take from first click to conversion.
        """
        return self._client.get(
            "/conversions/time-to-convert", params=dict(params) if params else None
        )
