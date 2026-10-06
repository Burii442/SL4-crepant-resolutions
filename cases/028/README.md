# Case 028 — YES

Current manuscript number **28**, group order **18**. Printed sieve(s): **F**.

The ordered integral generators are copied from old catalogue entry **91**. All old entries in this complex-conjugacy class: 91, 92, 93, 94, 95.

CrystCat class: system 22, Q-class 5 (global Q-class 120).

Junior conjugacy classes: 3; age-two classes: 2.

## Inputs and matrix transfer

The machine-readable [case index](../../cases/index.json) contains the ordered generators and the complete execution plan. [The reduction verifier](../../manuscript106/catalogue/verify_reduction.py) checks the full conjugating group sets.

- [manuscript106/catalogue/catalogue.json](../../manuscript106/catalogue/catalogue.json)
- [manuscript106/catalogue/catalogue_reduced.json](../../manuscript106/catalogue/catalogue_reduced.json)
- [manuscript106/catalogue/conjugacy_certificates.json](../../manuscript106/catalogue/conjugacy_certificates.json)
- [legacy245/catalogue.json](../../legacy245/catalogue.json)
- [legacy245/criteria_incidence.csv](../../legacy245/criteria_incidence.csv)
- [legacy245/91/invariant_ring/ring_certificate.json](../../legacy245/91/invariant_ring/ring_certificate.json)

## Mathematical checks

- **Sieve F.** Check complete invariant presentations, double-cover branch models and the admissible resolution calculation. Reference key: `CynkSzembergDoubleCovers`.

Run the supported old-catalogue stages from the repository root:

```sh
python3 legacy245/run_verification.py --steps catalogue,criteria,representatives,geometry --output-dir /tmp/sl4-case-028
```

The selected global stages also check other entries. For Cox cases the order binding → Cox → endpoint is intentional; ordinary invariant generation must be checked with the same inputs.

Additional checks required for the complete indexed scope:

- `sieve-f`: Additional full matrix binding, square completion, reduced branch factors, and all double-cover resolution models. Entry point: [extensions/geometry/verify_F.py](../../extensions/geometry/verify_F.py).

The repository runner combines these additional checks with the legacy stages. The legacy-only command above does not run extensions.

## Scope

- A stored YES/NO label and the existence of program files do not constitute a fresh proof run.
- The cited geometric theorems and their mathematical deductions remain part of the proof.
