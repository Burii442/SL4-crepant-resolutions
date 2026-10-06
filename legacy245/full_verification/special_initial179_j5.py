"""Complete initial5 kernel via injective monomial coordinates and localization."""
from sage.all import *
from pathlib import Path
import json,time
from exact_algebra import saturation_basis
from sage.libs.singular.function_factory import singular_function

def compute_initial_kernel(invariant_data,output_dir):
    begin=time.time();out=Path(output_dir);out.mkdir(parents=True,exist_ok=True)
    A=invariant_data;data=json.loads(Path(__file__).with_name('179_initial5_localization_hints.json').read_text())
    X=PolynomialRing(QQ,A['polynomial_coordinate_order']);forms=[X(s) for s in A['junior_initial_generators'][4]]
    n=len(forms);assert n==31
    degrees=list(A['polynomial_degrees']);tags=A['finite_degree_matrix'];assert A['finite_degree_orders']==[2]
    U=PolynomialRing(QQ,[f'u{j+1}' for j in range(n)],order=TermOrder('wdegrevlex',degrees));u=U.gens()
    C=PolynomialRing(QQ,['a','b','c','d']);a,b,c,d=C.gens()
    E=matrix(ZZ,[[2,0,1,0],[0,2,0,1],[0,0,1,0],[0,0,0,1]]);assert E.det()!=0;inverse=E.inverse()
    compressed=[]
    for j,f in enumerate(forms):
        coeff={}
        for e,v in f.dict().items():
            q=inverse*vector(ZZ,e);assert all(t in ZZ and t>=0 for t in q)
            assert E*vector(ZZ,q)==vector(ZZ,e)
            assert (q[2]+q[3])%2==tags[0][j]%2
            coeff[tuple(map(int,q))]=v
        compressed.append(C(coeff))
    assert compressed[0]==2*a+b
    core=[j-1 for j in data['core_indices']]
    G=PolynomialRing(QQ,['a','c','d']+[str(u[j]) for j in core],order='degrevlex');gs=G.gens();vs=gs[3:]
    transform=C.hom([gs[0],vs[0]-2*gs[0],gs[1],gs[2]],G)
    graph=[vs[q]-transform(compressed[j]) for q,j in enumerate(core) if q]
    print('179_INITIAL5_FULL_COMPRESSED_GRAPH_START',flush=True)
    full=G.ideal(graph).elimination_ideal(list(gs[:3]))
    assert all(all(e[k]==0 for k in range(3)) for f in full.gens() for e in f.exponents())
    S=PolynomialRing(QQ,[str(u[j]) for j in core],order=TermOrder('wdegrevlex',[degrees[j] for j in core]))
    core_ideal=S.ideal([S({tuple(e[3:]):c for e,c in f.dict().items()}) for f in full.gens()])
    # Exact homogeneous minimal generation preserves the freshly eliminated
    # full ideal, and prevents redundant graph equations from inflating the
    # subsequent thirty-one-variable contraction.
    minimal=list(singular_function('minbase')(core_ideal))
    restore=S.hom([u[j] for j in core],U)
    core_kernel=[restore(f) for f in minimal]
    print('179_INITIAL5_FULL_CORE_KERNEL',len(core_kernel),flush=True)
    known=set(core);recoveries=[];evaluate=U.hom(forms,X)
    for row in data['recoveries']:
        j=int(row['index'])-1;num=U(row['numerator']);power=int(row['power'])
        assert j not in known and all(all(e[k]==0 for k in range(n) if k not in known) for e in num.exponents())
        f=u[0]**power*u[j]-num
        assert evaluate(f)==0
        recoveries.append(f);known.add(j)
    assert len(known)==n and forms[0]!=0
    # The injective monomial coordinates prove the core graph computation is
    # exact. Every additional variable is a graph after inverting u1, a
    # nonzero element of this image domain. Saturation is the contraction.
    ids=list(range(n-1,0,-1))+[0]
    R=PolynomialRing(QQ,[str(u[j]) for j in ids],order=TermOrder('wdegrevlex',[degrees[j] for j in ids]))
    inputs=[R({tuple(e[j] for j in ids):v for e,v in f.dict().items()}) for f in core_kernel+recoveries]
    print('179_INITIAL5_FULL_CONTRACTION_START',len(inputs),flush=True)
    gb=saturation_basis(R.ideal(inputs),R.gen(n-1),keep_rational=True)
    inverse_ids=[ids.index(j) for j in range(n)];result=[]
    for f in gb:
        low=min(e[n-1] for e in f.exponents())
        assert f.leading_monomial().exponents()[0][n-1]==low
        result.append(U({tuple(e[inverse_ids[j]]-(low if j==0 else 0) for j in range(n)):v for e,v in f.dict().items()}))
    result=list(U.ideal(result).interreduced_basis())
    for f in result:
        assert len({sum(e[j]*tags[0][j] for j in range(n))%2 for e in f.exponents()})==1
        assert evaluate(f)==0
    certificate=dict(complete_ordinary_kernel=True,complete_tagged_kernel=True,full_generator_set=True,finite_character_homogeneous=True,monomial_exponent_matrix=[list(map(int,row)) for row in E.rows()],core_indices=data['core_indices'],core_kernel_generators=len(core_kernel),exact_recoveries=len(recoveries),full_kernel_generators=len(result),elapsed_seconds=time.time()-begin)
    output=dict(relations=list(map(str,result)),core_indices=list(range(1,n+1)),full_generator_set=True,certificate=certificate)
    (out/'179_initial5_complete_kernel.json').write_text(json.dumps(output,indent=2)+'\n')
    print('179_INITIAL5_COMPLETE_KERNEL_PASS',len(result),time.time()-begin,flush=True)
    return output
