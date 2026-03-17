#!/bin/bash
# Evolving Lite - Post-clone setup
# Replaces ${CLAUDE_PLUGIN_ROOT} with actual install path in hooks.json
# Run once after cloning.

set -e

PLUGIN_ROOT="$(cd "$(dirname "$0")" && pwd)"
HOOKS_FILE="${PLUGIN_ROOT}/hooks/hooks.json"

if [[ ! -f "$HOOKS_FILE" ]]; then
  echo "Error: hooks.json not found at ${HOOKS_FILE}"
  exit 1
fi

# Replace placeholder with actual path
sed -i.bak "s|\${CLAUDE_PLUGIN_ROOT}|${PLUGIN_ROOT}|g" "$HOOKS_FILE"
rm -f "${HOOKS_FILE}.bak"

echo "Evolving Lite setup complete."
echo "Plugin root: ${PLUGIN_ROOT}"
echo "Hooks configured with absolute paths."
echo ""
echo "Next: Add to ~/.claude/settings.json:"
echo "  \"pluginDirectories\": [\"${PLUGIN_ROOT}\"]"
