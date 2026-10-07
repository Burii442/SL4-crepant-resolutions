[← Case 066](../066/README.md) · [All 106 cases](../README.md) · [Case 068 →](../068/README.md)

# Case 067 · YES

A projective crepant resolution exists. Primary sieve: [B — A fixed factor](../../docs/methods.md#sieve-b).

![Case 067: age profile (1, 5, 0); conjugacy-class counts](../../assets/catalogue/067-age-profile.svg)

## Invariants

| Invariant | Value |
|---|---|
| Group order $\lvert G\rvert$ | 6 |
| Junior conjugacy classes | 5 |
| Age-two conjugacy classes | 0 |
| Total conjugacy classes | 6 |
| Applicable sieves | [B](../../docs/methods.md#sieve-b), [C](../../docs/methods.md#sieve-c) |
| Legacy source | [180](../../legacy245/catalogue.json) |
| All legacy integral representatives | 180 |
| CrystCat reference | System 9; Q-class 1; global Q-class 29 |

The age polynomial records conjugacy classes:

$$
A_G(t) = 1 + 5t.
$$

The displayed numbers count conjugacy classes by age, as in the manuscript. [Definition of the age polynomial](../../docs/catalogue.md#age-profiles).

## Exact generators

These ordered integral matrices define the displayed representation. The [matrix-transfer certificates](../../manuscript106/catalogue/conjugacy_certificates.json) identify all its legacy representatives.

$$
g_{1}=\begin{pmatrix}1&0&0&0\\0&1&0&0\\0&0&0&1\\0&0&-1&1\end{pmatrix}\qquad g_{2}=\begin{pmatrix}1&0&0&0\\0&1&0&0\\0&0&0&-1\\0&0&1&-1\end{pmatrix}.
$$

## Verify this case

Run from the repository root:

```sh
python3 verify.py --case 67 --plan
python3 verify.py --case 67 --output-dir ../sl4-results/case-067
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
- [legacy245/abelian_characters.csv](../../legacy245/abelian_characters.csv)
- [legacy245/180/triangulation.json](../../legacy245/180/triangulation.json)

### Applicable arguments

- **[Sieve B](../../docs/methods.md#sieve-b).** Compute the common fixed subspace. A positive dimension reduces the quotient to a resolved quotient of dimension at most three. Manuscript reference: `BKR`.
- **[Sieve C](../../docs/methods.md#sieve-c).** Bind the actual character lattice and check a coherent unimodular triangulation covering the complete junior simplex. Manuscript reference: `DHZ`.

### Execution stages

`catalogue, criteria, representatives, geometry`

Some selected stages also check other cases. Cox cases run binding, full Cox generation and endpoint geometry in that order with the same exact inputs.

### Included extensions

- **abelian-lattice.** Recompute the quotient lattice from the actual matrix character. [Program](../../extensions/abelian/verify.py) (python).

### Reading the result

Use the execution report to distinguish completed exact calculations from the cited geometric theorem inputs. The catalogue labels and this page are a navigation layer.

</details>

---

[← Case 066](../066/README.md) · [All 106 cases](../README.md) · [Case 068 →](../068/README.md)
