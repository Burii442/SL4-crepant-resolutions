# Exact representation and polynomial binding

From the supplement directory:

```sh
sage -python binding_verification/verify_binding.py --case 179 --output /tmp/binding-179.json
python3 run_verification.py --profile bindings --output-dir /tmp/all-bindings
```

The unified runner uses a fresh isolated snapshot. Each case report identifies
its actual catalogue, model, invariant data, matrix witnesses and program
bytes by SHA-256.

The validator reconstructs the entire finite matrix group and its commutator.
It checks the convention `P^-1 G_catalogue P = G_polynomial` by comparing all
group elements, verifies every chosen junior and its complete conjugacy class,
and proves that these classes cover all juniors. Exact polynomial operations
then check commutator invariance, all valuations, the supplied initial forms
or full eigenbasis expressions, and the finite character lattice. Finally it
recomputes Molien from every commutator element.

`standard_groups.json` and `special_groups.json` contain mathematical matrix
witnesses, with no stored correctness flags. The latter covers 114, 138, 231
and 233. The explicit changes within the junior eigenspaces for 227 are in
`227_initial_bases.json`; both their diagonalization and all resulting initial
forms are checked. `valuation_maps.py` supplies the same actual substitutions
to the full algebra validator.

For 179, `triangular_invariance.py` verifies 25 identities
`F_j = P_j(F_1,...,F_{j-1})`, each monic in the new generator. It evaluates each
identity in the actual four-variable polynomial ring. Invariance of the first
six generators under the complete generating set of the commutator therefore
implies invariance of all 31, by induction. No claim about completeness of a
relation ideal is required for this inference. The report records both the
direct substitution count and all identities used in the induction.

A complete binding proves that the proposed polynomials are invariants of the
stated representation with the stated valuations and characters. Generation
of the entire invariant algebra is a separate assertion: the fresh complete
ordinary-kernel Hilbert series must match the freshly recomputed Molien
series, or another complete generation proof must be supplied. The unified
`all` profile and the documented comparison of isolated fresh runs perform
this additional check. The article's case 194 uses its separate paper83
certificate; the uniform binding of its older model does not replace it.
