# Case 177

Catalogue entries: 177. Final decision: **YES**.

The public presentation has 27 ordered invariant generators, 4 exceptional variables, and 742 displayed relations. Read `model.json` and `invariants.json` together using the conventions in `../COX_README.md`. The number of displayed equations depends on the chosen generating basis; it is not the codimension.

The invariant and junior data available directly in the normalized input include: `junior_representatives_in_coordinates`, `junior_initial_generators`, `coordinate_change_from_catalogue`.

## Run the verification

From the supplement directory, run:

```sh
python3 run_verification.py --steps binding-177,cox-177,endpoint-177 --output-dir /tmp/asl4-case-177
```

Use a new or empty output directory. This runs the complete representation binding, full polynomial-map criterion and geometric endpoint, and compares the fresh commutator Molien and complete-kernel Hilbert series. The isolated input hashes, actual completed scopes and logs are recorded in the result. See `../COX_README.md` for conventions and exact scope.
