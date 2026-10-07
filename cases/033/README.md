[← Case 032](../032/README.md) · [All 106 cases](../README.md) · [Case 034 →](../034/README.md)

# Case 033 · YES

A projective crepant resolution exists. Primary sieve: [F — Double covers](../../docs/methods.md#sieve-f).

![Case 033: age profile (1, 7, 2); conjugacy-class counts](../../assets/catalogue/033-age-profile.svg)

## Invariants

| Invariant | Value |
|---|---|
| Group order $\lvert G\rvert$ | 16 |
| Junior conjugacy classes | 7 |
| Age-two conjugacy classes | 2 |
| Total conjugacy classes | 10 |
| Applicable sieves | [F](../../docs/methods.md#sieve-f) |
| Legacy source | [107](../../legacy245/catalogue.json) |
| All legacy integral representatives | 107, 108, 109, 110, 111 |
| CrystCat reference | System 13; Q-class 9; global Q-class 52 |

The age polynomial records conjugacy classes:

$$
A_G(t) = 1 + 7t + 2t^{2}.
$$

The displayed numbers count conjugacy classes by age, as in the manuscript. [Definition of the age polynomial](../../docs/catalogue.md#age-profiles).

## Exact generators

These ordered integral matrices define the displayed representation. The [matrix-transfer certificates](../../manuscript106/catalogue/conjugacy_certificates.json) identify all its legacy representatives.

$$
g_{1}=\begin{pmatrix}1&0&0&0\\0&1&0&0\\0&0&-1&1\\0&0&-2&1\end{pmatrix}\qquad g_{2}=\begin{pmatrix}-1&0&0&0\\0&-1&0&0\\0&0&-1&0\\0&0&0&-1\end{pmatrix}.
$$

$$
g_{3}=\begin{pmatrix}1&0&0&0\\0&1&0&0\\0&0&-1&0\\0&0&0&-1\end{pmatrix}\qquad g_{4}=\begin{pmatrix}1&0&0&0\\0&-1&0&0\\0&0&1&-1\\0&0&0&-1\end{pmatrix}.
$$

## Verify this case

Run from the repository root:

```sh
python3 verify.py --case 33 --plan
python3 verify.py --case 33 --output-dir ../sl4-results/case-033
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
- [legacy245/107/invariant_ring/ring_certificate.json](../../legacy245/107/invariant_ring/ring_certificate.json)

### Applicable arguments

- **[Sieve F](../../docs/methods.md#sieve-f).** Check complete invariant presentations, double-cover branch models and the admissible resolution calculation. Manuscript reference: `CynkSzembergDoubleCovers`.

### Execution stages

`catalogue, criteria, representatives, geometry`

Some selected stages also check other cases. Cox cases run binding, full Cox generation and endpoint geometry in that order with the same exact inputs.

### Included extensions

- **sieve-f.** Additional full matrix binding, square completion, reduced branch factors, and all double-cover resolution models. [Program](../../extensions/geometry/verify_F.py) (sage).

### Reading the result

Use the execution report to distinguish completed exact calculations from the cited geometric theorem inputs. The catalogue labels and this page are a navigation layer.

</details>

---

[← Case 032](../032/README.md) · [All 106 cases](../README.md) · [Case 034 →](../034/README.md)
