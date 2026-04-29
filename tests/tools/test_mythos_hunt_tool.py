"""Tests for the mythos_hunt structured audit-loop tool."""

import json

from tools.mythos_hunt_tool import mythos_hunt_tool


def test_initialize_creates_depth_cache_and_plan(tmp_path):
    target = tmp_path / "target"
    target.mkdir()

    result = json.loads(mythos_hunt_tool(
        target_path=str(target),
        scope="contracts/**/*.sol",
        action="initialize",
        constraints=["source is read-only", "must falsify before report"],
    ))

    assert result["status"] == "initialized"
    cache_path = target / "notes" / "mythos_hunt_depth_cache.md"
    plan_path = target / "notes" / "mythos_hunt_plan.md"
    assert cache_path.exists()
    assert plan_path.exists()
    cache = cache_path.read_text()
    assert "contracts/**/*.sol" in cache
    assert "source is read-only" in cache
    assert "Falsification Gate" in cache


def test_record_candidate_appends_hypothesis_and_falsification_status(tmp_path):
    target = tmp_path / "target"
    target.mkdir()
    mythos_hunt_tool(target_path=str(target), scope="src", action="initialize")

    result = json.loads(mythos_hunt_tool(
        target_path=str(target),
        scope="src",
        action="record_candidate",
        candidate={
            "id": "H-01",
            "title": "Dust poisons orientation",
            "hypothesis": "Attacker can initialize state with reversed pair",
            "impact": "Migration DoS",
            "evidence": ["unit test reproduces revert"],
            "falsification": ["checked upstream duplicate risk"],
            "status": "survived",
        },
    ))

    assert result["status"] == "candidate_recorded"
    cache = (target / "notes" / "mythos_hunt_depth_cache.md").read_text()
    assert "H-01" in cache
    assert "Dust poisons orientation" in cache
    assert "survived" in cache
    assert "checked upstream duplicate risk" in cache


def test_finalize_blocks_report_until_candidate_survives_falsification(tmp_path):
    target = tmp_path / "target"
    target.mkdir()
    mythos_hunt_tool(target_path=str(target), scope="src", action="initialize")

    result = json.loads(mythos_hunt_tool(
        target_path=str(target),
        scope="src",
        action="finalize_report_gate",
    ))

    assert result["status"] == "blocked"
    assert "No candidate marked survived" in result["reason"]


def test_finalize_allows_report_when_candidate_survives_falsification(tmp_path):
    target = tmp_path / "target"
    target.mkdir()
    mythos_hunt_tool(target_path=str(target), scope="src", action="initialize")
    mythos_hunt_tool(
        target_path=str(target),
        scope="src",
        action="record_candidate",
        candidate={"id": "H-01", "title": "real", "status": "survived"},
    )

    result = json.loads(mythos_hunt_tool(
        target_path=str(target),
        scope="src",
        action="finalize_report_gate",
    ))

    assert result["status"] == "ready_for_report"
    assert "H-01" in result["survived_candidates"]
