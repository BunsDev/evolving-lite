---
description: Check for updates and update Evolving Lite
---

Check if a new version of Evolving Lite is available and update.

## Process

1. **Check git status**:
   ```bash
   git -C ${CLAUDE_PLUGIN_ROOT} fetch origin main 2>/dev/null
   ```

2. **Compare versions**:
   ```bash
   LOCAL=$(git -C ${CLAUDE_PLUGIN_ROOT} rev-parse HEAD)
   REMOTE=$(git -C ${CLAUDE_PLUGIN_ROOT} rev-parse origin/main 2>/dev/null)
   ```

3. **If up to date**: "Evolving Lite is up to date (commit: {short_hash})"

4. **If update available**:
   ```
   Update available for Evolving Lite!

   Current: {local_short_hash}
   Latest:  {remote_short_hash}

   Changes:
   {git log --oneline local..remote}

   Update now? This will run: git -C {plugin_root} pull origin main
   ```

5. **After update**: Read `CHANGELOG.md` and show new entries since last version.

## If git is not available

"git is not installed. To update manually, download the latest version from:
https://github.com/primeline-ai/evolving-lite"

## If not a git repo

"This installation is not a git clone. To enable updates, reinstall via:
git clone https://github.com/primeline-ai/evolving-lite ~/.claude-plugins/evolving-lite"
