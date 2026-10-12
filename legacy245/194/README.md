# Manuscript case 75: legacy entries 194–197

The final decision for [manuscript case 75](../../cases/075/README.md) is **YES**. The supported calculation uses the presentation identified as **paper83**:

- `paper_invariants83.json`: the literal four matrix groups, the commutator
  eigenbasis, the ordered twelve invariant polynomials, three junior
  representatives, their exact eigenbases, valuations and initial forms;
- `paper_model83.json`: its fifteen coordinates, all 83 relations, the raw
  grading and its specified primitive integral basis;
- `paper_charts83.json`: the character, all six principal opens and gauges,
  the first polynomial parametrization, and the invariant-cone witness;
- `verify194.py`: a self-contained exact reconstruction of the complete proof.

The older normalized files `model.json` and `invariants.json` are a second
presentation, with **51 relations**. Its coordinate names denote different
functions. The formulas for paper83 must be evaluated using the three
`paper_*83.json` files.
Both presentations refer to the literal representation of legacy case 194, but no
identity of their equally spelled coordinate names is asserted.

## Reproduce the full proof

From the repository root, with SageMath 10.9 or a compatible version:

```sh
sage -python legacy245/194/verify194.py \
    --output-dir ../sl4-results/legacy-194-paper83
```

The program uses SageMath's exact number fields, polynomial rings, elimination
and saturation implementation. It has no private paths, no imports from the
original research workspace, and no dependence on the archived source tarball.
Execution time depends on the computer and other running calculations.
An error or failed assertion is fatal. The result `ALL_PAPER83_CHECKS_PASS` is
written only after every section completes. No stored PASS flag is used to
establish a mathematical assertion. The final certificate records the input
hashes and SageMath version.

For a separately recorded partial check, `--sections` accepts `group`,
`algebra`, `charts`, and `cover`. The matrix and invariant checks always run;
partial runs have the distinct status `REQUESTED_SECTIONS_PASS`.

The alternative 51-relation model also has a separate complete polynomial-map
verification (ordinary kernel, all parameter saturations and all three full
simultaneous initial-kernel tests):

```sh
sage -python legacy245/full_verification/verify_cox.py \
    --case 194 --stage all --output-dir ../sl4-results/legacy-194-model51
```

This command reads `model.json` and `invariants.json`. The dedicated
`verify194.py` command above reads **paper83** and verifies its six specified
slices. The two commands deliberately refer to their respective coordinate
systems. Group invariance and the Molien comparison for the 51-relation
model are supplied by `binding_verification/verify_binding.py --case 194`.

## What is proved

1. Exact closure of the literal group, its commutator and all conjugacy
   classes gives order 12, commutator order 3, and exactly three junior
   classes. Their conjugates generate the full group. Invertible matrices
   intertwine this representation with each of legacy entries 195, 196 and 197.
2. Over `QQ(zeta)`, with `zeta^2-zeta+1=0`, the substitution `x=P*y` gives
   commutator weights `(1,1,2,2)` modulo three. The twelve displayed
   polynomials form an invertible basis of the four mixed quadratics and
   eight pure cubics; those monomials generate the entire invariant monoid.
   Every valuation and initial form is rebuilt from the literal junior
   matrix, rather than inferred from a stored degree label.
3. Full ordinary graph elimination followed by simultaneous
   multihomogenization and saturation yields the entire candidate ideal.
   Both ideal inclusions with all 83 displayed relations are checked after
   adjoining the order-two roots of the exceptional coordinates. Three
   complete character-tagged initial kernels are independently eliminated,
   homogenized and saturated; all simultaneous Schmitt inclusions vanish.
4. All six gauges have determinant ±1 in the specified primitive class
   lattice. Eight constant linear eliminations on each gauge slice leave
   four free variables. Their inverse maps and every original equation are
   checked. The second and third principal opens localize these polynomial
   rings. The displayed first parametrization is checked by equality of
   its graph ideal with the full gauge-slice ideal in both directions.
5. Every independent cone of at most three degree columns is examined.
   Each semistable ambient basis open has empty intersection with the
   complement of the six specified opens, by a newly computed unit
   saturated ideal. This proves full coverage without assuming a stored
   list of realized faces. The character avoids all lower-dimensional
   cones. Its raw degree is strictly negative and has the explicit
   invariant-cone expression `D1+2*D9+2*D10`; the three positive-valuation
   gcds are also recomputed as units. Thus the sufficient admissibility
   test in the manuscript applies.

The dedicated verifier is the supported entry point for legacy entries 194–197, which represent manuscript case 75.
