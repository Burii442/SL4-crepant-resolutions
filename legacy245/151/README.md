# Case 151

Catalogue entries: 151, 152. Final decision: **YES**.

The public presentation has 14 ordered invariant generators, 4 exceptional variables, and 153 displayed relations. Read `model.json` and `invariants.json` together using the conventions in `../COX_README.md`. The number of displayed equations depends on the chosen generating basis; it is not the codimension.

The invariant and junior data available directly in the normalized input include: `canonical_juniors`, `junior_initial_generators`, `canonical_conjugator`.

## Run the verification

From the supplement directory, run:

```sh
python3 run_verification.py --steps binding-151,cox-151,endpoint-151 --output-dir /tmp/asl4-case-151
```

Use a new or empty output directory. This runs the complete representation binding, full polynomial-map criterion and geometric endpoint, and compares the fresh commutator Molien and complete-kernel Hilbert series. The isolated input hashes, actual completed scopes and logs are recorded in the result. See `../COX_README.md` for conventions and exact scope.
