---
title: Safety Hooks Framework Pattern
type: pattern
domain: [safety, hooks]
created: 2026-03-02
confidence: 95%
source: "claude-code-tools (Deep Dive 2025-12-27)"
---

# Safety Hooks Framework Pattern

**Quelle**: claude-code-tools (Deep Dive 2025-12-27)
**Problem**: Claude Code kann gefährliche Operationen ausführen (rm, git checkout, .env lesen)
**Confidence**: 95% (aus Produktions-Code extrahiert)

---

## Konzept

PreToolUse Hooks die gefährliche Befehle blockieren, warnen oder User-Approval anfordern.

```
Tool Call
    │
    ├── PreToolUse Hook
    │   ├── check_rm_command()
    │   ├── check_git_checkout_command()
    │   ├── check_git_add_command()
    │   ├── check_git_commit_command()
    │   ├── check_env_file_access()
    │   └── check_file_length_limit()
    │
    └── Entscheidung
        ├── "approve" → Tool ausführen
        ├── "ask" → User-Approval anfordern
        └── "block/deny" → Tool blockieren mit Reason
```

---

## Architektur

### Unified Bash Hook (bash_hook.py)

Zentraler Hook der alle Bash-Checks orchestriert:

```python
def main():
    data = json.load(sys.stdin)

    if data.get("tool_name") != "Bash":
        return {"decision": "approve"}

    command = data.get("tool_input", {}).get("command", "")

    # Alle Checks ausführen
    checks = [
        check_rm_command,
        check_git_add_command,
        check_git_checkout_command,
        check_git_commit_command,
        check_env_file_access,
    ]

    block_reasons = []
    ask_reasons = []

    for check_func in checks:
        decision, reason = check_func(command)
        if decision == "block":
            block_reasons.append(reason)
        elif decision == "ask":
            ask_reasons.append(reason)

    # Priorität: block > ask > allow
    if block_reasons:
        return {"decision": "deny", "reason": combined_reason}
    elif ask_reasons:
        return {"decision": "ask", "reason": combined_reason}
    else:
        return {"decision": "approve"}
```

### hooks.json Konfiguration

```json
{
  "description": "Safety hooks to block or require approval",
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [{
          "type": "command",
          "command": "python3 hooks/bash_hook.py",
          "timeout": 10
        }]
      },
      {
        "matcher": "Edit",
        "hooks": [{
          "type": "command",
          "command": "python3 hooks/file_length_limit_hook.py",
          "timeout": 10
        }]
      },
      {
        "matcher": "Write",
        "hooks": [{
          "type": "command",
          "command": "python3 hooks/file_length_limit_hook.py",
          "timeout": 10
        }]
      }
    ]
  }
}
```

---

## Die 7 Safety Hooks

### 1. rm_block_hook.py

**Zweck**: Blockiert `rm` Befehle, empfiehlt TRASH-Ordner statt löschen

```python
def check_rm_command(command):
    """
    Patterns die gematched werden:
    - rm ...
    - /bin/rm ...
    - command && rm ...
    """
    if re.search(r'(^|[;&|]\s*)(/\S*/)?rm\b', normalized_cmd):
        reason = (
            "Instead of using 'rm':\n"
            "- MOVE files to TRASH directory\n"
            "- Add entry to TRASH-FILES.md with reason"
        )
        return True, reason
    return False, None
```

**Alternative**: Dateien in TRASH/ verschieben + TRASH-FILES.md dokumentieren

---

### 2. env_file_protection_hook.py

**Zweck**: Schützt .env Dateien vor Lesen/Schreiben

```python
env_patterns = [
    # Reading
    r'\bcat\s+.*\.env\b',
    r'\bless\s+.*\.env\b',
    r'\bhead\s+.*\.env\b',
    r'\btail\s+.*\.env\b',

    # Editors
    r'\bnano\s+.*\.env\b',
    r'\bvi\s+.*\.env\b',
    r'\bvim\s+.*\.env\b',
    r'\bcode\s+.*\.env\b',

    # Writing
    r'>\s*\.env\b',
    r'>>\s*\.env\b',
    r'\bsed\s+.*-i.*\.env\b',
    r'\bcp\s+.*\.env\b',
    r'\bmv\s+.*\.env\b',

    # Searching
    r'\bgrep\s+.*\.env\b',
    r'\brg\s+.*\.env\b',
    r'\bfind\s+.*-name\s+["\']?\.env',
]
```

**Empfehlung**: `env-safe` CLI Tool stattdessen:
- `env-safe list` - Keys auflisten (ohne Values!)
- `env-safe check KEY` - Prüfen ob Key existiert
- `env-safe validate` - Syntax prüfen

---

### 3. git_checkout_safety_hook.py

**Zweck**: Warnt bei uncommitted changes, blockiert gefährliche Checkouts

