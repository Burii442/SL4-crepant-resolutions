"""Complete Case 173 first-initial kernel by localization and binary elimination.

Write P for the seven initial forms involving only x1,x2.  Their complete
kernel is computed by graph elimination.  Three physical identities solve
u14,u15,u6 after inverting h=u21*(11*u21^3-15*u1-28*u7).  The remaining u2,u4
are algebraically independent over Frac(QQ[P]): their coefficient matrix in
x3,x4 has nonzero determinant.  Consequently the localized presentation is
injective, and saturation by h is exactly the full polynomial kernel.

The bundled 35 relations are optional computational accelerators.  Each is
proved to vanish under the literal initial forms before it is added.  Since
the smaller presentation is already proved injective after localization,
adding these identities does not change its saturation.  Neither their
number nor their archived status is used to infer completeness.
"""
from pathlib import Path
import hashlib,json,time
from sage.all import QQ,PolynomialRing,TermOrder,matrix,gcd


def compute_initial_kernel(invariant_data, output_dir):
    started=time.time();out=Path(output_dir);out.mkdir(parents=True,exist_ok=True)
    assert int(invariant_data['case'])==173
    hintpath=Path(__file__).with_name('173_initial1_hints.json')
    hints=json.loads(hintpath.read_text());ids=list(map(int,hints['core_indices']))
    assert len(ids)==len(set(ids))==12
    Y=PolynomialRing(QQ,names=invariant_data['polynomial_coordinate_order'])
    assert Y.ngens()==4
    F={i:Y(invariant_data['junior_initial_generators'][0][i-1]) for i in ids}
    pure=[i for i in ids if all(not e[2] and not e[3] for e in F[i].exponents())]
    assert set(pure)=={21,1,7,3,9,5,16}
    assert set(ids)-set(pure)=={2,4,6,14,15}
    for i in set(ids)-set(pure):
        assert all(e[2]+e[3]==1 for e in F[i].exponents())
    ringids=list(reversed(ids))
    A=PolynomialRing(QQ,names=['u'+str(i) for i in ringids],
                     order=TermOrder('wdegrevlex',[F[i].total_degree() for i in ringids]))
    phi=A.hom([F[i] for i in ringids],Y)
    H=list(map(A,hints['relations']))
    assert len(H)==35 and all(phi(f)==0 for f in H)
    P=PolynomialRing(QQ,names=['x1','x2']+['u'+str(i) for i in pure],
                     order=TermOrder('wdegrevlex',[1,1]+[F[i].total_degree() for i in pure]))
    x=P.gens();graph=[x[j+2]-P(str(F[i])) for j,i in enumerate(pure)]
    purenames={'u'+str(i) for i in pure}
    purehints=[P(str(f)) for f in H if all(str(v) in purenames for v in f.variables())]
    # These hints are physically zero, so this is the full graph ideal.
    Ip=P.ideal(graph+purehints).elimination_ideal(list(x[:2]))
    pureGB=list(Ip.groebner_basis())
    assert all(not f.degree(x[0]) and not f.degree(x[1]) for f in pureGB)
    (out/'173_initial1_binary_kernel.json').write_text(json.dumps({
        'core_indices':pure,'relations':list(map(str,pureGB))},indent=2)+'\n')
    print('173_INITIAL1_COMPLETE_BINARY_KERNEL',len(pureGB),flush=True)
    lookup={str(v):v for v in A.gens()};u=lambda i:lookup['u'+str(i)]
    h=u(21)*(11*u(21)**3-15*u(1)-28*u(7));assert phi(h)!=0
    linear=[H[i] for i in [1,2,8]];cov=[u(14),u(15),u(6)]
    coefficients=matrix(A,[[f.derivative(v) for v in cov] for f in linear])
    assert all(all(str(v) in purenames for v in c.variables()) for c in coefficients.list())
    for f,row in zip(linear,coefficients.rows()):
        residual=f-sum(c*v for c,v in zip(row,cov))
        assert all(str(v) in purenames|{'u2','u4'} for v in residual.variables())
    determinant=coefficients.det();assert determinant
    remainder=determinant
    while not remainder.is_constant():
        divisor=gcd(remainder,h);assert not divisor.is_constant()
        remainder=remainder//divisor
    assert remainder
    # Thus the three variables are uniquely eliminated over the pure algebra[h^-1].
    physical_matrix=matrix(Y,[[F[i].derivative(Y.gen(j)) for j in [2,3]] for i in [2,4]])
    physical_det=physical_matrix.det();assert physical_det
    # The literal linear map on x3,x4 is invertible over QQ(x1,x2), so its
    # outputs u2,u4 are algebraically independent even over that larger field.
    J=A.ideal([A(str(f)) for f in pureGB]+linear+H)
    complete=J.saturation(A.ideal(h))[0]
    kernel=list(complete.groebner_basis())
    assert all(phi(f)==0 for f in kernel)
    assert complete.dimension()==4
    # Optional but useful: the full kernel is already character homogeneous.
    orders=list(map(int,invariant_data['finite_degree_orders']))
    chars=invariant_data['finite_degree_matrix']
    homogeneous=True
    for f in kernel:
        degrees={tuple(sum(int(e[j])*int(chars[k][ringids[j]-1]) for j in range(len(ringids)))%orders[k]
                       for k in range(len(orders))) for e in f.exponents()}
        homogeneous=homogeneous and len(degrees)<=1
    certificate={
        'status':'PASS','complete_initial_kernel':True,'junior':1,
        'pure_core_indices':pure,'complete_binary_kernel_generators':len(pureGB),
        'physically_verified_accelerators':len(H),'linear_relations':list(map(str,linear)),
        'localizer':str(h),'nonzero_localizer_image':str(phi(h)),
        'linear_matrix_determinant':str(determinant),
        'linear_matrix_invertible_after_localization':True,
        'nonzero_physical_covariant_determinant':str(physical_det),
        'complete_localized_injectivity_then_saturation':True,
        'complete_kernel_generators':len(kernel),'dimension':4,
        'finite_character_homogeneous':bool(homogeneous),
        'hint_sha256':hashlib.sha256(hintpath.read_bytes()).hexdigest(),
        'seconds':time.time()-started}
    result={'core_indices':ringids,'relations':list(map(str,kernel)),'certificate':certificate}
    (out/'173_initial1_complete_kernel.json').write_text(json.dumps(result,indent=2)+'\n')
    print('173_INITIAL1_COMPLETE_KERNEL_PASS',len(kernel),'seconds',certificate['seconds'],flush=True)
    return result


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',type=Path,required=True)
    args=parser.parse_args()
    data=json.loads((Path(__file__).resolve().parents[1]/'173/invariants.json').read_text())
    compute_initial_kernel(data,args.output_dir)
