import logging
import os
import requests
from typing import Any, Dict
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


def call_chat_service(
    session_id: str,
    profile_id: str,
    message: str,
    image_file: Any = None,
    audio_file: Any = None,
) -> Dict[str, Any]:
    base_url = os.getenv("BASE_URL")
    if not base_url:
        raise ExternalAPIConfigError("External service BASE_URL is not configured.")

    endpoint = base_url
    payload = {
        "session_id": session_id,
        "profile_id": profile_id,
        "message": message,
    }

    files = {}
    if image_file:
        files["image_data"] = (image_file.name, image_file.read(), image_file.content_type)
    if audio_file:
        files["audio"] = (audio_file.name, audio_file.read(), audio_file.content_type)

    session = _build_session()
    logger.info("Chat external API request started for session_id=%s with files=%s", session_id, list(files.keys()))

    try:
        if files:
            response = session.post(endpoint, data=payload, files=files, timeout=30)
        else:
            response = session.post(endpoint, json=payload, timeout=15)
    except requests.Timeout as exc:
        logger.warning("Chat external API timeout.")
        raise ExternalAPIError("External service timeout.") from exc
    except requests.RequestException as exc:
        logger.warning("Chat external API request failed.")
        raise ExternalAPIError("External service request failed.") from exc

    logger.info("Chat external API response status=%s", response.status_code)

    if response.status_code != 200:
        raise ExternalAPIError("External service returned a non-200 response.")

    try:
        response_json = response.json()
    except ValueError as exc:
        raise ExternalAPIError("External service returned invalid JSON.") from exc

    if isinstance(response_json, list):
        if not response_json:
            raise ExternalAPIError("External service returned empty list.")
        data_dict = response_json[0]
    elif isinstance(response_json, dict):
        data_dict = response_json
    else:
        raise ExternalAPIError("Invalid response type from external service.")

    required = ["status", "ai_response"]
    missing = [field for field in required if field not in data_dict]
    if missing:
        raise ExternalAPIError(
            "External service response missing fields: " + ", ".join(missing)
        )

    return {
        "status": data_dict["status"],
        "ai_response": data_dict["ai_response"],
        "response_type": data_dict.get("response_type", "ai_agent"),
    }
