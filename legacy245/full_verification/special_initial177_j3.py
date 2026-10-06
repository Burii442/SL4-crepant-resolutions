"""Complete Case177 initial3 kernel from a binary algebra and one character.

The fresh binary graph and two independent outputs define a domain of
dimension four. Three recovery matrices become invertible after localizing
the binary variable v26. Exact saturation therefore gives the full ordinary
kernel. Its second C2 character is already homogeneous. The first character
is recovered as v19/v17, followed by a full exact contraction. Finally the
literal nonzero variable scalings and one checked monic graph restore all27
public generators. Candidate identities are only checked accelerators.
"""
from pathlib import Path
import json,time,hashlib
from sage.all import *
from sage.libs.singular.function_factory import singular_function
from exact_algebra import saturation_basis
from rational_tags import recovered_tag_kernel

def compute_initial_kernel(invariant_data,output_dir):
    begin=time.time();out=Path(output_dir);out.mkdir(parents=True,exist_ok=True)
    A=invariant_data;assert int(A['case'])==177
    source=Path(__file__).with_name('177_initial3_localization_hints.json');w=json.loads(source.read_text())
    K=NumberField(PolynomialRing(QQ,'zeta')(A['cyclotomic_minpoly']),'zeta');zeta=K.gen();assert zeta**2==-1
    X=PolynomialRing(K,A['polynomial_coordinate_order']);assert X.ngens()==4
    F=[X(s) for s in A['junior_initial_generators'][2]];assert len(F)==27
    ids=w['ids'];assert ids==list(range(1,25))+[26,27]
    scales=[K(s) for s in w['scales']];assert len(scales)==26 and all(scales)
    forms=[F[i-1]/s for i,s in zip(ids,scales)];degrees=[int(A['polynomial_degrees'][i-1]) for i in ids]
    assert all({sum(e) for e in f.exponents()}=={d} for f,d in zip(forms,degrees))
    U=PolynomialRing(QQ,['v'+str(j+1) for j in range(26)],order=TermOrder('wdegrevlex',degrees));v=U.gens();phi=U.hom(forms,X)
    pure=[j for j,f in enumerate(forms) if all(e[2]+e[3]==0 for e in f.exponents())]
    assert [j+1 for j in pure]==w['pure_indices'] and len(pure)==7 and 25 in pure
    pure_names={str(v[j]) for j in pure}
    H=list(map(U,w['binary_kernel_hints']))
    assert all(phi(f)==0 and all(str(t) in pure_names for t in f.variables()) for f in H)
    # This invertible physical coordinate change descends the complete
    # binary graph to QQ; extension back to K is faithfully flat.
    change=X.hom([X.gen(0),zeta*X.gen(1),X.gen(2),X.gen(3)],X)
    binary_forms=[change(forms[j]) for j in pure]
    assert all(c in QQ for f in binary_forms for c in f.coefficients())
    Jp=matrix(X,[[forms[j].derivative(X.gen(k)) for k in [0,1]] for j in pure])
    assert any(Jp.matrix_from_rows([i,j]).det()!=0 for i in range(7) for j in range(i+1,7))
    selected=[j-1 for j in w['selected']];assert selected==[2,8]
    physical_det=matrix(X,[[forms[j].derivative(X.gen(k)) for k in [2,3]] for j in selected]).det();assert physical_det!=0
    order=list(reversed(pure));P=PolynomialRing(QQ,['x1','x2']+[str(v[j]) for j in order],order=TermOrder('wdegrevlex',[1,1]+[degrees[j] for j in order]))
    p=P.gens();graph=[p[2+k]-P(str(change(forms[j]))) for k,j in enumerate(order)]
    print('177_INITIAL3_FULL_BINARY_GRAPH_START',flush=True)
    binary=P.ideal(graph+[P(str(f)) for f in H]).elimination_ideal(list(p[:2]));BG=list(binary.groebner_basis())
    assert all(f.degree(p[0])==f.degree(p[1])==0 for f in BG)
    bg=[U(str(f)) for f in BG];print('177_INITIAL3_FULL_BINARY_KERNEL',len(bg),flush=True)
    known=set(pure+selected);relations=[];blockreports=[]
    for block in w['blocks']:
        targets=[j-1 for j in block['targets']];rels=list(map(U,block['relations']))
        assert len(targets)==len(rels) and set(targets).isdisjoint(known)
        C=matrix(U,[[f.derivative(v[j]) for j in targets] for f in rels])
        assert all(all(str(t) in pure_names for t in c.variables()) for c in C.list())
        for f,row in zip(rels,C.rows()):
            residual=f-sum(c*v[j] for c,j in zip(row,targets))
            assert all(int(str(t)[1:])-1 in known for t in residual.variables())
            assert phi(f)==0
        det=C.det();assert det==U(block['determinant']) and phi(det)!=0
        assert len(det.dict())==1 and all(e[j]==0 for e in det.exponents() for j in range(25))
        known|=set(targets);relations+=rels
        blockreports.append({'targets':block['targets'],'determinant':str(det)})
    assert known==set(range(26)) and phi(v[25])!=0
    # After inverting v26 the quotient is the binary image domain with
    # two independent polynomial variables. Saturation is its contraction.
    order=list(range(24,-1,-1))+[25]
    R=PolynomialRing(QQ,[str(v[j]) for j in order],order=TermOrder('wdegrevlex',[degrees[j] for j in order]))
    initial=[R(str(f)) for f in bg+relations]
    print('177_INITIAL3_FULL_ORDINARY_CONTRACTION_START',len(initial),flush=True)
    standard=list(saturation_basis(R.ideal(initial),R.gen(25),keep_rational=True));ordinary=[]
    for f in standard:
        assert len({sum(e[j]*degrees[order[j]] for j in range(26)) for e in f.exponents()})==1
        low=min(e[25] for e in f.exponents());assert f.leading_monomial().exponents()[0][25]==low
        ordinary.append(U(str(f//R.gen(25)**low)))
    ordinary=list(singular_function('minbase')(U.ideal(ordinary)))
    assert all(phi(f)==0 for f in ordinary)
    print('177_INITIAL3_COMPLETE_ORDINARY_KERNEL',len(ordinary),flush=True)
    tags=[[int(row[i-1]) for i in ids] for row in A['finite_degree_matrix']];assert A['finite_degree_orders']==[2,2]
    def homogeneous(f,rows):
        return len({tuple(sum(e[j]*row[j] for j in range(26))%2 for row in rows) for e in f.exponents()})<=1
    assert all(homogeneous(f,[tags[1]]) for f in ordinary)
    assert forms[16]==forms[18] and forms[16]!=0 and tags[1][16]==tags[1][18]
    def emit(event,**data):print(json.dumps({'event':event,**data}),flush=True)
    tagged=recovered_tag_kernel(U.ideal(ordinary),forms,U,[tags[0]],[2],[(18,16)],degrees,emit)
    tagged=list(singular_function('minbase')(tagged))
    assert all(phi(f)==0 and homogeneous(f,tags) for f in tagged)
    # Since the complete ordinary ideal is stable under the second
    # character, and the ratio is invariant under it, its first-character
    # contraction is already stable under both characters. Thus this is
    # the complete C2 x C2 tagged kernel, rather than only one component.
    V=PolynomialRing(K,['u'+str(j+1) for j in range(27)],order=TermOrder('wdegrevlex',A['polynomial_degrees']));u=V.gens()
    restore=U.hom([u[i-1]/s for i,s in zip(ids,scales)],V)
    expression=U(w['original25_expression_scaled']);extension=u[24]-restore(expression)
    evalall=V.hom(F,X);assert evalall(extension)==0 and extension.derivative(u[24])==1
    result=[restore(f) for f in tagged]+[extension]
    allt=A['finite_degree_matrix']
    for f in result:
        assert evalall(f)==0
        assert len({tuple(sum(e[j]*row[j] for j in range(27))%2 for row in allt) for e in f.exponents()})==1
    certificate={'status':'PASS','complete_initial_kernel':True,'complete_tagged_kernel':True,'full_generator_set':True,'finite_character_homogeneous':True,'complete_binary_kernel_generators':len(bg),'binary_dimension_two_checked':True,'independent_outputs':w['selected'],'nonzero_physical_determinant':str(physical_det),'recovery_blocks':blockreports,'full_ordinary_kernel_generators':len(ordinary),'full_tagged_core_generators':len(tagged),'full_kernel_generators':len(result),'physically_checked_monic_extensions':1,'hint_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'elapsed_seconds':time.time()-begin}
    output={'core_indices':list(range(1,28)),'relations':list(map(str,result)),'full_generator_set':True,'certificate':certificate}
    (out/'177_initial3_complete_kernel.json').write_text(json.dumps(output,indent=2)+'\n')
    print('177_INITIAL3_COMPLETE_TAGGED_KERNEL_PASS',len(result),time.time()-begin,flush=True)
    return output

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output-dir',type=Path,required=True);args=p.parse_args()
    compute_initial_kernel(json.loads((Path(__file__).resolve().parents[1]/'177/invariants.json').read_text()),args.output_dir)
