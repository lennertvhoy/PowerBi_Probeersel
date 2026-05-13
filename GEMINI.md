# PowerBi_Probeersel Agent Context

This repository uses State Driven Development in bootstrap mode. Read `AGENTS.md`,
`STATUS.md`, `PROJECT_STATE.yaml`, `PROJECT_DNA.yaml`, and `NEXT_ACTIONS.md`
before implementation work.

Power Platform skills are platform-neutral and live in `skills/power-platform/`.
When a request matches a skill, read that skill's `SKILL.md` first, then only
load referenced files from its `resources/` directory as needed.

Adapter paths:
- Claude Code: `.claude/skills/`
- Codex: `.codex/skills/`
- Kimi CLI: `.kimi/plugins/`
- Gemini CLI: this `GEMINI.md` plus `.gemini/extensions/power-platform-skills/`

The adapter paths are symlink views of the canonical `skills/power-platform/`
folders. Edit the canonical skill files, not the adapter symlinks.
