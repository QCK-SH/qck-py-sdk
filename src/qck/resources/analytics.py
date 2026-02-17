"""Query click analytics through the QCK API."""

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
    """Query analytics summaries and timeseries data."""

    def __init__(self, client: "HttpClient") -> None:
        self._client = client

    def summary(self, params: Optional["AnalyticsSummaryParams"] = None) -> "AnalyticsSummary":
        return self._client.get("/analytics/summary", params=dict(params) if params else None)

    def timeseries(self, params: Optional["TimeseriesParams"] = None) -> List["TimeseriesPoint"]:
        return self._client.get("/analytics/timeseries", params=dict(params) if params else None)

    def geo(self, params: Optional["GeoAnalyticsParams"] = None) -> List["GeoAnalyticsEntry"]:
        """Get geographic analytics (clicks by country)."""
        return self._client.get("/analytics/geo", params=dict(params) if params else None)

    def devices(self, params: Optional["DeviceAnalyticsParams"] = None) -> List["DeviceAnalyticsEntry"]:
        """Get device/browser analytics."""
        return self._client.get("/analytics/devices", params=dict(params) if params else None)

    def referrers(self, params: Optional["ReferrerAnalyticsParams"] = None) -> List["ReferrerAnalyticsEntry"]:
        """Get referrer analytics (clicks by traffic source)."""
        return self._client.get("/analytics/referrers", params=dict(params) if params else None)

    def hourly(self, params: Optional["HourlyAnalyticsParams"] = None) -> List["HourlyAnalyticsEntry"]:
        """Get hourly analytics (click distribution by hour of day)."""
        return self._client.get("/analytics/hourly", params=dict(params) if params else None)
