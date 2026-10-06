# Independent determinant-one count in the classical catalogue

Result: **106 Q-classes and 245 Z-classes** of finite determinant-one
four-dimensional integral matrix groups, selected from **all 227 Q-classes
and 710 Z-classes** in the classical catalogue. The 106 classical spectral
distributions agree exactly with all 106 classes in the current manuscript.

This enumeration used GAP 4.15.1 and its officially distributed CrystCat
1.1.10 package. CrystCat derives from Brown–Bülow–Neubüser–Wondratschek–
Zassenhaus, *Crystallographic groups of four-dimensional space* (Wiley,
1978), and was brought into GAP format by Volkmar Felsch. See the
[official repository](https://github.com/gap-packages/crystcat) and the
[maintainer's documentation](https://www.math.uni-bielefeld.de/~gaehler/gap/packages.php#CrystCat).
The underlying matrix representatives are documented as those of Table 1
in that monograph. The distributed matrix data are in `all_qclasses.json`; `case_map.json` gives the expected correspondence, rechecked by the comparator.

The computation independently enumerates all 33 crystal systems and all
227 Q-classes. For each class it takes `MatGroupZClass(4, system, qclass, 1)`
and checks the determinant of every generator. It also adds the number of
Z-classes in each selected Q-class. Determinant is invariant under
conjugacy, so the result does not depend on the chosen Z-class representative.
The manuscript's 245 entries are not used as a source of completeness.

## Reproduce

From this directory, with GAP and CrystCat installed:

```sh
gap -q --quitonbreak count_crystcat.g
python3 compare_catalogue.py ../manuscript106/catalogue/catalogue.json
```

The first command writes `all_qclasses.json`, with all 227 classes, their
matrix generators, determinant lists, orders and Z-class counts. Its output:

```text
ALL_Q=227 ALL_Z=710 SL4_Q=106 SL4_Z=245
```

The second command uses only the Python standard library. It checks
integer determinants again, reconstructs all 106 selected finite groups
by exact multiplication (4211 elements in total), and computes each
characteristic-polynomial distribution using Newton identities. It also
reconstructs every manuscript group. The distributions are pairwise
distinct on both sides and coincide as sets. The result is `comparison.json`,
including the complete bijection between manuscript case numbers and
classical `[dimension, system, qclass, zclass=1]` references.

## Meaning of the equivalence relations

Z-classes mean conjugacy in GL_4(Z), not necessarily in SL_4(Z). They retain
integral lattice information. Q-classes mean conjugacy in GL_4(Q).

For two subgroups with rational matrices, conjugacy in GL_4(C) already
implies conjugacy in GL_4(Q). A fixed complex conjugating matrix induces a
bijection between the groups. The intertwining equations for that
bijection have rational coefficients. Their rational solution space,
after scalar extension to C, contains an invertible matrix. The determinant
polynomial is therefore not identically zero on this rational vector
space; since Q is infinite, it has an invertible rational point. This
proves descent of the conjugating matrix. In particular GL_4(Q), GL_4(R)
and GL_4(C) give the same classes here.

Finally GL_4(C)-conjugacy agrees with SL_4(C)-conjugacy: multiply an
invertible conjugating matrix P by a scalar lambda with
lambda^4 det(P)=1. Scalar multiplication does not change the conjugation.
No analogous assertion is being made for conjugacy in SL_4(Z).

Because the classical list is complete and has 106 determinant-one
Q-classes, and the manuscript has 106 pairwise distinct conjugacy
invariants, the manuscript exhausts precisely that classical subset.
Equality of spectral distributions alone is not asserted to classify
arbitrary matrix groups; the classical completeness and equal count are
part of this argument.
