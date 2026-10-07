[← Case 099](../099/README.md) · [All 106 cases](../README.md) · [Case 101 →](../101/README.md)

# Case 100 · YES

A projective crepant resolution exists. Primary sieve: [E — Complete-intersection blow-ups](../../docs/methods.md#sieve-e).

![Case 100: age profile (1, 3, 6); resolution Betti numbers](../../assets/catalogue/100-age-profile.svg)

## Invariants

| Invariant | Value |
|---|---|
| Group order $\lvert G\rvert$ | 120 |
| Junior conjugacy classes | 3 |
| Age-two conjugacy classes | 6 |
| Total conjugacy classes | 10 |
| Applicable sieves | [E](../../docs/methods.md#sieve-e) |
| Legacy source | [236](../../legacy245/catalogue.json) |
| All legacy integral representatives | 236, 237 |
| CrystCat reference | System 31; Q-class 6; global Q-class 189 |

The age polynomial records conjugacy classes:

$$
A_G(t) = 1 + 3t + 6t^{2}.
$$

For a projective crepant resolution $Y \to \mathbb{C}^4/G$, the ordinary rational Poincaré polynomial is

$$
P_Y(q) = 1 + 3q^{2} + 6q^{4}.
$$

Thus $(b_0,b_2,b_4)=(1,3,6)$; all odd Betti numbers and all $b_k$ with $k>4$ vanish. This follows from [Batyrev’s cohomological McKay theorem](../../docs/catalogue.md#age-profiles).

## Exact generators

These ordered integral matrices define the displayed representation. The [matrix-transfer certificates](../../manuscript106/catalogue/conjugacy_certificates.json) identify all its legacy representatives.

$$
g_{1}=\begin{pmatrix}-1&0&0&0\\0&-1&0&0\\0&0&-1&0\\0&0&0&-1\end{pmatrix}\qquad g_{2}=\begin{pmatrix}0&0&-1&0\\0&-1&0&0\\-1&0&0&0\\1&1&1&1\end{pmatrix}.
$$

$$
g_{3}=\begin{pmatrix}0&-1&0&0\\0&0&0&-1\\0&0&-1&0\\-1&0&0&0\end{pmatrix}.
$$

## Verify this case

Run from the repository root:

```sh
python3 verify.py --case 100 --plan
python3 verify.py --case 100 --output-dir ../sl4-results/case-100
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
- [legacy245/geometry_proofs/236](../../legacy245/geometry_proofs/236)

### Applicable arguments

- **[Sieve E](../../docs/methods.md#sieve-e).** Check complete invariant presentations and the stated blow-up charts, including the separate 132, 234 and 236 geometric packages. Manuscript reference: `manuscript Sieve E`.

### Execution stages

`catalogue, criteria, representatives, geometry, geometry-236`

Some selected stages also check other cases. Cox cases run binding, full Cox generation and endpoint geometry in that order with the same exact inputs.

### Included extensions

- **sieve-e.** Additional matrix-to-invariant-ring binding, blow-up chart and discrepancy checks from the current Sieve E audit. [Program](../../extensions/geometry/verify_E.py) (sage).

### Reading the result

Use the execution report to distinguish completed exact calculations from the cited geometric theorem inputs. The catalogue labels and this page are a navigation layer.

</details>

---

[← Case 099](../099/README.md) · [All 106 cases](../README.md) · [Case 101 →](../101/README.md)
