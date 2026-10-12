[← Case 061](../061/README.md) · [All 106 cases](../README.md) · [Case 063 →](../063/README.md)

# Case 062 · NO

No projective crepant resolution exists. Primary sieve: [I — Cox rings and GIT](../../docs/methods.md#sieve-i).

![Case 062: age profile (1, 3, 11); conjugacy-class counts](../../assets/catalogue/062-age-profile.svg)

## Invariants

| Invariant | Value |
|---|---|
| Group order $\lvert G\rvert$ | 144 |
| Junior conjugacy classes | 3 |
| Age-two conjugacy classes | 11 |
| Total conjugacy classes | 15 |
| Applicable sieves | [I](../../docs/methods.md#sieve-i) |
| Legacy source | [173](../../legacy245/catalogue.json) |
| All legacy integral representatives | 173 |
| CrystCat reference | System 33; Q-class 11; global Q-class 222 |

The age polynomial records conjugacy classes:

$$
A_G(t) = 1 + 3t + 11t^{2}.
$$

The displayed numbers count conjugacy classes by age, as in the manuscript. [Definition of the age polynomial](../../docs/catalogue.md#age-profiles).

## Exact generators

These ordered integral matrices define the displayed representation. The [matrix-transfer certificates](../../manuscript106/catalogue/conjugacy_certificates.json) identify all its legacy representatives.

```math
g_{1}=\begin{pmatrix}
0 & 0 & 0 & -1 \\
0 & 1 & 0 & 2 \\
0 & 0 & 1 & -1 \\
1 & 0 & 0 & -1
\end{pmatrix}
```

```math
g_{2}=\begin{pmatrix}
0 & 1 & 1 & 0 \\
1 & 0 & -1 & 1 \\
-1 & 0 & 1 & 0 \\
0 & 0 & 1 & -1
\end{pmatrix}
```

```math
g_{3}=\begin{pmatrix}
-1 & 0 & 0 & 0 \\
0 & -1 & 0 & 0 \\
0 & 0 & -1 & 0 \\
0 & 0 & 0 & -1
\end{pmatrix}
```

```math
g_{4}=\begin{pmatrix}
0 & -1 & -1 & -1 \\
0 & 1 & 2 & 0 \\
0 & -1 & -1 & 0 \\
1 & 0 & -1 & 0
\end{pmatrix}
```

```math
g_{5}=\begin{pmatrix}
-1 & 0 & 0 & 1 \\
0 & -1 & 0 & -2 \\
0 & 1 & 1 & 1 \\
0 & 0 & 0 & 1
\end{pmatrix}
```

```math
g_{6}=\begin{pmatrix}
0 & 0 & 1 & -1 \\
0 & 1 & 0 & 2 \\
-1 & -1 & 0 & -1 \\
0 & -1 & 0 & -1
\end{pmatrix}
```

## Verify this case

Run from the repository root:

```sh
python3 verify.py --case 62 --plan
python3 verify.py --case 62 --output-dir ../sl4-results/case-062
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
- [legacy245/173/model.json](../../legacy245/173/model.json)
- [legacy245/173/invariants.json](../../legacy245/173/invariants.json)

### Applicable arguments

- **[Sieve I](../../docs/methods.md#sieve-i).** Bind the actual representation, prove complete Cox generation including ordinary invariant generation, and verify the positive charts or negative geometric obstruction. Manuscript reference: `Yamagishi;ADHL;SchmittMUVAK`.

### Execution stages

`catalogue, criteria, representatives, binding-173, cox-173, endpoint-173`

Some selected stages also check other cases. Cox cases run binding, full Cox generation and endpoint geometry in that order with the same exact inputs.

### Reading the result

Use the execution report to distinguish completed exact calculations from the cited geometric theorem inputs. The catalogue labels and this page are a navigation layer.

</details>

---

[← Case 061](../061/README.md) · [All 106 cases](../README.md) · [Case 063 →](../063/README.md)
