#!/bin/bash
# An advisory hook for the Write tool (PostToolUse): when a new file is created
# where a generator or a tool should have created it, it adds a reminder that
# names the command. It never blocks: it always exits 0, and every error is
# swallowed, so that a broken hook cannot stop work. It needs only bash, cat and
# sed. The messages hold no double quote, so no JSON escaping is needed.
trap 'exit 0' ERR EXIT
input="$(cat 2>/dev/null)"
file="$(printf '%s' "$input" | sed -n 's/.*"file_path"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -n 1)"
message=""
case "$file" in
*/docs/adr/README.md) message="docs/adr/README.md is generated: run 'mise run generate'." ;;
*/docs/adr/*.md) message="A decision record is made with 'adrs new', not by writing the file: use 'adrs new <title>', then 'mise run adr:check' (`anima-repository-conventions`)." ;;
*/skills/README.md | */.claude/skills/* | */.claude/rules/* | */.claude/agents/* | */docs/catalog.md) message="This file is generated from its neutral source: run 'mise run generate' instead of writing it." ;;
*/docs/postmortems/TEMPLATE.md) ;;
*/docs/postmortems/*.md) message="Start a postmortem from docs/postmortems/TEMPLATE.md and close it with a guard that exists (PM ids are not reused)." ;;
*/backlog/tasks/*.md) message="A task is created with the backlog tool: run 'mise exec -- backlog task create' (see skills/anima-tech-backlog-md.md)." ;;
esac
if [ -n "$message" ]; then
    printf '{"hookSpecificOutput":{"hookEventName":"PostToolUse","additionalContext":"%s"}}\n' "$message"
fi
exit 0
