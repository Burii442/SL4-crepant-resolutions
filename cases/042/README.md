# Case 042 — YES

Current manuscript number **42**, group order **24**. Printed sieve(s): **E**.

The ordered integral generators are copied from old catalogue entry **132**. All old entries in this complex-conjugacy class: 132, 133, 134, 135, 136, 137.

CrystCat class: system 24, Q-class 2 (global Q-class 139).

Junior conjugacy classes: 4; age-two classes: 3.

## Inputs and matrix transfer

The machine-readable [case index](../../cases/index.json) contains the ordered generators and the complete execution plan. [The reduction verifier](../../manuscript106/catalogue/verify_reduction.py) checks the full conjugating group sets.

- [manuscript106/catalogue/catalogue.json](../../manuscript106/catalogue/catalogue.json)
- [manuscript106/catalogue/catalogue_reduced.json](../../manuscript106/catalogue/catalogue_reduced.json)
- [manuscript106/catalogue/conjugacy_certificates.json](../../manuscript106/catalogue/conjugacy_certificates.json)
- [legacy245/catalogue.json](../../legacy245/catalogue.json)
- [legacy245/criteria_incidence.csv](../../legacy245/criteria_incidence.csv)
- [legacy245/geometry_proofs/132](../../legacy245/geometry_proofs/132)

## Mathematical checks

- **Sieve E.** Check complete invariant presentations and the stated blow-up charts, including the separate 132, 234 and 236 geometric packages. Reference key: `manuscript Sieve E`.

Run the supported old-catalogue stages from the repository root:

```sh
python3 legacy245/run_verification.py --steps catalogue,criteria,representatives,geometry,geometry-132 --output-dir /tmp/sl4-case-042
```

The selected global stages also check other entries. For Cox cases the order binding → Cox → endpoint is intentional; ordinary invariant generation must be checked with the same inputs.

Additional checks required for the complete indexed scope:

- `sieve-e`: Additional matrix-to-invariant-ring binding, blow-up chart and discrepancy checks from the current Sieve E audit. Entry point: [extensions/geometry/verify_E.py](../../extensions/geometry/verify_E.py).

The repository runner combines these additional checks with the legacy stages. The legacy-only command above does not run extensions.

## Scope

- A stored YES/NO label and the existence of program files do not constitute a fresh proof run.
- The cited geometric theorems and their mathematical deductions remain part of the proof.
