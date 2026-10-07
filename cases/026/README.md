[← Case 025](../025/README.md) · [All 106 cases](../README.md) · [Case 027 →](../027/README.md)

# Case 026 · YES

A projective crepant resolution exists. Primary sieve: [E — Complete-intersection blow-ups](../../docs/methods.md#sieve-e).

![Case 026: age profile (1, 3, 2); conjugacy-class counts](../../assets/catalogue/026-age-profile.svg)

## Invariants

| Invariant | Value |
|---|---|
| Group order $\lvert G\rvert$ | 12 |
| Junior conjugacy classes | 3 |
| Age-two conjugacy classes | 2 |
| Total conjugacy classes | 6 |
| Applicable sieves | [E](../../docs/methods.md#sieve-e) |
| Legacy source | [85](../../legacy245/catalogue.json) |
| All legacy integral representatives | 85, 86, 87, 88 |
| CrystCat reference | System 14; Q-class 5; global Q-class 58 |

The age polynomial records conjugacy classes:

$$
A_G(t) = 1 + 3t + 2t^{2}.
$$

The displayed numbers count conjugacy classes by age, as in the manuscript. [Definition of the age polynomial](../../docs/catalogue.md#age-profiles).

## Exact generators

These ordered integral matrices define the displayed representation. The [matrix-transfer certificates](../../manuscript106/catalogue/conjugacy_certificates.json) identify all its legacy representatives.

![Case 026: ordered generating matrices](../../assets/catalogue/026-generators.svg)

<details>
<summary>Copyable matrix notation</summary>

```latex
g_{1}=\begin{pmatrix}-1&0&0&0\\0&-1&0&0\\0&0&-1&0\\0&0&0&-1\end{pmatrix}
```

```latex
g_{2}=\begin{pmatrix}1&0&0&0\\0&-1&0&0\\0&0&-1&-1\\0&0&0&1\end{pmatrix}
```

```latex
g_{3}=\begin{pmatrix}1&0&0&0\\0&1&0&0\\0&0&0&1\\0&0&-1&-1\end{pmatrix}
```

</details>

## Verify this case

Run from the repository root:

```sh
python3 verify.py --case 26 --plan
python3 verify.py --case 26 --output-dir ../sl4-results/case-026
```

The case runner combines its assigned legacy stages and extensions. Results are written to a new directory outside the checkout. The [full reproduction guide](../../docs/reproducibility.md) covers installation, shared checks, long computations and resumable runs.

<details>
<summary>Exact inputs, proof scope and additional checks</summary>

### Input files

[This case as JSON](case.json) · [Complete machine index](../index.json) · [245-to-106 reduction verifier](../../manuscript106/catalogue/verify_reduction.py)

- [manuscript106/catalogue/catalogue.json](../../manuscript106/catalogue/catalogue.json)
- [manuscript106/catalogue/catalogue_reduced.json](../../manuscript106/catalogue/catalogue_reduced.json)
- [manuscript106/catalogue/conjugacy_certificates.json](../../manuscript106/catalogue/conjugacy_certificates.json)
- [legacy245/catalogue.json](../../legacy245/catalogue.json)
- [legacy245/criteria_incidence.csv](../../legacy245/criteria_incidence.csv)
- [legacy245/85/invariant_ring/ring_certificate.json](../../legacy245/85/invariant_ring/ring_certificate.json)

### Applicable arguments

- **[Sieve E](../../docs/methods.md#sieve-e).** Check complete invariant presentations and the stated blow-up charts, including the separate 132, 234 and 236 geometric packages. Manuscript reference: `manuscript Sieve E`.

### Execution stages

`catalogue, criteria, representatives, geometry`

Some selected stages also check other cases. Cox cases run binding, full Cox generation and endpoint geometry in that order with the same exact inputs.

### Included extensions

- **sieve-e.** Additional matrix-to-invariant-ring binding, blow-up chart and discrepancy checks from the current Sieve E audit. [Program](../../extensions/geometry/verify_E.py) (sage).

### Reading the result

Use the execution report to distinguish completed exact calculations from the cited geometric theorem inputs. The catalogue labels and this page are a navigation layer.

</details>

---

[← Case 025](../025/README.md) · [All 106 cases](../README.md) · [Case 027 →](../027/README.md)
