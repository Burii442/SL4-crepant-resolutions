# Legacy case 243

This calculation supports [manuscript case 105](../../cases/105/README.md). All indices below use the legacy 245-entry catalogue.

Catalogue entries: 243, 244. Final decision: **NO**.

The public presentation has 6 ordered invariant generators, 4 exceptional variables, and 2 displayed relations. Read `model.json` and `invariants.json` together using the conventions in `../COX_README.md`. The number of displayed equations depends on the chosen generating basis; it is not the codimension.

The invariant and junior data available directly in the normalized input include: `junior_representatives_in_coordinates`, `junior_initial_generators`.

## Run the verification

From the `legacy245/` directory, run:

```sh
python3 run_verification.py --steps binding-243,cox-243,endpoint-243 --output-dir /tmp/sl4-legacy-243
```

Use a new or empty output directory. This runs the complete representation binding, full polynomial-map criterion and geometric endpoint, and compares the fresh commutator Molien and complete-kernel Hilbert series. The isolated input hashes, actual completed scopes and logs are recorded in the result. See `../COX_README.md` for conventions and exact scope.
