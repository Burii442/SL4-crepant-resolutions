# Case 064 — YES

Current manuscript number **64**, group order **192**. Printed sieve(s): **I**.

The ordered integral generators are copied from old catalogue entry **177**. All old entries in this complex-conjugacy class: 177.

CrystCat class: system 33, Q-class 12 (global Q-class 223).

Junior conjugacy classes: 4; age-two classes: 12.

## Inputs and matrix transfer

The machine-readable [case index](../../cases/index.json) contains the ordered generators and the complete execution plan. [The reduction verifier](../../manuscript106/catalogue/verify_reduction.py) checks the full conjugating group sets.

- [manuscript106/catalogue/catalogue.json](../../manuscript106/catalogue/catalogue.json)
- [manuscript106/catalogue/catalogue_reduced.json](../../manuscript106/catalogue/catalogue_reduced.json)
- [manuscript106/catalogue/conjugacy_certificates.json](../../manuscript106/catalogue/conjugacy_certificates.json)
- [legacy245/catalogue.json](../../legacy245/catalogue.json)
- [legacy245/criteria_incidence.csv](../../legacy245/criteria_incidence.csv)
- [legacy245/177/model.json](../../legacy245/177/model.json)
- [legacy245/177/invariants.json](../../legacy245/177/invariants.json)

## Mathematical checks

- **Sieve I.** Bind the actual representation, prove complete Cox generation including ordinary invariant generation, and verify the positive charts or negative geometric obstruction. Reference key: `Yamagishi;ADHL;SchmittMUVAK`.

Run the supported old-catalogue stages from the repository root:

```sh
python3 legacy245/run_verification.py --steps catalogue,criteria,representatives,binding-177,cox-177,endpoint-177 --output-dir /tmp/sl4-case-064
```

The selected global stages also check other entries. For Cox cases the order binding → Cox → endpoint is intentional; ordinary invariant generation must be checked with the same inputs.

## Scope

- A stored YES/NO label and the existence of program files do not constitute a fresh proof run.
- The cited geometric theorems and their mathematical deductions remain part of the proof.
- Run binding, full Cox and endpoint in this order in the same fresh run so that the exact Hilbert–Molien generation comparison is performed; case 194 uses its dedicated paper83 argument.
