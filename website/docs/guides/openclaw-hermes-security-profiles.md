---
sidebar_position: 9
title: "OpenClaw-style security profiles (recipes)"
description: "Example Hermes profile layouts for recon, web2 bug hunting, and web3 auditing — mapping IDENTITY, TOOLS, HEARTBEAT, and BOOTSTRAP without a second prompt system."
---

# OpenClaw-style security profiles (recipes)

Hermes already has the layers you need: [`SOUL.md`](/docs/user-guide/features/context-files) (identity), [`AGENTS.md`](/docs/user-guide/features/context-files) + optional [`TOOLS.md`](/docs/user-guide/features/context-files) (project rules), [skills](/docs/user-guide/features/skills) (heavy playbooks), [cron](/docs/user-guide/features/cron) + [`HEARTBEAT.md`](/docs/user-guide/features/context-files) (recurring checklists), and [profiles](/docs/user-guide/profiles) (isolation). This page gives **three copy-paste-oriented recipes** for security research personas. It does **not** add a parallel prompt stack — it only documents how to map OpenClaw habits onto Hermes.

**Canonical mapping:** See [OpenClaw and Hermes hybrid model](/docs/guides/openclaw-hermes-hybrid). After `hermes claw migrate`, archived `IDENTITY.md` and `BOOTSTRAP.md` are explained in the CLI; merge identity into `SOUL.md`, and treat `BOOTSTRAP.md` as a **one-time skill**, not a standing system prompt.

## Shared conventions (all three recipes)

| OpenClaw artifact | Hermes placement | Persistent in every message? |
|-------------------|------------------|-----------------------------|
| `IDENTITY.md` | Top of **`HERMES_HOME/SOUL.md`** under `## Identity` | Yes (short block) |
| `TOOLS.md` | Repo **`TOOLS.md`** or **`AGENTS.md`** § Tools; optional **`HERMES_HOME/TOOLS.md`** for profile-global hints | Yes, with caps (see [context files](/docs/user-guide/features/context-files)) |
| `HEARTBEAT.md` | **`HERMES_HOME/HEARTBEAT.md`** *or* a **skill** + **`hermes cron`** | Heartbeat file: yes except **cron** sessions skip it; cron+skill: checklist on schedule only |
| `BOOTSTRAP.md` | **One-off skill** (e.g. `skills/openclaw-bootstrap/SKILL.md`), run once, then remove or archive | **No** — never mirror OpenClaw’s “always-on bootstrap” in Hermes |

**Profile creation (once per persona):**

```bash
hermes profile create recon
# repeat for web2-hunter, web3-auditor — or use names you prefer
```

Use `hermes -p <profile>` or `HERMES_HOME=~/.hermes/profiles/<name>` so each persona gets its own `SOUL.md`, memories, skills, and cron jobs.

---

## Recipe: `recon` (OSINT / mapping / low-touch)

**Intent:** Broad surface mapping, passive collection, structured notes — minimize tool blast radius.

**`SOUL.md` (excerpt)**

```markdown
## Identity
- **Name:** Recon
- **Role:** Surface mapping and OSINT; no exploitation without explicit scope.

## Persona and boundaries
- Prefer read-only tooling; document sources and confidence.
- Scope: only targets in AGENTS.md or current ticket.
```

**Project context**

- Repo root **`AGENTS.md`**: legal/scope, allowed sources, evidence format (screenshots, hashes, timestamps).
- Optional **`TOOLS.md`** in repo or `HERMES_HOME`: which browsers, search APIs, and note paths to use.

**Heartbeat**

- Short checklist in **`HERMES_HOME/HEARTBEAT.md`** *or* skill `heartbeat-recon` + cron, e.g. daily: “Review yesterday’s notes, open questions, and scope drift.”

**Bootstrap**

- If migrating from OpenClaw: paste archived `BOOTSTRAP.md` into `skills/openclaw-bootstrap/SKILL.md`, invoke once with `/skill openclaw-bootstrap`, then disable or delete the skill.

---

## Recipe: `web2-hunter` (appsec / bug bounty)

**Intent:** Web apps, auth, business-logic bugs; heavy on reproducible steps and report quality.

**`SOUL.md` (excerpt)**

```markdown
## Identity
- **Name:** Web2 Hunter
- **Role:** Application security review and coordinated disclosure.

## Persona and boundaries
- Every finding: impact, steps, affected component, remediation hint.
- No destructive testing outside program rules.
```

**Project context**

- **`AGENTS.md`**: program URL, in-scope hosts, out-of-scope, rate limits, PII rules.
- **`TOOLS.md`** or AGENTS subsection: Burp/proxy conventions, test account handling, where to save PoCs.

**Skills (examples)**

- `report-template` — structured markdown for submissions.
- `owasp-top10-check` — methodology reminder (slash-invoked when needed).

**Heartbeat**

- Cron + skill: weekly “triage backlog + duplicate issues + program status.”

**Bootstrap**

- One-time skill: environment setup (VPN, browser profile, proxy cert) — **not** loaded every session.

---

## Recipe: `web3-auditor` (smart contracts / DeFi)

**Intent:** Solidity/Move audits, invariant thinking, economic reasoning; isolate high-risk toolchains.

**`SOUL.md` (excerpt)**

```markdown
## Identity
- **Name:** Web3 Auditor
- **Role:** Smart contract and protocol review; exploitability-first reasoning.

## Persona and boundaries
- Distinguish design risk vs permissionless exploit path.
- Prefer minimal PoC descriptions; no mainnet attacks without scope.
```

**Project context**

- **`AGENTS.md`**: compiler version, fork/network for tests, scope (files, contracts).
- **`TOOLS.md`**: Foundry/Hardhat/slither invocation patterns; **never** duplicate tool schemas — only *workflow* hints.

**Skills (examples)**

- `audit-report-sections` — severity rubric aligned with your team.
- `invariant-checklist` — token/accounting invariants to re-read before sign-off.

**Heartbeat**

- `HEARTBEAT.md` or cron: “Open issues from last fuzz run, diff coverage, dependency advisories.”

**Bootstrap**

- One-time skill: clone submodules, install solc, run `forge build` — run once per repo clone.

---

## Example migration flow (OpenClaw → Hermes, security-focused)

1. **`hermes claw migrate`** (optionally `--workspace-target` for `AGENTS.md`).
2. **Merge archived `IDENTITY.md` into `SOUL.md`** — CLI prints a suggested paste after migrate.
3. **Map `TOOLS.md`:** copy into repo `TOOLS.md` or merge into `AGENTS.md`; use `HERMES_HOME/TOOLS.md` only for profile-wide tool habits.
4. **Map `HEARTBEAT.md`:** copy to `HERMES_HOME/HEARTBEAT.md` *or* convert to skill + `hermes cron create` (cron platform skips injected heartbeat — see [context files](/docs/user-guide/features/context-files)).
5. **`BOOTSTRAP.md`:** create a **skill**, run once, do **not** add to system prompt. CLI prints guidance when `BOOTSTRAP.md` was archived.
6. **Split personas:** create profiles `recon`, `web2-hunter`, `web3-auditor` (or your names); copy the relevant `SOUL.md` / skills / `TOOLS.md` per profile home.

## Related

- [OpenClaw and Hermes hybrid model](/docs/guides/openclaw-hermes-hybrid)
- [Migrate from OpenClaw](/docs/guides/migrate-from-openclaw)
- [Context files](/docs/user-guide/features/context-files)
- [Profiles](/docs/user-guide/profiles)
- [Cron](/docs/user-guide/features/cron)
- [Skills](/docs/user-guide/features/skills)
