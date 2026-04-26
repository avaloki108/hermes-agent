# OpenClaw ↔ Hermes hybrid: gap analysis

This document maps OpenClaw’s **agent workspace** model to Hermes’s runtime, based on:

- OpenClaw: `openclaw/docs/concepts/agent-workspace.md`, `openclaw/src/agents/workspace.ts`
- Hermes: `website/docs/guides/migrate-from-openclaw.md`, `optional-skills/migration/openclaw-migration/scripts/openclaw_to_hermes.py`, `website/docs/user-guide/features/context-files.md`, `website/docs/user-guide/features/memory.md`, `website/docs/user-guide/profiles.md`

## 1. Source summaries (inspection notes)

### 1.1 OpenClaw `agent-workspace.md`

- **Workspace** is the agent’s home: default cwd for tools and injected context; not a hard sandbox unless sandboxing is enabled.
- **Location**: default `~/.openclaw/workspace`, or `~/.openclaw/workspace-<profile>` when `OPENCLAW_PROFILE` ≠ `default`; overridable in config.
- **Standard files**: `AGENTS.md`, `SOUL.md`, `USER.md`, `IDENTITY.md`, `TOOLS.md`, `HEARTBEAT.md`, `BOOT.md`, `BOOTSTRAP.md`, optional `MEMORY.md`, `memory/YYYY-MM-DD.md`, optional `skills/` (highest precedence for that workspace), optional `canvas/`.
- **Multi-agent**: different workspaces per agent possible (channel routing).
- **Git**: workspace treated as private memory; recommended private repo.

### 1.2 OpenClaw `workspace.ts`

- Resolves default workspace directory from home + `OPENCLAW_PROFILE`.
- **Bootstrap set**: seeds `AGENTS`, `SOUL`, `TOOLS`, `IDENTITY`, `USER`, `HEARTBEAT`, and conditionally `BOOTSTRAP`; loads `MEMORY.md` or `memory.md` if present.
- **Session filtering**: for **subagent** and **cron** session keys, bootstrap is reduced to a **minimal allowlist**: `AGENTS`, `TOOLS`, `SOUL`, `IDENTITY`, `USER` only — `HEARTBEAT`, `BOOTSTRAP`, `MEMORY` are dropped from injection for those sessions.
- Reads are **boundary-safe**, cached by file identity, with size limits.

### 1.3 Hermes migration guide + script

- **Migrated**: `SOUL.md` → `HERMES_HOME/SOUL.md`; `AGENTS.md` → `--workspace-target`; `MEMORY.md` / `USER.md` → `memories/` with `§` entries; `workspace/memory/*.md` **merged** into `MEMORY.md`; skills → `~/.hermes/skills/openclaw-imports/` (with conflict modes).
- **Archived** (no direct slot): `IDENTITY.md`, `TOOLS.md`, `HEARTBEAT.md`, `BOOTSTRAP.md`, plus cron/plugins/hooks/memory-backend/skills-registry/ui-identity/logging, multi-agent list, bindings, deep channels, etc. (`migrate-from-openclaw.md` table + `archive_docs()` in `openclaw_to_hermes.py`).

### 1.4 Hermes context files

- **Project context**: `.hermes.md` / `HERMES.md` (git root) → `AGENTS.md` (recursive) → `CLAUDE.md` → `.cursorrules` — **one** project context chain wins (first match).
- **`AGENTS.md`**: hierarchical concatenation from cwd upward (monorepo-friendly).
- **`SOUL.md`**: **only** from `HERMES_HOME`, always loaded as identity (independent of project file priority); not discovered in repo cwd.

### 1.5 Hermes memory

- **`MEMORY.md` / `USER.md`**: live under `HERMES_HOME/memories/`, bounded char limits, `§` delimiters, frozen at session start; mutated via `memory` tool.
- **Daily files**: not first-class; migration **folds** OpenClaw `memory/*.md` into the single `MEMORY.md` store.
- **Session search**: FTS over SQLite sessions — complementary to static memory.

### 1.6 Hermes profiles

- **Profile** = separate `HERMES_HOME` tree: config, `.env`, `SOUL.md`, memories, sessions, skills, **cron**, gateway, state DB.
- Rough analogue to OpenClaw’s `OPENCLAW_PROFILE` + separate workspace, but Hermes does **not** use a single “workspace directory” bundle for all identity files; **cwd** + **`HERMES_HOME`** split the story.

