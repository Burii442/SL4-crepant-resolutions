# Exact identifications for criteria D, H, I and Z

Run all calculations afresh with SageMath and GAP:

```sh
sage -python criteria_geometry/run.py --output-dir /tmp/asl4-criteria-geometry
```

The directory must be new or empty. The entry point copies the required public
inputs, reconstructs the GAP matrix list from `catalogue.json`, and writes
separate live logs, input hashes and `report.json`. It never reads old reports.

- **D:** all 26 recorded cotangent representations have a faithful irreducible
  two-dimensional constituent `psi`, with `chi=psi+psi*`; the elements acting
  as reflections on `psi` generate the whole group. Actual class characters
  and representatives are written out. The 15 positive entries are also
  explicitly intertwined with the displayed A2, G(m,1,2), or G4 models.
- **H:** five full four-dimensional representations are intertwined with
  `det(U) direct_sum U` for the specified rational three-dimensional model.
  Its nine reflections generate the complete group of order 48.
- **I:** five full representations are intertwined with the common even-sign
  model and its coordinate involution. Exact simplex intersections, lattice
  determinants, strict convex support inequalities and involution action are
  checked for the eight-cone fan. Stable strata have a positive fixed tangent
  direction. The two isolated fixed points of the alternative diagonal are
  checked by direct differentiation.
- **Z:** the eight supplied rational intertwiners identify the complete
  catalogue groups with the explicit tower models of order `4*m^2`. Each
  model's four generators, rotation/reflection identities, whole matrix
  groups and intertwining equations are recomputed.

There are **25 intertwiners** in the common D/H/I computation: 15 + 5 + 5.
The 26 cotangent checks and eight tower checks are distinct counts. The
matrices in `tower_matrices.json` are input witnesses whose equations are
tested by the verifier.

These computations supply the concrete representations and toric geometry
used in the article. They do not reprove the classification or existence
theorems cited to deduce crepant resolvability from those hypotheses.
