[← Case 059](../059/README.md) · [All 106 cases](../README.md) · [Case 061 →](../061/README.md)

# Case 060 · NO

No projective crepant resolution exists. Primary sieve: [I — Cox rings and GIT](../../docs/methods.md#sieve-i).

![Case 060: age profile (1, 3, 9); conjugacy-class counts](../../assets/catalogue/060-age-profile.svg)

## Invariants

| Invariant | Value |
|---|---|
| Group order $\lvert G\rvert$ | 96 |
| Junior conjugacy classes | 3 |
| Age-two conjugacy classes | 9 |
| Total conjugacy classes | 13 |
| Applicable sieves | [I](../../docs/methods.md#sieve-i) |
| Legacy source | [171](../../legacy245/catalogue.json) |
| All legacy integral representatives | 171 |
| CrystCat reference | System 33; Q-class 9; global Q-class 220 |

The age polynomial records conjugacy classes:

$$
A_G(t) = 1 + 3t + 9t^{2}.
$$

The displayed numbers count conjugacy classes by age, as in the manuscript. [Definition of the age polynomial](../../docs/catalogue.md#age-profiles).

## Exact generators

These ordered integral matrices define the displayed representation. The [matrix-transfer certificates](../../manuscript106/catalogue/conjugacy_certificates.json) identify all its legacy representatives.

$$
g_{1}=\begin{pmatrix}-1&-1&0&-1\\1&1&1&1\\-1&-1&-1&0\\0&-1&-1&-1\end{pmatrix}\qquad g_{2}=\begin{pmatrix}-1&0&0&0\\0&-1&0&0\\0&0&-1&0\\0&0&0&-1\end{pmatrix}.
$$

$$
g_{3}=\begin{pmatrix}1&1&0&0\\0&-1&0&0\\0&1&1&0\\0&0&0&-1\end{pmatrix}\qquad g_{4}=\begin{pmatrix}0&-1&-1&-1\\0&1&2&0\\0&-1&-1&0\\1&0&-1&0\end{pmatrix}.
$$

$$
g_{5}=\begin{pmatrix}0&0&-1&0\\0&1&2&0\\0&0&-1&1\\-1&-1&-1&0\end{pmatrix}\qquad g_{6}=\begin{pmatrix}0&1&1&1\\0&-1&0&-2\\-1&0&0&1\\0&1&0&1\end{pmatrix}.
$$

## Verify this case

Run from the repository root:

```sh
python3 verify.py --case 60 --plan
python3 verify.py --case 60 --output-dir ../sl4-results/case-060
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
- [legacy245/171/model.json](../../legacy245/171/model.json)
- [legacy245/171/invariants.json](../../legacy245/171/invariants.json)

### Applicable arguments

- **[Sieve I](../../docs/methods.md#sieve-i).** Bind the actual representation, prove complete Cox generation including ordinary invariant generation, and verify the positive charts or negative geometric obstruction. Manuscript reference: `Yamagishi;ADHL;SchmittMUVAK`.

### Execution stages

`catalogue, criteria, representatives, binding-171, cox-171, endpoint-171`

Some selected stages also check other cases. Cox cases run binding, full Cox generation and endpoint geometry in that order with the same exact inputs.

### Reading the result

Use the execution report to distinguish completed exact calculations from the cited geometric theorem inputs. The catalogue labels and this page are a navigation layer.

</details>

---

[← Case 059](../059/README.md) · [All 106 cases](../README.md) · [Case 061 →](../061/README.md)