---

## 2. Concept mapping: OpenClaw → Hermes

| OpenClaw concept | Hermes equivalent today | Classification |
|------------------|-------------------------|----------------|
| **SOUL.md** (workspace) | `HERMES_HOME/SOUL.md` (global to profile) | **Partially mapped** — same *role* (persona/tone), different *placement* (OpenClaw: co-located in workspace dir; Hermes: never cwd-scoped). |
| **AGENTS.md** (workspace root) | Recursive `AGENTS.md` from cwd + optional `.hermes.md` | **Native** for project instructions; **not** a single fixed “agent home” file unless user sets cwd/git root. |
| **USER.md** | `memories/USER.md` (bounded, tool-managed) | **Native** with different mechanics (entry limits, frozen snapshot). |
| **MEMORY.md** | `memories/MEMORY.md` | **Native** with same caveat (size limits, tool API, not arbitrary long-form doc). |
| **IDENTITY.md** | No dedicated file; migration says merge into `SOUL.md`; optional UI via `/skin` for CLI | **Unmapped** as first-class file; **partially** covered by SOUL + skin branding. |
| **TOOLS.md** | Tool schemas + `toolsets` + docs in AGENTS; migration archives | **Unmapped** as dedicated injectable doc; **partially** “native” as built-in tool behavior + project AGENTS. |
| **HEARTBEAT.md** | No workspace file; `hermes cron` for periodic runs | **Unmapped** as workspace-injected checklist; **partially** mapped to **cron** (different UX). |
| **BOOTSTRAP.md** | No one-time ritual file; skills + context files | **Unmapped**; migration suggests context files or skills. |
| **BOOT.md** (OpenClaw gateway restart checklist) | Gateway hooks / startup behavior (see hooks docs) | **Unmapped** as same artifact name; **partially** achievable manually. |
| **workspace/skills** | `HERMES_HOME/skills/` (+ bundled); migration → `openclaw-imports/` | **Native** skills system; **partially** mapped — **not** per-repo workspace overlay by default (skills are profile-local unless tooling copies them). |
| **Multi-agent routing** (per-agent workspace, bindings) | **Profiles** (`HERMES_HOME` per profile); separate gateways/tokens | **Partially mapped** — isolation matches; **no** Hermes-native “routing table” like OpenClaw channel bindings (archived in migration). |
| **Daily memory files** `memory/YYYY-MM-DD.md` | Merged into `MEMORY.md` on migration only; no ongoing daily file workflow | **Unmapped** for **ongoing** use; **partially** mapped as one-time merge. |

### 2.1 Legend

- **Already native in Hermes**: Feature exists with clear Hermes idiom (may differ in path or limits).
- **Partially mapped**: Same intent, different shape, or one-time migration only.
- **Unmapped and needs implementation**: No equivalent artifact or behavior without new code/docs conventions.
- **Should remain manual/user-authored**: Appropriate as human-maintained content or policy, not framework magic.

---

## 3. OpenClaw-only semantics during migration (what Hermes “archives”)

From `migrate-from-openclaw.md` and `openclaw_to_hermes.py` (`archive_docs` and related):

| Artifact / config | Hermes handling |
|-------------------|-----------------|
| `IDENTITY.md` | Copied to archive; user told to merge into `SOUL.md` |
| `TOOLS.md` | Archived; “Hermes has built-in tool instructions” |
| `HEARTBEAT.md` | Archived; “use cron jobs” |
| `BOOTSTRAP.md` | Archived; “context files or skills” |
| OpenClaw **cron** | `cron-config.json` + cron store archived → `hermes cron create` |
| **Plugins / extensions** | Archived |
| **Hooks / webhooks** | Archived |
| **Memory backend** (OpenClaw) | Archived → e.g. `hermes honcho` / external providers |
| **Skills registry** (per-skill config) | Archived → `hermes skills config` |
| **UI / identity** (theme, display) | Archived → `/skin`, config |
| **Multi-agent list** | Archived → profiles |
| **Channel bindings** | Archived → manual platform setup |
| **Deep channel config** | Archived / partial import |

