---
description: Create a new custom automation hook
argument-hint: [hook-name]
---

Create a new hook that runs automatically on Claude Code events.

## Input: $ARGUMENTS

If empty: "What should the hook do? Which event should trigger it?"

## Available Events

| Event | When it fires | Common use |
|-------|--------------|-----------|
| SessionStart | Session begins | Init, health checks |
| UserPromptSubmit | User sends a message | Input analysis, routing |
| PreToolUse | Before any tool runs | Validation, security |
| PostToolUse | After any tool runs | Logging, tracking |
| PreCompact | Before context compaction | Save important data |
| Stop | Session ends | Cleanup, summaries |

## Process

1. **Name**: kebab-case (e.g., `my-validator`)
2. **Event**: Which event triggers it
3. **Matcher**: Which tools/patterns (e.g., "Bash" for PreToolUse, ".*" for all)
4. **Language**: Python or Bash
5. **Write script** to `${CLAUDE_PLUGIN_ROOT}/hooks/scripts/{name}.py` or `.sh`
6. **Register** in `${CLAUDE_PLUGIN_ROOT}/hooks/hooks.json`

## Template (Python)

```python
#!/usr/bin/env python3
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "lib"))
from common import PLUGIN_ROOT, write_sentinel, read_hook_input

def main():
    hook_input = read_hook_input()
    # Your logic here
    write_sentinel("{name}", "ok")
    sys.exit(0)

if __name__ == "__main__":
    main()
```

## Important

- Every hook MUST call `write_sentinel()` for health monitoring
- Keep hooks under 200ms to avoid perceptible lag
- Use `sys.exit(0)` for success, `sys.exit(2)` to block a tool call
- Read input from stdin (JSON from Claude Code)
