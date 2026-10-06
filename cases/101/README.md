# Case 101 — YES

Current manuscript number **101**, group order **12**. Printed sieve(s): **C**.

The ordered integral generators are copied from old catalogue entry **238**. All old entries in this complex-conjugacy class: 238.

CrystCat class: system 20, Q-class 1 (global Q-class 90).

Junior conjugacy classes: 5; age-two classes: 6.

## Inputs and matrix transfer

The machine-readable [case index](../../cases/index.json) contains the ordered generators and the complete execution plan. [The reduction verifier](../../manuscript106/catalogue/verify_reduction.py) checks the full conjugating group sets.

- [manuscript106/catalogue/catalogue.json](../../manuscript106/catalogue/catalogue.json)
- [manuscript106/catalogue/catalogue_reduced.json](../../manuscript106/catalogue/catalogue_reduced.json)
- [manuscript106/catalogue/conjugacy_certificates.json](../../manuscript106/catalogue/conjugacy_certificates.json)
- [legacy245/catalogue.json](../../legacy245/catalogue.json)
- [legacy245/criteria_incidence.csv](../../legacy245/criteria_incidence.csv)
- [legacy245/abelian_characters.csv](../../legacy245/abelian_characters.csv)
- [legacy245/238/triangulation.json](../../legacy245/238/triangulation.json)

## Mathematical checks

- **Sieve C.** Bind the actual character lattice and check a coherent unimodular triangulation covering the complete junior simplex. Reference key: `DHZ`.

Run the supported old-catalogue stages from the repository root:

```sh
python3 legacy245/run_verification.py --steps catalogue,criteria,representatives,geometry --output-dir /tmp/sl4-case-101
```

The selected global stages also check other entries. For Cox cases the order binding → Cox → endpoint is intentional; ordinary invariant generation must be checked with the same inputs.

Additional checks required for the complete indexed scope:

- `abelian-lattice`: Recompute the quotient lattice from the actual matrix character. Entry point: [extensions/abelian/verify.py](../../extensions/abelian/verify.py).

The repository runner combines these additional checks with the legacy stages. The legacy-only command above does not run extensions.

## Scope

- A stored YES/NO label and the existence of program files do not constitute a fresh proof run.
- The cited geometric theorems and their mathematical deductions remain part of the proof.
