#!/usr/bin/env python3
"""Check current API rate limit status."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.utils.rate_limiter import get_rate_limiter

rate_limiter = get_rate_limiter()
status = rate_limiter.get_status()

print("=" * 70)
print("📊 Google API Rate Limit Status")
print("=" * 70)
print(f"Current requests in window: {status['current_requests']}/{status['max_requests']}")
print(f"Requests available: {status['requests_available']}")
print(f"Time window: {status['window_seconds']} seconds")
print(f"Wait time before next request: {status['wait_time_seconds']:.1f} seconds")
print(f"Can make request now: {'✅ YES' if status['can_make_request'] else '❌ NO (must wait)'}")
print("=" * 70)

if not status["can_make_request"]:
    print(f"\n⏳ Please wait {status['wait_time_seconds']:.0f} seconds before making another request.")
else:
    print(f"\n✅ You can make {status['requests_available']} more requests right now!")
