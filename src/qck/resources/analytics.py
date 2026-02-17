"""Query click analytics through the QCK API."""

from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from .._client import HttpClient
    from .._types import (
        AnalyticsSummary,
        AnalyticsSummaryParams,
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
