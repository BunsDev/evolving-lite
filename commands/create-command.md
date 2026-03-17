---
description: Create a new custom slash command
argument-hint: [command-name]
---

Create a new slash command for your Evolving Lite installation.

## Input: $ARGUMENTS

If empty: "What should the command be called? (kebab-case, e.g., 'run-tests')"

## Process

1. **Name**: Validate kebab-case, check for conflicts with existing commands
2. **Purpose**: Ask what the command should do
3. **Arguments**: Does it take arguments? (argument-hint in frontmatter)
4. **Write template**:

```markdown
---
description: {one-line description}
argument-hint: {hint for arguments, or remove if none}
---

{Command instructions here}

## Input: $ARGUMENTS

{How to handle input}

## Process

{Step-by-step instructions for Claude}

## Output

{Expected output format}
```

5. **Save to**: `${CLAUDE_PLUGIN_ROOT}/commands/{name}.md`
6. **Confirm**: "Created /{{name}}. Available in your next message."

## Notes

- Commands are Markdown files with YAML frontmatter
- They are auto-discovered by Claude Code's plugin system
- The `description` field appears in autocomplete
- `$ARGUMENTS` receives everything after the command name
