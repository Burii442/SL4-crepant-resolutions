"""Full Case177 junior2 kernel from a binary algebra and a rank-three quadric.

The exact binary graph gives B. Three quadratic covariants have a relation
q of rank three over Frac(B), monic in u9 after inverting u10. Consequently
B_h[u3,u6,u9]/q is torsion-free over B_h and generically geometrically
integral, hence a domain. A physical Jacobian of rank four proves its
injectivity. Two recovery blocks and one monic extension give every other
literal form. Exact weighted variable saturation contracts the full kernel.
"""
from pathlib import Path
import hashlib,json,time
from sage.all import QQ,ZZ,PolynomialRing,TermOrder,matrix,gcd
from exact_algebra import saturation_basis


def compute_initial_kernel(invariant_data,output_dir):
    started=time.time();out=Path(output_dir);out.mkdir(parents=True,exist_ok=True)
    assert int(invariant_data['case'])==177
    hp=Path(__file__).with_name('177_initial2_localization_hints.json');w=json.loads(hp.read_text())
    all_ids=list(reversed(range(1,28)));ids=list(reversed(w['core_indices']))
    assert len(ids)==len(set(ids))==26 and set(all_ids)-set(ids)=={25}
    X=PolynomialRing(QQ,names=invariant_data['polynomial_coordinate_order']);assert X.ngens()==4
    assert X.variable_names()==('x1','x2','x3','x4')
    F={i:X(invariant_data['junior_initial_generators'][1][i-1]) for i in all_ids}
    degrees={i:int(F[i].total_degree()) for i in all_ids}
    assert all(degrees[i]>0 and {sum(e) for e in F[i].exponents()}=={degrees[i]} for i in all_ids)
    assert [degrees[i] for i in range(1,28)]==list(invariant_data['polynomial_degrees'])
    pure=[i for i in ids if all(e[2]+e[3]==0 for e in F[i].exponents())]
    assert set(pure)==set(w['pure_indices']) and len(pure)==7
    pure_names={'u'+str(i) for i in pure}
    U=PolynomialRing(QQ,names=['u'+str(i) for i in ids],order=TermOrder('wdegrevlex',[degrees[i] for i in ids]))
    u={i:U('u'+str(i)) for i in ids};phi=U.hom([F[i] for i in ids],X)
    Jp=matrix(X,[[F[i].derivative(X.gen(j)) for j in [0,1]] for i in pure])
    assert any(Jp.matrix_from_rows([i,j]).det()!=0 for i in range(len(pure)) for j in range(i+1,len(pure)))
    H=list(map(U,w['binary_kernel_hints']))
    assert all(phi(f)==0 and all(str(v) in pure_names for v in f.variables()) for f in H)
    P=PolynomialRing(QQ,names=['x1','x2']+['u'+str(i) for i in pure],order=TermOrder('wdegrevlex',[1,1]+[degrees[i] for i in pure]))
    x=P.gens();graph=[x[2+j]-P(str(F[i])) for j,i in enumerate(pure)]
    binary=P.ideal(graph+[P(str(f)) for f in H]).elimination_ideal(list(x[:2]));PG=list(binary.groebner_basis())
    assert all(f.degree(x[0])==f.degree(x[1])==0 for f in PG)
    print('177_INITIAL2_COMPLETE_BINARY_KERNEL',len(PG),flush=True)
    selected=list(w['selected_quadratic_indices']);assert selected==[3,6,9]
    assert all(all(e[2]+e[3]==2 for e in F[i].exponents()) for i in selected)
    physical_C=matrix(X,[[F[i].derivative(X.gen(2)).derivative(X.gen(2))/2,F[i].derivative(X.gen(2)).derivative(X.gen(3)),F[i].derivative(X.gen(3)).derivative(X.gen(3))/2] for i in selected])
    assert physical_C.det()!=0
    q=U(w['core_quadric'])*(QQ(9)/4096);assert phi(q)==0
    Q=matrix(U,[[q.derivative(u[i]).derivative(u[j])/2 for j in selected] for i in selected])
    assert q==sum(Q[i,j]*u[selected[i]]*u[selected[j]] for i in range(3) for j in range(3))
    assert all(all(str(v) in pure_names for v in c.variables()) for c in Q.list())
    assert phi(Q.det())!=0
    assert q.degree(u[9])==2 and q.derivative(u[9]).derivative(u[9])/2==u[10]
    core_jacobian=matrix(QQ,[[F[i].derivative(var)(1,2,3,5) for var in X.gens()] for i in pure+selected])
    assert core_jacobian.rank()==4
    assert {2,10,27}<=set(pure)
    h=u[2]*u[10]*u[27];assert h==U(w['localizer']) and phi(h)!=0
    known=set(pure)|set(selected);relations=[];block_reports=[]
    for block in w['blocks']:
        targets=list(block['targets']);fs=list(map(U,block['relations']))
        assert len(fs)==len(targets) and set(targets)<=set(ids)-known
        C=matrix(U,[[f.derivative(u[j]) for j in targets] for f in fs])
        assert all(all(str(v) in pure_names for v in c.variables()) for c in C.list())
        for f,row in zip(fs,C.rows()):
            residual=f-sum(c*u[j] for c,j in zip(row,targets))
            assert all(int(str(v)[1:]) in known for v in residual.variables()) and phi(f)==0
        determinant=C.det();assert determinant==U(block['determinant']) and phi(determinant)!=0
        remainder=determinant
        while not remainder.is_constant():
            divisor=gcd(remainder,h);assert not divisor.is_constant();remainder=remainder//divisor
        assert remainder
        known|=set(targets);relations+=fs
        block_reports.append({'targets':targets,'determinant':str(determinant),'invertible_after_localization':True})
    assert known==set(ids) and len(relations)==16
    initial=list(map(lambda f:U(str(f)),PG))+[q]+relations
    names=list(U.variable_names());weights={str(u[i]):degrees[i] for i in ids}
    for f in initial:assert len({sum(int(e[j])*weights[name] for j,name in enumerate(names)) for e in f.exponents()})==1
    ideal=U.ideal(initial);parameters=['u27','u10','u2'];stages=[]
    # For T=I:S^infinity and P_k the first k parameters, maintain
    # I:P_k^infinity <= I_k <= T. Partial satstd gives I_{k-1}<=J<=T;
    # Bayer gives I_k=J:t_k^infinity. Monotonicity and saturation of T
    # prove the bounds, which coincide at the last stage.
    for chosen in parameters:
        order=[name for name in names if name!=chosen]+[chosen]
        B=PolynomialRing(QQ,names=order,order=TermOrder('wdegrevlex',[weights[name] for name in order]))
        input_polys=[B(str(f)) for f in ideal.gens()]
        print('177_INITIAL2_SATURATION_START',chosen,len(input_polys),flush=True)
        basis=[f for f in saturation_basis(B.ideal(input_polys),[B(name) for name in parameters]) if f]
        (out/f'177_initial2_standard_basis_{chosen}.json').write_text(json.dumps({'variables':order,'relations':list(map(str,basis))},indent=2)+'\n')
        saturated=[]
        for f in basis:
            assert len({sum(int(e[j])*weights[name] for j,name in enumerate(order)) for e in f.exponents()})==1
            minimum=min(e[len(order)-1] for e in f.exponents())
            assert f.leading_monomial().exponents()[0][len(order)-1]==minimum
            saturated.append(U(str(f//B.gens()[len(order)-1]**minimum)))
        ideal=U.ideal(saturated);stages.append({'last_variable':chosen,'standard_basis_generators':len(basis),'weighted_Bayer_strip':True})
        print('177_INITIAL2_SATURATION_COMPLETE',chosen,len(basis),flush=True)
    A=PolynomialRing(QQ,names=['u'+str(i) for i in all_ids],order=TermOrder('wdegrevlex',[degrees[i] for i in all_ids]))
    full_phi=A.hom([F[i] for i in all_ids],X);extensions=list(map(A,w['extensions']))
    assert len(extensions)==1
    extension=extensions[0];v=A('u25');assert extension.degree(v)==1 and extension.derivative(v)==1
    assert all(str(z)!='u25' for z in (extension-v).variables()) and full_phi(extension)==0
    kernel=[A(str(f)) for f in ideal.gens()]+extensions
    assert kernel and all(full_phi(f)==0 for f in kernel)
    tags=matrix(ZZ,invariant_data['finite_degree_matrix']);orders=invariant_data['finite_degree_orders'];homogeneous=True
    for f in kernel:
        chars={tuple(sum(int(e[j])*int(tags[k,all_ids[j]-1]) for j in range(len(all_ids)))%int(orders[k]) for k in range(len(orders))) for e in f.exponents()}
        homogeneous=homogeneous and len(chars)<=1
    certificate={'status':'PASS','complete_initial_kernel':True,'junior':2,'full_generator_set':True,
        'pure_core_indices':pure,'binary_dimension_two_checked':True,'complete_binary_kernel_generators':len(PG),
        'physically_verified_binary_hints':len(H),'selected_quadratic_indices':selected,
        'core_quadric':str(q),'quadric_rank_over_binary_fraction_field':3,'monic_after_localizing_u10':True,
        'physical_core_jacobian_rank':4,'physical_jacobian_point':[1,2,3,5],
        'nonzero_quadratic_coefficient_determinant':str(physical_C.det()),'recovery_blocks':block_reports,
        'physically_checked_monic_extensions':1,'localizer':str(h),'nonzero_localizer_image':str(phi(h)),
        'complete_localized_injectivity_then_saturation':True,'saturation_steps':stages,
        'complete_kernel_generators':len(kernel),'dimension_from_injectivity':4,'finite_character_homogeneous':bool(homogeneous),
        'hint_sha256':hashlib.sha256(hp.read_bytes()).hexdigest(),'seconds':time.time()-started}
    result={'core_indices':all_ids,'relations':list(map(str,kernel)),'full_generator_set':True,'certificate':certificate}
    (out/'177_initial2_complete_kernel.json').write_text(json.dumps(result,indent=2)+'\n')
    print('177_INITIAL2_COMPLETE_KERNEL_PASS',len(kernel),'seconds',certificate['seconds'],flush=True)
    return result

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output-dir',type=Path,required=True)
    args=parser.parse_args();data=json.loads((Path(__file__).resolve().parents[1]/'177/invariants.json').read_text())
    compute_initial_kernel(data,args.output_dir)
