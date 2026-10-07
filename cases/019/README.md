[← Case 018](../018/README.md) · [All 106 cases](../README.md) · [Case 020 →](../020/README.md)

# Case 019 · YES

A projective crepant resolution exists. Primary sieve: [D — Cotangent reflection representations](../../docs/methods.md#sieve-d).

![Case 019: age profile (1, 2, 2); resolution Betti numbers](../../assets/catalogue/019-age-profile.svg)

## Invariants

| Invariant | Value |
|---|---|
| Group order $\lvert G\rvert$ | 8 |
| Junior conjugacy classes | 2 |
| Age-two conjugacy classes | 2 |
| Total conjugacy classes | 5 |
| Applicable sieves | [D](../../docs/methods.md#sieve-d) |
| Legacy source | [60](../../legacy245/catalogue.json) |
| All legacy integral representatives | 60, 61, 62 |
| CrystCat reference | System 16; Q-class 1; global Q-class 76 |

The age polynomial records conjugacy classes:

$$
A_G(t) = 1 + 2t + 2t^{2}.
$$

For a projective crepant resolution $Y \to \mathbb{C}^4/G$, the ordinary rational Poincaré polynomial is

$$
P_Y(q) = 1 + 2q^{2} + 2q^{4}.
$$

Thus $(b_0,b_2,b_4)=(1,2,2)$; all odd Betti numbers and all $b_k$ with $k>4$ vanish. This follows from [Batyrev’s cohomological McKay theorem](../../docs/catalogue.md#age-profiles).

## Exact generators

These ordered integral matrices define the displayed representation. The [matrix-transfer certificates](../../manuscript106/catalogue/conjugacy_certificates.json) identify all its legacy representatives.

$$
g_{1}=\begin{pmatrix}0&0&-1&1\\0&1&2&0\\0&-1&-1&0\\-1&-1&-1&0\end{pmatrix}\qquad g_{2}=\begin{pmatrix}-1&0&0&0\\0&-1&0&0\\0&0&-1&0\\0&0&0&-1\end{pmatrix}.
$$

$$
g_{3}=\begin{pmatrix}-1&0&0&0\\0&-1&0&0\\0&1&1&0\\0&1&0&1\end{pmatrix}.
$$

## Verify this case

Run from the repository root:

```sh
python3 verify.py --case 19 --plan
python3 verify.py --case 19 --output-dir ../sl4-results/case-019
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

- **[Sieve D](../../docs/methods.md#sieve-d).** Check the actual cotangent/reflection representation and its model identification; apply the cited positive or negative classification theorem. Manuscript reference: `BellamyV3`.

### Execution stages

`catalogue, criteria, representatives, criteria-geometry`

Some selected stages also check other cases. Cox cases run binding, full Cox generation and endpoint geometry in that order with the same exact inputs.

### Reading the result

Use the execution report to distinguish completed exact calculations from the cited geometric theorem inputs. The catalogue labels and this page are a navigation layer.

</details>

---

[← Case 018](../018/README.md) · [All 106 cases](../README.md) · [Case 020 →](../020/README.md)
