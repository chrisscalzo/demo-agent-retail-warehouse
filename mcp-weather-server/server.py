from datetime import datetime, timezone
from functools import lru_cache
import json
import logging
import time
from typing import Any, Dict, List

import requests
from mcp.server.fastmcp import FastMCP
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


mcp = FastMCP(
    "warehouse-weather",
    host="0.0.0.0",
    port=8080,
    stateless_http=True,
    json_response=True,
    streamable_http_path="/mcp/",
)

logging.basicConfig(level=logging.INFO, format="%(message)s")
LOGGER = logging.getLogger("warehouse-weather")

GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
DEFAULT_TIMEOUT_SECONDS = 25


def _build_session() -> requests.Session:
    retry = Retry(
        total=4,
        connect=4,
        read=4,
        status=4,
        backoff_factor=0.6,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session = requests.Session()
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


SESSION = _build_session()


def _log_event(event: str, **fields: Any) -> None:
    payload = {
        "event": event,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        **fields,
    }
    LOGGER.info(json.dumps(payload, ensure_ascii=True, default=str))


def _get_json(url: str, params: Dict[str, Any], operation: str) -> Dict[str, Any]:
    started = time.perf_counter()
    try:
        response = SESSION.get(url, params=params, timeout=DEFAULT_TIMEOUT_SECONDS)
        response.raise_for_status()
        _log_event(
            "provider_request_succeeded",
            operation=operation,
            url=url,
            status_code=response.status_code,
            elapsed_ms=round((time.perf_counter() - started) * 1000, 1),
        )
        return response.json()
    except requests.RequestException as exc:
        _log_event(
            "provider_request_failed",
            operation=operation,
            url=url,
            elapsed_ms=round((time.perf_counter() - started) * 1000, 1),
            error_type=type(exc).__name__,
            error=str(exc),
        )
        raise RuntimeError(
            f"{operation} failed because the weather provider timed out or was unavailable. Please retry in a moment."
        ) from exc


@lru_cache(maxsize=128)
def _geocode(location: str) -> Dict[str, Any]:
    clean_location = location.strip()
    query_candidates = [clean_location]
    if "," in clean_location:
        city_only = clean_location.split(",", 1)[0].strip()
        if city_only and city_only not in query_candidates:
            query_candidates.append(city_only)

    top: Dict[str, Any] | None = None
    for query in query_candidates:
        payload = _get_json(
            GEOCODE_URL,
            params={"name": query, "count": 1, "language": "en", "format": "json"},
            operation="Geocoding request",
        )
        results: List[Dict[str, Any]] = payload.get("results", [])
        if results:
            top = results[0]
            break

    if not top:
        raise ValueError(f"No location match found for '{clean_location}'.")

    return {
        "name": top.get("name"),
        "admin1": top.get("admin1"),
        "country": top.get("country"),
        "latitude": top.get("latitude"),
        "longitude": top.get("longitude"),
        "timezone": top.get("timezone"),
    }


@mcp.tool()
def get_current_weather(location: str) -> Dict[str, Any]:
    """Get current weather for a city, ZIP, or place name."""
    started = time.perf_counter()
    _log_event("tool_call_started", tool="get_current_weather", location=location)
    try:
        place = _geocode(location)
        payload = _get_json(
            FORECAST_URL,
            params={
                "latitude": place["latitude"],
                "longitude": place["longitude"],
                "current": ["temperature_2m", "relative_humidity_2m", "wind_speed_10m", "weather_code"],
                "temperature_unit": "fahrenheit",
                "wind_speed_unit": "mph",
                "precipitation_unit": "inch",
                "timezone": "auto",
            },
            operation="Current weather request",
        )

        result = {
            "location": place,
            "observed_at_utc": datetime.now(timezone.utc).isoformat(),
            "current": payload.get("current", {}),
            "source": "Open-Meteo (no-auth)",
        }
        _log_event(
            "tool_call_succeeded",
            tool="get_current_weather",
            location=location,
            resolved_location=result["location"].get("name"),
            elapsed_ms=round((time.perf_counter() - started) * 1000, 1),
        )
        return result
    except Exception as exc:
        _log_event(
            "tool_call_failed",
            tool="get_current_weather",
            location=location,
            elapsed_ms=round((time.perf_counter() - started) * 1000, 1),
            error_type=type(exc).__name__,
            error=str(exc),
        )
        raise


@mcp.tool()
def get_daily_forecast(location: str, days: int = 3) -> Dict[str, Any]:
    """Get a multi-day weather forecast for a city, ZIP, or place name (1-7 days)."""
    started = time.perf_counter()
    _log_event("tool_call_started", tool="get_daily_forecast", location=location, requested_days=days)
    try:
        safe_days = max(1, min(days, 7))
        place = _geocode(location)

        payload = _get_json(
            FORECAST_URL,
            params={
                "latitude": place["latitude"],
                "longitude": place["longitude"],
                "daily": [
                    "weather_code",
                    "temperature_2m_max",
                    "temperature_2m_min",
                    "precipitation_probability_max",
                    "uv_index_max",
                ],
                "temperature_unit": "fahrenheit",
                "precipitation_unit": "inch",
                "forecast_days": safe_days,
                "timezone": "auto",
            },
            operation="Daily forecast request",
        )

        result = {
            "location": place,
            "days": safe_days,
            "daily": payload.get("daily", {}),
            "source": "Open-Meteo (no-auth)",
        }
        _log_event(
            "tool_call_succeeded",
            tool="get_daily_forecast",
            location=location,
            requested_days=days,
            days=safe_days,
            resolved_location=result["location"].get("name"),
            elapsed_ms=round((time.perf_counter() - started) * 1000, 1),
        )
        return result
    except Exception as exc:
        _log_event(
            "tool_call_failed",
            tool="get_daily_forecast",
            location=location,
            requested_days=days,
            elapsed_ms=round((time.perf_counter() - started) * 1000, 1),
            error_type=type(exc).__name__,
            error=str(exc),
        )
        raise


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
