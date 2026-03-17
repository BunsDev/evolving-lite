#!/usr/bin/env python3
"""
Delegation Enforcer - UserPromptSubmit hook.
Adapted from Evolving (1137 lines -> ~250 lines).

Calculates delegation score from user prompt keywords.
If score >= 3, suggests delegation to appropriate agent + model.

Tier 2: Only active from session 3+.

Removed from Evolving version:
- Team detection (lines 583-726)
- Gap tracking (lines 131-237)
- Ambiguous prompt detection (lines 389-435)
- Worktree isolation hints
- Trait fitness lookup
- Stop event handler
- Context persistence across prompts
"""

import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "lib"))
from common import (
    PLUGIN_ROOT, GRAPH_CACHE_DIR, write_sentinel,
    is_tier_active, read_hook_input, safe_read_json
)

MIN_PROMPT_LENGTH = 10
DELEGATION_THRESHOLD = 3

# Inline hints: [hint] or #hint -> task_type
INLINE_HINTS = {
    "explore": "exploration", "exp": "exploration", "find": "exploration",
    "debug": "debugging", "dbg": "debugging",
    "plan": "planning",
    "review": "code_review", "rev": "code_review",
    "sec": "security", "security": "security",
    "fix": "bug_fix", "bugfix": "bug_fix",
    "arch": "architecture", "design": "architecture",
    "research": "research", "learn": "research",
    "doc": "documentation", "docs": "documentation",
    "creative": "creative", "brainstorm": "creative",
}

# Score factors
POSITIVE_KEYWORDS = {
    "exploration": ["find", "search", "where", "grep", "locate", "list all", "show all",
                    "finde", "suche", "wo ist", "zeig alle"],
    "bulk": ["all files", "every", "batch", "bulk", "alle dateien", "jede"],
    "research": ["research", "investigate", "learn about", "deep dive",
                 "recherchiere", "untersuche"],
    "code_review": ["review", "check quality", "audit", "prüfe", "überprüfe"],
    "multi_file": ["across", "multiple files", "codebase", "repo", "projekt"],
    "independent": ["separately", "parallel", "independent", "unabhängig"],
}

CRITICAL_KEYWORDS = [
    "production", "deploy", "payment", "password", "secret",
    "credential", "api key", "delete all", "drop database", "rm -rf",
    "produktion", "passwort", "geheimnis"
]

USER_WANTS_TO_SEE = [
    "show me", "explain", "walk me through", "tell me",
    "zeig mir", "erkläre", "erklär mir"
]

# Destructive patterns - NEVER delegate
DESTRUCTIVE_PATTERNS = [
    r"delete\s+(all|every|.*\*)",
    r"rm\s+-rf",
    r"drop\s+(table|database)",
    r"overwrite\s+(all|every)",
    r"reset\s+--hard",
    r"force\s+push",
    r"truncate",
    r"destroy"
]


def extract_keywords(text: str) -> list:
    """Extract keywords from user prompt."""
    return re.findall(r'\b[\w\u00C0-\u024F]+\b', text.lower())


def extract_inline_hint(text: str) -> str | None:
    """Extract [hint] or #hint from prompt."""
    for pattern in [r'\[(\w+)\]', r'#(\w+)']:
        for match in re.findall(pattern, text.lower()):
            if match in INLINE_HINTS:
                return INLINE_HINTS[match]
    return None


def is_destructive(text: str) -> bool:
    """Check if prompt contains destructive patterns."""
    text_lower = text.lower()
    for pattern in DESTRUCTIVE_PATTERNS:
        if re.search(pattern, text_lower):
            return True
    return False


def calculate_score(text: str, keywords: list) -> tuple:
    """Calculate delegation score. Returns (score, matched_factors)."""
    text_lower = text.lower()
    score = 0
    factors = []

    # Positive factors
    for factor, kw_list in POSITIVE_KEYWORDS.items():
        if any(kw in text_lower for kw in kw_list):
            points = 3 if factor == "exploration" else 2
            score += points
            factors.append(f"+{points} {factor}")

    # Negative factors
    if any(kw in text_lower for kw in CRITICAL_KEYWORDS):
        score -= 10
        factors.append("-10 critical_keyword")

    if any(kw in text_lower for kw in USER_WANTS_TO_SEE):
        score -= 5
        factors.append("-5 user_wants_to_see")

    return score, factors


