# Full polynomial-kernel verification

Run from any working directory with SageMath 10.x:

```
sage -python full_verification/verify_cox.py --case 114 --output-dir verification-results/114
```

The verifier reads the public `CASE/invariants.json` and `CASE/model.json`; it does not load the research archive, author's programs, old result flags, or purported complete initial ideals. The printed case194 model with 83 relations is checked separately by `194/verify194.py`; the generic entry point would instead check its alternate 51-relation presentation. There is no built-in time limit. `--junior N` selects one junior; omit it to check all. `--stage base`, `--stage initial`, and `--stage simultaneous` select the corresponding stages (`all` is the default). `--stage core` checks only the preliminary exact triangular identities and is not a full kernel check. `--direct` disables this optimization. `--resume` reuses local checkpoints only when the recorded public inputs, verifier dependencies and algorithm options match.

The generic graph route removes redundant variables using monic linear graph equations. Candidate equations come from the public ordinary relations or their valuation initials. Each selected identity is re-evaluated exactly on the supplied polynomials, and each tagged identity is checked for finite-character homogeneity. The remaining physical graph is eliminated completely; re-adjoining the checked triangular equations gives the full kernel. When the core forms descend to rational coefficients after nonzero rescaling, the graph is computed over QQ and those rescalings are reversed exactly. The larger cases also use the complete-intersection, localization and Hilbert-bound proofs described below. These are alternative proofs of complete kernels; a list of vanishing candidate relations alone is never accepted as a kernel.

The simultaneous criterion uses the full multihomogenization of every complete tagged initial kernel. The generic route constructs it by homogenizing with respect to all valuations and successively saturating by the valuation parameters. Case 174 also supports the exact target-regularity proof described below, which proves the same full containment without materializing that larger ideal. The default ordinary route identifies the public ideal with the full ordinary multihomogenization by specialization and saturation; the optional direct route reconstructs it by homogenization. The generic saturation implementation uses a positive weighted reverse lexicographic order with the saturation variable last: divide each element of a newly computed Gröbner basis by its maximal common power of that variable. Homogeneity is checked before applying this Bayer saturation step. For the public presentation179, the complete characteristic-zero Hilbert identity described below proves the same saturation equalities. No supplied list is assumed to be a Gröbner basis.

The resulting ordinary full kernel is compared in both directions with the public Cox presentation after adjoining unit valuation parameters, via `e_i = t_i**r_i`. Each full homogenized initial kernel is proved to lie in the full ordinary homogenized kernel plus `t_i`, either by exact reduction of its complete generators or by the target-regularity proof below. A complete successful run proves the simultaneous polynomial-map criterion for the supplied generators, valuations, and character data.

For 171, 173, 177 and 221, the automatic ordinary-certificate route invokes the actual group/valuation binding and proves full generation of the commutator invariant algebra, as explained below. For the other cases, a complete ordinary kernel and its exact Hilbert series prove full invariant generation only after comparison with the commutator Molien series from a fresh binding certificate. The public top-level runner performs that comparison and checks matching mathematical input hashes. A selected polynomial-kernel stage alone must not be reported as a complete Cox-ring proof.

Outputs include `events.jsonl`, one JSON checkpoint per exact stage, and `report.json`. A report with `complete_simultaneous_criterion: false` is partial, even when the requested selected stages passed. Failed computations raise an error and do not write a successful final report. Checkpoints are a local resume mechanism, not externally trusted certificates: a clean output directory recomputes every stage.

## Ordinary invariant generation and modular certificates

`verify_generation.py --case N --output-dir PATH --kernel-hilbert` recomputes the commutator and its Molien series from the catalogue matrices. It computes the ranks of products of the public generators over a finite field, in every ordinary degree through the characteristic-zero Noether bound `|[G,G]|`. The chosen prime and the root defining the coefficient reduction are recorded. A nonzero minor after reduction is also nonzero in characteristic zero. Thus matching the Molien dimensions supplies the required lower bounds; exact invariance and the actual-representation identification supply the upper bounds. Those latter hypotheses are explicitly marked as separate in this program's output.

