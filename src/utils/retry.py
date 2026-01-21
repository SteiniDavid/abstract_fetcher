"""Retry utilities for HTTP requests with exponential backoff."""

import logging
from typing import Callable, TypeVar

import requests
from tenacity import (
    RetryError,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
    wait_fixed,
    before_sleep_log,
)

logger = logging.getLogger(__name__)

T = TypeVar("T")


class RateLimitError(Exception):
    """Raised when rate limit (429) is encountered."""

    def __init__(self, message: str, retry_after: int | None = None):
        super().__init__(message)
        self.retry_after = retry_after


def _is_retryable_exception(exc: BaseException) -> bool:
    """Check if exception is retryable (transient failure)."""
    if isinstance(exc, RateLimitError):
        return True
    if isinstance(exc, requests.Timeout):
        return True
    if isinstance(exc, requests.ConnectionError):
        return True
    if isinstance(exc, requests.HTTPError):
        response = exc.response
        if response is not None:
            # Retry on 429 (rate limit), 500, 502, 503, 504
            return response.status_code in (429, 500, 502, 503, 504)
    return False


def _get_retry_after(response: requests.Response) -> int | None:
    """Extract Retry-After header value in seconds."""
    retry_after = response.headers.get("Retry-After")
    if retry_after:
        try:
            return int(retry_after)
        except ValueError:
            pass
    return None


def retry_on_http_error(
    max_attempts: int = 3,
    min_wait: float = 1.0,
    max_wait: float = 30.0,
    exponential_base: float = 2.0,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator for retrying HTTP requests with exponential backoff.

    Handles transient failures:
    - requests.Timeout
    - requests.ConnectionError
    - requests.HTTPError for status codes 429, 500, 502, 503, 504

    Special handling for 429 (rate limit):
    - Respects Retry-After header if present
    - Falls back to exponential backoff otherwise

    Args:
        max_attempts: Maximum number of retry attempts (default: 3)
        min_wait: Minimum wait time between retries in seconds (default: 1.0)
        max_wait: Maximum wait time between retries in seconds (default: 30.0)
        exponential_base: Base for exponential backoff calculation (default: 2.0)

    Returns:
        Decorated function with retry logic.
    """
    return retry(
        retry=retry_if_exception_type((
            requests.Timeout,
            requests.ConnectionError,
            RateLimitError,
        )) | retry_if_exception_type(requests.HTTPError).func(
            lambda e: e.response is not None and e.response.status_code in (429, 500, 502, 503, 504)
        ),
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(
            multiplier=min_wait,
            max=max_wait,
            exp_base=exponential_base,
        ),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )


def check_rate_limit(response: requests.Response) -> None:
    """Check response for rate limit and raise RateLimitError if applicable.

    Call this after response.raise_for_status() to handle 429 errors specially.

    Args:
        response: The HTTP response to check.

    Raises:
        RateLimitError: If response status is 429 (Too Many Requests).
    """
    if response.status_code == 429:
        retry_after = _get_retry_after(response)
        raise RateLimitError(
            f"Rate limit exceeded. Retry after: {retry_after or 'unknown'} seconds",
            retry_after=retry_after,
        )
