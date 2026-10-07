# Reading the catalogue

[All 106 cases](../cases/README.md) · [61 YES](../cases/yes.md) · [45 NO](../cases/no.md) · [Sieves A–J](methods.md)

This catalogue accompanies *Crepant resolutions of four-dimensional finite quotients* (`arxiv_3`). It contains **106 complex conjugacy classes of four-dimensional finite quotient representations admitting an integral representative in $\mathrm{SL}_4(\mathbb{Z})$**. They arise from the 245 integral catalogue entries. Exact conjugating matrices certify this reduction; the original numbering is retained for polynomial inputs and earlier programs.

A **YES** means that $\mathbb{C}^4/G$ admits a projective crepant resolution. A **NO** means that the stated sieve gives an obstruction to such a resolution. Here projectivity is relative to the affine quotient: the resolving variety $Y$ need not be compact or projective over a point. Each page presents its actual ordered matrices, the applicable arguments and a case-specific execution plan.

<a id="age-profiles"></a>
## Age profiles

Write the eigenvalues of an element $g$ of order $r$ as $\exp(2\pi i a_k/r)$, with $0\leq a_k<r$. Its age is

$$
\operatorname{age}(g)=\frac{a_1+a_2+a_3+a_4}{r}.
$$

For these real representations,

$$
\operatorname{age}(g)=\frac{1}{2}\operatorname{rank}(g-I_4).
$$

Consequently the only ages are $0,1,2$, and age zero consists of the identity. A *junior* is an element of age one. The three numbers on a card count **conjugacy classes**, not individual group elements:

$$
A_G(t)=1+j(G)t+a_2(G)t^2.
$$

Their sum is the total number of conjugacy classes. The manuscript uses these age counts and the age polynomial alongside the YES/NO classification. The decision follows from the indicated sieve.

## Matrices and numbering

Generators appear as exact integer matrices, with at most two in each display. The trivial case shows $I_4$. No abstract-group label is substituted for the representation: different representations can have different resolution behavior.

- **Case number:** the current manuscript number, 001–106.
- **Legacy source:** the earlier entry whose ordered matrices are displayed.
- **Legacy representatives:** all integral entries identified with this complex class.
- **CrystCat reference:** the crystallographic system, rational class and global rational-class identifier recorded in the exact comparison.

The [machine index](../cases/index.json), [classification comparison](../classification/case_map.json) and [conjugacy certificates](../manuscript106/catalogue/conjugacy_certificates.json) retain the complete correspondence. Each case also has a `case.json` file containing its indexed data and derived age profile.

## Verification

From the repository root, inspect a case plan and run it into a new directory outside the checkout:

```sh
python3 verify.py --case 35 --plan
python3 verify.py --case 35 --output-dir ../sl4-results/case-035
```

The runner includes the assigned legacy stages and extensions. The [full reproduction guide](reproducibility.md) explains dependencies, the complete shared suite, resumable execution and report interpretation. A page’s YES/NO label records the mathematical classification; a fresh execution report records which calculations were actually completed.

The catalogue itself is generated with the Python standard library:

```sh
python3 tools/build_case_index.py
python3 tools/build_case_index.py --check
```

Recompute the conjugacy classes and ages directly from the matrices with the independent exact verifier:

```sh
python3 tools/verify_age_profiles.py
python3 tools/verify_age_profiles.py --case 35
```

The catalogue check compares every generated page, per-case JSON record and SVG with the exact distributed inputs, validates the SVG age entries, and checks relative links. It preserves the existing machine-index schema and does not execute the geometric proof calculations.
