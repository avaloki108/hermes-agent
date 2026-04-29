---
sidebar_position: 8
title: "OpenClaw and Hermes hybrid model"
description: "Map OpenClaw workspace files to Hermes — SOUL, AGENTS, memory, skills, cron, and profiles — without losing the sense of self."
---

# OpenClaw and Hermes hybrid model

Hermes is the **runtime** (agent loop, tools, gateway, [profiles](/docs/user-guide/profiles), [memory](/docs/user-guide/features/memory), [context files](/docs/user-guide/features/context-files)). OpenClaw’s **agent workspace** is a single directory of markdown “standing orders” and identity. After [migrating from OpenClaw](/docs/guides/migrate-from-openclaw), you can recreate that **mental model** using Hermes primitives below.

Developer-facing deep dives (same repo): [`docs/openclaw-hermes-hybrid-gap-analysis.md`](https://github.com/NousResearch/hermes-agent/blob/main/docs/openclaw-hermes-hybrid-gap-analysis.md), [`docs/openclaw-hermes-hybrid-implementation-plan.md`](https://github.com/NousResearch/hermes-agent/blob/main/docs/openclaw-hermes-hybrid-implementation-plan.md).

## OpenClaw mental model in Hermes

| OpenClaw workspace file | Role in OpenClaw | Hermes equivalent |
|------------------------|------------------|-------------------|
| `SOUL.md` | Persona, tone, boundaries | [`HERMES_HOME/SOUL.md`](/docs/user-guide/features/context-files) — per [profile](/docs/user-guide/profiles), not read from the project directory |
| `AGENTS.md` | Operating instructions | Recursive [`AGENTS.md`](/docs/user-guide/features/context-files) from working directory (and optional `.hermes.md` at git root) |
| `USER.md` | Who the user is | Bounded [`USER` memory](/docs/user-guide/features/memory) in `memories/USER.md` (tool-managed) |
| `MEMORY.md` | Long-term notes | Bounded [`memory` store](/docs/user-guide/features/memory) in `memories/MEMORY.md` |
| `IDENTITY.md` | Name, vibe, emoji | No separate file — merge into **SOUL.md** (short block at top); [`hermes claw migrate`](/docs/guides/migrate-from-openclaw) prints a suggested paste; CLI branding via [`/skin`](/docs/user-guide/features/skins) |
| `TOOLS.md` | Tool conventions | Injected **[`TOOLS.md`](/docs/user-guide/features/context-files)** (CWD, then `HERMES_HOME/TOOLS.md`) with size caps; *or* fold into **AGENTS.md** / [skills](/docs/user-guide/features/skills) if you prefer not to use the loader |
| `HEARTBEAT.md` | Tiny recurring checklist | Optional **[`HERMES_HOME/HEARTBEAT.md`](/docs/user-guide/features/context-files)** (skipped when `platform=cron`) **and/or** [cron job](/docs/user-guide/features/cron) + **skill** with the checklist |
| `BOOTSTRAP.md` | One-time first-run ritual | **Not** injected every session — one-off [skill](/docs/user-guide/features/skills); `hermes claw migrate` prints guidance when archived; see [security profile recipes](/docs/guides/openclaw-hermes-security-profiles) |
| `workspace/skills/` | Highest-precedence skills | `HERMES_HOME/skills/` per profile; migrated skills often land in `skills/openclaw-imports/` |
| `memory/YYYY-MM-DD.md` | Daily log | Optional **`HERMES_HOME/memory/daily/YYYY-MM-DD.md`** (today + yesterday) in [context assembly](/docs/user-guide/features/context-files); skipped for `platform=cron`. Else [memory tool](/docs/user-guide/features/memory), session search, or [memory providers](/docs/user-guide/features/memory-providers) |
| Multi-agent / routing | Per-agent workspace, bindings | **One Hermes [profile](/docs/user-guide/profiles) per persona** — separate gateways and tokens; channel setup is manual |

**Important:** Hermes loads **`SOUL.md` only from `HERMES_HOME`**, not from a repo path. Do not expect a project-root `SOUL.md` to be injected unless you use a profile whose home is that tree (not the default layout).

## Copy-paste `SOUL.md` structure (Identity + persona)

Use a short **Identity** block at the top (what OpenClaw often split into `IDENTITY.md`), then persona and boundaries:

```markdown
## Identity

- **Name:** …
- **Emoji / sign-off:** …
- **Voice:** …

## Persona and boundaries

- Tone: …
- Refusals / scope: …
- How to address the user: …
```

Edit with `hermes config` / your editor at `~/.hermes/SOUL.md`, or under `~/.hermes/profiles/<name>/SOUL.md` for a [profile](/docs/user-guide/profiles).

## Heartbeat-style review (cron + skill)

OpenClaw’s `HEARTBEAT.md` is a small checklist for scheduled runs. In Hermes:

1. Add a **skill** (e.g. `~/.hermes/skills/heartbeat/SKILL.md`) with your checklist — keep it short.
2. Schedule a [cron job](/docs/user-guide/features/cron) that runs a fixed prompt, with that skill attached.

Example CLI:

```bash
hermes cron create "0 9 * * *" \
  "Run the heartbeat checklist: review yesterday's notes, open tasks, and any cron failures. Be brief." \
  --skill heartbeat \
  --name "Daily heartbeat"
```

Adjust the schedule expression and skill name to match your setup.

## Security research workflows

- **Repo rules:** Put scope, evidence bar, disclosure policy, and tool policy in **`AGENTS.md`** or `.hermes.md` at the project root.
- **Heavy playbooks:** Use **skills** (methodology, report templates) under `HERMES_HOME/skills/`.
- **Separation of concerns:** Use **multiple profiles** — for example dedicated personas for reconnaissance, web2, and web3 work — each with its own `SOUL.md`, memories, skills, and `.env`.
- **Concrete layouts:** [OpenClaw-style security profiles (recipes)](/docs/guides/openclaw-hermes-security-profiles) — `recon`, `web2-hunter`, `web3-auditor`.

## Related

- [OpenClaw-style security profiles (recipes)](/docs/guides/openclaw-hermes-security-profiles)
- [Migrate from OpenClaw](/docs/guides/migrate-from-openclaw)
- [Profiles](/docs/user-guide/profiles)
- [Context files](/docs/user-guide/features/context-files)
- [Memory](/docs/user-guide/features/memory)
- [Cron](/docs/user-guide/features/cron)
- [Skills](/docs/user-guide/features/skills)
