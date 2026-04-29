#!/usr/bin/env python3
"""Mythos Hunt tool — structured recurrent audit-loop cache.

This is the agent-layer transplant of OpenMythos' recurrent/depth-cache idea:
keep a durable depth cache in ``notes/`` so long hunts preserve objective,
constraints, hypotheses, falsification state, and report gates across turns.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from tools.registry import registry, tool_error

CACHE_FILE = "mythos_hunt_depth_cache.md"
PLAN_FILE = "mythos_hunt_plan.md"
VALID_ACTIONS = {"initialize", "record_loop", "record_candidate", "finalize_report_gate"}
SURVIVED_MARKER = "Status: survived"


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def _as_list(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    text = str(value).strip()
    return [text] if text else []


def _notes_dir(target_path: str) -> Path:
    target = Path(target_path).expanduser().resolve()
    if not target.exists():
        raise FileNotFoundError(f"target_path does not exist: {target}")
    if not target.is_dir():
        raise NotADirectoryError(f"target_path is not a directory: {target}")
    notes = target / "notes"
    notes.mkdir(parents=True, exist_ok=True)
    return notes


def _write_initial_files(notes: Path, target: Path, scope: str, constraints: List[str]) -> None:
    constraint_lines = "\n".join(f"- {c}" for c in constraints) or "- No explicit constraints recorded yet."
    cache = f"""# Mythos Hunt Depth Cache

[PERSISTENT CONTEXT INVARIANT]
Target: {target}
Scope: {scope or "(unspecified)"}
Constraints:
{constraint_lines}
Invariant: preserve objective, constraints, verified facts, falsified hypotheses, and report gates across compression.

## Current Objective
Find exploitable, in-scope, economically meaningful vulnerabilities. Prefer evidence over hype.

## Recurrent Loop State
- Depth 0 — map attack surface
- Depth 1 — generate hypotheses
- Depth 2 — falsify hypotheses
- Depth 3 — build proof / PoC
- Depth 4 — report gate

## Verified Facts

## Falsified Hypotheses

## Open Hypotheses

## Candidate Findings

## Falsification Gate
A candidate is not report-ready until it has:
- concrete exploit path
- reproducible evidence or exact code path
- attempted falsification notes
- scope / duplicate / privilege assumptions checked
- `Status: survived`

## Loop Log
- {_utc_now()} — initialized mythos hunt cache.
"""
    plan = f"""# Mythos Hunt Plan

Target: {target}
Scope: {scope or "(unspecified)"}
Created: {_utc_now()}

## Loop Protocol

1. Map
   - contracts/modules/entrypoints/trust boundaries
   - privileged vs permissionless paths
   - value-bearing state transitions

2. Hypothesize
   - write narrow hypotheses, not vibes
   - bias toward weird seams and economic edge cases

3. Falsify
   - try to prove each hypothesis false
   - record reason when dead
   - do not promote scanner noise

4. Prove
   - minimal PoC or exact transaction/code path
   - impact quantified pessimistically

5. Report Gate
   - only candidates marked `Status: survived` pass
   - no report without falsification notes
