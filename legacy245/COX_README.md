# Cox presentations and computational proofs

Numbered directories use the **legacy 245-entry catalogue**. `cox_index.json` gives the other integral entries covered by the same calculation. Use the [current case catalogue](../cases/README.md) and [numbering map](../cases/index.json) to locate the corresponding manuscript case among the 106 quotient classes. All case numbers below are legacy indices unless stated otherwise.

The directly readable files are the current mathematical data:

**Legacy case 194 (manuscript case 75) is an exception to the uniform filenames:** its supported calculation uses
`194/paper_model83.json`, `194/paper_invariants83.json` and
`194/paper_charts83.json`. Its `model.json` and `invariants.json` retain the
different 51-relation presentation. Equal coordinate names in those two
presentations do not denote equal functions. The supported Cox and endpoint
steps use only the dedicated paper83 data and verifier.

- `N/model.json` gives the complete list of relation polynomials, the exact order of the Cox coordinates, the valuation grading, and the primitive integral grading. Each entry of `equations` is set equal to zero. Relations need not form a minimal generating set.
- `N/invariants.json` gives the ordered invariant polynomials, their polynomial coordinate names, junior orders, and valuations. Whenever present, `junior_initial_generators` records the initial polynomials used in the complete generation tests. Extra matrix and coordinate-change fields retain the exact representation binding.
- `N/README.md` identifies the presentation and verification commands. The remaining `N/export_model.sing` files regenerate their associated polynomial inputs.

## Coordinate convention

Write the ordered invariant polynomials as F_1,...,F_n, and let r_l be the order of the l-th chosen junior representative. For independent Laurent variables s_l, the defining map is

    u_j -> F_j product_l s_l^(-nu_l(F_j)),    e_l -> s_l^(r_l).

The variables occur in precisely the order recorded in `coordinate_order`. The first n columns of `valuation_grading` are minus the valuation matrix; its final columns are diag(r_l). The primitive grading has the same rational row space and its columns generate the full character lattice. No permutation of generators is implicit. In Case 177 the quadratic invariant is **the last invariant**, u_27. In Cases 114 and 138 the original polynomial coordinates are named z_1,...,z_4; these are different from the Cox coordinates u_j.

The coefficient field of a displayed relation ideal can be smaller than the field used to write its invariant polynomials or eigenbases. `cyclotomic_minpoly` and the occurrences of `zeta` specify the latter extension. Powers use `^`; all coefficients are exact rational numbers or elements of the indicated cyclotomic field.

## Junior representatives and eigenbases

The fields `junior_representatives_in_coordinates` or `canonical_juniors` specify the chosen junior matrices in the coordinates of the F_j. Fields `coordinate_change_from_catalogue`, `coordinate_change_to_original`, or `canonical_conjugator`, when present, bind those coordinates to the catalogue.

Cases 114 and 138 retain explicit `junior_eigenbases` and `junior_full_generators`. Case 231 retains representation intertwiners and physical initial forms in `bindings` and `physical_initials`; its invariant polynomials use the monomial model defined in the same file. The supported matrix witnesses for all four special cases 114, 138, 231 and 233 are in `binding_verification/special_groups.json`. Their complete group conjugacies and junior classes are verified again from the public catalogue.

`binding_verification/valuation_maps.py` computes the ordered eigenbasis substitutions from the actual junior matrices, ordering eigenspaces by exponents 0,...,r_l-1. Case 227 uses the explicit within-eigenspace changes in `binding_verification/227_initial_bases.json`; the validator checks their diagonalization and exact agreement with every stored initial polynomial. A change of basis within a weight space changes the written initial polynomials but preserves their valuations and the generation condition. The supported commands verify the chosen convention from these public witnesses and require no source-archive scripts.

## Supported fresh checks

Run from the `legacy245/` directory. Each command uses a fresh isolated copy and writes its results outside the checkout:

```sh
python3 run_verification.py --steps cox-models --output-dir /tmp/sl4-cox-gradings
python3 run_verification.py --steps binding-161,cox-161,endpoint-161 --output-dir /tmp/sl4-legacy-161
python3 run_verification.py --steps binding-194,cox-194,endpoint-194 --output-dir /tmp/sl4-legacy-194
```

Prefer the unified `run_verification.py` described in the main README when running several cases. It copies inputs into a new directory and saves commands, scopes, input hashes and live logs. The Cox profile uses the dedicated validator for 194 and the full polynomial-map validator for the other representatives. Endpoint calculations are separate steps.

The uniform `check_cox_models.sage.py` checks raw valuation columns, equality of rational grading row spaces, primitivity by Smith form, and homogeneity of all relations. Its three evaluations in a split finite field are consistency checks, not characteristic-zero identity proofs. `--symbolic` adds exact substitution of every invariant polynomial into every relation. Such substitution proves containment in the kernel, not equality with it or completeness of Cox generators.

`binding_verification/verify_binding.py` reconstructs the complete catalogue group and its commutator, checks the supplied coordinate conjugacy against every group element, and verifies that the ordered junior matrices cover all junior conjugacy classes. It then checks exact invariance of every polynomial, all valuations, the stored initial forms or full eigenbasis expressions, and the complete finite character grading, and recomputes the commutator Molien series. `binding_verification/valuation_maps.py` derives the required polynomial substitutions from the actual matrices. The supplied conjugating matrices are mathematical witnesses, never stored verification flags. The `bindings` profile runs these checks for all 21 representatives.

For case 179, invariance is proved by exact substitutions on six core
polynomials and 25 checked monic triangular identities for the remaining
polynomials. Each identity is evaluated in the actual four-variable polynomial
ring; induction then proves invariance of all 31 generators under every
commutator generator. The report distinguishes direct substitutions from
equalities proved by these identities and records the chosen identities and
the helper's hash. Group enumeration, all valuations and stored initial-form
checks retain their full scope.

`full_verification/verify_cox.py` recomputes the complete ordinary polynomial-map kernel and complete finite-character-tagged initial kernels. It homogenizes and saturates with respect to every valuation and checks the simultaneous containments. It also compares the supplied presentation with the full homogenized ordinary kernel in both directions. The default `--stage all` and no `--junior` selection performs the entire polynomial-map criterion; selected stages are explicitly partial. See [full_verification/README.md](full_verification/README.md) for the exact algorithm and checkpoint policy.

The public-presentation method can certify the ordinary multihomogenization by checking its full multigrading, exact dehomogenization to the complete ordinary kernel, and saturation with respect to each valuation parameter. This proves the same ideal equality while avoiding unnecessarily large intermediate homogenizations. The proof and reusable helper are in `full_verification/native_checks/`.

These calculations have separate logical prerequisites: the ordinary generators must generate the complete invariant algebra of the stated commutator group, and the valuations and characters must be bound to the actual representation. A successful polynomial-map criterion alone does not establish those prerequisites. Conversely, testing valuations separately does not establish the simultaneous criterion. The binding validator supplies the representation, valuation and character checks; generation of the invariant algebra additionally requires a full-kernel Hilbert comparison with the recomputed Molien series, or the stated independent generation argument.

The endpoint validator recomputes the required chart equations, Jacobian or minor identities, full support covers, and negative point/cone witnesses for each supported representative. Its result concerns the geometric end of the proof, conditional on the algebra and representation identification. In particular a smooth chart calculation cannot repair an incorrect presentation.

The dedicated legacy case 194 validator supports manuscript case 75 using its ordered 83-relation presentation, and checks the input binding and all six slices. The alternative 51-relation presentation has a different coordinate ordering and must be checked separately.
