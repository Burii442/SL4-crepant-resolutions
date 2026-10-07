[← Case 062](../062/README.md) · [All 106 cases](../README.md) · [Case 064 →](../064/README.md)

# Case 063 · YES

A projective crepant resolution exists. Primary sieve: [I — Cox rings and GIT](../../docs/methods.md#sieve-i).

![Case 063: age profile (1, 5, 7); conjugacy-class counts](../../assets/catalogue/063-age-profile.svg)

## Invariants

| Invariant | Value |
|---|---|
| Group order $\lvert G\rvert$ | 192 |
| Junior conjugacy classes | 5 |
| Age-two conjugacy classes | 7 |
| Total conjugacy classes | 13 |
| Applicable sieves | [I](../../docs/methods.md#sieve-i) |
| Legacy source | [174](../../legacy245/catalogue.json) |
| All legacy integral representatives | 174, 175, 176 |
| CrystCat reference | System 32; Q-class 20; global Q-class 210 |

The age polynomial records conjugacy classes:

$$
A_G(t) = 1 + 5t + 7t^{2}.
$$

The displayed numbers count conjugacy classes by age, as in the manuscript. [Definition of the age polynomial](../../docs/catalogue.md#age-profiles).

## Exact generators

These ordered integral matrices define the displayed representation. The [matrix-transfer certificates](../../manuscript106/catalogue/conjugacy_certificates.json) identify all its legacy representatives.

![Case 063: ordered generating matrices](../../assets/catalogue/063-generators.svg)

<details>
<summary>Copyable matrix notation</summary>

```latex
g_{1}=\begin{pmatrix}0&0&0&-1\\0&1&0&2\\0&0&1&-1\\1&0&0&-1\end{pmatrix}
```

```latex
g_{2}=\begin{pmatrix}-1&0&0&0\\0&-1&0&0\\0&0&-1&0\\0&0&0&-1\end{pmatrix}
```

```latex
g_{3}=\begin{pmatrix}1&1&0&0\\0&-1&0&0\\0&1&1&0\\0&0&0&-1\end{pmatrix}
```

```latex
g_{4}=\begin{pmatrix}-1&0&0&0\\0&-1&0&0\\0&1&1&0\\0&1&0&1\end{pmatrix}
```

```latex
g_{5}=\begin{pmatrix}1&0&0&-1\\0&1&0&2\\0&0&1&-1\\0&-1&0&-1\end{pmatrix}
```

```latex
g_{6}=\begin{pmatrix}0&-1&-1&-1\\0&1&2&0\\0&0&-1&0\\-1&-1&-1&0\end{pmatrix}
```

```latex
g_{7}=\begin{pmatrix}0&1&1&1\\0&-1&0&-2\\-1&0&0&1\\0&1&0&1\end{pmatrix}
```

</details>

## Verify this case

Run from the repository root:

```sh
python3 verify.py --case 63 --plan
python3 verify.py --case 63 --output-dir ../sl4-results/case-063
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
- [legacy245/174/model.json](../../legacy245/174/model.json)
- [legacy245/174/invariants.json](../../legacy245/174/invariants.json)

### Applicable arguments

- **[Sieve I](../../docs/methods.md#sieve-i).** Bind the actual representation, prove complete Cox generation including ordinary invariant generation, and verify the positive charts or negative geometric obstruction. Manuscript reference: `Yamagishi;ADHL;SchmittMUVAK`.

### Execution stages

`catalogue, criteria, representatives, binding-174, cox-174, endpoint-174`

Some selected stages also check other cases. Cox cases run binding, full Cox generation and endpoint geometry in that order with the same exact inputs.

### Reading the result

Use the execution report to distinguish completed exact calculations from the cited geometric theorem inputs. The catalogue labels and this page are a navigation layer.

</details>

---

[← Case 062](../062/README.md) · [All 106 cases](../README.md) · [Case 064 →](../064/README.md)
