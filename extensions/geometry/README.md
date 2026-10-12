# Exact geometry checks for E and F

These SageMath programs reproduce the manuscript's complete-intersection
and double-cover computations. Inputs come from this repository's `legacy245/`
and `manuscript106/catalogue/`; no manuscript source, private directory or
historical calculation archive is required.

From the repository root:

```sh
sage -python extensions/geometry/verify_E.py --output-dir /tmp/sl4-sieve-E
sage -python extensions/geometry/verify_F.py --output-dir /tmp/sl4-sieve-F
```

Both output directories must be new or empty. The programs leave the supplied
inputs unchanged. They produce `report.json` and `verification.log`, with
input hashes, execution time, and a final `PASS`, `FAILED`, or `INTERRUPTED`
status. A nonzero exit status means that the check did not pass. Python
optimization (`-O` or `PYTHONOPTIMIZE`) is rejected because these validators
use assertions for exact mathematical checks.

Optional `--legacy-root PATH` replaces the legacy input directory. Repository
defaults are resolved relative to the installed programs, independently of
the working directory. The example matrices are always compared between the
current and legacy catalogues. An optional `--paper /external/path/arxiv_3.tex`
additionally checks the corresponding section's displayed matrices. The
external paper must contain the appropriate `sec:sieve-E` or `sec:sieve-F`
section label; missing, malformed or mismatching supplied files fail the check.
The example report records `paper_display.status` as `not_requested` when
`--paper` is omitted and `PASS` only after a successful comparison. This
optional audit does not affect the scope of the algebraic calculations.
`--help` works under ordinary Python; the calculations
require the Sage Python interpreter, Singular and GAP from the Sage environment.

## E: complete intersections

E reconstructs all 20 applicable old catalogue groups and their exact
representative conjugacies. It checks full invariant presentations for 72 and
85 by invariance, graph elimination and Molien/Hilbert equality, then their
saturated blow-up charts, Jacobian smoothness and discrepancy calculations.
It also binds example 236 to current catalogue case 100 and checks its
discriminant and stratum parametrizations. With `--paper`, it additionally
compares the displayed generators.

By default E executes the distributed `legacy245/geometry_proofs/run.py`
afresh for 132, 234 and 236. Their work, certificates and individual logs are
saved in `OUTPUT/geometry_132`, `OUTPUT/geometry_234`, and
`OUTPUT/geometry_236`. The final report binds every expected source file and
every required stage log, checks the completion assertions, and records these
runs as `fresh_in_this_invocation`. `--singular PATH` and `--gap PATH` can
override executable discovery for these detailed stages.

Existing detailed runs can be supplied explicitly:

```sh
sage -python extensions/geometry/verify_E.py \
  --geometry-runs /tmp/sl4-sieve-E \
  --output-dir /tmp/sl4-sieve-E-rebinding
```

The supplied directory must contain all three `geometry_<index>/run.json`
files and their logs. In this mode the group, ring, 72/85 charts and catalogue
checks still run afresh, as does the optional external-paper comparison,
while the three supplied detailed runs are
hash-checked and labelled `provided_prior_outputs`. This is a comparison with
prior evidence, not a new execution of those three geometric constructions.
The recorded mode must be preserved in any higher-level summary.

## F: double covers

F reconstructs all 29 applicable old catalogue groups and their conjugacies.
It verifies ten full invariant rings, completing the square and checking
their reduced branch equations. It then checks both saturated charts of
each required plane blow-up, smooth final branches, the transverse
cross-factor intersections, and the exceptional discriminant construction
for 127. Every one of these checks is recomputed; F consumes no retained
calculation logs.

Current case 106 is old index 245. Its five generators have degrees
2, 2, 4, 6, 10 and its relation has degree 20. Its branch factors are
`c*(a^2-4*c)*(2*b^3-d)*(22*b^3-9*d)`. F checks its invariant ring and both
plane branch constructions using `legacy245/245/invariant_ring/`.

## Numbering and scope

| Sieve | Old representatives | Current paper cases |
|---|---|---|
| E | 72, 85, 132, 234, 236 | 23, 26, 42, 99, 100 |
| F | 91, 107, 127, 145, 190, 204, 219, 224, 241, 245 | 28, 33, 41, 47, 74, 79, 87, 90, 104, 106 |

The JSON reports use old integral catalogue indices for the algebraic inputs.
The repository's catalogue mapping supplies the corresponding current case
numbers. These computations verify the algebra and charts used in the paper;
projectivity, global gluing and crepancy also use the geometric arguments
stated there. Neither a full invariant-ring presentation alone nor a stored
`PASS` label proves existence of a crepant resolution.

For D, G, H and J, use the
[representation and geometry checks](../../legacy245/criteria_geometry/README.md).
Their instructions run the calculations in an isolated output directory.
