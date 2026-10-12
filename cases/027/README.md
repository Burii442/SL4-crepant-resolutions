[← Case 026](../026/README.md) · [All 106 cases](../README.md) · [Case 028 →](../028/README.md)

# Case 027 · NO

No projective crepant resolution exists. Primary sieve: [D — Cotangent reflection representations](../../docs/methods.md#sieve-d).

![Case 027: age profile (1, 2, 3); conjugacy-class counts](../../assets/catalogue/027-age-profile.svg)

## Invariants

| Invariant | Value |
|---|---|
| Group order $\lvert G\rvert$ | 12 |
| Junior conjugacy classes | 2 |
| Age-two conjugacy classes | 3 |
| Total conjugacy classes | 6 |
| Applicable sieves | [D](../../docs/methods.md#sieve-d) |
| Legacy source | [89](../../legacy245/catalogue.json) |
| All legacy integral representatives | 89, 90 |
| CrystCat reference | System 17; Q-class 2; global Q-class 78 |

The age polynomial records conjugacy classes:

$$
A_G(t) = 1 + 2t + 3t^{2}.
$$

The displayed numbers count conjugacy classes by age, as in the manuscript. [Definition of the age polynomial](../../docs/catalogue.md#age-profiles).

## In the manuscript

Junior generation does not imply existence of a projective crepant resolution (CE-04).

## Exact generators

These ordered integral matrices define the displayed representation. The [matrix-transfer certificates](../../manuscript106/catalogue/conjugacy_certificates.json) identify all its legacy representatives.

```math
g_{1}=\begin{pmatrix}
-1 & 0 & 0 & 0 \\
0 & -1 & 0 & 0 \\
0 & 0 & -1 & 0 \\
0 & 0 & 0 & -1
\end{pmatrix}
```

```math
g_{2}=\begin{pmatrix}
1 & 0 & 0 & -1 \\
-1 & 1 & 1 & 1 \\
0 & -1 & 0 & -1 \\
1 & 0 & 0 & 0
\end{pmatrix}
```

```math
g_{3}=\begin{pmatrix}
-1 & 0 & 0 & 1 \\
0 & -1 & 0 & -2 \\
0 & 1 & 1 & 1 \\
0 & 0 & 0 & 1
\end{pmatrix}
```

## Verify this case

Run from the repository root:

```sh
python3 verify.py --case 27 --plan
python3 verify.py --case 27 --output-dir ../sl4-results/case-027
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

[← Case 026](../026/README.md) · [All 106 cases](../README.md) · [Case 028 →](../028/README.md)