For the relation ideal, denominators are cleared and primitive integral generators are reduced modulo the prime. Its modular Hilbert series is an **upper bound**, degree by degree, for the characteristic-zero quotient Hilbert function. If exact physical relation identities and generation have been verified, the Molien series is the matching lower bound. Equality of the modular Hilbert series with Molien therefore proves equality in characteristic zero and completeness of the ordinary relation ideal. This is a specialization-rank argument, not an assumption that one prime detects every error.

`ordinary_certificate.py` combines these calculations with a fresh invocation of the actual binding/invariance verifier and exact evaluation of every ordinary relation on the supplied polynomials. Only after all hypotheses pass does it mark `ordinary_kernel_complete` and `ordinary_invariant_generation_proved` as true. The main verifier selects this path automatically for 171, 173, 177, and 221; `--ordinary-method graph` forces direct graph elimination, while `--ordinary-method molien` requests the modular-dimension proof explicitly. Running the Noether computation for groups with a very large commutator can be expensive, so the automatic selection is deliberate.

## Complete-intersection certificates

For 179 the six-generator core has two separate equations `u5^2=f(u1,u2,u3,u4)` and `u6^2=g(u1,u2,u3,u4)`. The verifier checks that both radicands are nonconstant and squarefree and that their gcd is a unit. Their square classes, including their product, are therefore nontrivial over the fraction field. The generic biquadratic quotient is a field; the whole quotient is free of rank four over the polynomial parameter ring and consequently is a domain. Both physical identities and a rank-four Jacobian witness are checked exactly, so this prime ideal of dimension four is the complete core kernel. All 25 extra variables are adjoined by checked monic graph equations. The weighted Hilbert series is the corresponding complete-intersection series.

For 178, `special_kernels.py` first solves a relation linearly for `u2` after inverting `u1`. The remaining cubic has unit leading coefficient over a Laurent polynomial ring. An irreducible rational cubic specialization and coprimality of its degree with the coefficient-field degree prove irreducibility after that extension. The section `u1=0` is a regular sequence of the expected codimension; hence `u1` is a nonzerodivisor in the complete-intersection quotient. The original core quotient is therefore a domain. Exact defining identities, a rank-four Jacobian witness, and all 12 triangular extensions finish the kernel proof.

## Finite tags and the public multihomogenization

The generic `--tag-method characters` route computes the finite-tag kernel by Chinese-remainder decomposition: compute the complete untagged kernel, twist it by every character value, and intersect all these ideals exactly. A complete untagged kernel already homogeneous for every finite character is unchanged. The special localized helpers also use the exact ratio-character reconstruction described below. All required roots of unity are in the declared coefficient field. `--tag-method graph` instead eliminates the finite-character variables and their order equations in one graph. Both constructions give the complete tagged kernel. The default `--tag-method auto` uses the physical graph for case227 juniors1 and2, and character intersections for its third junior. For case161 junior2, it uses `finite_ordinary_graph.py`: apply the inverse finite-character automorphism to the entire proved ordinary ideal, adjoin all equations `c_k^r_k-1`, and eliminate only these finite variables. Flat coefficient descent and this exact contraction give its full tagged kernel. Other cases use character intersections or the specialized complete helpers described below. Character-compatible monic variables are removed before the case227 intersection and restored afterwards. This choice avoids the larger unreduced intersection for its second junior. Explicit `--tag-method graph` and `--tag-method characters` remain available to select either complete method for every junior.

The default `--base-method public-saturation` uses `native_checks/public_saturation.py`. It checks every ordinary and valuation grading of the public presentation, identifies its specialization at all parameters equal to one with the already proved complete ordinary kernel, and verifies saturation at every parameter. Multihomogeneity identifies the localized ideal with the ordinary kernel after the invertible variable rescaling; saturation recovers its unique contraction. This proves that the public ideal is the complete multihomogenized kernel. `--base-method homogenize` retains the direct homogenize-and-saturate reconstruction for comparison.

