"""
Rate limiter for Google API calls.

Tracks API requests and enforces rate limits to prevent quota exhaustion.
"""

import logging
import time
from collections import deque
from datetime import datetime
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Rate limiter that tracks API calls and enforces limits.

    Limits:
    - Maximum 10 API requests per minute per project
    - Maximum 4 videos returned per request
    """

    def __init__(
        self,
        max_requests_per_minute: int = 10,
        window_seconds: int = 60,
        state_file: Optional[str] = None,
    ):
        """
        Initialize rate limiter.

        Args:
            max_requests_per_minute: Maximum requests allowed per minute (default: 10)
            window_seconds: Time window in seconds (default: 60)
            state_file: Optional file to persist state across runs
        """
        self.max_requests = max_requests_per_minute
        self.window_seconds = window_seconds
        self.state_file = Path(state_file) if state_file else Path(".rate_limit_state")

        # Track request timestamps in a sliding window
        self.request_times = deque()

        # Load previous state if exists
        self._load_state()

        logger.info(f"RateLimiter initialized: {max_requests_per_minute} requests per {window_seconds}s")

    def _load_state(self):
        """Load previous request history from state file."""
        if self.state_file.exists():
            try:
                with open(self.state_file, "r") as f:
                    for line in f:
                        timestamp = float(line.strip())
                        # Only keep recent requests within the window
                        if time.time() - timestamp < self.window_seconds:
                            self.request_times.append(timestamp)
                logger.debug(f"Loaded {len(self.request_times)} recent requests from state file")
            except Exception as e:
                logger.warning(f"Failed to load rate limit state: {e}")

    def _save_state(self):
        """Save current request history to state file."""
        try:
            with open(self.state_file, "w") as f:
                for timestamp in self.request_times:
                    f.write(f"{timestamp}\n")
        except Exception as e:
            logger.warning(f"Failed to save rate limit state: {e}")

    def _cleanup_old_requests(self):
        """Remove requests outside the current time window."""
        current_time = time.time()
        cutoff_time = current_time - self.window_seconds

        # Remove old requests from the left of the deque
        while self.request_times and self.request_times[0] < cutoff_time:
            self.request_times.popleft()

    def get_current_count(self) -> int:
        """
        Get number of requests in current time window.

        Returns:
            Number of requests in the current window
        """
        self._cleanup_old_requests()
        return len(self.request_times)

    def get_time_until_available(self) -> float:
        """
        Get seconds until a request slot becomes available.

        Returns:
            Seconds to wait (0 if slot is available now)
        """
        self._cleanup_old_requests()

        if len(self.request_times) < self.max_requests:
            return 0.0

        # Calculate when the oldest request will expire
        oldest_request = self.request_times[0]
        time_until_expire = (oldest_request + self.window_seconds) - time.time()

        return max(0.0, time_until_expire)

    def can_make_request(self) -> bool:
        """
        Check if a request can be made now.

        Returns:
            True if request can be made without exceeding limits
        """
        return self.get_time_until_available() == 0.0

    def wait_if_needed(self, operation_name: str = "API call"):
        """
        Wait if necessary to respect rate limits.

        Args:
            operation_name: Name of the operation for logging
        """
        wait_time = self.get_time_until_available()

        if wait_time > 0:
            current_count = self.get_current_count()
            logger.info(
                f"Rate limit: {current_count}/{self.max_requests} requests used. "
                f"Waiting {wait_time:.1f}s before {operation_name}..."
            )
            time.sleep(wait_time + 0.1)  # Add small buffer

    def record_request(self, operation_name: str = "API call"):
        """
        Record that a request was made.

        Args:
            operation_name: Name of the operation for logging
        """
        self.wait_if_needed(operation_name)

        current_time = time.time()
        self.request_times.append(current_time)
        self._save_state()

        current_count = self.get_current_count()
        logger.debug(
            f"Request recorded for '{operation_name}': " f"{current_count}/{self.max_requests} in current window"
        )

    def get_status(self) -> dict:
        """
        Get current rate limiter status.

        Returns:
            Dictionary with status information
        """
        self._cleanup_old_requests()

        return {
            "current_requests": len(self.request_times),
            "max_requests": self.max_requests,
            "window_seconds": self.window_seconds,
            "requests_available": self.max_requests - len(self.request_times),
            "wait_time_seconds": self.get_time_until_available(),
            "can_make_request": self.can_make_request(),
        }

    def reset(self):
        """Clear all request history."""
        self.request_times.clear()
        self._save_state()
        logger.info("Rate limiter reset")


# Global rate limiter instance (shared across all API clients)
_global_rate_limiter = None


def get_rate_limiter() -> RateLimiter:
    """
    Get the global rate limiter instance.

    Returns:
        Shared RateLimiter instance
    """
    global _global_rate_limiter
    if _global_rate_limiter is None:
        _global_rate_limiter = RateLimiter(
            max_requests_per_minute=10, window_seconds=60, state_file=".google_api_rate_limit"
        )
    return _global_rate_limiter
