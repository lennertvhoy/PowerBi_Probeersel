# Fallback Mode: Single-Agent Structured Planning

Use this when parallel agents or subagents are not available in the current agent runtime.

## How It Works

Instead of spawning three agents, the Lead performs all three roles sequentially
using sequential role passes and any safe research/delegation mechanism the current platform provides.

## Workflow

### Step 1 — Requirements Gathering

Same as Phase 1 in the team workflow. Ask the user about personas, data, workflows.

### Step 2 — Data Architecture Pass

Put on the "Data Architect" hat. Read `resources/roles/data-architect.md` for the
output format and domain knowledge references.

Design the full schema: tables, columns, relationships, option sets.

### Step 3 — UX Design Pass

Put on the "UX Designer" hat. Read `resources/roles/ux-designer.md` for the
output format and domain knowledge references.

Design the full app structure: forms, views, sitemap, user flows.

### Step 4 — Skeptic Review Pass

Put on the "Skeptic" hat. Read `resources/roles/the-skeptic.md` for the full
review checklist.

Go through EVERY item on the checklist. Document findings. Revise the schema
and UX design to address Critical and High findings.

### Step 5 — Consolidation

Merge everything into the plan template from `resources/plan-template.md`.

Present to user for approval.

## Quality Notes

Single-agent planning produces good results but has one weakness compared to
parallel agents or subagents: the same "mind" that designed the schema is reviewing it. Agent teams
provide genuinely independent perspectives that catch more blind spots.

To compensate:
- Be extra rigorous on the Skeptic pass — go through EVERY checklist item
- Consider spawning a sub-agent (Task tool, general-purpose) specifically for the
  Skeptic review, giving it the schema and UX design as input
- Ask the user to review the Skeptic findings themselves before finalizing

## Suggesting parallel agents or subagents

If the user seems to be planning a complex app (5+ tables, multiple personas,
approval workflows), suggest enabling parallel agents or subagents:

"This is a complex app. For better planning quality, use a platform/runtime with
parallel agents or subagents enabled. That lets three independent AI specialists
debate the design before implementation."
