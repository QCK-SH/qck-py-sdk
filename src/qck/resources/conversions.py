"""Track and query conversion analytics through the QCK API."""

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
        TrackConversionParams,
    )


class ConversionsResource:
    """Track conversion events and query conversion analytics."""

    def __init__(self, client: "HttpClient") -> None:
        self._client = client

    def track(self, params: "TrackConversionParams") -> None:
        """Track a conversion event by ingesting it as a journey event.

        Use this from server-side code, mobile apps, or any HTTP client.
        For browser-side tracking, use the qck-tracker.js snippet instead.
        """
        event_data: Dict[str, Any] = {
            **(params.get("event_data") or {}),
            "name": params["name"],
            "revenue": str(params.get("revenue", 0)),
            "currency": params.get("currency", "USD"),
            "event_type_override": "conversion",
        }

        event = {
            "link_id": params["link_id"],
            "visitor_id": params["visitor_id"],
            "session_id": params.get("session_id", ""),
            "event_type": "custom",
            "event_name": params["name"],
            "page_url": params.get("page_url", ""),
            "event_data": event_data,
        }

        self._client.post("/journey/events", {"events": [event]})

    def summary(
        self, params: Optional["ConversionScopeParams"] = None
    ) -> "ConversionSummary":
        return self._client.get(
            "/conversions/summary", params=dict(params) if params else None
        )

    def timeseries(
        self, params: Optional["ConversionTimeseriesParams"] = None
    ) -> List["ConversionTimeseriesPoint"]:
        return self._client.get(
            "/conversions/timeseries", params=dict(params) if params else None
        )

    def breakdown(
        self, params: "ConversionBreakdownParams"
    ) -> List["ConversionBreakdownEntry"]:
        return self._client.get("/conversions/breakdown", params=dict(params))
