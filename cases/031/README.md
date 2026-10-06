# Case 031 — YES

Current manuscript number **31**, group order **16**. Printed sieve(s): **H**.

The ordered integral generators are copied from old catalogue entry **100**. All old entries in this complex-conjugacy class: 100, 101, 102, 103, 104.

CrystCat class: system 18, Q-class 4 (global Q-class 82).

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

- **Sieve H.** Identify the even-sign model, verify the coherent equivariant fan and the fixed-stratum calculation. Reference key: `manuscript Sieve H`.

Run the supported old-catalogue stages from the repository root:

```sh
python3 legacy245/run_verification.py --steps catalogue,criteria,representatives,criteria-geometry --output-dir /tmp/sl4-case-031
```

The selected global stages also check other entries. For Cox cases the order binding → Cox → endpoint is intentional; ordinary invariant generation must be checked with the same inputs.

## Scope

- A stored YES/NO label and the existence of program files do not constitute a fresh proof run.
- The cited geometric theorems and their mathematical deductions remain part of the proof.
