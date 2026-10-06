# Case 035 — YES

Current manuscript number **35**, group order **16**. Printed sieve(s): **I**.

The ordered integral generators are copied from old catalogue entry **114**. All old entries in this complex-conjugacy class: 114.

CrystCat class: system 26, Q-class 2 (global Q-class 155).

Junior conjugacy classes: 2; age-two classes: 4.

## Inputs and matrix transfer

The machine-readable [case index](../../cases/index.json) contains the ordered generators and the complete execution plan. [The reduction verifier](../../manuscript106/catalogue/verify_reduction.py) checks the full conjugating group sets.

- [manuscript106/catalogue/catalogue.json](../../manuscript106/catalogue/catalogue.json)
- [manuscript106/catalogue/catalogue_reduced.json](../../manuscript106/catalogue/catalogue_reduced.json)
- [manuscript106/catalogue/conjugacy_certificates.json](../../manuscript106/catalogue/conjugacy_certificates.json)
- [legacy245/catalogue.json](../../legacy245/catalogue.json)
- [legacy245/criteria_incidence.csv](../../legacy245/criteria_incidence.csv)
- [legacy245/114/model.json](../../legacy245/114/model.json)
- [legacy245/114/invariants.json](../../legacy245/114/invariants.json)

## Mathematical checks

- **Sieve I.** Bind the actual representation, prove complete Cox generation including ordinary invariant generation, and verify the positive charts or negative geometric obstruction. Reference key: `Yamagishi;ADHL;SchmittMUVAK`.

Run the supported old-catalogue stages from the repository root:

```sh
python3 legacy245/run_verification.py --steps catalogue,criteria,representatives,binding-114,cox-114,endpoint-114 --output-dir /tmp/sl4-case-035
```

The selected global stages also check other entries. For Cox cases the order binding → Cox → endpoint is intentional; ordinary invariant generation must be checked with the same inputs.

## Scope

- A stored YES/NO label and the existence of program files do not constitute a fresh proof run.
- The cited geometric theorems and their mathematical deductions remain part of the proof.
- Run binding, full Cox and endpoint in this order in the same fresh run so that the exact Hilbert–Molien generation comparison is performed; case 194 uses its dedicated paper83 argument.