"""
    (notes / CACHE_FILE).write_text(cache, encoding="utf-8")
    (notes / PLAN_FILE).write_text(plan, encoding="utf-8")


def _append_section(path: Path, heading: str, lines: List[str]) -> None:
    with path.open("a", encoding="utf-8") as f:
        f.write(f"\n### {heading}\n")
        for line in lines:
            f.write(f"{line}\n")


def _format_candidate(candidate: Dict[str, Any]) -> List[str]:
    cid = str(candidate.get("id") or "candidate").strip()
    title = str(candidate.get("title") or "(untitled)").strip()
    status = str(candidate.get("status") or "open").strip().lower()
    lines = [f"- ID: {cid}", f"- Title: {title}", f"- Status: {status}"]
    for key in ("hypothesis", "impact", "exploit_path"):
        value = str(candidate.get(key) or "").strip()
        if value:
            lines.append(f"- {key.replace('_', ' ').title()}: {value}")
    for key in ("evidence", "falsification", "assumptions", "blockers"):
        items = _as_list(candidate.get(key))
        if items:
            lines.append(f"- {key.replace('_', ' ').title()}:")
            lines.extend(f"  - {item}" for item in items)
    if status == "survived":
        lines.append(f"- {SURVIVED_MARKER}")
    return lines


def _survived_candidates(cache_text: str) -> List[str]:
    survived: List[str] = []
    current_id: Optional[str] = None
    for raw in cache_text.splitlines():
        line = raw.strip()
        if line.startswith("- ID:"):
            current_id = line.split(":", 1)[1].strip()
        elif line == f"- {SURVIVED_MARKER}" and current_id:
            survived.append(current_id)
    return survived


def mythos_hunt_tool(
    target_path: str,
    scope: str = "",
    action: str = "initialize",
    constraints: Optional[List[str]] = None,
    loop_depth: Optional[int] = None,
    loop_notes: Optional[str] = None,
    candidate: Optional[Dict[str, Any]] = None,
) -> str:
    """Manage a Mythos recurrent audit-loop depth cache under target_path/notes."""
    try:
        action = (action or "initialize").strip().lower()
        if action not in VALID_ACTIONS:
            return tool_error(f"invalid action {action!r}; expected one of {sorted(VALID_ACTIONS)}")

        notes = _notes_dir(target_path)
        target = Path(target_path).expanduser().resolve()
        cache_path = notes / CACHE_FILE
        plan_path = notes / PLAN_FILE

        if action == "initialize":
            _write_initial_files(notes, target, scope, _as_list(constraints))
            return json.dumps({
                "status": "initialized",
                "cache_path": str(cache_path),
                "plan_path": str(plan_path),
                "message": "Mythos hunt depth cache initialized. Load this file before resuming the hunt.",
            }, ensure_ascii=False)

        if not cache_path.exists():
            _write_initial_files(notes, target, scope, _as_list(constraints))

        if action == "record_loop":
            depth = "?" if loop_depth is None else str(loop_depth)
            note = (loop_notes or "").strip() or "(no loop notes provided)"
            _append_section(cache_path, f"Loop depth {depth} — {_utc_now()}", [note])
            return json.dumps({"status": "loop_recorded", "cache_path": str(cache_path)}, ensure_ascii=False)

        if action == "record_candidate":
            if not isinstance(candidate, dict) or not candidate:
                return tool_error("record_candidate requires a non-empty candidate object")
            cid = str(candidate.get("id") or "candidate").strip()
            _append_section(cache_path, f"Candidate {cid} — {_utc_now()}", _format_candidate(candidate))
            return json.dumps({"status": "candidate_recorded", "cache_path": str(cache_path), "candidate_id": cid}, ensure_ascii=False)

        # finalize_report_gate
        text = cache_path.read_text(encoding="utf-8")
        survived = _survived_candidates(text)
        if not survived:
            return json.dumps({
                "status": "blocked",
                "reason": "No candidate marked survived falsification. Keep hunting or record falsification/evidence first.",
                "cache_path": str(cache_path),
            }, ensure_ascii=False)
        return json.dumps({
            "status": "ready_for_report",
            "survived_candidates": survived,
            "cache_path": str(cache_path),
            "message": "Report gate passed. Still verify scope, duplicate risk, and PoC self-sufficiency before submission.",
        }, ensure_ascii=False)

    except Exception as exc:
        return tool_error(str(exc))


def check_mythos_hunt_requirements() -> bool:
    return True


MYTHOS_HUNT_SCHEMA = {
    "name": "mythos_hunt",
    "description": (
        "Manage a structured recurrent Web3 audit loop inspired by OpenMythos. "
        "Creates/updates target_path/notes/mythos_hunt_depth_cache.md, preserves "
        "scope/constraints/hypotheses/evidence, and blocks report finalization "
        "until a candidate is explicitly marked as survived falsification."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "target_path": {"type": "string", "description": "Absolute or relative path to the audit target repo/workspace."},
            "scope": {"type": "string", "description": "In-scope files/modules/contracts or bounty scope summary."},
            "action": {"type": "string", "enum": sorted(VALID_ACTIONS), "default": "initialize"},
            "constraints": {"type": "array", "items": {"type": "string"}, "description": "Hard constraints to preserve across compression."},
            "loop_depth": {"type": "integer", "description": "Current recurrent loop depth/stage when action=record_loop."},
            "loop_notes": {"type": "string", "description": "Facts, falsified hypotheses, or next evidence step for record_loop."},
            "candidate": {"type": "object", "description": "Candidate finding object for record_candidate. Use status='survived' only after falsification."},
        },
        "required": ["target_path"],
    },
}


registry.register(
    name="mythos_hunt",
    toolset="bounty",
    schema=MYTHOS_HUNT_SCHEMA,
    handler=lambda args, **kw: mythos_hunt_tool(
        target_path=args.get("target_path", ""),
        scope=args.get("scope", ""),
        action=args.get("action", "initialize"),
        constraints=args.get("constraints"),
        loop_depth=args.get("loop_depth"),
        loop_notes=args.get("loop_notes"),
        candidate=args.get("candidate"),
    ),
    check_fn=check_mythos_hunt_requirements,
    emoji="🧬",
)
