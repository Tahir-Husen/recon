"""
Optional API keys, read from environment variables so nothing
sensitive gets hardcoded or committed to version control.

    export NUMVERIFY_API_KEY="your_free_tier_key"

Get a free key at https://numverify.com (free tier: ~100 req/month).
Everything else in this tool works with zero API keys.
"""

import os

NUMVERIFY_API_KEY = os.environ.get("NUMVERIFY_API_KEY", "")