def determine_routing(text: str, keywords: list, config: dict) -> dict:
    """Determine agent type and model for delegation."""
    text_lower = text.lower()
    task_routing = config.get("task_type_routing", {})

    # Check inline hint first
    hint = extract_inline_hint(text)
    if hint and hint in task_routing:
        routing = task_routing[hint]
        return {"task_type": hint, "model": routing.get("model", "sonnet"),
                "effort": routing.get("effort", "medium"), "source": "inline_hint"}

    # Keyword-based detection
    if any(kw in text_lower for kw in ["find", "search", "grep", "where", "locate", "finde", "suche"]):
        return {"task_type": "exploration", "model": "haiku", "effort": "low", "source": "keyword"}
    if any(kw in text_lower for kw in ["debug", "error", "bug", "crash", "fehler"]):
        return {"task_type": "debugging", "model": "sonnet", "effort": "medium", "source": "keyword"}
    if any(kw in text_lower for kw in ["review", "audit", "quality", "prüfe"]):
        return {"task_type": "code_review", "model": "sonnet", "effort": "medium", "source": "keyword"}
    if any(kw in text_lower for kw in ["research", "investigate", "learn", "recherchiere"]):
        return {"task_type": "research", "model": "sonnet", "effort": "medium", "source": "keyword"}
    if any(kw in text_lower for kw in ["plan", "design", "architect", "struktur"]):
        return {"task_type": "planning", "model": "sonnet", "effort": "medium", "source": "keyword"}

    # Default
    return {"task_type": "general", "model": "sonnet", "effort": "medium", "source": "default"}


def format_delegation_message(score: int, factors: list, routing: dict) -> str:
    """Format the delegation suggestion message."""
    task_type = routing["task_type"]
    model = routing["model"]
    effort = routing["effort"]
    source = routing["source"]

    # Agent type mapping
    agent_map = {
        "exploration": "Explore agent (subagent_type='Explore')",
        "debugging": "debugger agent (subagent_type='debugger')",
        "planning": "Plan agent (subagent_type='Plan')",
    }
    agent_hint = agent_map.get(task_type, f"general-purpose agent (model='{model}')")

    msg = (
        f"DELEGATION SUGGESTED (score: {score}, factors: {', '.join(factors)}). "
        f"Task type: {task_type} ({source}). "
        f"Use: {agent_hint}. "
        f"Effort: {effort}."
    )

    if model == "haiku":
        msg += " Haiku is sufficient and 10x cheaper for this task."

    return msg


def main():
    try:
        # Tier gate
        if not is_tier_active(2):
            write_sentinel("delegation-enforcer", "skip-tier")
            sys.exit(0)

        hook_input = read_hook_input()
        user_input = hook_input.get("content", hook_input.get("message", ""))

        if not user_input or len(user_input) < MIN_PROMPT_LENGTH:
            write_sentinel("delegation-enforcer", "skip-short")
            sys.exit(0)

        # Never delegate destructive operations
        if is_destructive(user_input):
            write_sentinel("delegation-enforcer", "skip-destructive")
            sys.exit(0)

        keywords = extract_keywords(user_input)
        score, factors = calculate_score(user_input, keywords)

        if score < DELEGATION_THRESHOLD:
            write_sentinel("delegation-enforcer", "below-threshold")
            sys.exit(0)

        # Load config for routing
        config = safe_read_json(GRAPH_CACHE_DIR / "delegation-config.json")
        routing = determine_routing(user_input, keywords, config)

        msg = format_delegation_message(score, factors, routing)

        output = {
            "decision": "allow",
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": msg
            }
        }
        print(json.dumps(output))

        write_sentinel("delegation-enforcer", "suggested")

    except Exception:
        write_sentinel("delegation-enforcer", "error")

    sys.exit(0)


if __name__ == "__main__":
    main()
