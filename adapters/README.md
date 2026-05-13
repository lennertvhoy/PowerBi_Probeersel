# Agent Skill Adapters

Canonical skills live in `skills/power-platform/`.

The repository includes symlink adapters for common agent runtimes:

- `.claude/skills/` for Claude Code-style skill discovery.
- `.codex/skills/` for Codex-style local skill discovery where supported.
- `.kimi/plugins/` for Kimi CLI plugin/skill discovery layouts.
- `.gemini/extensions/power-platform-skills/` plus root `GEMINI.md` for Gemini CLI.

If a runtime only scans a user-level directory, copy or symlink each canonical
skill folder into that runtime's configured skills root. Keep
`skills/power-platform/` as the source of truth and regenerate adapters from it
when skill content changes.