```python
# IMMER blockieren:
dangerous_patterns = [
    (r'\bgit\s+checkout\s+(-f|--force)\b',
     "FORCES checkout and DISCARDS all uncommitted changes!"),
    (r'\bgit\s+checkout\s+\.',
     "Will DISCARD ALL changes in current directory!"),
    (r'\bgit\s+checkout\s+.*\s+--\s+\.',
     "Will DISCARD ALL changes!"),
]

# Bei uncommitted changes: Warnung + Alternativen
if has_changes:
    warning = f"WARNING: {num_changes} uncommitted change(s)!"
    warning += "\nOptions:"
    warning += "\n1. git stash"
    warning += "\n2. git commit -am 'message'"
    warning += "\n3. git restore <files>"
    warning += "\n4. git switch (safer)"
    return True, warning
```

**Schlüssel-Feature**: Führt `git status --porcelain` aus um tatsächlichen Status zu prüfen!

---

### 4. git_add_block_hook.py

**Zweck**: Warnt bei problematischen git add Operationen

```python
# Beispiele die geprüft werden:
# - git add . (alles hinzufügen)
# - git add -A (alles inkl. deletions)
# - git add *.log (sensitive files)
```

---

### 5. git_commit_block_hook.py

**Zweck**: Prüft Commit-Operationen

```python
# Beispiele:
# - Commit ohne Message
# - Commit mit sensitive Dateien im Staging
# - Force-Commits
```

---

### 6. file_length_limit_hook.py

**Zweck**: Verhindert zu große Source-Dateien (> 10.000 Zeilen)

```python
MAX_FILE_LINES = 10000

SOURCE_CODE_EXTENSIONS = {
    '.py', '.tsx', '.ts', '.jsx', '.js',
    '.rs', '.c', '.cpp', '.go', '.java',
    '.kt', '.swift', '.rb', '.php', '.cs'
}

def check_file_length_limit(data):
    tool_name = data.get("tool_name")  # Edit oder Write

    # Berechne resultierende Zeilenzahl
    if tool_name == "Write":
        lines = count_lines(tool_input.get("content", ""))
    elif tool_name == "Edit":
        # Simuliere Edit und zähle Zeilen
        lines = calculate_edit_result_lines(...)

    if lines > MAX_FILE_LINES:
        # Speed Bump Pattern: Erstes Mal blockieren, zweites Mal erlauben
        if not flag_file.exists():
            flag_file.touch()
            return block_with_refactoring_suggestion()
        else:
            flag_file.unlink()
            return allow()
```

**Speed Bump Pattern**:
1. Erster Versuch: Blockieren + Warnung + Flag-File erstellen
2. Zweiter Versuch: Flag-File existiert → Erlauben + Flag löschen

---

### 7. session_resume_hook.py (UserPromptSubmit)

**Zweck**: Ermöglicht Session-Handoff via Trigger-Wort

```python
TRIGGERS = (">resume", ">continue", ">handoff")

def main():
    if prompt.startswith(">resume"):
        # Session ID in Clipboard kopieren
        copy_to_clipboard(session_id)

        # Prompt blockieren mit Anweisungen
        return {
            "decision": "block",
            "reason": (
                "Session ID copied to clipboard!\n\n"
                "To continue:\n"
                "1. Quit Claude (Ctrl+D twice)\n"
                "2. Start new session and paste ID"
            )
        }
```

**Event**: UserPromptSubmit (nicht PreToolUse!)

---

## Decision Types

| Decision | Verhalten | Use Case |
|----------|-----------|----------|
| `approve` | Tool wird ausgeführt | Sicherer Befehl |
| `ask` | User-Prompt erscheint | Potenziell gefährlich |
| `block`/`deny` | Tool wird blockiert | Definitiv gefährlich |

---

## Hook Output Format

### Für PreToolUse

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "Detailed reason..."
  }
}
```

### Für UserPromptSubmit

```json
{
  "decision": "block",
  "reason": "Message to show user..."
}
```

---

## Fehlerbehandlung

```python
try:
    # Hook-Logik
except Exception as e:
    # Bei Fehler: IMMER approve um Claude nicht zu brechen!
    print(json.dumps({
        "decision": "approve",
        "error": str(e)
    }))
```

**Wichtig**: Hooks dürfen niemals Claude Code crashen - im Zweifel approve!

---

## Recommended Setup

### Directory Structure

```bash
hooks/
├── hooks.json
├── bash_hook.py        # Unified Bash Hook
├── rm_block_hook.py
├── env_protection.py
├── git_safety.py
└── file_length.py
```

### Customization Tips

1. **TRASH-Pattern adoptieren**: Statt rm → mv zu TRASH/ + TRASH-FILES.md
2. **env-safe Alternative**: Oder .env komplett aus Claude Code Zugriff ausschließen
3. **File Length**: Passe MAX_FILE_LINES an Projektgröße an (1.000-10.000)

---

## Best Practices

1. **Fail-Safe**: Bei Fehlern immer `approve` zurückgeben
2. **Timeout**: 10 Sekunden Maximum pro Hook
3. **Helpful Messages**: Nicht nur blockieren, sondern Alternativen anbieten
4. **Speed Bump**: Bei nicht-kritischen Warnungen zweite Chance geben
5. **Compound Commands**: `cd x && git checkout` - alle Subcommands prüfen!

---

## Related

- [Reflection Pattern](reflection-pattern.md) - For iterative quality improvement
- [Progressive Disclosure Pattern](progressive-disclosure-pattern.md) - For layered security configuration
