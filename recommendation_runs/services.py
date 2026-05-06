import logging
import os
from typing import Any, Dict

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class ExternalAPIError(Exception):
    pass


class ExternalAPIConfigError(Exception):
    pass


def _build_session() -> requests.Session:
    retry = Retry(
        total=2,
        connect=2,
        read=2,
        backoff_factor=0.5,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("POST",),
    )
    adapter = HTTPAdapter(max_retries=retry)
    session = requests.Session()
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def call_recommendations_service(
    user_profile: Dict[str, Any], context: Dict[str, Any]
) -> Dict[str, Any]:
    base_url = os.getenv("BASE_URL")
    if not base_url:
        raise ExternalAPIConfigError("External service BASE_URL is not configured.")

    normalized_base = base_url.rstrip("/")
    if normalized_base.endswith("/recommendations"):
        endpoint = normalized_base
    else:
        endpoint = f"{normalized_base}/recommendations"

    payload = {
        "user_profile": user_profile,
        "context": context,
    }

    session = _build_session()
    logger.info("Recommendations external API request started.")

    try:
        response = session.post(endpoint, json=payload, timeout=10)
    except requests.Timeout as exc:
        logger.warning("Recommendations external API timeout.")
        raise ExternalAPIError("External service timeout.") from exc
    except requests.RequestException as exc:
        logger.warning("Recommendations external API request failed.")
        raise ExternalAPIError("External service request failed.") from exc

    logger.info("Recommendations external API response status=%s", response.status_code)

    if response.status_code != 200:
        raise ExternalAPIError("External service returned a non-200 response.")

    try:
        response_json = response.json()
    except ValueError as exc:
        raise ExternalAPIError("External service returned invalid JSON.") from exc

    payload_data = response_json.get("data")
    if not isinstance(payload_data, dict):
        raise ExternalAPIError("Invalid response structure: missing data.")

    required_fields = [
        "recommendations",
        "summary",
        "metadata",
    ]
    missing = [field for field in required_fields if field not in payload_data]
    if missing:
        raise ExternalAPIError(
            "External service response missing fields: " + ", ".join(missing)
        )

    result = {
        "message": response_json.get("message", "Recommendations generated successfully"),
        "context_used": payload_data.get("context_used"),
        "recommendations": payload_data["recommendations"],
        "summary": payload_data["summary"],
        "metadata": payload_data["metadata"],
    }

    logger.info("Recommendations external API response parsed.")
    return result
