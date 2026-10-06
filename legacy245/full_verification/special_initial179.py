"""Complete first initial kernel of Case 179 from a prime quadratic core.

Five literal forms u1,u2,u5,u6,u8 satisfy a primitive ternary quadratic
in u5,u6,u8 over QQ[u1,u2]. Its rank is three, hence it is geometrically
irreducible over QQ(u1,u2). A nonzero four-by-four physical Jacobian proves
that this is their FULL kernel. The remaining twenty-six forms are
symmetric separately in (x1^2,x2^2) and (x3^2,x4^2). Elementary symmetric
recurrences give exact rational recoveries from the five forms, with all
denominators supported on h=u1*u2*(u1^3+4*u2). Every identity is verified
against the literal four-variable input. Localization is therefore
injective; complete saturation contracts the full kernel. The generators
of the contracted kernel are all physically checked and C2-homogeneous,
so this is also the full finite-tagged kernel, after any field extension.
"""
from pathlib import Path
import json,time
from sage.all import QQ,PolynomialRing,TermOrder,matrix,gcd


def symmetric_power(n,s,p):
    """s=x+y, p=xy: return x^n+y^n for n>0, and 1 for n=0."""
    if n==0:return s.parent()(1)
    if n==1:return s
    previous,current=s.parent()(2),s
    for _ in range(2,n+1):previous,current=current,s*current-p*previous
    return current


