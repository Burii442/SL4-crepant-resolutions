# Computational Supplement

**Dominik Burek and Sławomir Cynk: Crepant resolutions of four-dimensional finite quotients.**

Numbered directories retain the **245 integral catalogue indices**. The manuscript uses **106 quotient classes**, whose ordered generators appear in Appendix A. The [current case catalogue](../cases/README.md) and [numbering map](../cases/index.json) identify the manuscript case for every legacy entry. Equivalent representations share the stated representative's geometric construction; `catalogue.json` records that representative. All arithmetic is exact. Polynomial variable and generator orders are part of the mathematical data.

## Supported fresh verification

Install SageMath with Singular, GAP and SymPy available through its environment. The exhaustive geometric endpoint checks also require a C++17 compiler (`c++`, `g++`, or `clang++`) on PATH. The unified runner uses the Python standard library and finds `sage` on PATH; `--sage /path/to/sage` overrides that choice.

The reference runs use SageMath 10.9, its Python 3.14.3, Singular 4.4.1,
GAP 4.14.0 and SymPy 1.14.0. The wrapper itself also runs under Python 3.9.

From the `legacy245/` directory:

```sh
python3 run_verification.py --list
python3 run_verification.py --profile all --output-dir /tmp/sl4-full-verification
```

The output directory must be new or empty and outside this supplement. The runner creates an isolated copy of the supported inputs. Every selected command executes afresh; no saved PASS file or checkpoint is used. `verification.json` is updated during the run. It records the exact commands, per-step scope, elapsed time, return codes and log hashes; `input_manifest.json` identifies the copied inputs by SHA-256. Fresh mathematical certificates and complete logs remain under `steps/`. A failed or interrupted check cannot produce an overall PASS. By default execution stops at the first failure; `--keep-going` continues independent checks while preserving the failed overall status.

Full elimination and simultaneous Cox-generation tests can take hours. There is no short default timeout. For a specific scope:

```sh
python3 run_verification.py --profile core --output-dir /tmp/sl4-core
python3 run_verification.py --profile geometry --output-dir /tmp/sl4-geometry
python3 run_verification.py --profile bindings --output-dir /tmp/sl4-bindings
python3 run_verification.py --profile cox --output-dir /tmp/sl4-cox
python3 run_verification.py --profile endpoints --output-dir /tmp/sl4-endpoints
python3 run_verification.py --steps catalogue,geometry-234 --output-dir /tmp/sl4-selected
```

A PASS applies only to the selected steps. In particular, `core` does not include the 21 representation bindings, full Cox generation, endpoint proofs or the three detailed blow-up packages. `bindings` checks all 21 Cox representations and their polynomial inputs. `--list` gives the complete step names and scope. Missing supported entry points are reported as errors, never silently skipped. Resumption options belonging to individual algebra validators are documented separately; the unified fresh runner does not request resumption.

When a Cox step follows its binding step in the same fresh run, the runner also compares the exact Hilbert series of the certified complete ordinary kernel with the freshly recomputed commutator Molien series. It checks common input hashes and compares rational functions by exact coefficient cross-products. Only a successful comparison is recorded in `ordinary_generation`. Legacy case 194 (manuscript case 75) instead uses its dedicated complete monomial-generation argument for the supported 83-relation model. The `all` profile performs these combined checks; a Cox-only profile retains its stated polynomial-map scope.

Completed fresh binding and Cox runs from separate isolated copies can be joined
with `python3 compare_generation_reports.py --pairs /path/to/pairs.json --output /tmp/sl4-joined.json`.
The input is an explicit JSON list of objects with `case`, `binding_report`,
`cox_directory`, `binding_snapshot` and `cox_snapshot` paths. This command checks
the actual snapshot bytes against each report, the complete scopes, agreement
of the mathematical inputs and exact Molien/Hilbert equality. It records the
program hashes in both snapshots, allowing different tested program versions
to be identified. It compares the supplied completed runs and does not rerun
their calculations. Case 194 remains a separate dedicated certificate.

## Data and exact scope

| File or program | Meaning and scope |
|---|---|
| `catalogue.json` | The 245 specified integral representations, ordered generators, group orders, age-class counts, decisions and proof families. |
| `criteria_incidence.csv`; `verify_criteria.py` | The recorded applicability sets of the ten criteria; checks coverage and decision consistency, not their geometric justifications. |
| `criteria_geometry/` | Fresh checks for manuscript sieves D/G/H/J (legacy keys D/H/I/Z): all 26 cotangent character/reflection checks, 25 exact D/G/H intertwiners, the complete equivariant fan calculation and all eight tower group identifications. Included in `core` and `all`; the cited geometric existence/classification theorems remain separate inputs. |
| `verify_catalogue.py` | Reconstructs all 245 groups and checks determinants, conjugacy classes, age counts, junior subgroups, fixed spaces and invariant alternating forms by two methods; checks exact applicability of A/B/C and consistency of the recorded coverage. |
| `representative_conjugacies.json`; `verify_representatives.py` | The 73 explicit rational conjugating matrices, checked afresh by comparing the full groups: 2,342 element comparisons. These affine identifications do not assert integral conjugacy of compact actions. |
| `abelian_characters.csv`; `<index>/triangulation.json` | Character lattices and all 46 positive abelian fans. |
| `<index>/invariant_ring/`; `verify_geometry.py` | Twelve invariant presentations: exact invariance, complete elimination kernels and Molien/Hilbert equality. Also checks all 46 fans, 337 tetrahedra and 1,958 pair intersections, including coherence and full coverage. |
| `geometry_proofs/` | Supported complete geometric calculations for 132–137, 234–235 and 236–237, including saturated charts, input binding, complete stratum kernels and boundary checks. See its README. |
| `<index>/model.json`, `<index>/invariants.json` | The ordered Cox presentations for 21 representatives. See [COX_README.md](COX_README.md). |
| `binding_verification/verify_binding.py` | Reconstructs each complete group, conjugates it to the polynomial coordinates, covers every junior class, checks exact commutator invariance, valuations, stored initial forms and finite character grading, and recomputes the commutator Molien series. This does not by itself establish generation of the invariant algebra. |
| `full_verification/verify_cox.py` | Fresh ordinary kernels, junior initial tests and simultaneous character-compatible generation tests; individual stage scopes and limitations are reported explicitly. |
| `194/verify194.py` | Dedicated binding and verification of the 83-relation model and six slices for manuscript case 75. |
| `endpoint_verification/verify_endpoints.py` | Supported positive chart and negative point/cone checks, distinct from the full-generation checks. |

Direct entry points also locate their distributed inputs relative to their own files. The unified runner is preferred because older uniform programs write their fresh summary JSON beside the inputs; the runner confines these writes to its isolated copy. The runner supplies a private `DOT_SAGE` directory and records its path and ownership in `verification.json`. If the output path contains whitespace, it selects a fresh temporary cache without whitespace so that Sage's external GAP interface can read its temporary input files. Nested geometric checks inherit that cache. Temporary caches are removed only after every subprocess group created by the runner has exited; output-local caches remain with the run.

An interrupted step terminates its own registered subprocess group, including descendants whose group leader has already exited. After a bounded grace period following `SIGTERM`, surviving group members receive `SIGKILL`. The report records whether the complete group exited. If its state cannot be established, the temporary cache is retained and the interruption remains explicitly recorded.
