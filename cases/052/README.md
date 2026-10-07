[← Case 051](../051/README.md) · [All 106 cases](../README.md) · [Case 053 →](../053/README.md)

# Case 052 · YES

A projective crepant resolution exists. Primary sieve: [G — Determinant extensions](../../docs/methods.md#sieve-g).

![Case 052: age profile (1, 6, 3); resolution Betti numbers](../../assets/catalogue/052-age-profile.svg)

## Invariants

| Invariant | Value |
|---|---|
| Group order $\lvert G\rvert$ | 48 |
| Junior conjugacy classes | 6 |
| Age-two conjugacy classes | 3 |
| Total conjugacy classes | 10 |
| Applicable sieves | [G](../../docs/methods.md#sieve-g) |
| Legacy source | [154](../../legacy245/catalogue.json) |
| All legacy integral representatives | 154, 155, 156, 157, 158 |
| CrystCat reference | System 25; Q-class 6; global Q-class 148 |

The age polynomial records conjugacy classes:

$$
A_G(t) = 1 + 6t + 3t^{2}.
$$

For a projective crepant resolution $Y \to \mathbb{C}^4/G$, the ordinary rational Poincaré polynomial is

$$
P_Y(q) = 1 + 6q^{2} + 3q^{4}.
$$

Thus $(b_0,b_2,b_4)=(1,6,3)$; all odd Betti numbers and all $b_k$ with $k>4$ vanish. This follows from [Batyrev’s cohomological McKay theorem](../../docs/catalogue.md#age-profiles).

## Exact generators

These ordered integral matrices define the displayed representation. The [matrix-transfer certificates](../../manuscript106/catalogue/conjugacy_certificates.json) identify all its legacy representatives.

$$
g_{1}=\begin{pmatrix}1&0&0&0\\0&1&0&0\\0&0&-1&1\\0&0&-2&1\end{pmatrix}\qquad g_{2}=\begin{pmatrix}-1&0&0&0\\0&-1&0&0\\0&0&-1&0\\0&0&0&-1\end{pmatrix}.
$$

$$
g_{3}=\begin{pmatrix}1&0&0&0\\0&-1&0&0\\0&0&1&0\\0&0&2&-1\end{pmatrix}\qquad g_{4}=\begin{pmatrix}1&0&0&0\\0&1&0&0\\0&0&-1&0\\0&0&0&-1\end{pmatrix}.
$$

$$
g_{5}=\begin{pmatrix}1&0&0&0\\0&0&1&-1\\0&1&0&0\\0&1&-1&0\end{pmatrix}.
$$

## Verify this case

Run from the repository root:

```sh
python3 verify.py --case 52 --plan
python3 verify.py --case 52 --output-dir ../sl4-results/case-052
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

- **[Sieve G](../../docs/methods.md#sieve-g).** Identify the determinant extension and its three-dimensional reflection model; apply the cited existence theorem. Manuscript reference: `IshiiNimura`.

### Execution stages

`catalogue, criteria, representatives, criteria-geometry`

Some selected stages also check other cases. Cox cases run binding, full Cox generation and endpoint geometry in that order with the same exact inputs.

### Reading the result

Use the execution report to distinguish completed exact calculations from the cited geometric theorem inputs. The catalogue labels and this page are a navigation layer.

</details>

---

[← Case 051](../051/README.md) · [All 106 cases](../README.md) · [Case 053 →](../053/README.md)