For case 174, `native_checks/native_colons.py` proves parameter saturation using complete first-colon equalities: `I:e_k = I` implies `I:e_k^m = I` for every positive integer `m`. The complete colon is computed by exact ideal quotient, or equality is certified by the absence of the parameter from every leading monomial of a freshly computed complete Gröbner basis. All colon generators are checked. The rational coefficient descent is faithfully flat, and adjoining `t_k` with `e_k=t_k^r_k` is a finite free extension.

For the case 174 simultaneous tests, the same helper freshly homogenizes every generator of the complete tagged initial kernel. It requires that these raw homogeneous polynomials be independent of the own parameter `t_i`. It then sets `t_i=0` in the full ordinary homogeneous ideal, checks every raw polynomial in this quotient target, and proves that target saturated at every remaining parameter by complete first-colon equalities. Consequently the saturation of the entire raw initial ideal remains in the target. The raw ideal and its remaining saturation extend from the ring without `t_i`, so saturation at the own parameter adds nothing. This proves the full simultaneous containment; it does not merely check a selected set of relations. The separate `--stage initial` still constructs the full homogeneous initial ideal directly.

For case 174 junior 2, `special_initial174_j2.py` freshly proves the complete unsigned kernel using five forms `u1,u2,u5,u6,u7`: their primitive rank-three quadratic relation and a nonzero physical Jacobian minor give the entire five-form kernel. Twenty checked polynomial graph equations restore all 25 forms. One of those graphs, `u4 - (-u1^2/8 + u2/2)`, is not homogeneous for the finite C2 character and is never accepted as a tagged relation. The verifier removes only the other nineteen character-homogeneous monic graphs, computes the complete intersection of the two character twists in the resulting six-variable ring, and restores the nineteen graph equations. The stored JSON supplies candidate identities, all rechecked on the literal physical forms; it supplies no trusted completeness flag.

For cases 171 and 177, `native_checks/exact_images.py` proves the forward ordinary inclusion by evaluating every public relation on the actual polynomial generators in characteristic zero. It is an exact polynomial homomorphism, with a separately checked numbered zero result for every input. The already proved completeness of the ordinary kernel makes these vanishing tests equivalent to ideal membership. The reverse inclusion is still checked by full ideal reduction. Cases 178 and 179 instead use a smaller exact quotient obtained from literal monic definitions; every generator of the complete ordinary kernel is imposed in that quotient. Neither route assumes that a supplied small relation list is complete.

For case 173, `native_checks/kronecker_images.py` computes these exact physical images in `QQ[T]`. Every generator and relation is checked for the required homogeneity. On the physical homogeneous component of degree `d`, setting the last variable to one is injective; the remaining exponents are at most `d`. Substituting `T, T^(d+1), T^((d+1)^2)` therefore remains injective by uniqueness of mixed-radix expansion. The univariate polynomial is computed exactly and must be zero for every relation. This is neither evaluation at a numerical point nor a probabilistic identity test.

`base_hilbert.json` always identifies whether the ordinary kernel has been proved complete in characteristic zero. An exact ordinary-image Hilbert series together with a freshly verified actual binding and equality to the commutator Molien series proves invariant generation. A bare modular Hilbert series must never be substituted for that proof; use the combined ordinary certificate when selecting the modular route.

### Artinian Hilbert upper bounds

For case 171 the ordinary relation ideal has 36 variables. The default
`verify_generation.py --kernel-hilbert` avoids its expensive unrestricted
Groebner basis by adjoining four explicitly recorded homogeneous parameters
of degrees 2, 6, 8, 12 over the coefficient residue field. The full Groebner
basis of this enlarged ideal yields the polynomial

