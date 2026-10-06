# Part VI: exact finite models and named Hodge profiles

```sh
sage -python ihs_verification/verify_named_hodge.py --output /tmp/named-hodge.json
sage -python ihs_verification/run.py --check torsion --output-dir /tmp/seven-torsion
sage -python ihs_verification/run.py --check models --output-dir /tmp/extra-models
```

The Hodge program reads only the current public `catalogue.json`. For indices 98, 99, 211, 41, 42, 43, 61, 150, 199 and 226 it closes the actual matrix groups, enumerates conjugacy classes and centralizers, computes Smith forms with unimodular transformations, acts on the torsion component group, and averages the exact exterior-character polynomials. Its output includes every sector, not only final numbers. A second Euler calculation uses all commuting pairs and the Smith divisors of their stacked 8-by-4 fixed-point matrix; it does not use the Hodge coefficients. These are the ten profiles singled out in Part VI, not all 245 profiles. Numerical agreement alone is not a geometric identification or an existence proof.

The GAP programs contain explicit exact cyclotomic transcriptions of the matrices in the finite-exclusion and explicit-matrix sections of Part VI. In `verify_seven_torsion.g`, the generators `oo1`–`oo4`, `pp1`–`pp4`, and `vee`, `ss` are respectively the displayed O, P and extended-block models. The program freshly closes W(O1), W(O2), W(P1), W(P2), E(mu6 T), E(OT4), E(OT2), enumerates all reflection-generated subgroups avoiding minus the identity, and recomputes the coset marks and determinant witnesses used in all seven exclusions. The irrational trace witnesses for O3 and P3 are checked too. Assertions are enabled explicitly; GAP's final completion marker is required in addition to its exit code.

`verify_extra_models.g` checks the published type-V matrices and automorphism, its four-dimensional group and reflections, and the displayed model G32, including all reflection-generated subgroups containing minus the identity. The selected matrices are mathematical inputs in these programs; they are not inferred from stored group names or past success flags. These checks verify the finite arithmetic. The classification theorems, actual stabilizer arguments, lattice geometry and deformation-type deductions retain their separate proofs in the article.

Output directories for GAP runs must be new or empty. The wrapper records input and output hashes and complete fresh logs. None of these entry points reads the referee report or historical calculation outputs.
