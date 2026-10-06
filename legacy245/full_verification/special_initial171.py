"""Complete first-junior initial kernel for Case 171 from a binary subalgebra.

The full binary kernel is recomputed by graph elimination.  The two outputs
u7,u8 are independent over QQ(x1,x2), and seventeen triangular identities
solve every other covariant after inverting u1*u6.  Thus the localized
presentation is injective.  Its full saturation is the full ordinary kernel.

The 78 binary relations in the companion JSON are verified accelerators;
no stored claim of completeness is trusted. Singular satstd supplies only
intermediate partially saturated standard bases. Weighted homogeneous Bayer
stripping, with each chosen variable last, completes the saturation by both
u1 and u6. All intermediate ideals lie between I and I:(u1*u6)^infinity.
"""
from pathlib import Path
import hashlib,json,time
from sage.all import QQ,PolynomialRing,TermOrder,matrix,gcd,vector,ZZ
from exact_algebra import saturation_basis


def compute_initial_kernel(invariant_data, output_dir):
    start=time.time();out=Path(output_dir);out.mkdir(parents=True,exist_ok=True)
    assert int(invariant_data['case'])==171
    hp=Path(__file__).with_name('171_initial1_localization_hints.json')
    hints=json.loads(hp.read_text());ids=list(reversed(hints['core_indices']))
    assert len(set(ids))==len(ids)==30
    X=PolynomialRing(QQ,names=invariant_data['polynomial_coordinate_order'])
    assert X.ngens()==4
    forms={i:X(invariant_data['junior_initial_generators'][0][i-1]) for i in ids}
    degrees={i:forms[i].total_degree() for i in ids}
    assert all(degrees[i]>0 for i in ids)
    pure=[i for i in ids if all(e[2]+e[3]==0 for e in forms[i].exponents())]
    assert set(pure)==set(hints['pure_indices'])
    binary_jacobian=matrix(X,[[forms[i].derivative(X.gen(j)) for j in [0,1]] for i in pure])
    assert any(binary_jacobian.matrix_from_rows([i,j]).det()!=0
               for i in range(len(pure)) for j in range(i+1,len(pure)))
    for i in set(ids)-set(pure):
        assert len({e[2]+e[3] for e in forms[i].exponents()})==1
    A=PolynomialRing(QQ,names=['u'+str(i) for i in ids],
                     order=TermOrder('wdegrevlex',[degrees[i] for i in ids]))
    phi=A.hom([forms[i] for i in ids],X)
    pure_hints=list(map(A,hints['binary_kernel_hints']))
    assert all(phi(f)==0 for f in pure_hints)
    assert all(all(int(str(v)[1:]) in pure for v in f.variables()) for f in pure_hints)
    P=PolynomialRing(QQ,names=['x1','x2']+['u'+str(i) for i in pure],
                     order=TermOrder('wdegrevlex',[1,1]+[degrees[i] for i in pure]))
    x=P.gens();graph=[x[2+j]-P(str(forms[i])) for j,i in enumerate(pure)]
    binary=P.ideal(graph+[P(str(f)) for f in pure_hints]).elimination_ideal(list(x[:2]))
    binary_basis=list(binary.groebner_basis())
    assert all(f.degree(x[0])==f.degree(x[1])==0 for f in binary_basis)
    (out/'171_initial1_binary_kernel.json').write_text(json.dumps({
        'pure_indices':pure,'relations':list(map(str,binary_basis))},indent=2)+'\n')
    print('171_INITIAL1_COMPLETE_BINARY_KERNEL',len(binary_basis),flush=True)
    selected=list(hints['selected_linear_indices']);assert selected==[7,8]
    assert all(all(e[2]+e[3]==1 for e in forms[i].exponents()) for i in selected)
    determinant=matrix(X,[[forms[i].derivative(X.gen(j)) for j in [2,3]] for i in selected]).det()
    assert determinant!=0
    known=set(pure)|set(selected);relations=[];h=A('u1')*A('u6');assert phi(h)!=0
    for row in hints['triangular_relations']:
        j=int(row['index']);assert j in ids and j not in known
        f=A(row['relation']);c=A(row['coefficient']);u=A('u'+str(j))
        assert phi(f)==0 and f.degree(u)==1 and f.derivative(u)==c
        assert all(int(str(v)[1:]) in known|{j} for v in f.variables())
        assert all(int(str(v)[1:]) in pure for v in c.variables())
        remainder=c
        while not remainder.is_constant():
            divisor=gcd(remainder,h);assert not divisor.is_constant()
            remainder=remainder//divisor
        assert remainder
        known.add(j);relations.append(f)
    assert known==set(ids)
    ideal=A.ideal([A(str(f)) for f in binary_basis]+relations)
    for f in ideal.gens():
        assert len({sum(int(e[j])*degrees[i] for j,i in enumerate(ids)) for e in f.exponents()})<=1
    steps=[]
    # Let I be the original ideal, S the product of all parameters and
    # T=I:S^infinity. After k stages the invariant is
    # I:(t_1*...*t_k)^infinity <= I_k <= T. The partial satstd ideal J
    # lies between I_{k-1} and T; weighted Bayer gives I_k=J:t_k^infinity.
    # Monotonicity proves the lower bound, and T being t_k-saturated the
    # upper bound. At the last stage both bounds equal T. No saturation
    # of intermediate I_k with respect to earlier parameters is assumed.
    for chosen in [1,6]:
        order=[i for i in ids if i!=chosen]+[chosen]
        B=PolynomialRing(QQ,names=['u'+str(i) for i in order],
                         order=TermOrder('wdegrevlex',[degrees[i] for i in order]))
        input_polys=[B(str(f)) for f in ideal.gens()]
        print('171_INITIAL1_SATURATION_START',chosen,len(input_polys),flush=True)
        basis=list(saturation_basis(B.ideal(input_polys),[B('u1'),B('u6')]))
        basis=[f for f in basis if f]
        (out/f'171_initial1_standard_basis_u{chosen}.json').write_text(json.dumps({
            'variables':list(B.variable_names()),'relations':list(map(str,basis))},indent=2)+'\n')
        saturated=[]
        for f in basis:
            assert len({sum(int(e[j])*degrees[i] for j,i in enumerate(order)) for e in f.exponents()})==1
            power=min(e[len(order)-1] for e in f.exponents())
            assert f.leading_monomial().exponents()[0][len(order)-1]==power
            saturated.append(A(str(f//B.gens()[len(order)-1]**power)))
        ideal=A.ideal(saturated)
        steps.append({'last_variable':chosen,'standard_basis_generators':len(basis),
                      'both_variable_partial_saturation':True,'weighted_Bayer_strip':True})
        print('171_INITIAL1_SATURATION_COMPLETE',chosen,len(basis),flush=True)
    kernel=list(ideal.gens())
    assert all(phi(f)==0 for f in kernel)
    tags=matrix(ZZ,invariant_data['finite_degree_matrix']);orders=invariant_data['finite_degree_orders']
    homogeneous=True
    for f in kernel:
        characters={tuple(sum(int(e[j])*int(tags[k,ids[j]-1]) for j in range(len(ids)))%int(orders[k])
                          for k in range(len(orders))) for e in f.exponents()}
        homogeneous=homogeneous and len(characters)<=1
    certificate={'status':'PASS','complete_initial_kernel':True,'junior':1,
        'pure_core_indices':pure,'complete_binary_kernel_generators':len(binary_basis),
        'physically_verified_binary_hints':len(pure_hints),'triangular_relations':len(relations),
        'independent_linear_outputs':selected,'nonzero_physical_determinant':str(determinant),
        'localizer':str(h),'nonzero_localizer_image':str(phi(h)),
        'complete_localized_injectivity_then_saturation':True,'saturation_steps':steps,
        'complete_kernel_generators':len(kernel),'dimension_from_injectivity':4,
        'finite_character_homogeneous':bool(homogeneous),
        'hint_sha256':hashlib.sha256(hp.read_bytes()).hexdigest(),'seconds':time.time()-start}
    result={'core_indices':ids,'relations':list(map(str,kernel)),'certificate':certificate}
    (out/'171_initial1_complete_kernel.json').write_text(json.dumps(result,indent=2)+'\n')
    print('171_INITIAL1_COMPLETE_KERNEL_PASS',len(kernel),'seconds',certificate['seconds'],flush=True)
    return result


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output-dir',type=Path,required=True)
    args=parser.parse_args();data=json.loads((Path(__file__).resolve().parents[1]/'171/invariants.json').read_text())
    compute_initial_kernel(data,args.output_dir)