`1 + 6*t^6 + 8*t^8 + 18*t^12 + 8*t^16 + 6*t^18 + t^24`.

No regular-sequence assumption enters this check. For any homogeneous element
h of degree d, its multiplication exact sequence gives
`H_R <= H_(R/(h))/(1-t^d)` coefficient by coefficient. Iteration gives a
Hilbert upper bound from the parameter quotient. Specialization also gives
`H_(S_Q/I_Q) <= H_(S_Fp/I_Fp)`. The actual invariant-algebra binding, modular
ranks through the characteristic-zero Noether bound, and exact ordinary
relation identities give the opposite Molien lower bound. Equality of the
computed parameter bound with Molien therefore proves both the full ordinary
kernel and its characteristic-zero Hilbert series. All four parameter
polynomials, their degrees, the coefficient prime, and the full quotient
Hilbert polynomial are written to the result; `--hilbert-method full` selects
the slower unrestricted quotient calculation.

### Small initial hypersurfaces

`special_kernels.quadratic_hypersurface` recognizes five-generator initial
maps in case179, juniors2 and3, whose defining polynomial is quadratic with constant nonzero leading
coefficient. It factors the rational discriminant and verifies an odd
nonconstant factor multiplicity, proving irreducibility after extension of
the coefficient field. Every defining identity and a rank-four Jacobian
minor are checked. Together with the exact monic graph extensions this proves
the complete ordinary initial-map kernel. For case 179, character-compatible
monic graph variables are then removed before taking finite-character
intersections, and restored afterwards. The intersections are of the full
small kernels, never of an assumed truncated relation list.

### Sequential full multihomogenization

For the large cases the default homogenizes one valuation at a time. At each
step the entire current ideal is homogenized in a new parameter and exactly
saturated by that parameter using a positive weighted reverse lexicographic
Groebner basis. Older parameters have weight zero for the newly introduced
valuation. Their previous saturation is preserved by this homogenization and
contraction. Inductively, the result is the full multihomogenized kernel.
The order changes runtime but not the resulting ideal; the CLI
`--hom-method simultaneous` retains the all-at-once alternative and
`--hom-order` selects a parameter permutation. If a parameter is absent,
saturation by it is the identity operation and is recorded as such.
For case 177, junior 1 uses the verified parameter order `3,2,4,1`;
the other juniors retain their separate default orders. This only changes
the intermediate presentations, not the full multihomogenized ideals.

### Parameter and Reynolds generation bound

For cases 173 and 177 the public verifier improves the general Noether bound
by computing a full Groebner basis of the four actual homogeneous parameter
polynomials, of degrees 2, 6, 8, 12, in the four physical variables modulo a
good coefficient prime. The leading ideal contains a pure power of each
variable; those powers, the basis, and the coefficients expressing the
parameters in the public generators are recorded. Full ranks of the
homogeneous parameter-ideal coefficient matrices lift this finite-colength
statement to characteristic zero.

Four homogeneous parameters form a regular sequence in the polynomial ring
in four variables. Its quotient has no terms above degree
`(2-1)+(6-1)+(8-1)+(12-1)=24`. Graded Nakayama therefore gives polynomial-ring
module generators over the parameter algebra in degrees at most 24. The
Reynolds operator is linear over that algebra and preserves degree, so the
invariant ring has module generators within the same bound. Once the exact
actual-group binding supplies invariance, the independently recomputed ranks
of products of the public generators through degree 24 prove full generation.
This argument uses no assumption about a presentation or an initial algebra.
`--generation-bound noether` retains the longer general-bound calculation.

### Parameter power compression

Before each Bayer saturation, the verifier checks divisibility of every
parameter exponent by its junior order. Where this holds, it computes in
`e_j=t_j^r_j`, with the parameter weight multiplied by `r_j`, then restores the
original powers. The extension from the e-polynomial ring to the t-polynomial
ring is finite free. Colons by powers of e commute with this flat extension,
and saturation by t equals saturation by e. Thus this reduces the computation
without weakening it. `--parameter-compression none` disables the optimization.


