import logging
import os
from typing import Any, Dict

import requests
from django.utils import timezone
from django.utils.dateparse import parse_datetime
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


def _parse_timestamp(value: str, field_name: str):
    if not value:
        raise ExternalAPIError(f"External service missing {field_name}.")
    parsed = parse_datetime(value)
    if parsed is None:
        raise ExternalAPIError(f"External service returned invalid {field_name}.")
    if timezone.is_naive(parsed):
        parsed = timezone.make_aware(parsed, timezone=timezone.utc)
    return parsed


def call_assessment_service(payload: Dict[str, Any]) -> Dict[str, Any]:
    base_url = os.getenv("BASE_URL")
    if not base_url:
        raise ExternalAPIConfigError("External service BASE_URL is not configured.")

    normalized_base = base_url.rstrip("/")
    if normalized_base.endswith("/assessment"):
        endpoint = normalized_base
    else:
        endpoint = f"{normalized_base}/assessment"

    session = _build_session()
    logger.info("Assessment external API request started.")

    try:
        response = session.post(endpoint, json=payload, timeout=10)
    except requests.Timeout as exc:
        logger.warning("Assessment external API timeout.")
        raise ExternalAPIError("External service timeout.") from exc
    except requests.RequestException as exc:
        logger.warning("Assessment external API request failed.")
        raise ExternalAPIError("External service request failed.") from exc

    logger.info("Assessment external API response status=%s", response.status_code)

    if response.status_code != 200:
        raise ExternalAPIError("External service returned a non-200 response.")

    # ✅ FIX 1: Proper JSON parsing
    try:
        response_json = response.json()
    except ValueError as exc:
        raise ExternalAPIError("External service returned invalid JSON.") from exc

    # ✅ FIX 2: Navigate correct structure
    try:
        profile = response_json["data"]["profile"]
    except KeyError as exc:
        raise ExternalAPIError("Invalid response structure: missing data.profile") from exc

    # ✅ FIX 3: Required fields (removed updated_at)
    required_fields = [
        "profile_id",
        "language",
        "version",
        "summary",
        "social",
        "sensory",
        "support",
        "raw_data",
        "metadata",
        "created_at",
    ]

    missing = [field for field in required_fields if field not in profile]
    if missing:
        raise ExternalAPIError(
            "External service response missing fields: " + ", ".join(missing)
        )

    # ✅ FIX 4: Handle timestamps safely
    created_at = _parse_timestamp(profile["created_at"], "created_at")

    # updated_at not provided → fallback strategy
    updated_at_raw = profile.get("updated_at")
    if updated_at_raw:
        updated_at = _parse_timestamp(updated_at_raw, "updated_at")
    else:
        updated_at = created_at  # fallback

    # ✅ Final normalized result
    result = {
        "profile_id": profile["profile_id"],
        "language": profile["language"],
        "version": profile.get("version", "1.0"),
        "summary": profile["summary"],
        "social": profile["social"],
        "sensory": profile["sensory"],
        "support": profile["support"],
        "raw_data": profile["raw_data"],
        "metadata": profile["metadata"],
        "created_at": created_at,
        "updated_at": updated_at,
    }

    logger.info(
        "Assessment external API response parsed for profile_id=%s",
        result["profile_id"],
    )

    return result