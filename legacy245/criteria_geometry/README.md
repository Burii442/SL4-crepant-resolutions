# Exact identifications for manuscript sieves D, G, H and J

The programs retain the legacy keys D, H, I and Z, corresponding respectively to manuscript sieves D, G, H and J. With SageMath and GAP available, run from the repository root:

```sh
python3 legacy245/run_verification.py --steps criteria-geometry --output-dir ../sl4-results/criteria-geometry-001
```

The directory must be new or empty. The runner copies the required inputs,
reconstructs the GAP matrix list from `catalogue.json`, and writes live logs
and input hashes. Read `verification.json` in the output directory and
`steps/criteria-geometry/result/report.json` for the detailed calculations.
It never reads old reports.

- **D:** all 26 recorded cotangent representations have a faithful irreducible
  two-dimensional constituent `psi`, with `chi=psi+psi*`; the elements acting
  as reflections on `psi` generate the whole group. Actual class characters
  and representatives are written out. The 15 positive entries are also
  explicitly intertwined with the displayed A2, G(m,1,2), or G4 models.
- **G (legacy H):** five full four-dimensional representations are intertwined with
  `det(U) direct_sum U` for the specified rational three-dimensional model.
  Its nine reflections generate the complete group of order 48.
- **H (legacy I):** five full representations are intertwined with the common even-sign
  model and its coordinate involution. Exact simplex intersections, lattice
  determinants, strict convex support inequalities and involution action are
  checked for the eight-cone fan. Stable strata have a positive fixed tangent
  direction. The two isolated fixed points of the alternative diagonal are
  checked by direct differentiation.
- **J (legacy Z):** the eight supplied rational intertwiners identify the complete
  catalogue groups with the explicit tower models of order `4*m^2`. Each
  model's four generators, rotation/reflection identities, whole matrix
  groups and intertwining equations are recomputed.

There are **25 intertwiners** in the common D/G/H computation: 15 + 5 + 5.
The 26 cotangent checks and eight tower checks are distinct counts. The
matrices in `tower_matrices.json` are exact inputs whose equations are
tested by the verifier.

These computations supply the concrete representations and toric geometry
used in the article. They do not reprove the classification or existence
theorems cited to deduce crepant resolvability from those hypotheses.