### Saturation standard bases and exact coefficient descent

The default `--saturation-method satstd` uses Singular `customstd.lib` to
compute a standard basis of an intermediate ideal `I <= J <= I:t^infinity`.
The algorithm performs exact standard-basis operations and may divide by the
specified parameter. Every original input is then reduced to zero by that
basis, explicitly checking `I <= J`. We do **not** assume this partial
saturation is complete in a weighted order. The subsequent homogeneous
Bayer last-variable stripping computes `J:t^infinity=I:t^infinity`.
Interreduction after stripping preserves the ideal and removes redundant
polynomials before their coefficient-field lift and export.
`--saturation-method groebner` retains ordinary standard-basis computation.
For case 233 a direct exact ideal saturation in the ordinary degree reverse
lexicographic order is considerably faster and is used instead.

When all normalized coefficients are rational, these computations and the
ordinary membership checks take place over QQ. A faithfully flat field
extension restores the declared coefficient field. This is an exact
characteristic-zero operation. It is separate from the explicitly identified
finite-field dimension arguments in `verify_generation.py`.

For a finite-character intersection, `exact_algebra.py` also detects when
all normalized coefficients lie in a proper subfield generated by a common
power of the declared number-field generator. It computes that generator's
minimal polynomial, constructs the explicit field embedding, and checks
every translated coefficient under the embedding. The intersection can then
be computed in the smaller field and restored exactly, by flat base change.
For the second initial map of161 this descends from the degree-eight field
to the quadratic field generated by `zeta^4`.

For that map, the default `--tag-method auto` uses
`finite_ordinary_graph.py`. Starting with the freshly proved complete ordinary
kernel, it adjoins the finite variables and their order equations
`c_k^r_k=1`, applies the inverse character twist to every ordinary generator,
and completely eliminates the finite variables. Twisting is an automorphism
modulo the order equations, so this contraction is the entire tagged kernel.
The exact coefficient descent described above also applies to this finite
graph. Explicit `--tag-method characters` retains the full intersection route;
neither method reads a saved assertion of kernel completeness.

### Complete localized initial kernels

The helpers read the literal public polynomial maps. Auxiliary equations
serve only as accelerators and are evaluated exactly; no stored assertion of
kernel completeness is accepted.

* `special_initial173.py`: seven core forms depend on two physical variables.
  Their complete binary graph kernel is computed afresh. Three verified
  linear relations recover three other covariants after inverting
  `u21*(11*u21^3-15*u1-28*u7)`. A nonzero physical determinant proves that the
  two retained linear covariants are independent over the binary fraction
  field. The localized quotient is consequently a polynomial extension of
  the binary image domain. Full saturation contracts its complete kernel.
* `special_initial171.py`: eleven binary forms have a freshly eliminated full
  kernel. Seventeen triangular equations recover the remaining covariants
  after inverting `u1*u6`, leaving two linearly independent physical
  covariants. The same localization argument proves completeness, and full
  saturations by both denominators contract the kernel. Every resulting
  generator is checked for finite-character homogeneity.
  `special_initial171_j2.py` uses the analogous second initial decomposition.
  `special_initial171_j3.py` retains seven binary forms and the independent
  outputs `u6,u7`; three recovery blocks of sizes eight, nine and four have
  determinants supported on `u1,u8,u20`. Their complete contractions use only
  these three variable denominators. Every extra equation used to accelerate
  a saturation is first evaluated in the literal physical map.
* `special_initial161.py`: the second initial map is compressed by an
  injective physical monomial substitution and exact descent from the
  declared cyclotomic field to its smaller coefficient field. The helper
  verifies the entire compression, computes the complete kernel of seven
  binary forms, and checks ten linear recovery equations. Their common
  denominator and the independent two-column determinant give the localized
  full kernel. Saturation, coefficient-field restoration, and exact checking
  of every exported image complete the certificate.
