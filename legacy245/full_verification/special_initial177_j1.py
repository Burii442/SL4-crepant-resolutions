"""Complete Case 177 first-initial kernel by one exact recovery block.

A fresh graph elimination gives the binary kernel. Two independent linear
covariants provide the remaining transcendental variables. A six-by-six
matrix recovers all other core generators after inverting h=u3*u27. Its
determinant and every physical identity are recomputed.
Exact variable saturations are completed by weighted Bayer steps.
The remaining C2 character is recovered from equal forms after a graded
polynomial coordinate change; exact contraction gives the full finite-tagged
kernel of all27 literal forms.
"""
from pathlib import Path
import hashlib,json,time
from sage.all import QQ,ZZ,PolynomialRing,TermOrder,matrix,gcd
from exact_algebra import saturation_basis
from rational_tags import recovered_tag_kernel


def compute_initial_kernel(invariant_data, output_dir):
    started=time.time();out=Path(output_dir);out.mkdir(parents=True,exist_ok=True)
    assert int(invariant_data['case'])==177
    hp=Path(__file__).with_name('177_initial1_localization_hints.json');w=json.loads(hp.read_text())
    ids=list(reversed(w['core_indices']));assert len(ids)==len(set(ids))==14
    X=PolynomialRing(QQ,names=invariant_data['polynomial_coordinate_order']);assert X.ngens()==4
    F={i:X(invariant_data['junior_initial_generators'][0][i-1]) for i in ids}
    degrees={i:F[i].total_degree() for i in ids};assert all(d>0 for d in degrees.values())
    pure=[i for i in ids if all(e[2]+e[3]==0 for e in F[i].exponents())]
    assert set(pure)==set(w['pure_indices']) and len(pure)==6
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
    (out/'177_initial1_binary_kernel.json').write_text(json.dumps({'pure_indices':pure,'relations':list(map(str,PG))},indent=2)+'\n')
    print('177_INITIAL1_COMPLETE_BINARY_KERNEL',len(PG),flush=True)
    selected=list(w['selected_linear_indices']);assert selected==[2,17]
    assert all(all(e[2]+e[3]==1 for e in F[i].exponents()) for i in selected)
    physical_det=matrix(X,[[F[i].derivative(X.gen(j)) for j in [2,3]] for i in selected]).det();assert physical_det
    assert {3,27}<=set(pure)
    h=u[3]*u[27]
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
    assert known==set(ids) and len(relations)==6
    A=U;names=list(U.variable_names());weights={str(u[i]):int(degrees[i]) for i in ids}
    # The localized-injectivity proof already identifies the saturation
    # with the physical kernel T. Physically zero extra relations are in T,
    # so adding them before saturation preserves I:S^infinity exactly.
    extra=list(map(U,w['extra_kernel_hints']));assert all(phi(f)==0 for f in extra)
    initial=extra+[A(str(f)) for f in PG]+relations
    for f in initial:assert len({sum(int(e[j])*weights[name] for j,name in enumerate(names)) for e in f.exponents()})==1
    ideal=A.ideal(initial);parameters=['u27','u3'];stages=[]
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
        print('177_INITIAL1_SATURATION_START',chosen,len(input_polys),flush=True)
        basis=list(saturation_basis(B.ideal(input_polys),[B(name) for name in parameters]));basis=[f for f in basis if f]
        (out/f'177_initial1_standard_basis_{chosen}.json').write_text(json.dumps({'variables':order,'relations':list(map(str,basis))},indent=2)+'\n')
        saturated=[]
        for f in basis:
            assert len({sum(int(e[j])*weights[name] for j,name in enumerate(order)) for e in f.exponents()})==1
            minimum=min(e[len(order)-1] for e in f.exponents())
            assert f.leading_monomial().exponents()[0][len(order)-1]==minimum
            saturated.append(A(str(f//B.gens()[len(order)-1]**minimum)))
        ideal=A.ideal(saturated);stages.append({'last_variable':chosen,'standard_basis_generators':len(basis),'weighted_Bayer_strip':True})
        print('177_INITIAL1_SATURATION_COMPLETE',chosen,len(basis),flush=True)
    core_kernel=list(ideal.gens());assert all(phi(f)==0 for f in core_kernel)
    all_ids=list(reversed(range(1,28)))
    V=PolynomialRing(QQ,names=['u'+str(i) for i in all_ids],order=TermOrder('wdegrevlex',[int(invariant_data['polynomial_degrees'][i-1]) for i in all_ids]))
    all_forms=[X(invariant_data['junior_initial_generators'][0][i-1]) for i in all_ids]
    assert all({e[2]+e[3] for e in f.exponents()}=={int(invariant_data['valuation_matrix'][0][i-1])} for i,f in zip(all_ids,all_forms))
    full_phi=V.hom(all_forms,X);extensions=list(map(V,w['extensions']));known=set(ids)
    assert len(extensions)==13
    for f in reversed(extensions):
        missing=[v for v in f.variables() if int(str(v)[1:]) not in known]
        assert len(missing)==1;v=missing[0];coefficient=f.derivative(v)
        assert coefficient.is_constant() and coefficient and f.degree(v)==1 and full_phi(f)==0
        known.add(int(str(v)[1:]))
    assert known==set(all_ids)
    ordinary=V.ideal([V(str(f)) for f in core_kernel]+extensions)
    # The sum of the two finite characters is transverse degree modulo2.
    full_tags=matrix(ZZ,invariant_data['finite_degree_matrix'])
    assert invariant_data['finite_degree_orders']==[2,2]
    assert all((int(full_tags[0,i-1])+int(full_tags[1,i-1]))%2==int(invariant_data['valuation_matrix'][0][i-1])%2 for i in all_ids)
    # A graded polynomial coordinate change makes two physical forms equal:
    # v6=3*u6-3*u3*u27/2 and v10=u10-u9/4. The monic extension for u10
    # proves v6=v10 physically. Its character difference recovers the
    # remaining C2. The forward and inverse changes are verified exactly.
    pos6=all_ids.index(6);pos10=all_ids.index(10);z={i:V('u'+str(i)) for i in all_ids}
    forward=list(V.gens());inverse=list(V.gens())
    forward[pos6]=3*z[6]-QQ(3)/2*z[3]*z[27];forward[pos10]=z[10]-z[9]/4
    inverse[pos6]=z[6]/3+z[3]*z[27]/2;inverse[pos10]=z[10]+z[9]/4
    back=V.hom(forward,V);change=V.hom(inverse,V)
    assert all(back(change(v))==v and change(back(v))==v for v in V.gens())
    for j,f in enumerate(forward+inverse):
        source_j=j%len(all_ids)
        for k in range(2):
            assert {sum(int(e[l])*int(full_tags[k,all_ids[l]-1]) for l in range(len(all_ids)))%2 for e in f.exponents()}=={int(full_tags[k,all_ids[source_j]-1])}
    ordinary=V.ideal([change(f) for f in ordinary.gens()])
    scaled_forms=[full_phi(f) for f in forward]
    assert scaled_forms[pos6]==scaled_forms[pos10]!=0
    degree_list=[int(invariant_data['polynomial_degrees'][i-1]) for i in all_ids]
    assert all({sum(e) for e in f.exponents()}=={d} for f,d in zip(all_forms,degree_list))
    for f in ordinary.gens():
        assert len({sum(int(e[j])*degree_list[j] for j in range(len(all_ids))) for e in f.exponents()})==1
    def emit(event,**details):print('177_INITIAL1_'+event,json.dumps(details),flush=True)
    tagged=recovered_tag_kernel(ordinary,scaled_forms,V,[[int(full_tags[0,i-1]) for i in all_ids]],[2],[(pos6,pos10)],degree_list,emit)
    kernel=[back(f) for f in tagged.gens()]
    assert kernel and all(full_phi(f)==0 for f in kernel)
    ids=all_ids

    tags=matrix(ZZ,invariant_data['finite_degree_matrix']);orders=invariant_data['finite_degree_orders'];homogeneous=True
    for f in kernel:
        chars={tuple(sum(int(e[j])*int(tags[k,ids[j]-1]) for j in range(len(ids)))%int(orders[k]) for k in range(len(orders))) for e in f.exponents()}
        homogeneous=homogeneous and len(chars)<=1
    assert homogeneous
    certificate={'status':'PASS','complete_initial_kernel':True,'junior':1,
        'pure_core_indices':pure,'binary_dimension_two_checked':True,
        'complete_binary_kernel_generators':len(PG),'physically_verified_binary_hints':len(H),'physically_verified_extra_hints':len(extra),
        'independent_linear_outputs':selected,'nonzero_physical_determinant':str(physical_det),
        'recovery_blocks':block_reports,'localizer':str(h),'nonzero_localizer_image':str(phi(h)),
        'complete_localized_injectivity_then_saturation':True,'saturation_steps':stages,
        'full_generator_set':True,'complete_tagged_initial_kernel':True,'recovered_character_pair_after_graded_change':[6,10],'sum_of_characters_from_transverse_degree_mod2':True,'polynomial_coordinate_change_and_inverse_verified':True,'physically_checked_monic_extensions':13,'complete_kernel_generators':len(kernel),'dimension_from_injectivity':4,
        'finite_character_homogeneous':bool(homogeneous),
        'hint_sha256':hashlib.sha256(hp.read_bytes()).hexdigest(),'seconds':time.time()-started}
    result={'full_generator_set':True,'core_indices':ids,'relations':list(map(str,kernel)),'certificate':certificate}
    (out/'177_initial1_complete_kernel.json').write_text(json.dumps(result,indent=2)+'\n')
    print('177_INITIAL1_COMPLETE_KERNEL_PASS',len(kernel),'seconds',certificate['seconds'],flush=True)
    return result


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output-dir',type=Path,required=True)
    args=parser.parse_args();data=json.loads((Path(__file__).resolve().parents[1]/'177/invariants.json').read_text())
    compute_initial_kernel(data,args.output_dir)
