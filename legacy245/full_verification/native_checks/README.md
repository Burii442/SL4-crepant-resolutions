# Public-presentation saturation certificate

`public_saturation.py` supplies a reusable exact alternative to constructing a
large multihomogenization from an ordinary relation ideal. It takes a complete
ordinary polynomial-map kernel proved by the calling validator. The coefficient
ring is an exact field of characteristic zero. The standalone triangular
quotient and native membership helpers check these prerequisites explicitly;
normalizing a leading coefficient over the integers would not preserve ideals.

Write `u_j` for the generator variables and `t_k` for the unit valuation
parameters, with multidegrees `deg(u_j)=-nu(F_j)` and `deg(t_k)=e_k`. The helper
checks the public equations after `e_k=t_k^r_k` are homogeneous in every such
degree, that setting all `t_k=1` gives precisely the complete ordinary kernel,
and that the public ideal is unchanged by saturation with respect to each
`t_k`. Ideal containments are checked by exact Groebner reduction; saturation
already provides one inclusion by definition. For case 233 only, containment
of the dehomogenized public equations in the complete ordinary kernel is
checked by exact substitution into its small polynomial-map coordinates.
This is the same membership test because the complete kernel of that map
has already been proved. All public equations are tested, including the
largest ones; the opposite inclusion is still checked by Groebner reduction.

For cases 171 and 177, `exact_images.py` performs the same complete first
containment test in the actual polynomial coordinates. It transports typed
coefficient dictionaries to a fresh rational polynomial ring and checks the
exact zero image of every public equation. The complete ordinary kernel is
still a prerequisite, and the reverse ideal containment is still checked.

For case 173, `kronecker_images.py` checks these exact physical images in
`QQ[T]`. It first verifies the homogeneous degree of each image. Setting the
last physical variable to one is injective on that homogeneous component;
base `d+1` encoding of the remaining exponents is then injective because each
exponent is at most `d`. All polynomial arithmetic is rational and exact;
this is not numerical evaluation or reduction modulo a prime.

`parallel_kronecker.py` can partition this same exact check between two to four
independent Sage Python processes. `kronecker_worker.py` reconstructs typed
rational polynomials from coefficient dictionaries and calls the unchanged
serial helper. Both layers enforce its exact-field and homogeneity assumptions.
The parent checks literal input and source SHA256 before and after calculation,
all worker exit codes, the complete serial marker sequence and each original
index exactly once. Only a complete run replays `EXACT_KRONECKER_IMAGE_ZERO`
in the original order; earlier progress uses separate `PARALLEL_KRONECKER_*`
events. A nonzero image, malformed result, timeout or interruption cannot pass.
Workers have separately registered process groups, which are cleaned up on
failure or interruption; cache removal requires confirmed group termination.
The worker CLI does not import the main verifier or use multiprocessing spawn.
All source copies, requests and worker logs are retained with the proof output.
The case-173 public-presentation check uses four workers by default. The main
verifier supplies `image_work_directory`; each call creates a new `run-*`
subdirectory so a resumed attempt preserves the earlier evidence unchanged.

For cases 178 and 179, `triangular_quotient.py` checks this first containment in
an isomorphic quotient with six variables. It selects 12 or 25 literal monic graph
definitions from the already proved complete ordinary kernel and recovers
the other variables in a verified triangular order. All core-only kernel
equations are imposed immediately to limit expression size. The images of
**every** complete kernel generator are then imposed as well, so completeness
of a selected small list of core equations is never assumed. Monic
elimination identifies this core quotient with the original 18- or 31-variable
quotient. A fresh Singular computation maps all 2051 or 2619 public dehomogenized
relations, respectively, into it and explicitly reduces each image in the quotient ring.
The wrapper requires the complete ordered sequence of zero checks; an
unreduced displayed representative or an incomplete run cannot pass. The
opposite ideal inclusion is still verified in the original variables.

After inverting the `t_k`, multihomogeneity identifies the ideal with the
ordinary kernel by the change of variables `u_j -> u_j product t_k^nu_k(F_j)`.
Separate saturation by every parameter says that the original ideal equals
the contraction of this localization. Thus these checks identify precisely
the full multihomogenization. They do not use a supplied large purported
Groebner basis or any historical result flag.