* `special_initial178.py`: for the first ten initial forms, five exact monic
  equations leave a primitive ternary quadratic over two free parameters.
  Its rank-three matrix proves geometric irreducibility, and a physical
  rank-four Jacobian proves equality with the ordinary map kernel. The two
  independent finite characters are recovered as the ratios `u6/u3` and
  `u5/u4` of equal unsigned forms. `rational_tags.py` untwists the **complete**
  ordinary kernel, imposes both ratio-order equations, and fully saturates
  by their denominators. Eight more exact graph equations recover the
  remaining generators after inverting `u1`; a final full saturation gives
  the complete tagged kernel on all eighteen public generators.

For the ratio-character argument, the denominator is nonzero in every
component of the finite product of physical polynomial domains. It is
therefore a nonzerodivisor in the target. Recovering the finite parameters
establishes equality after localization, and exact saturation gives equality
before localization. No bounded search or presumed list of initial
relations is used to infer completeness.


The analogous `special_initial179.py` proves the first initial kernel by a
primitive rank-three quadratic on five retained forms, an exact rank-four
Jacobian and twenty-six localized recoveries. All recovered denominators are
powers of explicitly nonzero core polynomials; full ideal saturation
contracts the localized graph, and every exported relation is evaluated.
`special_initial179_j5.py` uses the injective monomial coordinates
`a=x1^2,b=x2^2,c=x1*x3,d=x2*x4`. A complete graph elimination on seven retained
forms (with the linear coordinate `b=u1-2*a` eliminated explicitly) gives the
full core kernel. Twenty-four checked recoveries and saturation by `u1`
extend it to all thirty-one forms. The physical automorphism
`(c,d) -> (-c,-d)` realizes the finite character, so this whole kernel is
already the tagged kernel. The remaining fourth initial kernel uses a full
physical graph accelerated by individually verified redundant equations;
those equations are never assumed complete.

`special_initial177_j2.py` computes the full binary kernel and adjoins a
rank-three quadratic relation between three quadratic covariants. After
inverting its leading coefficient, this relation is monic and geometrically
irreducible over the binary fraction field; the localized quotient is a
domain. An exact rank-four physical Jacobian proves injectivity. Two recovery
blocks, full contraction by three binary variables and one checked monic
extension restore all twenty-seven literal generators.

`special_initial177_j3.py` uses the complete binary graph and two independent
outputs. Its three recovery blocks have determinants equal to constants times
powers of a single binary variable. Saturating by that variable gives the
complete ordinary kernel. The second finite character is already homogeneous;
the first is recovered as the ratio of two equal scaled physical forms.
`rational_tags.py` imposes its order equation and computes the full contraction.
Reducing ratio exponents modulo their finite order is exact modulo those order
equations and avoids unnecessary powers in the intermediate relations. A
checked monic extension and nonzero coefficient scalings give the literal
twenty-seven-generator tagged kernel.

`special_initial177_j1.py` and `special_initial177_j4.py` use complete binary
graphs, two independent outputs and recovery matrices with explicitly
factored binary denominators. After full contraction and checked monic
extensions, one character follows from the exact physical transverse
degree. The remaining character is recovered by a ratio of equal forms.
The first case uses two explicitly invertible graded coordinate changes to
exhibit that ratio; the fourth needs only one nonzero scalar change. Both
helpers restore the original coordinates and check every final relation in
the literal physical map and both finite character gradings.

Some localized helpers permit `satstd` to divide by all final denominator
variables while each Bayer step places one of them last. This has a direct
sandwich proof. Let `T=I:S^infinity`, where S is their product, and let P_k be
the product of the first k processed variables. Inductively
`I:P_(k-1)^infinity <= I_(k-1) <= T`. A partial saturation gives
`I_(k-1) <= J <= T`, and the full Bayer step gives `I_k=J:t_k^infinity`.
Consequently `I:P_k^infinity <= I_k <= T`. At the final step the lower bound
is T. Preservation of intermediate saturations is not assumed. The code also
checks that the leading monomial has the minimum exponent of the last
variable before stripping it.