def symmetric_rewrite(f,Z,physical):
    """Rewrite a separately symmetric polynomial without interpolation."""
    a,b,z,v=Z.gens();terms={tuple(e):c for e,c in f.dict().items()}
    result=Z(0)
    for e,coefficient in terms.items():
        assert all(q%2==0 for q in e)
        i,j,k,l=[q//2 for q in e]
        assert terms.get((2*j,2*i,2*k,2*l),0)==coefficient
        assert terms.get((2*i,2*j,2*l,2*k),0)==coefficient
        if i<j or k<l:continue
        result+=coefficient*b**j*symmetric_power(i-j,a,b)*v**l*symmetric_power(k-l,z,v)
    assert physical(result)==f
    return result


def compute_initial_kernel(invariant_data,output_dir):
    started=time.monotonic();out=Path(output_dir);out.mkdir(parents=True,exist_ok=True)
    assert int(invariant_data['case'])==179
    assert invariant_data['polynomial_coordinate_order']==['x1','x2','x3','x4']
    D=list(map(int,invariant_data['polynomial_degrees']))
    X=PolynomialRing(QQ,['x1','x2','x3','x4']);x=X.gens()
    F=[X(raw) for raw in invariant_data['junior_initial_generators'][0]]
    assert len(F)==len(D)==31
    assert all(f and {sum(e) for e in f.exponents()}=={degree} for f,degree in zip(F,D))
    assert list(map(int,invariant_data['finite_degree_orders']))==[2]
    assert [list(map(int,row)) for row in invariant_data['finite_degree_matrix']]==[[int(j in [5,6]) for j in range(1,32)]]
    Z=PolynomialRing(QQ,['a','b','z','v'])
    a0=x[0]**2+x[1]**2;b0=x[0]**2*x[1]**2;e0=(x[0]**2-x[1]**2)**2
    z0=x[2]**2+x[3]**2;v0=x[2]**2*x[3]**2
    physical=Z.hom([a0,b0,z0,v0],X)
    core=[1,2,5,6,8]
    assert [F[j-1] for j in core]==[2*a0,-2*a0*e0,
        256*b0**2*(x[0]**2-x[1]**2)*(x[2]**2-x[3]**2),
        16*x[0]*x[1]*e0**2*x[2]*x[3],3072*a0*b0*e0*z0]
    C=PolynomialRing(QQ,[f'u{j}' for j in core],order=TermOrder('wdegrevlex',[D[j-1] for j in core]))
    u1,u2,u5,u6,u8=C.gens();T=C.fraction_field()
    a=T(u1)/2;b=(u1**3+4*u2)/(16*T(u1));e=-T(u2)/u1
    z=-u1*u8/(96*T(u2)*(u1**3+4*u2));v=T(u6**2)/(256*b*e**4)
    substitution=Z.hom([a,b,z,v],T)
    quadratic=(u5**2-65536*b**4*e*(z**2-4*v)).numerator()
    quadratic=quadratic/quadratic.leading_coefficient()
    physical_core=C.hom([F[j-1] for j in core],X)
    assert physical_core(quadratic)==0
    qvars=[u5,u6,u8]
    qmatrix=matrix(C,[[quadratic.derivative(i).derivative(j)/2 for j in qvars] for i in qvars])
    assert quadratic==sum(qmatrix[i,j]*qvars[i]*qvars[j] for i in range(3) for j in range(3))
    assert all(all(str(v) in {'u1','u2'} for v in coefficient.variables()) for coefficient in qmatrix.list())
    assert qmatrix.det()!=0 and gcd(qmatrix.list())==1
    jacobian=matrix(QQ,[[F[j-1].derivative(var)(1,2,3,5) for var in x] for j in [1,2,5,6]])
    assert jacobian.det()!=0
    print('179_INITIAL1_FULL_PRIME_QUADRATIC_CORE',flush=True)
    ids=list(reversed(range(1,32)))
    A=PolynomialRing(QQ,[f'u{j}' for j in ids],order=TermOrder('wdegrevlex',[D[j-1] for j in ids]))
    u={j:A.gen(ids.index(j)) for j in ids};lift=C.hom([u[j] for j in core],A)
    h=u[1]*u[2]*(u[1]**3+4*u[2]);phi=A.hom([F[j-1] for j in ids],X)
    assert phi(h)!=0
    relations=[lift(quadratic)];recoveries=[]
    for j in range(1,32):
        if j in core:continue
        rewritten=symmetric_rewrite(F[j-1],Z,physical)
        expression=substitution(rewritten)
        denominator=lift(expression.denominator());numerator=lift(expression.numerator())
        assert denominator and all(str(v) in {'u1','u2'} for v in denominator.variables())
        remainder=denominator
        while not remainder.is_constant():
            divisor=gcd(remainder,h)
            assert not divisor.is_constant()
            remainder=remainder//divisor
        assert remainder
        relation=denominator*u[j]-numerator
        assert phi(relation)==0
        relations.append(relation)
        recoveries.append({'index':j,'denominator':str(denominator),'numerator':str(numerator)})
    assert len(recoveries)==26
    for f in relations:
        assert len({sum(e[k]*D[j-1] for k,j in enumerate(ids)) for e in f.exponents()})==1
        assert len({(e[ids.index(5)]+e[ids.index(6)])%2 for e in f.exponents()})==1
    (out/'179_initial1_localized_witness.json').write_text(json.dumps({
        'core_indices':core,'quadric':str(quadratic),'localizer':str(h),
        'recoveries':recoveries,'relations':list(map(str,relations))},indent=2)+'\n')
    # This is complete saturation, not a bounded search or a saved basis.
    complete=A.ideal(relations).saturation(A.ideal(h))[0]
    kernel=list(complete.groebner_basis());assert kernel and complete.dimension()==4
    for f in kernel:
        assert phi(f)==0
        assert len({(e[ids.index(5)]+e[ids.index(6)])%2 for e in f.exponents()})<=1
    certificate={'status':'PASS','junior':1,'complete_initial_kernel':True,
        'complete_tagged_initial_kernel':True,'characteristic_zero':True,
        'full_generator_set':True,'finite_character_homogeneous':True,
        'prime_core_indices':core,'prime_core_quadric':str(quadratic),
        'primitive_ternary_quadric_rank':3,'physical_jacobian_witness':[1,2,3,5],
        'physical_jacobian_determinant':str(jacobian.det()),
        'all_symmetric_rewrites_physically_verified':True,
        'physically_verified_rational_recoveries':len(recoveries),
        'all_denominators_invertible_after_localizing':str(h),
        'complete_localized_injectivity_then_saturation':True,
        'every_exported_relation_physically_verified':True,
        'complete_kernel_generators':len(kernel),'dimension':4,
        'seconds':time.monotonic()-started}
    result={'core_indices':ids,'relations':list(map(str,kernel)),
            'full_generator_set':True,'certificate':certificate}
    (out/'179_initial1_complete_kernel.json').write_text(json.dumps(result,indent=2)+'\n')
    print('179_INITIAL1_COMPLETE_TAGGED_KERNEL_PASS',len(kernel),'seconds',certificate['seconds'],flush=True)
    return result


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',type=Path,required=True)
    args=parser.parse_args()
    data=json.loads((Path(__file__).resolve().parents[1]/'179/invariants.json').read_text())
    compute_initial_kernel(data,args.output_dir)
