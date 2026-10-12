[← Case 104](../104/README.md) · [All 106 cases](../README.md) · [Case 106 →](../106/README.md)

# Case 105 · NO

No projective crepant resolution exists. Primary sieve: [I — Cox rings and GIT](../../docs/methods.md#sieve-i).

## Invariants

| Invariant | Value |
|---|---|
| Group order $\lvert G\rvert$ | 24 |
| Junior conjugacy classes | 4 |
| Age-two conjugacy classes | 4 |
| Total conjugacy classes | 9 |
| Applicable sieves | [I](../../docs/methods.md#sieve-i) |
| Legacy source | [243](../../legacy245/catalogue.json) |
| All legacy integral representatives | 243, 244 |
| CrystCat reference | System 20; Q-class 11; global Q-class 100 |

The age polynomial records conjugacy classes:

$$
A_G(t) = 1 + 4t + 4t^{2}.
$$

The displayed numbers count conjugacy classes by age, as in the manuscript. [Definition of the age polynomial](../../docs/catalogue.md#age-profiles).

## In the manuscript

A complete intersection without a projective crepant resolution (CE-01).

## Exact generators

These ordered integral matrices define the displayed representation. The [matrix-transfer certificates](../../manuscript106/catalogue/conjugacy_certificates.json) identify all its legacy representatives.

```math
g_{1}=\begin{pmatrix}
1 & -1 & 0 & 0 \\
0 & -1 & 0 & 0 \\
0 & 0 & 0 & 1 \\
0 & 0 & 1 & 0
\end{pmatrix}
```

```math
g_{2}=\begin{pmatrix}
-1 & 0 & 0 & 0 \\
0 & -1 & 0 & 0 \\
0 & 0 & 0 & 1 \\
0 & 0 & -1 & 0
\end{pmatrix}
```

```math
g_{3}=\begin{pmatrix}
1 & 0 & 0 & 0 \\
0 & 1 & 0 & 0 \\
0 & 0 & -1 & 0 \\
0 & 0 & 0 & -1
\end{pmatrix}
```

```math
g_{4}=\begin{pmatrix}
0 & -1 & 0 & 0 \\
1 & -1 & 0 & 0 \\
0 & 0 & 1 & 0 \\
0 & 0 & 0 & 1
\end{pmatrix}
```

## Verify this case

Run from the repository root:

```sh
python3 verify.py --case 105 --plan
python3 verify.py --case 105 --output-dir ../sl4-results/case-105
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
- [legacy245/243/model.json](../../legacy245/243/model.json)
- [legacy245/243/invariants.json](../../legacy245/243/invariants.json)

### Applicable arguments

- **[Sieve I](../../docs/methods.md#sieve-i).** Bind the actual representation, prove complete Cox generation including ordinary invariant generation, and verify the positive charts or negative geometric obstruction. Manuscript reference: `Yamagishi;ADHL;SchmittMUVAK`.

### Execution stages

`catalogue, criteria, representatives, binding-243, cox-243, endpoint-243`

Some selected stages also check other cases. Cox cases run binding, full Cox generation and endpoint geometry in that order with the same exact inputs.

### Included extensions

- **dhz.** Enhanced complete-intersection and singular-point obstruction certificates for the four DHZ counterexamples. [Program](../../extensions/dhz/verify.py) (sage).

### Reading the result

Use the execution report to distinguish completed exact calculations from the cited geometric theorem inputs. The catalogue labels and this page are a navigation layer.

</details>

---

[← Case 104](../104/README.md) · [All 106 cases](../README.md) · [Case 106 →](../106/README.md)
