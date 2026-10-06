"""Complete Case 161 second-initial kernel over characteristic zero.

The literal forms descend from K24 to K6 and compress injectively through
c=x3^3, d=x3*x4. Seven forms depend only on a,b. Their FULL kernel is
recomputed by graph elimination. The remaining twelve forms are linear in
c,d. Two have nonzero coefficient determinant; ten checked identities solve
the others after inverting a polynomial h in the seven pure forms. Thus the
localized presentation embeds in K6(a,b)[c,d], and contraction, computed by
full saturation, is exactly the full initial kernel. Scalar extension from
K6 to K24 is faithfully flat. Optional zero identities only accelerate the
computation; every one is checked against the literal supplied forms.
"""
from pathlib import Path
import hashlib,json,re,shutil,subprocess,time
from sage.all import QQ,NumberField,PolynomialRing,TermOrder,matrix


def read_kernel_export(text):
    """Reject incomplete exports, including ignored continuation lines."""
    assert text.count('FULL_KERNEL_BEGIN\n')==text.count('FULL_KERNEL_END\n')==1
    counts=re.findall(r'FULL_KERNEL_COUNT\n(\d+)\n',text)
    assert len(counts)==1;count=int(counts[0]);assert count>0
    block=text.split('FULL_KERNEL_BEGIN\n',1)[1].split('FULL_KERNEL_END\n',1)[0]
    lines=[line.strip() for line in block.splitlines() if line.strip()]
    records=[re.fullmatch(r'J\[(\d+)\]=(.*)',line) for line in lines]
    assert all(records), 'unexpected or wrapped kernel output line'
    assert [int(item.group(1)) for item in records]==list(range(1,count+1)), 'incomplete kernel export'
    return [item.group(2) for item in records]


