[← Case 074](../074/README.md) · [All 106 cases](../README.md) · [Case 076 →](../076/README.md)

# Case 075 · YES

A projective crepant resolution exists. Primary sieve: [I — Cox rings and GIT](../../docs/methods.md#sieve-i).

![Case 075: age profile (1, 3, 2); resolution Betti numbers](../../assets/catalogue/075-age-profile.svg)

## Invariants

| Invariant | Value |
|---|---|
| Group order $\lvert G\rvert$ | 12 |
| Junior conjugacy classes | 3 |
| Age-two conjugacy classes | 2 |
| Total conjugacy classes | 6 |
| Applicable sieves | [I](../../docs/methods.md#sieve-i) |
| Legacy source | [194](../../legacy245/catalogue.json) |
| All legacy integral representatives | 194, 195, 196, 197 |
| CrystCat reference | System 21; Q-class 3; global Q-class 114 |

The age polynomial records conjugacy classes:

$$
A_G(t) = 1 + 3t + 2t^{2}.
$$

For a projective crepant resolution $Y \to \mathbb{C}^4/G$, the ordinary rational Poincaré polynomial is

$$
P_Y(q) = 1 + 3q^{2} + 2q^{4}.
$$

Thus $(b_0,b_2,b_4)=(1,3,2)$; all odd Betti numbers and all $b_k$ with $k>4$ vanish. This follows from [Batyrev’s cohomological McKay theorem](../../docs/catalogue.md#age-profiles).

## Exact generators

These ordered integral matrices define the displayed representation. The [matrix-transfer certificates](../../manuscript106/catalogue/conjugacy_certificates.json) identify all its legacy representatives.

$$
g_{1}=\begin{pmatrix}0&-1&0&0\\1&-1&0&0\\0&0&-1&1\\0&0&-1&0\end{pmatrix}\qquad g_{2}=\begin{pmatrix}1&0&0&0\\1&-1&0&0\\0&0&0&-1\\0&0&-1&0\end{pmatrix}.
$$

$$
g_{3}=\begin{pmatrix}1&0&0&0\\0&1&0&0\\0&0&-1&0\\0&0&0&-1\end{pmatrix}.
$$

## Verify this case

Run from the repository root:

```sh
python3 verify.py --case 75 --plan
python3 verify.py --case 75 --output-dir ../sl4-results/case-075
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
- [legacy245/194/paper_model83.json](../../legacy245/194/paper_model83.json)
- [legacy245/194/paper_invariants83.json](../../legacy245/194/paper_invariants83.json)
- [legacy245/194/paper_charts83.json](../../legacy245/194/paper_charts83.json)

### Applicable arguments

- **[Sieve I](../../docs/methods.md#sieve-i).** Bind the actual representation, prove complete Cox generation including ordinary invariant generation, and verify the positive charts or negative geometric obstruction. Manuscript reference: `Yamagishi;ADHL;SchmittMUVAK`.

### Execution stages

`catalogue, criteria, representatives, binding-194, cox-194, endpoint-194`

Some selected stages also check other cases. Cox cases run binding, full Cox generation and endpoint geometry in that order with the same exact inputs.

### Reading the result

Use the execution report to distinguish completed exact calculations from the cited geometric theorem inputs. The catalogue labels and this page are a navigation layer.

</details>

---

[← Case 074](../074/README.md) · [All 106 cases](../README.md) · [Case 076 →](../076/README.md)
