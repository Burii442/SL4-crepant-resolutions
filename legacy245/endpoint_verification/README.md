# Complete geometric endpoint verification

Run one representative, or omit `--case` to run all 21:

```
sage -python verify_endpoints.py --case 143 --output-dir /tmp/endpoint143
sage -python verify_endpoints.py --output-dir /tmp/all-endpoints
```

Requirements: SageMath (tested with 10.9), its Singular installation, and a C++17 compiler (`c++`, `g++`, or `clang++`). All inputs are included in this supplement. There are no imports or data dependencies on an author's workspace, review directory, historical log, or unpacked source archive. The output directory can be anywhere writable; the installed input tree is not modified.

A successful `report.json` has `status: ALL_REQUESTED_ENDPOINT_CHECKS_PASS`, `complete: true`, and exactly the requested cases. It records input and verifier hashes and rejects changes during a run. A failed or interrupted calculation cannot produce that status. Each case also emits its mathematical certificate and, where appropriate, fresh Singular programs and logs. Individual historical `status` fields in witness JSON files are not accepted as proof.

This is the **geometric endpoint** of the argument. The independent full Cox-ring identification, invariant generation, ordinary kernels and simultaneous MUVAK tests are supplied by the algebra verification entrypoints. Case 194 explicitly uses its separately named `paper83` model; its full algebra-and-geometry entrypoint is `../194/verify194.py`.

## What is recomputed

For cases 143, 151, 161, 167, 174, 177, 206, 221 and 222, `supports.cpp` exhausts every Boolean assignment satisfying the necessary condition that no full Cox relation has exactly one surviving monomial. It uses only logically forced assignments and visits both branches of every remaining variable. These are **necessary supports**, not an assertion that each support contains an actual point. All monomial masks are regenerated from the complete public `model.json`.

Exact rational cones then select every semistable support, check that the character is in its full-dimensional interior, and check the primitive support lattice. Divisor omissions, negative raw character and the invariant gcd tests verify admissibility. For the scalar-fixed method, all scalar degree equations are reconstructed from public invariant degrees, and the resulting support list is compared with the complete list of checked strata. Positivity of scalar degrees and projectivity reduce global smoothness to these fixed strata, as proved in the manuscript.

| Case | Full geometric check |
|---|---|
| 114 | Both characters: six scalar profiles give 163 candidate supports; 128 are excluded by a single surviving monomial. The remaining 35 strata are checked by full Jacobian ranks, emptiness, one full smooth slice (5,9), or two exact reduced points. Four global residual stabilizer checks prove freeness. |
| 143 | Six smooth coordinate opens; a fresh Groebner basis of their complement leaves one possible exact support, where the full ambient Jacobian has 12 invertible pivots. All 436 necessary semistable supports are accounted for. |
| 151 | All 16 minimal opens; exact linear eliminations, transported localizations, dimensions and complete localized singular ideals. |
| 161 | All 22 possible scalar-fixed supports: fresh stratum Groebner bases, full ambient derivatives, pivot inverses, residual unit identities and the four disjoint residual blocks. |
| 167 | All 23 possible scalar-fixed supports, with fresh Groebner bases and exact full-Jacobian rank certificates. |
| 174 | All 12 charts; 185 supplied smaller generators are first proved equal to the full public 589-generator ideal in both directions using a fresh weighted Groebner basis. Every localized elimination, inverse equation, unit condition and selected actual Jacobian minor is checked. |
| 177 | All 75 possible scalar-fixed supports, with fresh Groebner bases and exact Jacobian certificates. |
| 194 | Literal group binding, all six paper83 charts, every one of the 37 possible simplicial semistable bases, and admissibility. The full separate 194 entrypoint also rebuilds the Cox algebra. |
| 206 | All 12 minimal opens; exact eliminations and complete localized Jacobian ideals. |
| 221 | All 28 possible scalar-fixed supports, with fresh Groebner bases and exact Jacobian certificates. |
| 222 | All 789 necessary semistable supports are enumerated and checked for stability and freeness. Their 32 possible scalar-fixed supports are exhaustively checked using full ambient differentiation before specialization, Laurent unit pivots and fresh residual/empty-stratum ideals. No precomputed aface list is used. |
| 231 | All six negative-weight coordinate opens; three exact chart calculations and an explicitly reconstructed signed permutation of invariants exchanging chart pairs. Both ideal inclusions under that automorphism are verified against all 490 public equations. |
| 233 | All 26 simplicial semistable opens: 12 smooth gauges and 14 unit-ideal checks proving the cover, directly from all public relations. |
| 138, 140, 171, 173, 178, 179, 227, 243 | Every displayed obstruction point satisfies every full public equation. Exact ambient Jacobian ranks, support Smith indices, exceptional-prime omission regions, support cones and complete closed-region covers are recomputed. Applicable stabilizer characters and tangent eigenspaces are also reconstructed. |

The shared fixed-stratum verifier does not infer a rank from the number of recorded pivots: it reconstructs each actual matrix, replays every row operation and verifies every inverse modulo the freshly recomputed stratum ideal. Residual minors must be actual entries/minors of that matrix, and their supplied unit-ideal identities are multiplied out exactly.

The chart verifier checks source equations and invertible coefficients before eliminating a variable; localized rational substitutions preserve every required nonzero condition. Groebner-basis comparison establishes equality of the final presented ideal. Smoothness is established by the Jacobian criterion in characteristic zero. Selected minors suffice when they generate the unit ideal together with the chart equations and localizations; the argument does not claim to enumerate all minors when only a sufficient subset is needed.
