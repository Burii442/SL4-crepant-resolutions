# Case 178

Catalogue entries: 178. Final decision: **NO**.

The public presentation has 18 ordered invariant generators, 5 exceptional variables, and 2051 displayed relations. Read `model.json` and `invariants.json` together using the conventions in `../COX_README.md`. The number of displayed equations depends on the chosen generating basis; it is not the codimension.

The invariant and junior data available directly in the normalized input include: `junior_representatives_in_coordinates`, `canonical_juniors`, `junior_initial_generators`, `coordinate_change_from_catalogue`.

## Run the verification

From the supplement directory, run:

```sh
python3 run_verification.py --steps binding-178,cox-178,endpoint-178 --output-dir /tmp/asl4-case-178
```

Use a new or empty output directory. This runs the complete representation binding, full polynomial-map criterion and geometric endpoint, and compares the fresh commutator Molien and complete-kernel Hilbert series. The isolated input hashes, actual completed scopes and logs are recorded in the result. See `../COX_README.md` for conventions and exact scope.
