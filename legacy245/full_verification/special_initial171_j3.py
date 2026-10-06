"""Complete Case 171 third-initial kernel by three exact recovery blocks.

A fresh graph elimination gives the binary kernel. Two independent linear
covariants provide the remaining transcendental variables. Three matrices
of sizes 8,9,4 recover all other generators after inverting
h=u1*u8*u20. Their determinants and every physical identity are recomputed.
Exact variable saturations are completed by weighted Bayer steps.
"""
from pathlib import Path
import hashlib,json,time
from sage.all import QQ,ZZ,PolynomialRing,TermOrder,matrix,gcd
from exact_algebra import saturation_basis,groebner_basis


def compute_initial_kernel(invariant_data, output_dir):
    started=time.time();out=Path(output_dir);out.mkdir(parents=True,exist_ok=True)
    assert int(invariant_data['case'])==171
    hp=Path(__file__).with_name('171_initial3_localization_hints.json');w=json.loads(hp.read_text())
    ids=list(reversed(w['core_indices']));assert len(ids)==len(set(ids))==30
    X=PolynomialRing(QQ,names=invariant_data['polynomial_coordinate_order']);assert X.ngens()==4
    F={i:X(invariant_data['junior_initial_generators'][2][i-1]) for i in ids}
    degrees={i:F[i].total_degree() for i in ids};assert all(d>0 for d in degrees.values())
    pure=[i for i in ids if all(e[2]+e[3]==0 for e in F[i].exponents())]
    assert set(pure)==set(w['pure_indices']) and len(pure)==7
    Jp=matrix(X,[[F[i].derivative(X.gen(j)) for j in [0,1]] for i in pure])
    assert any(Jp.matrix_from_rows([i,j]).det()!=0 for i in range(len(pure)) for j in range(i+1,len(pure)))
    U=PolynomialRing(QQ,names=['u'+str(i) for i in ids],order=TermOrder('wdegrevlex',[degrees[i] for i in ids]))
    phi=U.hom([F[i] for i in ids],X);u={i:U('u'+str(i)) for i in ids}
    H=list(map(U,w['binary_kernel_hints']));assert all(phi(f)==0 for f in H)
    pure_names={'u'+str(i) for i in pure}
    assert all(all(str(v) in pure_names for v in f.variables()) for f in H)
    P=PolynomialRing(QQ,names=['x1','x2']+['u'+str(i) for i in pure],order=TermOrder('wdegrevlex',[1,1]+[degrees[i] for i in pure]))
    x=P.gens();graph=[x[2+j]-P(str(F[i])) for j,i in enumerate(pure)]
    binary=P.ideal(graph+[P(str(f)) for f in H]).elimination_ideal(list(x[:2]));PG=list(binary.groebner_basis())
    assert all(f.degree(x[0])==f.degree(x[1])==0 for f in PG)
    (out/'171_initial3_binary_kernel.json').write_text(json.dumps({'pure_indices':pure,'relations':list(map(str,PG))},indent=2)+'\n')
    print('171_INITIAL3_COMPLETE_BINARY_KERNEL',len(PG),flush=True)
    selected=list(w['selected_linear_indices']);assert selected==[6,7]
    assert all(all(e[2]+e[3]==1 for e in F[i].exponents()) for i in selected)
    physical_det=matrix(X,[[F[i].derivative(X.gen(j)) for j in [2,3]] for i in selected]).det();assert physical_det
    h=u[1]*u[8]*u[20]
    assert h==U(w['localizer']) and phi(h)!=0
    known=set(pure)|set(selected);relations=[];block_reports=[]
    for block in w['blocks']:
        targets=list(block['targets']);fs=list(map(U,block['relations']))
        assert len(fs)==len(targets) and set(targets)<=set(ids)-known
        C=matrix(U,[[f.derivative(u[j]) for j in targets] for f in fs])
        assert all(all(str(v) in pure_names for v in c.variables()) for c in C.list())
        for f,row in zip(fs,C.rows()):
            residual=f-sum(c*u[j] for c,j in zip(row,targets))
            assert all(int(str(v)[1:]) in known for v in residual.variables())
            assert phi(f)==0
        det=C.det();assert det==U(block['determinant']) and phi(det)!=0
        remainder=det
        while not remainder.is_constant():
            divisor=gcd(remainder,h);assert not divisor.is_constant()
            remainder=remainder//divisor
        assert remainder
        known|=set(targets);relations+=fs
        block_reports.append({'targets':targets,'determinant':str(det),'invertible_after_localization':True})
    assert known==set(ids) and len(relations)==21
    A=U;names=list(U.variable_names());weights={str(u[i]):int(degrees[i]) for i in ids}
    # The localized-injectivity proof already identifies the saturation
    # with the physical kernel T. Physically zero extra relations are in T,
    # so adding them before saturation preserves I:S^infinity exactly.
    extra=list(map(U,w['extra_kernel_hints']));assert all(phi(f)==0 for f in extra)
    initial=extra+[A(str(f)) for f in PG]+relations
    for f in initial:assert len({sum(int(e[j])*weights[name] for j,name in enumerate(names)) for e in f.exponents()})==1
    ideal=A.ideal(initial);parameters=['u1','u8','u20'];stages=[]
    # Let I be the original ideal, S the product of all parameters and
    # T=I:S^infinity. After k stages the invariant is
    # I:(t_1*...*t_k)^infinity <= I_k <= T. The partial satstd ideal J
    # lies between I_{k-1} and T; weighted Bayer gives I_k=J:t_k^infinity.
    # Monotonicity proves the lower bound, and T being t_k-saturated the
    # upper bound. At the last stage both bounds equal T. No saturation
    # of intermediate I_k with respect to earlier parameters is assumed.
    for chosen in parameters:
        order=[name for name in names if name!=chosen]+[chosen]
        B=PolynomialRing(QQ,names=order,order=TermOrder('wdegrevlex',[weights[name] for name in order]))
        input_polys=[B(str(f)) for f in ideal.gens()]
        print('171_INITIAL3_SATURATION_START',chosen,len(input_polys),flush=True)
        basis=list(saturation_basis(B.ideal(input_polys),[B(name) for name in parameters]));basis=[f for f in basis if f]
        (out/f'171_initial3_standard_basis_{chosen}.json').write_text(json.dumps({'variables':order,'relations':list(map(str,basis))},indent=2)+'\n')
        saturated=[]
        for f in basis:
            assert len({sum(int(e[j])*weights[name] for j,name in enumerate(order)) for e in f.exponents()})==1
            minimum=min(e[len(order)-1] for e in f.exponents())
            assert f.leading_monomial().exponents()[0][len(order)-1]==minimum
            saturated.append(A(str(f//B.gens()[len(order)-1]**minimum)))
        ideal=A.ideal(saturated);stages.append({'last_variable':chosen,'standard_basis_generators':len(basis),'weighted_Bayer_strip':True})
        print('171_INITIAL3_SATURATION_COMPLETE',chosen,len(basis),flush=True)
    kernel=list(ideal.gens())
    assert kernel and all(phi(f)==0 for f in kernel)
    tags=matrix(ZZ,invariant_data['finite_degree_matrix']);orders=invariant_data['finite_degree_orders'];homogeneous=True
    for f in kernel:
        chars={tuple(sum(int(e[j])*int(tags[k,ids[j]-1]) for j in range(len(ids)))%int(orders[k]) for k in range(len(orders))) for e in f.exponents()}
        homogeneous=homogeneous and len(chars)<=1
    certificate={'status':'PASS','complete_initial_kernel':True,'junior':3,
        'pure_core_indices':pure,'binary_dimension_two_checked':True,
        'complete_binary_kernel_generators':len(PG),'physically_verified_binary_hints':len(H),'physically_verified_extra_hints':len(extra),
        'independent_linear_outputs':selected,'nonzero_physical_determinant':str(physical_det),
        'recovery_blocks':block_reports,'localizer':str(h),'nonzero_localizer_image':str(phi(h)),
        'complete_localized_injectivity_then_saturation':True,'saturation_steps':stages,
        'complete_kernel_generators':len(kernel),'dimension_from_injectivity':4,
        'finite_character_homogeneous':bool(homogeneous),
        'hint_sha256':hashlib.sha256(hp.read_bytes()).hexdigest(),'seconds':time.time()-started}
    result={'core_indices':ids,'relations':list(map(str,kernel)),'certificate':certificate}
    (out/'171_initial3_complete_kernel.json').write_text(json.dumps(result,indent=2)+'\n')
    print('171_INITIAL3_COMPLETE_KERNEL_PASS',len(kernel),'seconds',certificate['seconds'],flush=True)
    return result


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output-dir',type=Path,required=True)
    args=parser.parse_args();data=json.loads((Path(__file__).resolve().parents[1]/'171/invariants.json').read_text())
    compute_initial_kernel(data,args.output_dir)
