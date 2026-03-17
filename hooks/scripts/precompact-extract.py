#!/usr/bin/env python3
"""
Precompact Extract - PreCompact hook for knowledge rescue.
Adapted from Evolving (~150 lines -> ~100 lines).

Before context compaction wipes the conversation, scan the recent
transcript for decisions, solutions, and patterns worth saving.
Creates experience files from extracted knowledge.

Tier 3: Only active from session 10+.
Fail-open: never blocks compaction.

Removed from Evolving version:
- Kairn sync staging (writes directly to experiences)
"""

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "lib"))
from common import (
    write_sentinel, is_tier_active,
    create_experience, read_hook_input
)

# Markers that indicate extractable knowledge
EXTRACTION_PATTERNS = {
    "decision": [
        r"(?:decided|decision|chose|choice|picked|selected)\s+(?:to\s+)?(.{20,120})",
        r"(?:entschieden|entscheidung|gewählt)\s+(.{20,120})",
        r"(?:we(?:'ll| will) (?:use|go with|implement))\s+(.{20,100})",
    ],
    "solution": [
        r"(?:fix(?:ed)?|solved|resolved|solution)\s*(?::|was|is)?\s*(.{20,120})",
        r"(?:the (?:issue|problem|bug) was)\s+(.{20,120})",
        r"(?:root cause)\s*(?::|was|is)?\s*(.{20,120})",
    ],
    "pattern": [
        r"(?:pattern|approach|strategy|technique)\s*(?::|is|was)?\s*(.{20,120})",
        r"(?:always|never|rule of thumb)\s*(?::)?\s*(.{20,120})",
        r"(?:best practice|lesson learned)\s*(?::)?\s*(.{20,120})",
    ],
}


def extract_knowledge(text: str) -> list:
    """Extract knowledge markers from conversation text."""
    findings = []

    for knowledge_type, patterns in EXTRACTION_PATTERNS.items():
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                clean = match.strip().rstrip(".")
                if len(clean) >= 20:
                    findings.append({
                        "type": knowledge_type,
                        "content": clean,
                    })

    # Deduplicate by content similarity
    seen = set()
    unique = []
    for f in findings:
        key = f["content"][:50].lower()
        if key not in seen:
            seen.add(key)
            unique.append(f)

    return unique[:5]  # Max 5 extractions per compaction


def main():
    try:
        # Tier gate
        if not is_tier_active(3):
            write_sentinel("precompact-extract", "skip-tier")
            sys.exit(0)

        hook_input = read_hook_input()

        # The PreCompact hook receives the conversation transcript
        transcript = hook_input.get("transcript", hook_input.get("content", ""))

        if not transcript or len(transcript) < 100:
            write_sentinel("precompact-extract", "skip-short")
            sys.exit(0)

        findings = extract_knowledge(transcript)

        if not findings:
            write_sentinel("precompact-extract", "no-findings")
            sys.exit(0)

        # Save each finding as an experience
        saved = 0
        for finding in findings:
            result = create_experience(
                summary=f"Pre-compaction extract [{finding['type']}]: {finding['content'][:80]}",
                exp_type=finding["type"],
                tags=["precompact", "auto-extracted", finding["type"]],
                solution=finding["content"],
                confidence=0.6,  # Lower confidence for auto-extracted
                source="precompact-extract"
            )
            if result:
                saved += 1

        write_sentinel("precompact-extract", f"saved-{saved}")

    except Exception:
        # Fail-open: NEVER block compaction
        write_sentinel("precompact-extract", "error")

    sys.exit(0)


if __name__ == "__main__":
    main()
