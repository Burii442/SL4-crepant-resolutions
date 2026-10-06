# Case 073 — YES

Current manuscript number **73**, group order **12**. Printed sieve(s): **B**.

The ordered integral generators are copied from old catalogue entry **188**. All old entries in this complex-conjugacy class: 188, 189.

CrystCat class: system 15, Q-class 4 (global Q-class 67).

Junior conjugacy classes: 5; age-two classes: 0.

## Inputs and matrix transfer

The machine-readable [case index](../../cases/index.json) contains the ordered generators and the complete execution plan. [The reduction verifier](../../manuscript106/catalogue/verify_reduction.py) checks the full conjugating group sets.

- [manuscript106/catalogue/catalogue.json](../../manuscript106/catalogue/catalogue.json)
- [manuscript106/catalogue/catalogue_reduced.json](../../manuscript106/catalogue/catalogue_reduced.json)
- [manuscript106/catalogue/conjugacy_certificates.json](../../manuscript106/catalogue/conjugacy_certificates.json)
- [legacy245/catalogue.json](../../legacy245/catalogue.json)
- [legacy245/criteria_incidence.csv](../../legacy245/criteria_incidence.csv)

## Mathematical checks

- **Sieve B.** Compute the common fixed subspace. A positive dimension reduces the quotient to a resolved quotient of dimension at most three. Reference key: `BKR`.

Run the supported old-catalogue stages from the repository root:

```sh
python3 legacy245/run_verification.py --steps catalogue,criteria,representatives --output-dir /tmp/sl4-case-073
```

The selected global stages also check other entries. For Cox cases the order binding → Cox → endpoint is intentional; ordinary invariant generation must be checked with the same inputs.

## Scope

- A stored YES/NO label and the existence of program files do not constitute a fresh proof run.
- The cited geometric theorems and their mathematical deductions remain part of the proof.