def compute_initial_kernel(invariant_data, output_dir):
    started=time.monotonic();out=Path(output_dir);out.mkdir(parents=True,exist_ok=True)
    assert int(invariant_data['case'])==161
    assert invariant_data['polynomial_coordinate_order']==['x1','x2','x3','x4']
    witness_path=Path(__file__).with_name('161_initial2_witness.json')
    w=json.loads(witness_path.read_text())
    K=NumberField(PolynomialRing(QQ,'eta')('eta^2-eta+1'),'eta')
    L=NumberField(PolynomialRing(QQ,'zeta')(invariant_data['cyclotomic_minpoly']),'zeta')
    embedding=K.hom([L.gen()**4],L)
    assert embedding(K.gen())**2-embedding(K.gen())+1==0
    X=PolynomialRing(K,['a','b','c','d'])
    Y=PolynomialRing(QQ,['x1','x2','x3','x4','zeta'])
    original=PolynomialRing(L,['x1','x2','x3','x4'])
    reconstruct=X.hom([original.gen(0),original.gen(1),original.gen(2)**3,
                       original.gen(2)*original.gen(3)],original,base_map=embedding)
    # The exponent map (i,j,k,l) -> (i,j,3k+l,l) is injective on N^4.
    F=[]
    for raw in invariant_data['junior_initial_generators'][1]:
        terms={}
        for e,coefficient in Y(raw).dict().items():
            assert e[2]>=e[3] and (e[2]-e[3])%3==0 and e[4]%4==0
            compressed=tuple(e[:2])+((e[2]-e[3])//3,e[3])
            terms[compressed]=terms.get(compressed,K(0))+coefficient*K.gen()**(e[4]//4)
        f=X(terms);assert reconstruct(f)==original(raw);F.append(f)
    assert len(F)==19 and all(F)
    D=list(map(int,invariant_data['polynomial_degrees']))
    assert len(D)==19
    for f,degree in zip(F,D):
        assert {int(e[0]+e[1]+3*e[2]+2*e[3]) for e in f.exponents()}=={degree}
    pure=[j for j in range(1,20) if all(e[2]+e[3]==0 for e in F[j-1].exponents())]
    mixed=[j for j in range(1,20) if j not in pure]
    assert pure==list(map(int,w['pure_indices']))==[1,2,3,4,5,6,15]
    assert all(all(e[2]+e[3]==1 for e in F[j-1].exponents()) for j in mixed)
    free=list(map(int,w['free_indices']));solved=list(map(int,w['solved_indices']))
    assert free==[7,8] and sorted(free+solved)==mixed and len(set(free+solved))==12
    ids=list(reversed(range(1,20)))
    A=PolynomialRing(K,[f'u{j}' for j in ids],order=TermOrder('wdegrevlex',[D[j-1] for j in ids]))
    u={j:A.gen(ids.index(j)) for j in ids};phi=A.hom([F[j-1] for j in ids],X)
    H=list(map(A,w['hints']));linear=list(map(A,w['relations']));h=A(w['localizer']);power=int(w['localizer_power'])
    pure_names={f'u{j}' for j in pure}
    assert power>0 and h and all(str(v) in pure_names for v in h.variables())
    assert phi(h)!=0 and len(linear)==len(solved)==10
    h_degrees={sum(int(e[k])*D[j-1] for k,j in enumerate(ids)) for e in h.exponents()}
    assert len(h_degrees)==1;h_degree=h_degrees.pop();assert h_degree>0
    for j,f in zip(solved,linear):
        assert f.derivative(u[j])==h**power
        residual=f-h**power*u[j]
        assert all(str(v) in pure_names|{f'u{q}' for q in free} for v in residual.variables())
        assert all(sum(e[ids.index(q)] for q in free)==1 for e in residual.exponents())
    for index,f in enumerate(H+linear):
        assert phi(f)==0,('false physical identity',index)
        assert len({sum(int(e[k])*D[j-1] for k,j in enumerate(ids)) for e in f.exponents()})<=1
        if index%50==0:print('161_INITIAL2_EXACT_IDENTITY',index,flush=True)
    physical_matrix=matrix(X,[[F[j-1].derivative(v) for v in X.gens()[2:]] for j in free])
    physical_det=physical_matrix.det();assert physical_det
    pure_jac=matrix(X,[[F[j-1].derivative(v) for v in X.gens()[:2]] for j in pure])
    assert any(pure_jac.matrix_from_rows([i,j]).det() for i in range(len(pure)) for j in range(i+1,len(pure)))
    # Pure coefficients are rational here; check descent rather than assuming it.
    assert all(all(c in QQ for c in F[j-1].coefficients()) for j in pure)
    P=PolynomialRing(QQ,['a','b']+[f'u{j}' for j in pure],order=TermOrder('wdegrevlex',[1,1]+[D[j-1] for j in pure]))
    pg=P.gens();graph=[pg[i+2]-P(str(F[j-1])) for i,j in enumerate(pure)]
    pure_hints=[P(str(f)) for f in H if all(str(v) in pure_names for v in f.variables())]
    Ip=P.ideal(graph+pure_hints).elimination_ideal(list(pg[:2]));PG=list(Ip.groebner_basis())
    assert PG and all(not f.degree(pg[0]) and not f.degree(pg[1]) for f in PG)
    for f in PG:
        assert len({sum(int(e[i+2])*D[j-1] for i,j in enumerate(pure)) for e in f.exponents()})==1
    print('161_INITIAL2_COMPLETE_BINARY_KERNEL',len(PG),flush=True)
    (out/'161_initial2_binary_kernel.json').write_text(json.dumps({'indices':pure,'relations':list(map(str,PG))},indent=2)+'\n')
    I=[A(str(f)) for f in PG]+linear+H
    source='option(noredefine);LIB "customstd.lib";ring R=(0,eta),('+','.join(A.variable_names())+',zz),wp('+','.join(map(str,[D[j-1] for j in ids]+[h_degree]))+');minpoly=eta^2-eta+1;\nideal I='+',\n'.join(map(str,I))+',zz-('+str(h)+');\n'
    source+='''"SATSTD_START";ideal B=satstd(I,ideal(zz));"SATSTD_DONE";size(B);
"INITIAL_CONTAINMENT_REMAINDERS";size(simplify(reduce(I,B),2));
ideal C;int minimum;intvec ee;intvec et;
for(int j=1;j<=size(B);j++){
 ee=leadexp(B[j]);minimum=ee[nvars(basering)];
 for(int k=1;k<=size(B[j]);k++){et=leadexp(B[j][k]);if(et[nvars(basering)]<minimum){ERROR("BAYER_MINIMUM_FAILED");}}
 C[j]=B[j]/zz^minimum;
}
"FULL_SATURATION_DIMENSION";attrib(C,"isSB",1);dim(C);
'''
    source+='ideal contracted=subst(C,zz,('+str(h)+'));\nring S=(0,eta),('+','.join(A.variable_names())+'),wp('+','.join(map(str,[D[j-1] for j in ids]))+');minpoly=eta^2-eta+1;\nideal J=imap(R,contracted);option(redSB);J=std(J);\n\"FULL_KERNEL_COUNT\";size(J);\n\"FULL_KERNEL_BEGIN\";J;\"FULL_KERNEL_END\";\"DONE\";quit;\n'
    # satstd gives I <= B <= I:zz^infinity. In homogeneous weighted reverse
    # lex with zz last, removing minimum zz powers from this standard basis
    # is the full Bayer saturation. The leading/minimum condition is checked.
    program=out/'161_initial2_saturate.sing';program.write_text(source)
    log=out/'161_initial2_saturate.log'
    with log.open('w') as stream:
        process=subprocess.run([shutil.which('Singular'),'-q',str(program.resolve())],stdout=stream,stderr=subprocess.STDOUT)
    text=log.read_text()
    assert process.returncode==0 and not re.search(r'^\s*\?',text,re.M) and '\nDONE\n' in text
    assert 'INITIAL_CONTAINMENT_REMAINDERS\n0\n' in text
    assert 'FULL_SATURATION_DIMENSION\n4\n' in text
    kernel=[A(raw) for raw in read_kernel_export(text)]
    assert kernel and all(kernel)
    for index,f in enumerate(kernel):
        assert phi(f)==0,('false exported kernel identity',index)
    print('161_INITIAL2_CONTRACTED_KERNEL_PHYSICAL_CHECK',len(kernel),flush=True)
    # Return the actual K24 coefficients, so no symbolic generator-name
    # substitution can silently change the field embedding in the caller.
    AL=PolynomialRing(L,list(A.variable_names()))
    extended=[AL({e:embedding(c) for e,c in f.dict().items()}) for f in kernel]
    certificate={'status':'PASS','junior':2,'complete_initial_kernel':True,
        'characteristic_zero':True,'full_generator_set':True,
        'coefficient_descent':'eta^2-eta+1=0, eta maps to zeta^4',
        'injective_monomial_compression':'c=x3^3, d=x3*x4',
        'all_compressions_checked_against_literal_initial_forms':True,
        'pure_core_indices':pure,'complete_binary_kernel_generators':len(PG),
        'free_covariant_indices':free,'recovered_covariant_indices':solved,
        'physically_verified_accelerators':len(H),'physically_verified_recoveries':len(linear),
        'localizer':str(h),'localizer_power':power,'nonzero_localizer_image':str(phi(h)),
        'nonzero_physical_covariant_determinant':str(physical_det),
        'complete_localized_injectivity_then_saturation':True,
        'satstd_partial_containment_checked':True,'full_bayer_saturation':True,
        'complete_kernel_export_count_checked':True,'every_exported_relation_physically_verified':True,
        'complete_kernel_generators':len(extended),'dimension':4,
        'finite_character_homogeneous':False,
        'witness_sha256':hashlib.sha256(witness_path.read_bytes()).hexdigest(),
        'seconds':time.monotonic()-started}
    result={'core_indices':ids,'relations':list(map(str,extended)),
            'full_generator_set':True,'certificate':certificate}
    (out/'161_initial2_complete_kernel.json').write_text(json.dumps(result,indent=2)+'\n')
    print('161_INITIAL2_COMPLETE_KERNEL_PASS',len(extended),'seconds',certificate['seconds'],flush=True)
    return result


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',type=Path,required=True)
    args=parser.parse_args()
    data=json.loads((Path(__file__).resolve().parents[1]/'161/invariants.json').read_text())
    compute_initial_kernel(data,args.output_dir)
