# Case 052 — YES

Current manuscript number **52**, group order **48**. Printed sieve(s): **G**.

The ordered integral generators are copied from old catalogue entry **154**. All old entries in this complex-conjugacy class: 154, 155, 156, 157, 158.

CrystCat class: system 25, Q-class 6 (global Q-class 148).

Junior conjugacy classes: 6; age-two classes: 3.

## Inputs and matrix transfer

The machine-readable [case index](../../cases/index.json) contains the ordered generators and the complete execution plan. [The reduction verifier](../../manuscript106/catalogue/verify_reduction.py) checks the full conjugating group sets.

- [manuscript106/catalogue/catalogue.json](../../manuscript106/catalogue/catalogue.json)
- [manuscript106/catalogue/catalogue_reduced.json](../../manuscript106/catalogue/catalogue_reduced.json)
- [manuscript106/catalogue/conjugacy_certificates.json](../../manuscript106/catalogue/conjugacy_certificates.json)
- [legacy245/catalogue.json](../../legacy245/catalogue.json)
- [legacy245/criteria_incidence.csv](../../legacy245/criteria_incidence.csv)
- [legacy245/criteria_geometry/README.md](../../legacy245/criteria_geometry/README.md)

## Mathematical checks

- **Sieve G.** Identify the determinant extension and its three-dimensional reflection model; apply the cited existence theorem. Reference key: `IshiiNimura`.

Run the supported old-catalogue stages from the repository root:

```sh
python3 legacy245/run_verification.py --steps catalogue,criteria,representatives,criteria-geometry --output-dir /tmp/sl4-case-052
```

The selected global stages also check other entries. For Cox cases the order binding → Cox → endpoint is intentional; ordinary invariant generation must be checked with the same inputs.

## Scope

- A stored YES/NO label and the existence of program files do not constitute a fresh proof run.
- The cited geometric theorems and their mathematical deductions remain part of the proof.
