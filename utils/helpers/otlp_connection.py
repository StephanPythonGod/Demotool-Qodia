import logging
import time
from typing import Tuple

import requests


def check_otlp_connection(endpoint: str, max_retries: int = 3) -> Tuple[bool, str]:
    """
    Check OTLP HTTP endpoint connectivity with retries.
    Returns (success: bool, formatted_endpoint: str)
    """
    # Format endpoint
    if not endpoint.startswith(("http://", "https://")):
        endpoint = f"http://{endpoint}"

    # Remove any port from Cloud Run URL and ensure correct path
    base_url = endpoint.split("/")[0] if "/" in endpoint else endpoint
    host = base_url.replace("http://", "").replace("https://", "")
    if ":" in host:
        host = host.split(":")[0]

    # For Cloud Run, use HTTPS
    if "run.app" in host:
        endpoint = f"https://{host}"

    # Add the traces endpoint for testing
    test_endpoint = f"{endpoint}/v1/traces"

    # Retry logic
    retry_delay = 2  # seconds
    for attempt in range(max_retries):
        try:
            response = requests.post(
                test_endpoint,
                json={},
                headers={"Content-Type": "application/json"},
                timeout=10 if attempt == 0 else 5,
            )

            if response.status_code == 200:
                return True, endpoint
            else:
                raise Exception(f"HTTP {response.status_code}: {response.text}")

        except Exception as e:
            if attempt < max_retries - 1:
                logging.warning(
                    f"Failed to connect to OTLP endpoint (attempt {attempt + 1}/{max_retries}): {str(e)}"
                    f" Retrying in {retry_delay} seconds..."
                )
                time.sleep(retry_delay)
            else:
                logging.warning(
                    f"Failed to connect to OTLP endpoint after {max_retries} attempts: {str(e)}",
                    exc_info=True,
                )
                return False, endpoint