When both ordinary ideals have rational coefficients, their Groebner bases
and both membership directions are computed over the rationals with the same
monomial order. The rational ideal is extended to the stated coefficient
field by a faithfully flat extension, so the equalities are unchanged. The
public saturation containments use the same rational descent when possible;
nonrational membership tests retain the original coefficient field.

For case 174, `native_colons.py` proves the complete first ideal quotient
`I:e_k` equals `I` for each descended parameter. It first checks whether all
leading monomials of a fresh complete standard basis avoid that parameter.
If they do, multiplication by the parameter preserves nonzero normal forms,
which proves the colon equality directly. Otherwise it computes the complete
ideal quotient and verifies every resulting generator in that fresh basis. The equality `I:e_k=I`
implies `I:e_k^m=I` for every positive `m` by induction, and therefore proves
full saturation. This is a complete colon computation, not a test of a selected
subset of relations. Every coefficient and parameter exponent is checked
before rational and power descent. Since `e_k=t_k^r_k`, injectivity of `e_k`
after the flat extension also implies injectivity of `t_k`. The default
internal order places the invariant variables in reverse order and the first
valuation parameter last; an explicit complete variable permutation is also
supported. No earlier saturation or standard basis is used as an input.

For case 179, `hilbert_regularity.py` proves every parameter saturation over
QQ from one shared fresh complete Groebner basis. It checks rational scalar
descent, exact parameter-power divisibility, positive weights and homogeneity
of every descended input polynomial. For a parameter of degree d, the full
multiplication sequence gives
`H(A/e) = (1-z^d) H(A) + z^d H(Ann_A(e))`. Equality of the full rational
functions therefore proves injectivity, and hence full saturation. Every
graded piece is finite dimensional because all actual weights are positive.

The quotient ideal is generated by the images of the entire fresh basis after
setting the selected parameter to zero. The helper removes that variable,
computes a complete quotient basis, and obtains its full weighted Hilbert
series. Both complete numerators and denominators are retained; the comparison
uses rational functions and a separate exact polynomial cross product, so
removing a variable from the denominator is fully accounted for. All
parameters are checked. The only shortcut proves injectivity directly when
every leading monomial of the full shared basis omits that parameter. The
fixed order is `u2,...,u31,u1,e2,e3,e4,e5,e1`. No historical basis or truncated
Hilbert series is consumed. A failed equality records actual parameter torsion;
it cannot be reported as a completed positive saturation proof.

`native_bayer.py` also remains available as a standalone exact saturation
method. It computes a complete positive weighted reverse-lexicographic basis
with the selected parameter last, checks the minimum parameter exponent
against every term, and reduces every basis polynomial divided by that power.
The resulting complete saturation equality has the same mathematical scope.

For the simultaneous tests in case 174, `native_colons.py` also supplies
`verify_initial_target_containment`. It freshly homogenizes every generator of
the complete tagged initial kernel and checks independence of the own parameter
`t_i`. After setting `t_i=0` in the full ordinary homogeneous ideal, it checks
all raw homogeneous generators in the target and proves the target saturated
at every remaining parameter by complete first-colon equalities. The entire
saturation of the raw ideal therefore remains in the target. Both the raw
ideal and this saturation extend from the ring without `t_i`, so saturation
at the own parameter adds nothing. This is a proof of the full simultaneous
containment, without constructing a larger full homogeneous initial basis.

`native_membership.py` remains a standalone exact containment utility. Earlier
isolated 174 proofs used it to compare full saturations with the literal public
ideal; their source snapshots record that earlier valid method.

The public-presentation fullness certificate concerns the ordinary homogenized
kernel only. Every junior initial kernel still needs its own complete proof,
and its full simultaneous containment must be proved either by constructing
the full multihomogenization or by the target-regularity argument above. Generation of the
ordinary invariant algebra also requires its independent Molien/Hilbert
comparison or another complete generation argument.
