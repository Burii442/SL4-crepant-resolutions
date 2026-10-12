# Legacy case 173

This calculation supports [manuscript case 62](../../cases/062/README.md). All indices below use the legacy 245-entry catalogue.

Catalogue entries: 173. Final decision: **NO**.

The public presentation has 25 ordered invariant generators, 3 exceptional variables, and 835 displayed relations. Read `model.json` and `invariants.json` together using the conventions in `../COX_README.md`. The number of displayed equations depends on the chosen generating basis; it is not the codimension.

The invariant and junior data available directly in the normalized input include: `junior_representatives_in_coordinates`, `junior_initial_generators`, `coordinate_change_from_catalogue`.

## Run the verification

From the `legacy245/` directory, run:

```sh
python3 run_verification.py --steps binding-173,cox-173,endpoint-173 --output-dir /tmp/sl4-legacy-173
```

Use a new or empty output directory. This runs the complete representation binding, full polynomial-map criterion and geometric endpoint, and compares the fresh commutator Molien and complete-kernel Hilbert series. The isolated input hashes, actual completed scopes and logs are recorded in the result. See `../COX_README.md` for conventions and exact scope.

## Exact verification of the 835 physical relations

The full verifier checks every public equation after specializing the exceptional parameters to one. It first proves the complete ordinary kernel independently. To make the largest physical substitutions practical, `full_verification/native_checks/kronecker_images.py` performs exact arithmetic in `QQ[T]`.

For each relation, the verifier derives the homogeneous image degree `D` from the actual invariant polynomials and checks homogeneity. On this homogeneous component, it substitutes `x4 = 1`, `x1 = T`, `x2 = T^(D+1)`, and `x3 = T^((D+1)^2)`. The first three exponents uniquely determine the fourth, and their base-`D+1` encoding is injective. Consequently, a zero encoded polynomial proves that the original four-variable image is zero. No numerical sample or modular image is used.

This image check proves one ideal containment. The reverse ordinary containment, saturation in all three exceptional parameters, and all three simultaneous initial-kernel containments are separate required stages of the same full run. A partial log of the image checks does not certify the Cox presentation.
