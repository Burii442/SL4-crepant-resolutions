[← Case 085](../085/README.md) · [All 106 cases](../README.md) · [Case 087 →](../087/README.md)

# Case 086 · YES

A projective crepant resolution exists. Primary sieve: [J — Hilbert-square towers](../../docs/methods.md#sieve-j).

![Case 086: age profile (1, 4, 4); conjugacy-class counts](../../assets/catalogue/086-age-profile.svg)

## Invariants

| Invariant | Value |
|---|---|
| Group order $\lvert G\rvert$ | 36 |
| Junior conjugacy classes | 4 |
| Age-two conjugacy classes | 4 |
| Total conjugacy classes | 9 |
| Applicable sieves | [J](../../docs/methods.md#sieve-j) |
| Legacy source | [214](../../legacy245/catalogue.json) |
| All legacy integral representatives | 214, 215, 216, 217, 218 |
| CrystCat reference | System 29; Q-class 3; global Q-class 164 |

The age polynomial records conjugacy classes:

$$
A_G(t) = 1 + 4t + 4t^{2}.
$$

The displayed numbers count conjugacy classes by age, as in the manuscript. [Definition of the age polynomial](../../docs/catalogue.md#age-profiles).

## Exact generators

These ordered integral matrices define the displayed representation. The [matrix-transfer certificates](../../manuscript106/catalogue/conjugacy_certificates.json) identify all its legacy representatives.

$$
g_{1}=\begin{pmatrix}1&0&0&0\\1&-1&0&0\\0&0&0&-1\\0&0&-1&0\end{pmatrix}\qquad g_{2}=\begin{pmatrix}0&0&1&0\\0&0&1&-1\\0&-1&0&0\\-1&0&0&0\end{pmatrix}.
$$

$$
g_{3}=\begin{pmatrix}-1&1&0&0\\-1&0&0&0\\0&0&-1&1\\0&0&-1&0\end{pmatrix}\qquad g_{4}=\begin{pmatrix}1&0&0&0\\0&1&0&0\\0&0&0&-1\\0&0&1&-1\end{pmatrix}.
$$

## Verify this case

Run from the repository root:

```sh
python3 verify.py --case 86 --plan
python3 verify.py --case 86 --output-dir ../sl4-results/case-086
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
- [legacy245/criteria_geometry/README.md](../../legacy245/criteria_geometry/README.md)

### Applicable arguments

- **[Sieve J](../../docs/methods.md#sieve-j).** Identify the full group with its Hilbert-square tower model; apply the stated geometric construction. Manuscript reference: `Baird`.

### Execution stages

`catalogue, criteria, representatives, criteria-geometry`

Some selected stages also check other cases. Cox cases run binding, full Cox generation and endpoint geometry in that order with the same exact inputs.

### Reading the result

Use the execution report to distinguish completed exact calculations from the cited geometric theorem inputs. The catalogue labels and this page are a navigation layer.

</details>

---

[← Case 085](../085/README.md) · [All 106 cases](../README.md) · [Case 087 →](../087/README.md)
