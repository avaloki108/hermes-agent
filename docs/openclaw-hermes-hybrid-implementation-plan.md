# OpenClaw ↔ Hermes hybrid: smallest viable implementation plan

**Goal:** Keep **Hermes** as the runtime (agent loop, tools, gateway, profiles, memory tool, context loading), and adopt **OpenClaw’s** clearer **identity/workspace/selfhood** layering without a full fork.

**Non-goals (for this MVP):** Rewriting the agent loop, breaking prompt-cache policy, or duplicating OpenClaw’s Node gateway internals.

This plan ties back to the gap analysis in `openclaw-hermes-hybrid-gap-analysis.md`.

---

## 1. Design principles

1. **`HERMES_HOME` remains authoritative** for global-per-profile identity (`SOUL.md`, memories, skills). Project context stays **cwd/git-root based** (`AGENTS.md`, `.hermes.md`).
2. **Prefer conventions + thin docs** over new loaders until a pattern proves necessary.
3. **Anything periodic** → **`hermes cron`** (OpenClaw `HEARTBEAT.md` analogue).
4. **Anything large or occasional** → **skills** (OpenClaw workspace `skills/` analogue).
5. **Security research workflows** → **AGENTS.md** (repo) + **skills** (methodology) + **profile separation** (recon vs web2 vs web3).

---

## 2. MVP bundles (smallest viable)

### 2.1 Stronger sense of self

| Gap | MVP implementation |
|-----|----------------------|
| OpenClaw `IDENTITY.md` vs Hermes | **Document** that `HERMES_HOME/SOUL.md` should contain: (1) one short “Identity” block (name, emoji, voice), (2) “Persona & boundaries” body. Optional: ship a **starter template** in docs or `hermes setup` copyable section — no new parser required initially. |
| OpenClaw `SOUL` in workspace | Hermes loads SOUL only from `HERMES_HOME`. **MVP:** In hybrid docs, instruct: use **profiles** or a **single canonical repo** whose `AGENTS.md` points to “home” expectations; optional symlink `project/SOUL.md` → not supported by loader — **do not** rely on cwd SOUL. |
| Migration archive `IDENTITY.md` | User merges archived file into SOUL per migration guide; **automate later** with a `hermes claw migrate` post-step suggestion only (documentation-first). |

**Classification:** Mostly **manual/user-authored** + **documentation**; **optional** template file under `docs/` or website.

