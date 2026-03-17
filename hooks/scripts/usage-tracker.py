#!/usr/bin/env python3
"""
Usage Tracker - PostToolUse hook.
Adapted from Evolving. Simplified: no buffer, no analyzer trigger, no hash session ID.

Tracks tool usage counts (aggregated in usage.json).
Session counter is managed by health-sentinel.sh (SessionStart) only.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "lib"))
from common import (
    PLUGIN_ROOT, ANALYTICS_DIR, write_sentinel,
    safe_read_json, safe_write_json
)


def main():
    # Read hook input
    try:
        hook_input = json.loads(sys.stdin.read()) if not sys.stdin.isatty() else {}
    except (json.JSONDecodeError, OSError):
        hook_input = {}

    tool_name = hook_input.get("tool_name", "unknown")

    # Ensure analytics dir exists
    ANALYTICS_DIR.mkdir(parents=True, exist_ok=True)

    # Update aggregated usage counts
    usage_file = ANALYTICS_DIR / "usage.json"
    usage = safe_read_json(usage_file, {
        "total_calls": 0,
        "tools": {},
        "sessions": 0,
        "first_seen": datetime.now().isoformat(),
        "last_updated": None
    })

    usage["total_calls"] = usage.get("total_calls", 0) + 1
    usage["last_updated"] = datetime.now().isoformat()

    tools = usage.get("tools", {})
    tools[tool_name] = tools.get(tool_name, 0) + 1
    usage["tools"] = tools

    safe_write_json(usage_file, usage)

    write_sentinel("usage-tracker", "ok")
    sys.exit(0)


if __name__ == "__main__":
    main()