### Full Hilbert identities for parameter saturation

For case179, `native_checks/hilbert_regularity.py` first checks every literal
public equation after exact rational scalar and parameter-power descent. All
actual weights are positive, and every input must be homogeneous for those
weights. One complete fresh QQ Groebner basis supplies the full weighted
Hilbert series H(A). For each parameter e of degree d, the images of the whole
basis at e=0 generate the quotient ideal in the ring with that variable
removed. Its full new Groebner basis supplies H(A/e).

The graded multiplication sequence gives
`H(A/e) = (1-z^d)H(A) + z^d H(Ann_A(e))`.
Equality of the complete rational functions proves zero annihilator in every
degree, hence injectivity and full parameter saturation. The helper retains
the complete numerator and denominator of each series and also checks their
exact cross product. It accounts for the changed denominator when removing
the parameter. If all leading monomials of the shared full basis omit a
parameter, injectivity follows directly from standard monomials and the
quotient computation is unnecessary. All five parameters are covered in the
fixed order `u2,...,u31,u1,e2,e3,e4,e5,e1`; the subsequent junior-kernel proofs
and simultaneous containments remain separate required calculations.

### Exact target membership in unit parameters

For case179 juniors4 and5, `native_checks/residue_target_membership.py`
checks every generator of the complete simultaneous homogenization in
`Ihom+(t_k)`. After setting the unit parameter `t_k=0`, it descends the target
under `e_j=t_j^r_j` and computes fresh full rational bases of the source and
the quotient by `e_k`. Every remaining candidate monomial is assigned to its
exact residue class modulo the parameter orders. The decomposition is
reconstructed term by term, and every coefficient is reduced against the
complete quotient basis. This is the coefficientwise membership criterion
for a finite free polynomial extension; `(t_k)` is never replaced by
`(t_k^r_k)` in the unit-parameter ring. Source generators and whole candidates
must have rational coefficients after a single nonzero scalar normalization.
All classes and candidates are checked, even after a nonzero remainder.

### Case173 rational initial kernels and both character components

`special_initial173_j23.py` verifies the injective monomial compression,
invertible physical coordinate change, exact rational normalization, and
seventeen monic graph extensions for each of juniors2 and3. A complete
irreducible binary equation, an independent pair of mixed outputs and three
linear recoveries prove the localized eight-variable kernel. Full saturation
and the graph extensions give the full unsigned kernel; the literal physical
forms and their original weighted degrees are checked throughout.

`special_initial173_recovered_characters.py` retains all finite characters.
Thirteen checked character-homogeneous graphs leave twelve variables. Equal
nonzero physical forms with opposite characters are already coordinates for
junior2. For junior3 a checked triangular, graded, character-equivariant
automorphism makes them coordinates. Both compositions with its inverse are
checked exactly. `rational_tags.py` recovers the sign from their ratio, imposes
the order-two equation and computes the full contraction. The denominator is
nonzero in both target components. Both full ideal inclusions verify minimal
generation, and every exported relation is checked in the original physical
map and its full character grading. Each result has35 core equations and13
graphs; no partial list or assumed prime tagged kernel is used.

Case173's public ordinary images use four isolated workers in
`native_checks/parallel_kronecker.py`. Each calls the unchanged serial exact
`kronecker_images.py` over QQ[T]. The parent checks full input-index coverage,
worker exit codes, complete result protocols and unchanged source/input
hashes before emitting the ordinary completion markers in original order.
All literal requests and logs remain in the run's `public_kronecker_images`
directory. Errors and interruption clean up only owned process groups and
cannot produce a successful certificate.