**User-facing compatibility layer (website):** [OpenClaw and Hermes hybrid model](https://hermes-agent.nousresearch.com/docs/guides/openclaw-hermes-hybrid), [Migrate from OpenClaw](https://hermes-agent.nousresearch.com/docs/guides/migrate-from-openclaw) (archived-file checklist), and [OpenClaw-style security profiles (recipes)](https://hermes-agent.nousresearch.com/docs/guides/openclaw-hermes-security-profiles) (`recon`, `web2-hunter`, `web3-auditor`). CLI: after `hermes claw migrate`, suggested paste for archived **`IDENTITY.md`**; first-run guidance for archived **`BOOTSTRAP.md`** (not persistent prompt).

---

### 2.2 Security research workflows

| Gap | MVP implementation |
|-----|----------------------|
| Standing orders + methodology | Add **repo-level `AGENTS.md`** (or `.hermes.md`) sections: scope, evidence bar, disclosure, tool policy. |
| Heavy playbooks | **`~/.hermes/skills/<name>/SKILL.md`** (per profile) for “triage”, “exploit writeup”, “report format”. |
| Sensitive separation | **Profiles** `recon`, `web2`, `web3` with different `SOUL.md`, memories, skills packs, and `.env` where needed. |
| OpenClaw `TOOLS.md` | **AGENTS.md** subsection “Tool conventions” + link to skills; no new injector. |

**Classification:** **Native** Hermes features (AGENTS, skills, profiles); **documentation** to encode OpenClaw-style splits.

---

### 2.3 Repeatable heartbeat / review behavior

| Gap | MVP implementation |
|-----|----------------------|
| OpenClaw `HEARTBEAT.md` | Map checklist content to a **skill** (“heartbeat”) + **`hermes cron`** job that opens a session with a **fixed user message** (e.g. “Run heartbeat skill: review backlog, sessions, cron failures”). |
| OpenClaw internal cron session stripping | Hermes: keep checklist **short** in skill; avoid huge injected docs in cron **if** the implementation reuses the main system prompt path (verify current cron prompt assembly in code when implementing). |

**Classification:** **Cron jobs** + **skills** remain the primary repeatable review path.

**Implemented (Phase C):** Optional `HERMES_HOME/HEARTBEAT.md` + `TOOLS.md` + daily memory loaders in `build_context_files_prompt()` (strict caps; `platform=cron` skips heartbeat + daily). The skill + cron workflow above is still recommended for structured reviews.

---

### 2.4 Project-local tool conventions

| Gap | MVP implementation |
|-----|----------------------|
| `TOOLS.md` archived | **AGENTS.md** section “Tools & conventions”; optional **`docs/hermes-tools.md`** in repo if the team wants it versioned without polluting root. |
| Dynamic tool hints | Hermes already injects tool schemas; **don’t duplicate** in a parallel `TOOLS.md` unless we add a loader later. |

**Classification:** **Manual** (AGENTS) for MVP; **unmapped** as dedicated injected file until product decides otherwise.

---

### 2.5 Profile-separated recon / web2 / web3 personas

| Gap | MVP implementation |
|-----|----------------------|
| OpenClaw profile workspaces | **Hermes profiles** already isolate `SOUL.md`, memories, skills, cron, gateway tokens. |
| Naming | Document recommended profile names and what goes in each SOUL/skills set. |
| Multi-agent routing | Use **one profile per persona**; separate gateway processes/tokens; **no** OpenClaw-style bindings JSON in MVP. |

**Classification:** **Already native**; **documentation + conventions** for the hybrid.

---

## 3. Daily memory files

| Current Hermes behavior | MVP |
|-------------------------|-----|
| Migration merges `memory/*.md` into `MEMORY.md` | Users rely on **memory tool** + optional **external memory** for volume. |
| OpenClaw recommends read today + yesterday | **Optional cron + skill** “read recent notes”: instruct agent to `session_search` or read from a **user-maintained** `notes/` dir via file tools — **not** automatic injection. |

**Classification:** **Unmapped** for native daily files; **workaround** via skills + cron + file tools; **future** implementation could add `HERMES_HOME/memory/daily/` rotation with explicit injection policy (high design cost).

---

## 4. Workspace `skills` vs Hermes skills

| OpenClaw | Hermes MVP |
|----------|------------|
| `workspace/skills` highest precedence | Use **`HERMES_HOME/skills/`** per profile; for **repo-committed** skills, document copying or symlinking into profile skills dir, or use project-specific skill packs if the project already supports that layout. |
| Migration imports to `openclaw-imports/` | Keep; new work lands in profile skills directly. |

**Classification:** **Native** with different path story; **documentation** to explain mapping.

---

## 5. Multi-agent routing

| OpenClaw | Hermes MVP |
|----------|------------|
| `agents.list`, bindings, per-agent workspace | **Profiles** + per-profile gateway + token locks; manual channel setup. |

**Classification:** **Partially mapped**; **manual** for routing tables; revisit only if product adds first-class routing config.

---

## 6. Implementation phases (ordered)

### Phase A — Documentation only (zero code risk)

**Status: implemented** (website guide + migration guide link).

1. Link this plan + gap analysis from `website/docs/guides/migrate-from-openclaw.md` as “hybrid model”.
2. Add a short **“OpenClaw mental model in Hermes”** table: SOUL/AGENTS/memory/skills/cron.
3. Provide **copy-paste SOUL structure** (Identity + Persona) and **sample cron** lines for heartbeat.

Deliverables:

- `website/docs/guides/openclaw-hermes-hybrid.md` — mental model table, SOUL scaffold, heartbeat cron example, security/profile notes.
- `website/docs/guides/migrate-from-openclaw.md` — section linking to the hybrid guide.
- Repo: `docs/openclaw-hermes-hybrid-gap-analysis.md` and this file remain the detailed reference.

### Phase B — Optional scaffolding (small code / CLI)

**Status: partially implemented.**

1. `hermes profile create` prints a one-line pointer to the hybrid guide for multi-persona (recon / research / web3) workflows.
2. **`hermes claw migrate`** (after a successful run): if `archive/workspace/IDENTITY.md` exists under the migration report directory, print a **suggested paste** block for merging into `SOUL.md` (user still edits the file manually).

### Phase C — Deeper parity (OpenClaw-style context loaders)

**Status: implemented** (`agent/prompt_builder.py` — session-start only; does not reload mid-conversation).

1. **`HERMES_HOME/HEARTBEAT.md`** — scanned, truncated to `HEARTBEAT_MAX_CHARS`, prefixed with `## HEARTBEAT.md`.
2. **`TOOLS.md`** — project `TOOLS.md` / `tools.md` (CWD), then `HERMES_HOME/TOOLS.md`; each capped with `TOOLS_MD_MAX_CHARS`.
3. **Daily memory** — `HERMES_HOME/memory/daily/YYYY-MM-DD.md` for **today** and **yesterday** (timezone from `hermes_time.now()`), per-file and combined caps (`DAILY_MEMORY_*`).
4. **Assembly order** — project context (single winner) → CWD tools → home tools → `SOUL.md` (unless skipped) → heartbeat + daily.
5. **`platform=cron`** — skips heartbeat and daily memory so scheduled jobs do not inherit session checklists; tools still load.

---

## 7. Explicit mapping: migration archives → destination

| Archived OpenClaw artifact | Recommended Hermes destination (hybrid) |
|----------------------------|----------------------------------------|
| `IDENTITY.md` | **SOUL.md** (top section) |
| `TOOLS.md` | **AGENTS.md** / skills |
| `HEARTBEAT.md` | **Cron** + **heartbeat skill** |
| `BOOTSTRAP.md` | **Skills** (one-time ritual) + delete when done (manual) |
| `cron-config.json` | **`hermes cron create`** |
| Multi-agent / bindings | **Profiles** + manual gateway |

---

## 8. Success criteria

- A user coming from OpenClaw can **name** where each legacy file lives in Hermes terms without reading source code.
- **Persona** is stable per profile (`SOUL.md`).
- **Project rules** stay in repo (`AGENTS.md`).
- **Repeatable reviews** run on a schedule (`cron` + skill).
- **Recon / web2 / web3** isolation is achievable with **profiles** without custom routing JSON.

---

## 9. Related files

- `docs/openclaw-hermes-hybrid-gap-analysis.md`
- `website/docs/guides/migrate-from-openclaw.md`
- `website/docs/user-guide/features/context-files.md`
- `website/docs/user-guide/features/memory.md`
- `website/docs/user-guide/profiles.md`