**Daily memory files:** `migrate_daily_memory()` **merges** `workspace/memory/*.md` entries into `HERMES_HOME/memories/MEMORY.md` (bounded; overflow may be written aside). Separately, `archive_docs()` **also copies** the entire `workspace/memory/` tree into the migration `archive/` directory for manual review. So users may see both a merged store and an archived copy of the original tree (not “merge-only”).

---

## 4. Classification: what should become SOUL vs AGENTS vs skills vs cron

This is **recommendation** for a hybrid that preserves OpenClaw’s *separation of concerns* without breaking Hermes invariants (e.g. prompt caching, `HERMES_HOME` semantics).

| Kind of content | Prefer | Rationale |
|-----------------|--------|-----------|
| Persona, tone, boundaries, “who I am” | **SOUL** (`HERMES_HOME/SOUL.md`) | Matches both systems; global per profile. |
| Name, emoji, short public-facing identity **without** long ritual text | **SOUL** (or first paragraph) | OpenClaw `IDENTITY.md` migration target; keeps identity load small. |
| Operating rules, priorities, security workflow steps, tool *policies* | **AGENTS.md** (project) + optional `.hermes.md` | Hermes already elevates project instructions from cwd; good for repo-local security conventions. |
| Long procedural runbooks (e.g. bounty triage) | **Skills** (`SKILL.md` under profile skills dir) | Invoked on demand; avoids blowing context every turn. |
| Tiny recurring checklist (“check inbox”, “review findings”) | **Cron** + minimal prompt or slash command | Parallels OpenClaw heartbeat without faking a workspace file injector. |
| Tool naming aliases, “when to use X vs Y” | **AGENTS.md** or **skills**; not schema | Hermes tool availability is config/registry; *guidance* stays markdown. |
| User facts & preferences | **`USER` memory target** | Bounded store with tool API. |
| Durable environment/project facts | **`memory` target** or external memory provider | Matches Hermes memory design. |
| Per-session “standing orders” that must not change mid-session | **Manual discipline** or static files | Aligns with Hermes “no context reload mid-conversation” policy. |

**What should stay user-authored (not auto-generated):**

- Exact text of SOUL/AGENTS/skills (framework should scaffold, not overwrite).
- Profile-specific `.env` and gateway bindings.
- Choice to use external memory (Honcho, Mem0, etc.).

---

## 5. Cross-cutting gaps for a “stronger OpenClaw-like” Hermes

1. **Single workspace directory**: OpenClaw bundles identity + instructions + optional MEMORY/HEARTBEAT in one tree; Hermes splits **`HERMES_HOME`** (identity, memories, skills) vs **project cwd** (AGENTS). Users lose the “one folder is the agent” mental model unless they adopt conventions (e.g. always run from same repo, or symlink).
2. **IDENTITY vs SOUL**: Hermes has no `IDENTITY.md`; users must merge concepts into SOUL or branding.
3. **TOOLS.md**: No dedicated “tools appendix” injected beside AGENTS; content must live in AGENTS/skills or upstream tool descriptions.
4. **HEARTBEAT**: No `HEARTBEAT.md` injection; cron is the closest primitive.
5. **Daily memory files**: No native `memory/YYYY-MM-DD.md` rotation; everything is funneled into bounded `MEMORY.md` or external providers.
6. **Subagent/cron context**: OpenClaw explicitly **strips** HEARTBEAT/MEMORY/BOOTSTRAP for subagent/cron sessions; Hermes behavior must be verified per prompt path (not identical by construction).
7. **Multi-agent routing**: OpenClaw bindings → Hermes profiles + manual gateway envs; no drop-in routing config.

---

## 6. References (repo paths)

- OpenClaw workspace concept: `openclaw/docs/concepts/agent-workspace.md`
- OpenClaw loader/filtering: `openclaw/src/agents/workspace.ts`
- Hermes migration guide: `website/docs/guides/migrate-from-openclaw.md`
- Migration script: `optional-skills/migration/openclaw-migration/scripts/openclaw_to_hermes.py`
- Context files: `website/docs/user-guide/features/context-files.md`
- Memory: `website/docs/user-guide/features/memory.md`
- Profiles: `website/docs/user-guide/profiles.md`

See **`openclaw-hermes-hybrid-implementation-plan.md`** for the smallest viable implementation steps.
