#!/usr/bin/env python3
"""Recompute age profiles of the 106 real matrix representations exactly.

For a finite-order real matrix, nonreal eigenvalues occur in conjugate
reciprocal pairs. Each such pair contributes one to age and two to
rank(I-g). The remaining eigenvalues are 1 and -1. Determinant one forces
an even multiplicity of -1, each of which contributes 1/2 to age. Hence
age(g) = rank(I-g)/2 for the representations in this catalogue. This
formula is specific to real determinant-one representations; it must not
be applied to arbitrary finite subgroups of SL(4,C).

All ranks, group closures, conjugacy orbits and subgroup orders below use
exact integer or rational arithmetic. Stored counts are compared with the
fresh computation; they are never used to select conjugacy classes.

Public API: compute_profile(row) returns one JSON-compatible dictionary;
verify_profiles(catalogue=DEFAULT_CATALOGUE, cases=None) returns an ordered
list of dictionaries. The module and CLI write no result files.
"""

import argparse
from collections import Counter
from fractions import Fraction
import importlib.util
import json
from pathlib import Path
import sys
import time

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CATALOGUE = ROOT / "manuscript106/catalogue/catalogue.json"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def _matrix_api():
    # Importing this existing verifier only exposes arithmetic; its main()
    # writes a report, so it is deliberately not called.
    require(__debug__, "Run without -O: the matrix verifier uses assertions")
    path = ROOT / "manuscript106/catalogue/verify_catalogue.py"
    spec = importlib.util.spec_from_file_location("age_profile_matrix_api", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


MATRIX = _matrix_api()
IDENTITY = MATRIX.one


def rank(rows):
    """Exact rank of a rectangular rational matrix, including no rows."""
    if not rows:
        return 0
    a = [list(map(Fraction, row)) for row in rows]
    width = len(a[0])
    require(all(len(row) == width for row in a), "Nonrectangular rank input")
    r = 0
    for column in range(width):
        pivot = next((i for i in range(r, len(a)) if a[i][column]), None)
        if pivot is None:
            continue
        a[r], a[pivot] = a[pivot], a[r]
        for i in range(r + 1, len(a)):
            if a[i][column]:
                factor = a[i][column] / a[r][column]
                for j in range(column, width):
                    a[i][j] -= factor * a[r][j]
        r += 1
        if r == len(a):
            break
    return r


def inverse(matrix):
    """Exact integral inverse of a unimodular 4 by 4 matrix."""
    a = [[Fraction(x) for x in matrix[i] + IDENTITY[i]] for i in range(4)]
    for j in range(4):
        pivot = next((i for i in range(j, 4) if a[i][j]), None)
        require(pivot is not None, "Singular generator")
        a[j], a[pivot] = a[pivot], a[j]
        scale = a[j][j]
        a[j] = [x / scale for x in a[j]]
        for i in range(4):
            if i != j:
                factor = a[i][j]
                a[i] = [x - factor * y for x, y in zip(a[i], a[j])]
    require(all(x.denominator == 1 for row in a for x in row[4:]),
            "Generator is not unimodular")
    result = tuple(tuple(int(x) for x in row[4:]) for row in a)
    require(MATRIX.mul(matrix, result) == IDENTITY, "Incorrect inverse")
    return result


def conjugacy_classes(group, generators):
    """Enumerate all conjugacy orbits using the actual ordered generators."""
    actions = [(g, inverse(g)) for g in generators]
    remaining = set(group)
    classes = []
    while remaining:
        representative = min(remaining)
        orbit = {representative}
        queue = [representative]
        for x in queue:
            for g, gi in actions:
                conjugate = MATRIX.mul(MATRIX.mul(g, x), gi)
                require(conjugate in group, "Conjugate outside the computed group")
                if conjugate not in orbit:
                    orbit.add(conjugate)
                    queue.append(conjugate)
        require(orbit <= remaining, "Conjugacy classes overlap")
        remaining.difference_update(orbit)
        classes.append((representative, orbit))
    require(sum(len(orbit) for _, orbit in classes) == len(group),
            "Conjugacy classes do not cover the group")
    return classes


def subgroup_generated_by(elements, group):
    """Generate a subgroup without presupposing its order or normality."""
    generators = []
    subgroup = {IDENTITY}
    # Only add a new generator when it actually enlarges the subgroup.
    for element in sorted(elements):
        if element in subgroup:
            continue
        generators.append(element)
        subgroup = {IDENTITY}
        queue = [IDENTITY]
        for x in queue:
            for g in generators:
                y = MATRIX.mul(x, g)
                require(y in group, "Generated subgroup leaves the ambient group")
                if y not in subgroup:
                    subgroup.add(y)
                    queue.append(y)
    return subgroup


def compute_profile(row):
    """Compute one exact profile, checking the recorded order and age counts."""
    case = row["index"]
    require(type(case) is int and 1 <= case <= 106, "Invalid case number")
    require(type(row["order"]) is int and row["order"] >= 1,
            f"Case {case}: invalid group order")
    require(type(row["junior_classes"]) is int and row["junior_classes"] >= 0,
            f"Case {case}: invalid junior-class count")
    require(type(row["age2_classes"]) is int and row["age2_classes"] >= 0,
            f"Case {case}: invalid age-two count")
    raw = row["actual_generators"]
    require(isinstance(raw, list), f"Case {case}: generators must be a list")
    for g in raw:
        require(isinstance(g, list) and len(g) == 4 and
                all(isinstance(line, list) and len(line) == 4 and
                    all(type(x) is int for x in line) for line in g),
                f"Case {case}: expected integral 4 by 4 matrices")
    generators = [MATRIX.mat(g) for g in raw]
    group = MATRIX.closure(raw, row["order"])
    spectral = Counter(MATRIX.charpoly(g) for g in group)
    stored_spectral = Counter()
    for polynomial, count in row["characteristic_polynomial_distribution"]:
        key = tuple(polynomial)
        require(key not in stored_spectral and type(count) is int and count > 0,
                f"Case {case}: invalid spectral distribution")
        stored_spectral[key] = count
    require(spectral == stored_spectral, f"Case {case}: spectral counts differ")
    classes = conjugacy_classes(group, generators)
    counts = Counter({0: 0, 1: 0, 2: 0})
    sizes = {0: [], 1: [], 2: []}
    juniors = set()
    for representative, orbit in classes:
        difference = [[IDENTITY[i][j] - representative[i][j] for j in range(4)]
                      for i in range(4)]
        codimension = rank(difference)
        require(codimension in (0, 2, 4), f"Case {case}: odd fixed-space codimension")
        age = codimension // 2
        counts[age] += 1
        sizes[age].append(len(orbit))
        if age == 1:
            juniors.update(orbit)
    require(counts[0] == 1, f"Case {case}: identity age count differs")
    require(counts[1] == row["junior_classes"],
            f"Case {case}: computed {counts[1]} junior classes, recorded {row['junior_classes']}")
    require(counts[2] == row["age2_classes"],
            f"Case {case}: computed {counts[2]} age-two classes, recorded {row['age2_classes']}")
    junior_subgroup = subgroup_generated_by(juniors, group)
    fixed_equations = [[g[i][j] - IDENTITY[i][j] for j in range(4)]
                       for g in generators for i in range(4)]
    return {
        "case": case,
        "group_order": len(group),
        "age_counts": {str(age): counts[age] for age in range(3)},
        "class_count": len(classes),
        "class_sizes_by_age": {str(age): sorted(sizes[age]) for age in range(3)},
        "fixed_dimension": 4 - rank(fixed_equations),
        "junior_generated_order": len(junior_subgroup),
        "generated_by_juniors": junior_subgroup == group,
        "abelian": all(len(orbit) == 1 for _, orbit in classes),
    }


def verify_profiles(catalogue=DEFAULT_CATALOGUE, cases=None):
    """Return fresh profiles in catalogue order; optionally restrict cases."""
    rows = json.loads(Path(catalogue).read_text())
    require(isinstance(rows, list) and [r["index"] for r in rows] == list(range(1, 107)),
            "The catalogue must contain cases 1 through 106 exactly once")
    selected = set(range(1, 107)) if cases is None else set(cases)
    require(selected and all(type(case) is int and 1 <= case <= 106 for case in selected),
            "Selected cases must be integers between 1 and 106")
    return [compute_profile(row) for row in rows if row["index"] in selected]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", type=int, action="append", dest="cases",
                        help="check one case; may be repeated (default: all 106)")
    parser.add_argument("--catalogue", type=Path, default=DEFAULT_CATALOGUE,
                        help="catalogue input (default: bundled 106-case catalogue)")
    arguments = parser.parse_args()
    started = time.monotonic()
    profiles = verify_profiles(arguments.catalogue, arguments.cases)
    print(json.dumps({
        "status": "PASS", "cases": len(profiles),
        "group_elements": sum(row["group_order"] for row in profiles),
        "seconds": round(time.monotonic() - started, 3),
        "scope": "Exact matrix closure, conjugacy classes, age counts, fixed spaces and junior-generated subgroups. Crepant-resolution existence is supplied by the separately documented geometric arguments.",
        "profiles": profiles,
    }, indent=2))


if __name__ == "__main__":
    main()
