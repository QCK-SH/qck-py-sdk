"""Query click analytics through the QCK API.

Provides the :class:`AnalyticsResource` class for retrieving click
analytics data including summaries, timeseries, geographic breakdowns,
device/browser stats, referrer sources, and hourly distributions.

Every analytics endpoint returns ``{"analytics": ..., "usage": {...}}``:
the endpoint-specific payload plus tier usage metadata (monthly click
counts, limits, retention, and any over-limit cutoff date).

Example::

    from qck import QCK

    client = QCK(api_key="qck_...")
    result = client.analytics.summary({"days": 30})
    print(f"Total clicks: {result['analytics']['total_clicks']}")
    print(f"Usage: {result['usage']['clicks_this_month']}")
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .._client import HttpClient
    from .._types import (
        AnalyticsResult,
        AnalyticsSummaryParams,
        DeviceAnalyticsParams,
        GeoAnalyticsParams,
        HourlyAnalyticsParams,
        ReferrerAnalyticsParams,
        TimeseriesParams,
    )


class AnalyticsResource:
    """Query analytics summaries and timeseries data.

    Access via ``client.analytics``. Provides read-only access to
    click analytics data aggregated across all links or filtered by
    domain. Every method returns an :class:`~qck.AnalyticsResult`
    dict with ``analytics`` (the payload) and ``usage`` (tier usage
    metadata) keys.

    Attributes:
        _client: The underlying HTTP client used for API calls.
    """

    def __init__(self, client: "HttpClient") -> None:
        """Initialise the analytics resource.

        Args:
            client: HTTP client instance for making API requests.
        """
        self._client = client

    def summary(self, params: Optional["AnalyticsSummaryParams"] = None) -> "AnalyticsResult":
        """Get an aggregated analytics summary.

        Returns high-level metrics such as total clicks, unique
        visitors, active links, and this month's link/click counts
        for the given time period.

        Args:
            params: Date range and filter options. Pass ``None`` to
                use the API default period.

        Returns:
            ``{"analytics": AnalyticsSummary, "usage": AnalyticsUsage}``.

        Example:
            >>> result = client.analytics.summary({"days": 7})
            >>> print(result["analytics"]["total_clicks"])
            >>> print(result["usage"]["limit_exceeded"])
        """
        return self._client.get("/analytics/summary", params=dict(params) if params else None)

    def timeseries(self, params: Optional["TimeseriesParams"] = None) -> "AnalyticsResult":
        """Get click timeseries data.

        Returns a list of date-bucketed data points with click counts
        and unique visitor counts, suitable for charting.

        Args:
            params: Date range and filter options. Pass ``None`` to
                use the API default period.

        Returns:
            ``{"analytics": list[TimeseriesPoint], "usage": AnalyticsUsage}``.
            Points are ordered chronologically; each has ``date``
            (``YYYY-MM-DD``), ``clicks``, and ``unique_visitors``.

        Example:
            >>> result = client.analytics.timeseries({"days": 30})
            >>> for p in result["analytics"]:
            ...     print(p["date"], p["clicks"])
        """
        return self._client.get("/analytics/timeseries", params=dict(params) if params else None)

    def geo(self, params: Optional["GeoAnalyticsParams"] = None) -> "AnalyticsResult":
        """Get geographic analytics (clicks by country).

        Args:
            params: Date range and filter options. Pass ``None`` to
                use the API default period.

        Returns:
            ``{"analytics": list[GeoAnalyticsEntry], "usage": AnalyticsUsage}``.
            Entries have ``country_code`` (ISO 3166-1 alpha-2),
            ``clicks``, and ``unique_visitors``, sorted by clicks
            descending.

        Example:
            >>> result = client.analytics.geo({"days": 30})
            >>> for c in result["analytics"]:
            ...     print(c["country_code"], c["clicks"])
        """
        return self._client.get("/analytics/geo", params=dict(params) if params else None)

    def devices(self, params: Optional["DeviceAnalyticsParams"] = None) -> "AnalyticsResult":
        """Get device and browser analytics.

        Args:
            params: Date range and filter options. Pass ``None`` to
                use the API default period.

        Returns:
            ``{"analytics": list[DeviceAnalyticsEntry], "usage": AnalyticsUsage}``.
            Entries have ``device_type``, ``browser``, ``os``, and
            ``clicks``, sorted by clicks descending.

        Example:
            >>> result = client.analytics.devices({"days": 30})
            >>> for d in result["analytics"]:
            ...     print(d["browser"], d["clicks"])
        """
        return self._client.get("/analytics/devices", params=dict(params) if params else None)

    def referrers(self, params: Optional["ReferrerAnalyticsParams"] = None) -> "AnalyticsResult":
        """Get referrer analytics (clicks by traffic source).

        Args:
            params: Date range and filter options. Pass ``None`` to
                use the API default period.

        Returns:
            ``{"analytics": list[ReferrerAnalyticsEntry], "usage": AnalyticsUsage}``.
            Entries have ``referrer``, ``clicks``, and
            ``unique_visitors``, sorted by clicks descending.

        Example:
            >>> result = client.analytics.referrers({"days": 7})
            >>> for r in result["analytics"]:
            ...     print(r["referrer"], r["clicks"])
        """
        return self._client.get("/analytics/referrers", params=dict(params) if params else None)

    def hourly(self, params: Optional["HourlyAnalyticsParams"] = None) -> "AnalyticsResult":
        """Get hourly analytics (click distribution by hour of day).

        Returns 24 entries (one per UTC hour) showing the aggregate
        click distribution. Useful for identifying peak traffic hours.

        Args:
            params: Date range and filter options. Pass ``None`` to
                use the API default period.

        Returns:
            ``{"analytics": list[HourlyAnalyticsEntry], "usage": AnalyticsUsage}``.
            24 entries (hours 0-23) with click and unique visitor
            counts.

        Example:
            >>> result = client.analytics.hourly({"days": 30})
            >>> peak = max(result["analytics"], key=lambda h: h["clicks"])
            >>> print(f"Peak hour: {peak['hour']}:00 UTC")
        """
        return self._client.get("/analytics/hourly", params=dict(params) if params else None)
