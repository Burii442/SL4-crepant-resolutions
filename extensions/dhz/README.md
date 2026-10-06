# Four DHZ invariant-ring presentations

This extension recomputes the full-group invariant rings and minimal
complete-intersection presentations for manuscript cases 45,65,66,105. These
are the algebraic half of the Dais–Henk–Ziegler counterexamples. Cox-ring
nonexistence is verified separately in `legacy245/`; this command does not
claim to repeat that argument.

Run from the repository root, with Python 3 and SageMath available:

```sh
python3 extensions/dhz/verify.py --output-dir /tmp/sl4-dhz-all
python3 extensions/dhz/verify.py --case 45 --case 105 --output-dir /tmp/sl4-dhz-small
python3 extensions/dhz/verify.py --case 65 --case 66 --output-dir /tmp/sl4-dhz-rotation
```

`--case` uses manuscript numbering, may be repeated and defaults to all four.
`--sage /path/to/sage` selects an installation. Outputs must be new or empty
and outside the repository. The launcher supplies a private Sage cache and
rejects optimized Python. SageMath 10.9 and Singular 4.4.1 were used for the
recorded tests. No Magma, network access or historical result file is required.

| Manuscript | Source | Group order | Embedding dimension | Relation degrees |
|---:|---:|---:|---:|---|
| 45 | 140 | 36 | 6 | 12,12 |
| 105 | 243 | 24 | 6 | 10,10 |
| 65 | 178 | 288 | 6 | 24,24 |
| 66 | 179 | 576 | 5 | 48 |

## Exact proof scopes

For 45/105, `small_ci.py` first compares the literal Singular matrices with
both distributed catalogues and reconstructs the complete group. The pinned
`finvar.lib` computes full invariant generators and a complete relation ideal.
The script verifies the explicit physical generators, both inclusions between
the printed relation ideal and the computed full kernel, dimension 4 and the
absence of linear relations. Every required numeric output is checked,
including generator order and degrees; a zero process exit or a printed PASS
label alone is never accepted. Raw fresh Singular source and logs are retained.

For 65/66, `rotation_ci.py` reconstructs the full 1152-element reflection group,
its 576-element determinant kernel and, where needed, its 288-element derived
group. An explicit rational conjugator binds every actual catalogue generator;
complete group equality is checked. A nonzero Jacobian proves independence
of the four parameters. Distinct reflection characters prove independence of
the free basis `1,delta,z,delta*z` or `1,L`. The checked monic equations give
these complete kernels; equality with the full group Molien series proves
invariant-algebra generation. Every displayed physical identity and the
minimal embedding at the origin are checked exactly.

`rotation_bindings.json` contains numerical witnesses recovered from the
older character-matching calculation, with rational conjugators solved from
linear equations. It contains no trusted PASS flag: every intertwining
identity, invertibility and full group equality is verified anew.

A successful `report.json` has
`status: ALL_REQUESTED_DHZ_INVARIANT_CHECKS_PASS`, `complete: true`, the exact
selected cases and the hash of every input/program. Individual certificates
record `actual_catalogue_binding`, `full_invariant_ring`,
`complete_relation_kernel`, `complete_intersection`, `minimal_embedding` and
`cox_nonexistence_recomputed` is explicitly false in the overall report.
Failures leave an unsuccessful report and return a nonzero exit code.

## Sources and attribution

The two `.sing` files preserve the project's original explicit invariant
calculations. `rotation_ci.py` adapts the mathematical proof from
`ASL4_report/revision_2026_09_11/counterexamples_audit/audit_rotation_ci.py`,
replacing local logs and historical certificate imports by fresh matrix
bindings. All supplied mathematical data are checked by fresh calculations.

The unchanged `singular/vendor/finvar.lib` is version 4.3.1.3 (February 2023),
by Agnes E. Heydtmann and Simon A. King. Its original author and procedure
headers are retained. The upstream Singular copyright notice and GPLv2 text
are included beside it; Singular permits GPL version 2 or version 3. This vendor
library is distributed under those terms, independently of any license chosen
for the authors' original repository code. `license_sources.json` records the
upstream notice/license URLs and hashes. See
[Singular](https://www.singular.uni-kl.de/) and its
[citation guidance](https://www.singular.uni-kl.de/index.php/how-to-cite-singular).

The counterexample question is Conjecture 1.1 in Dais–Henk–Ziegler,
[All abelian quotient C.I.-singularities admit projective crepant resolutions
in all dimensions](https://arxiv.org/abs/alg-geom/9704007).
