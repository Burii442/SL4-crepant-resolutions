#!/usr/bin/env python3
"""Verify the finite minimum-cover claim using only Python's standard library.

This checks recorded decisive applications, not their geometric proofs.
All input paths are relative to this file; no project checkout is required.
"""
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read_json(name):
    return json.loads((HERE / name).read_text())


def read_csv(name):
    with (HERE / name).open(newline="") as stream:
        return list(csv.DictReader(stream))


def minimum_covers(cover):
    """Enumerate every one of the 2^14 subsets with exact integer bitsets."""
    names = list(cover)
    masks = [sum(1 << (i - 1) for i in cover[name]) for name in names]
    target = (1 << 106) - 1
    best, solutions = len(names) + 1, []
    for subset in range(1 << len(names)):
        union, chosen = 0, []
        for j, name in enumerate(names):
            if subset & (1 << j):
                union |= masks[j]
                chosen.append(name)
        if union == target and len(chosen) <= best:
            if len(chosen) < best:
                best, solutions = len(chosen), []
            solutions.append(chosen)
    return {"minimum": best, "covers": solutions,
            "subsets_checked": 1 << len(names)}


def main():
    provenance = read_json("provenance.json")
    for name, expected in provenance["portable_inputs"].items():
        actual = hashlib.sha256((HERE / name).read_bytes()).hexdigest()
        assert actual == expected, ("input hash", name)
    families = read_json("families.json")
    names = [row["id"] for row in families]
    retained = [row["id"] for row in families if row["retained"]]
    assert len(names) == len(set(names)) == 14
    assert retained == list("ABCDEFGHIJ")
    relabel = {row["historical_label"]: row["id"] for row in families}
    assert set(relabel) == set("ABCDEFGHIJKSUZ")
    cases = read_json("catalogue_projection.json")
    decisions = {row["case"]: row["decision"] for row in cases}
    assert len(cases) == len(decisions) == 106
    assert set(decisions) == set(range(1, 107))
    assert Counter(decisions.values()) == {"YES": 61, "NO": 45}
    projection = {}
    for row in cases:
        assert row["original_indices"]
        for old in row["original_indices"]:
            assert old not in projection, ("repeated original index", old)
            projection[old] = row["case"]
    assert set(projection) == set(range(1, 246))
    original = read_csv("original_applications.csv")
    assert len(original) == 341
    source_keys, projected = set(), defaultdict(set)
    for row in original:
        old, family = int(row["index"]), relabel[row["test"]]
        key = (old, family)
        assert key not in source_keys, ("duplicate original application", key)
        source_keys.add(key)
        case = projection[old]
        assert row["outcome"] == decisions[case], ("outcome", row)
        projected[(family, case, row["outcome"])].add(old)
    recorded = {}
    for row in read_csv("recorded_applications.csv"):
        key = (row["family"], int(row["case"]), row["outcome"])
        assert key not in recorded, ("duplicate projected application", key)
        recorded[key] = set(map(int, row["original_indices"].split()))
    assert recorded == dict(projected)
    assert len(recorded) == 155
    cover = {name: set() for name in names}
    outcomes = {name: Counter() for name in names}
    for family, case, outcome in recorded:
        cover[family].add(case)
        outcomes[family][outcome] += 1
    assert all(cover.values())
    for family in ("C", "cyclic"):
        negative = {i for i in cover[family] if decisions[i] == "NO"}
        assert negative <= cover["A"]
    witnesses = {row["id"]: row["private_case"] for row in families
                 if row["retained"]}
    assert list(witnesses.values()) == [16, 13, 15, 14, 23, 28, 52, 31, 35, 57]
    for family, case in witnesses.items():
        assert {name for name in names if case in cover[name]} == {family}
    assert set().union(*(cover[name] for name in retained)) == set(decisions)
    assignments = read_json("manuscript_assignments.json")
    current = {name: set(values) for name, values in assignments["sieves"].items()}
    assert set(current) == set(retained)
    for name in retained:
        expected = cover[name]
        if name == "C":
            expected = {case for case in expected if decisions[case] == "YES"}
        assert current[name] == expected, ("manuscript assignment", name)
    for name in ("D", "I"):
        for suffix, outcome in (("positive", "YES"), ("negative", "NO")):
            assert set(assignments[name + "_" + suffix]) == {
                case for case in current[name] if decisions[case] == outcome}
    normalized = {name: current.get(name, values) for name, values in cover.items()}
    historical_minimum = minimum_covers(cover)
    manuscript_minimum = minimum_covers(normalized)
    for result in (historical_minimum, manuscript_minimum):
        assert result["minimum"] == 10
        assert result["covers"] == [retained]
    report = {
        "status": "PASS", "cases": 106, "original_indices": 245,
        "original_applications": len(original), "projected_applications": len(recorded),
        "families": len(names), "decisions": dict(Counter(decisions.values())),
        "family_outcomes": {name: dict(counts) for name, counts in outcomes.items()},
        "private_witnesses": witnesses, "historical_library": historical_minimum,
        "with_manuscript_positive_only_sieve_C": manuscript_minimum,
        "scope": provenance["scope"],
        "input_sha256": provenance["portable_inputs"],
        "verifier_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    (HERE / "verification.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
