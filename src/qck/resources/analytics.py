"""Query click analytics through the QCK API.

Provides the :class:`AnalyticsResource` class for retrieving click
analytics data including summaries, timeseries, geographic breakdowns,
device/browser stats, referrer sources, and hourly distributions.

Example::

    from qck import QCK

    client = QCK(api_key="qck_...")
    summary = client.analytics.summary({"days": 30})
    print(f"Total clicks: {summary['total_clicks']}")
"""

from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from .._client import HttpClient
    from .._types import (
        AnalyticsSummary,
        AnalyticsSummaryParams,
        DeviceAnalyticsEntry,
        DeviceAnalyticsParams,
        GeoAnalyticsEntry,
        GeoAnalyticsParams,
        HourlyAnalyticsEntry,
        HourlyAnalyticsParams,
        ReferrerAnalyticsEntry,
        ReferrerAnalyticsParams,
        TimeseriesParams,
        TimeseriesPoint,
    )


class AnalyticsResource:
    """Query analytics summaries and timeseries data.

    Access via ``client.analytics``. Provides read-only access to
    click analytics data aggregated across all links or filtered by
    domain.

    Attributes:
        _client: The underlying HTTP client used for API calls.
    """

    def __init__(self, client: "HttpClient") -> None:
        """Initialise the analytics resource.

        Args:
            client: HTTP client instance for making API requests.
        """
        self._client = client

    def summary(self, params: Optional["AnalyticsSummaryParams"] = None) -> "AnalyticsSummary":
        """Get an aggregated analytics summary.

        Returns high-level metrics such as total clicks, unique
        visitors, and active links for the given time period.

        Args:
            params: Date range and filter options. Pass ``None`` to
                use the API default period.

        Returns:
            An analytics summary with aggregate metrics.

        Example:
            >>> summary = client.analytics.summary({"days": 7})
            >>> print(summary["total_clicks"])
        """
        return self._client.get("/analytics/summary", params=dict(params) if params else None)

    def timeseries(self, params: Optional["TimeseriesParams"] = None) -> List["TimeseriesPoint"]:
        """Get click timeseries data.

        Returns a list of time-bucketed data points with click counts
        and unique visitor counts, suitable for charting.

        Args:
            params: Date range and filter options. Pass ``None`` to
                use the API default period.

        Returns:
            List of timeseries data points ordered chronologically.

        Example:
            >>> points = client.analytics.timeseries({"days": 30})
            >>> for p in points:
            ...     print(p["timestamp"], p["clicks"])
        """
        return self._client.get("/analytics/timeseries", params=dict(params) if params else None)

    def geo(self, params: Optional["GeoAnalyticsParams"] = None) -> List["GeoAnalyticsEntry"]:
        """Get geographic analytics (clicks by country).

        Args:
            params: Date range and filter options. Pass ``None`` to
                use the API default period.

        Returns:
            List of entries with country, click count, and unique
            visitor count, sorted by clicks descending.

        Example:
            >>> countries = client.analytics.geo({"days": 30})
            >>> for c in countries:
            ...     print(c["country"], c["clicks"])
        """
        return self._client.get("/analytics/geo", params=dict(params) if params else None)

    def devices(self, params: Optional["DeviceAnalyticsParams"] = None) -> List["DeviceAnalyticsEntry"]:
        """Get device and browser analytics.

        Args:
            params: Date range and filter options. Pass ``None`` to
                use the API default period.

        Returns:
            List of entries with device type, browser, OS, and click
            count, sorted by clicks descending.

        Example:
            >>> devices = client.analytics.devices({"days": 30})
            >>> for d in devices:
            ...     print(d["browser"], d["clicks"])
        """
        return self._client.get("/analytics/devices", params=dict(params) if params else None)

    def referrers(self, params: Optional["ReferrerAnalyticsParams"] = None) -> List["ReferrerAnalyticsEntry"]:
        """Get referrer analytics (clicks by traffic source).

        Args:
            params: Date range and filter options. Pass ``None`` to
                use the API default period.

        Returns:
            List of entries with referrer domain, click count, and
            unique visitor count, sorted by clicks descending.

        Example:
            >>> refs = client.analytics.referrers({"days": 7})
            >>> for r in refs:
            ...     print(r["referrer"], r["clicks"])
        """
        return self._client.get("/analytics/referrers", params=dict(params) if params else None)

    def hourly(self, params: Optional["HourlyAnalyticsParams"] = None) -> List["HourlyAnalyticsEntry"]:
        """Get hourly analytics (click distribution by hour of day).

        Returns 24 entries (one per UTC hour) showing the aggregate
        click distribution. Useful for identifying peak traffic hours.

        Args:
            params: Date range and filter options. Pass ``None`` to
                use the API default period.

        Returns:
            List of 24 entries (hours 0-23) with click and unique
            visitor counts.

        Example:
            >>> hourly = client.analytics.hourly({"days": 30})
            >>> peak = max(hourly, key=lambda h: h["clicks"])
            >>> print(f"Peak hour: {peak['hour']}:00 UTC")
        """
        return self._client.get("/analytics/hourly", params=dict(params) if params else None)
