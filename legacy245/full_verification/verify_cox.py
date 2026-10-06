#!/usr/bin/env sage -python
"""Complete polynomial-map kernels and simultaneous valuation criterion.

Run with SageMath: sage -python full_verification/verify_cox.py --case 114 --output-dir verification-results/114
All mathematical inputs are adjacent public case JSONs. Cached ideals are
accepted only with matching input and verifier hashes. No archived PASS flag
or supplied purported full kernel is a proof input.
"""
from sage.all import *
from pathlib import Path
import argparse, hashlib, importlib.util, json, os, time
from exact_algebra import groebner_basis as exact_groebner_basis, intersection as exact_intersection, saturation_basis, saturation as exact_saturation

PARSER=argparse.ArgumentParser(description=__doc__)
PARSER.add_argument('--case',type=int,required=True)
PARSER.add_argument('--output-dir',type=Path,required=True)
PARSER.add_argument('--stage',choices=['all','base','initial','simultaneous','core'],default='all')
PARSER.add_argument('--junior',type=int)
PARSER.add_argument('--resume',action='store_true')
PARSER.add_argument('--ordinary-method',choices=['auto','graph','molien'],default='auto')
PARSER.add_argument('--base-method',choices=['public-saturation','homogenize'],default='public-saturation')
PARSER.add_argument('--parameter-compression',choices=['none','orders'],default='orders')
PARSER.add_argument('--saturation-method',choices=['satstd','groebner'],default='satstd')
PARSER.add_argument('--bayer-order',choices=['auto','reverse','natural','cyclic'],default='auto')
PARSER.add_argument('--hom-method',choices=['auto','simultaneous','sequential'],default='auto')
PARSER.add_argument('--hom-order',help='One-based comma-separated permutation of all junior parameters.')
PARSER.add_argument('--tag-method',choices=['auto','graph','characters'],default='auto',help='Auto selects proved localized kernels, a finite graph for161 junior2, physical graphs for227 juniors1/2, and exact character intersections otherwise.')
PARSER.add_argument('--direct',action='store_true',help='Disable exact triangular graph simplification.')
ARGS=PARSER.parse_args()
ROOT=Path(__file__).resolve().parent.parent
OUT=ARGS.output_dir.resolve(); OUT.mkdir(parents=True,exist_ok=True)
A_PATH=ROOT/str(ARGS.case)/'invariants.json'; M_PATH=ROOT/str(ARGS.case)/'model.json'
a=json.loads(A_PATH.read_text()); m=json.loads(M_PATH.read_text())
HASHES={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [A_PATH,M_PATH,ROOT/'catalogue.json',Path(__file__).resolve()]}
HASHES['parameter_compression']=ARGS.parameter_compression
HASHES['saturation_method']=ARGS.saturation_method
HASHES['bayer_order']=ARGS.bayer_order
HASHES['hom_method']=ARGS.hom_method
HASHES['hom_order']=ARGS.hom_order
HASHES['tag_method']=ARGS.tag_method
HASHES['base_method']=ARGS.base_method
HASHES['ordinary_method']=ARGS.ordinary_method
HASHES['direct']=ARGS.direct
BEGIN=time.time()
def emit(event,**kw):
    record=dict(event=event,case=ARGS.case,elapsed_seconds=float(round(time.time()-BEGIN,3)),**kw)
    print(json.dumps(record),flush=True)
    with (OUT/'events.jsonl').open('a') as stream:stream.write(json.dumps(record)+'\n')
mini=a['cyclotomic_minpoly']
K=NumberField(PolynomialRing(QQ,'zeta')(mini),'zeta') if mini else QQ
X=PolynomialRing(K,a['polynomial_coordinate_order'])
F=[X(f) for f in a['generator_polynomials']]
n=len(F); r=len(a['junior_orders']); nu=matrix(ZZ,a['valuation_matrix'])
nu_supports=[[(j,int(w)) for j,w in enumerate(row) if w] for row in nu.rows()]
degrees=list(map(int,a.get('polynomial_degrees',[f.total_degree() for f in F])))
# Reverse the invariant-variable tie order: late monic graph variables lead.
U_ORDER=TermOrder(matrix(ZZ,[degrees]+[[-int(j==k) for j in range(n)] for k in range(n-1)]))
U=PolynomialRing(K,[f'u{i+1}' for i in range(n)],order=U_ORDER)
uvars=list(U.gens())
hint_field=QQ if all('zeta' not in f for f in a.get('base_relations',[])) else K
HU=PolynomialRing(hint_field,list(U.variable_names()),order=U_ORDER)
base_hints=[U(HU(f)) for f in a.get('base_relations',[])]
orders=list(map(int,a['junior_orders']))
BOUND_MAPS=None

def actual_valuation_maps():
    global BOUND_MAPS
    if BOUND_MAPS is None:
        helper=ROOT/'binding_verification/valuation_maps.py'
        spec=importlib.util.spec_from_file_location('public_valuation_maps',helper)
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        BOUND_MAPS=module.load_maps(ARGS.case,target_ring=X)
    return BOUND_MAPS

for dependency in ['binding_verification/valuation_maps.py','binding_verification/227_initial_bases.json','binding_verification/special_groups.json','binding_verification/standard_groups.json','full_verification/native_checks/public_saturation.py','full_verification/ordinary_certificate.py','full_verification/special_kernels.py','full_verification/special_initial173.py','full_verification/173_initial1_hints.json','full_verification/verify_generation.py','full_verification/exact_algebra.py','full_verification/rational_tags.py','binding_verification/verify_binding.py']:
    dependency_path=ROOT/dependency
    if dependency_path.exists():HASHES[dependency]=hashlib.sha256(dependency_path.read_bytes()).hexdigest()
for dependency in ['full_verification/special_initial171.py','full_verification/171_initial1_localization_hints.json','full_verification/special_initial171_j2.py','full_verification/171_initial2_localization_hints.json','full_verification/special_initial171_j3.py','full_verification/171_initial3_localization_hints.json','full_verification/special_initial161.py','full_verification/161_initial2_witness.json']:
    dependency_path=ROOT/dependency
    if dependency_path.exists():HASHES[dependency]=hashlib.sha256(dependency_path.read_bytes()).hexdigest()
dependency_path=ROOT/'full_verification/special_initial178.py'
if dependency_path.exists():HASHES['full_verification/special_initial178.py']=hashlib.sha256(dependency_path.read_bytes()).hexdigest()
dependency_path=ROOT/'full_verification/finite_ordinary_graph.py'
if dependency_path.exists():HASHES['full_verification/finite_ordinary_graph.py']=hashlib.sha256(dependency_path.read_bytes()).hexdigest()
dependency_path=ROOT/'full_verification/native_checks/exact_images.py'
if dependency_path.exists():HASHES['full_verification/native_checks/exact_images.py']=hashlib.sha256(dependency_path.read_bytes()).hexdigest()
dependency_path=ROOT/'full_verification/native_checks/native_colons.py'
if dependency_path.exists():HASHES['full_verification/native_checks/native_colons.py']=hashlib.sha256(dependency_path.read_bytes()).hexdigest()
dependency_path=ROOT/'full_verification/native_checks/kronecker_images.py'
if dependency_path.exists():HASHES['full_verification/native_checks/kronecker_images.py']=hashlib.sha256(dependency_path.read_bytes()).hexdigest()
dependency_path=ROOT/'full_verification/native_checks/native_bayer.py'
if dependency_path.exists():HASHES['full_verification/native_checks/native_bayer.py']=hashlib.sha256(dependency_path.read_bytes()).hexdigest()
dependency_path=ROOT/'full_verification/native_checks/hilbert_regularity.py'
if dependency_path.exists():HASHES['full_verification/native_checks/hilbert_regularity.py']=hashlib.sha256(dependency_path.read_bytes()).hexdigest()
for dependency in ['full_verification/native_checks/parallel_kronecker.py', 'full_verification/native_checks/kronecker_worker.py', 'full_verification/native_checks/residue_target_membership.py', 'runtime_cache.py']:
    dependency_path=ROOT/dependency
    HASHES[dependency]=hashlib.sha256(dependency_path.read_bytes()).hexdigest()
for dependency in ['full_verification/special_initial173_j23.py', 'full_verification/special_initial173_recovered_characters.py', 'full_verification/173_initial23_localization_hints.json', 'full_verification/173_initial23_character_graphs.json', 'full_verification/173_initial23_sign_recovery.json']:
    dependency_path=ROOT/dependency
    HASHES[dependency]=hashlib.sha256(dependency_path.read_bytes()).hexdigest()
for dependency in ['full_verification/special_initial179_j5.py','full_verification/179_initial5_localization_hints.json','full_verification/special_initial179.py','full_verification/179_initial4_graph_hints.json']:
    dependency_path=ROOT/dependency
    if dependency_path.exists():HASHES[dependency]=hashlib.sha256(dependency_path.read_bytes()).hexdigest()
for dependency in ['full_verification/special_initial177_j1.py','full_verification/177_initial1_localization_hints.json','full_verification/special_initial177_j2.py','full_verification/177_initial2_localization_hints.json','full_verification/special_initial177_j3.py','full_verification/177_initial3_localization_hints.json','full_verification/special_initial177_j4.py','full_verification/177_initial4_localization_hints.json','full_verification/native_checks/triangular_quotient.py','full_verification/native_checks/native_membership.py']:
    dependency_path=ROOT/dependency
    if dependency_path.exists():HASHES[dependency]=hashlib.sha256(dependency_path.read_bytes()).hexdigest()
dependency_path=ROOT/'binding_verification/triangular_invariance.py'
if dependency_path.exists():HASHES['binding_verification/triangular_invariance.py']=hashlib.sha256(dependency_path.read_bytes()).hexdigest()
for dependency in ['full_verification/special_initial174_j2.py','full_verification/174_initial2_polynomial_graphs.json']:
    dependency_path=ROOT/dependency
    if dependency_path.exists():HASHES[dependency]=hashlib.sha256(dependency_path.read_bytes()).hexdigest()
if 'finite_degree_orders' not in a:
    data=actual_valuation_maps()
    a['finite_degree_orders']=data['finite_degree_orders'];a['finite_degree_matrix']=data['finite_degree_matrix']
finite_orders=list(map(int,a.get('finite_degree_orders',a['junior_orders'])))
tags=list(map(list,a.get('finite_degree_matrix',[[int(nu[k,j]%orders[k]) for j in range(n)] for k in range(r)])))
C=max([1]+[(sum(nu.column(j))+1)//degrees[j]+1 for j in range(n)])
weights=[C*degrees[j]-sum(nu.column(j)) for j in range(n)]+[1]*r
tie=list(range(n+r-1,n-1,-1))+list(range(n-1))
P_ORDER=TermOrder(matrix(ZZ,[weights]+[[-int(j==k) for j in range(n+r)] for k in tie]))
if ARGS.case==233:P_ORDER=TermOrder('degrevlex',n+r)
P=PolynomialRing(K,list(U.variable_names())+[f't{k+1}' for k in range(r)],order=P_ORDER)
ts=list(P.gens()[n:])

def cache(name,ring,build):
    path=OUT/(name+'.json')
    if ARGS.resume and path.exists():
        data=json.loads(path.read_text())
        if data.get('input_hashes')==HASHES and data.get('variables')==list(ring.variable_names()):
            emit('CHECKPOINT_RESUMED',name=name,count=len(data['generators']))
            return ring.ideal([ring(f) for f in data['generators']])
    emit('STEP_START',name=name)
    ideal=build()
    data=dict(input_hashes=HASHES,variables=list(ring.variable_names()),generators=[str(f) for f in ideal.gens()])
    temp=path.with_suffix('.tmp');temp.write_text(json.dumps(data));temp.replace(path)
    emit('STEP_COMPLETE',name=name,count=len(ideal.gens()))
    return ideal

def finite_homogeneous(f):
    es=list(f.dict())
    return all(all(sum(tags[k][j]*(e[j]-es[0][j]) for j in range(n))%finite_orders[k]==0 for k in range(len(tags))) for e in es)

def exact_graph_core(forms,hints,tagged,with_map=False):
    """Remove only literal monic linear graph variables, checking each identity.

    After each removal the chosen equation is u_j minus a polynomial in the
    remaining variables. Therefore adjoining these equations to the FULL
    kernel on retained variables gives exactly the FULL original kernel.
    """
    def potential_graph(f):
        exps=f.dict()
        for j in range(n):
            involving=[e for e in exps if e[j]]
            if len(involving)==1 and involving[0][j]==1 and sum(involving[0])==1:
                return True
        return False
    live=set(range(n)); chosen=[]; graph_map=list(uvars); equations=[f for f in hints if potential_graph(f)]
    mapping=U.hom(forms,X)
    while True:
        candidates=[]
        for q,f in enumerate(equations):
            if not f:continue
            exps=f.dict()
            for j in live:
                involving=[(e,c) for e,c in exps.items() if e[j]]
                if len(involving)==1 and involving[0][0][j]==1 and sum(involving[0][0])==1:
                    e,c=involving[0]; replacement=-(f-c*uvars[j])/c
                    candidates.append((-degrees[j],len(replacement.dict()),-j,q,replacement))
        if not candidates:break
        prefer_short_physical=ARGS.case==179 and forms==initial_forms(3)
        key=(lambda x:(x[0],-len(forms[-x[2]].dict()),x[1],x[2],x[3])) if prefer_short_physical else (lambda x:x[:4])
        _,_,negj,q,replacement=min(candidates,key=key)
        j=-negj
        relation=uvars[j]-replacement
        if tagged and not finite_homogeneous(relation):
            equations.pop(q);continue
        assert mapping(relation)==0,('Invalid proposed graph identity',j+1,str(relation))
        chosen.append(relation); live.remove(j)
        substitution=list(uvars);substitution[j]=replacement
        sub=U.hom(substitution,U)
        if with_map:graph_map=[sub(f) for f in graph_map]
        equations=[sub(f) for f in equations if f!=equations[q]]
        equations=[f for f in equations if f and potential_graph(f)]
    core=sorted(live)
    emit('EXACT_GRAPH_CORE',retained_indices=[j+1 for j in core],removed=len(chosen),tagged=tagged)
    return (core,chosen,graph_map) if with_map else (core,chosen)

def graded_graph_hints(forms,max_degree=16,max_products=2000):
    """Discover exact low-degree polynomial graph identities by linear algebra.

    The finite search only accelerates elimination. If it finds no identity,
    the variable is retained in the complete graph, so no degree bound is
    being used as an unproved completeness assertion.
    """
    kept=[];relations=[]
    for d in sorted(set(degrees)):
        ids=[j for j in range(n) if degrees[j]==d]
        if d>max_degree:
            kept.extend(ids);continue
        exponents=[]
        def enumerate_products(q,left,prefix):
            if len(exponents)>max_products:return
            if q==len(kept):
                if left==0:exponents.append(tuple(prefix))
                return
            for e in range(left//degrees[kept[q]]+1):enumerate_products(q+1,left-e*degrees[kept[q]],prefix+[e])
        enumerate_products(0,d,[])
        if len(exponents)>max_products:exponents=[]
        products=[prod(forms[j]**e[q] for q,j in enumerate(kept)) for e in exponents]
        formal=[prod(uvars[j]**e[q] for q,j in enumerate(kept)) for e in exponents]
        forms_d=products+[forms[j] for j in ids]; formal += [uvars[j] for j in ids]
        mons=sorted(set(e for f in forms_d for e in f.dict()))
        linear_field=QQ if all(c in QQ for f in forms_d for c in f.coefficients()) else K
        mat=matrix(linear_field,[[f.dict().get(e,0) for f in forms_d] for e in mons])
        pivots=set(mat.pivots())
        for rel in mat.right_kernel().basis():
            if any(rel[q] for q in range(len(products),len(forms_d))):relations.append(sum(c*f for c,f in zip(rel,formal)))
        kept.extend(j for q,j in enumerate(ids,len(products)) if q in pivots)
    emit('GRADED_GRAPH_HINTS_CHECKED',count=len(relations),retained=len(kept))
    return relations

def biquadratic_base_certificate(forms,extensions):
    # Case 179 has a rank-four biquadratic cover of a polynomial ring.
    # Squarefreeness and coprimality prove independent square classes even
    # after extending the coefficient field, so the quotient is a domain.
    emit('BIQUADRATIC_PRIMALITY_CERTIFICATE_START')
    rels=base_hints[:2]
    R0=PolynomialRing(QQ,['a','b','c','d'])
    rad=[]
    for k,rel in zip([4,5],rels):
        c=rel.monomial_coefficient(uvars[k]**2);assert c
        h=-(rel-c*uvars[k]**2)/c
        assert all(all(e[j]==0 for j in range(4,n)) for e in h.dict())
        h=R0({tuple(e)[:4]:QQ(c) for e,c in h.dict().items()});assert h.total_degree()>0
        gcd_derivatives=h
        for x in R0.gens():gcd_derivatives=gcd(gcd_derivatives,h.derivative(x))
        assert gcd_derivatives.is_unit(), 'Radicand is not squarefree'
        rad.append(h)
    assert gcd(rad[0],rad[1]).is_unit(),'Radicands have a common factor'
    evaluation=U.hom(forms,X)
    for k,rel in enumerate(rels,1):
        assert evaluation(rel)==0,('Biquadratic defining identity failed',k)
        emit('BIQUADRATIC_DEFINING_IDENTITY_ZERO',relation=k)
    jac=matrix(X,[[forms[j].derivative(x) for x in X.gens()] for j in range(4)])
    witness=None
    for point in [(1,2,3,5),(2,3,5,7),(1,3,7,11),(2,5,11,17)]:
        numeric=matrix(K,[[f(*point) for f in row] for row in jac.rows()])
        if numeric.det()!=0:witness=list(point);break
    assert witness is not None,'No algebraic-independence witness found'
    emit('BIQUADRATIC_FULL_KERNEL_PROVED',squarefree_radicands=True,coprime_radicands=True,jacobian_witness=witness)
    return U.ideal(rels+extensions)

def full_kernel(forms,hints,tagged=False):
    tag_method=ARGS.tag_method
    if tag_method=='auto':
        tag_method='graph' if ARGS.case==227 and tagged and forms!=initial_forms(2) else 'characters'
    if tagged and tag_method=='characters':
        if ARGS.case==173:
            for junior in (2,3):
                if forms==initial_forms(junior-1):
                    from special_initial173_recovered_characters import compute_tagged_kernel
                    return compute_tagged_kernel(forms,U,junior,degrees,tags,finite_orders,emit)
        if ARGS.case==177 and forms==initial_forms(0):
            from special_initial177_j1 import compute_initial_kernel
            certificate=compute_initial_kernel(a,OUT/'initial177_j1_localization')
            assert certificate.get('full_generator_set') is True
            emit('INITIAL177_J1_FULL_TAGGED_KERNEL_PROVED',generators=len(certificate['relations']))
            return U.ideal([U(f) for f in certificate['relations']])
        if ARGS.case==177 and forms==initial_forms(3):
            from special_initial177_j4 import compute_initial_kernel
            certificate=compute_initial_kernel(a,OUT/'initial177_j4_localization')
            assert certificate.get('full_generator_set') is True
            emit('INITIAL177_J4_FULL_TAGGED_KERNEL_PROVED',generators=len(certificate['relations']))
            return U.ideal([U(f) for f in certificate['relations']])
        if ARGS.case==177 and forms==initial_forms(2):
            from special_initial177_j3 import compute_initial_kernel
            certificate=compute_initial_kernel(a,OUT/'initial177_j3_localization')
            assert certificate.get('full_generator_set') is True
            assert certificate['certificate']['complete_tagged_kernel'] is True
            emit('INITIAL177_J3_FULL_TAGGED_KERNEL_PROVED',generators=len(certificate['relations']))
            return U.ideal([U(f) for f in certificate['relations']])
        if ARGS.case==178 and forms==initial_forms(0):
            from special_initial178 import compute_tagged_kernel
            return compute_tagged_kernel(forms,U,tags,finite_orders,degrees,emit)
        ordinary=full_kernel(forms,hints,False)
        if ARGS.stage=='core':return ordinary
        if all(finite_homogeneous(f) for f in ordinary.gens()):
            emit('FINITE_CHARACTER_KERNEL_ALREADY_HOMOGENEOUS',generators=len(ordinary.gens()))
            return ordinary
        if ARGS.tag_method=='auto' and ARGS.case==161 and forms==initial_forms(1):
            from finite_ordinary_graph import tagged_kernel
            return tagged_kernel(ordinary,tags,finite_orders,emit)
        if ARGS.case==178 and forms==initial_forms(0):
            from rational_tags import recovered_tag_kernel
            return recovered_tag_kernel(ordinary,forms,U,tags,finite_orders,[(5,2),(4,3)],degrees,emit)
        character_ring=U;restore=lambda f:f;character_extensions=[]
        character_indices=list(range(n));reduced_ordinary=ordinary
        if ARGS.case in [161,171,173,174,177,178,179,221,227]:
            character_hints=list(hints)+list(ordinary.gens()) if ARGS.case==174 else hints
            character_indices,character_extensions,projection=exact_graph_core(forms,character_hints,True,with_map=True)
            character_ring=PolynomialRing(K,[str(uvars[j]) for j in character_indices],order=TermOrder('wdegrevlex',[degrees[j] for j in character_indices]))
            project=U.hom(projection,U)
            reduced=[]
            for f in ordinary.gens():
                g=project(f)
                assert all(all(e[j]==0 for j in range(n) if j not in character_indices) for e in g.exponents())
                if g:reduced.append(character_ring({tuple(e[j] for j in character_indices):c for e,c in g.dict().items()}))
            reduced_ordinary=character_ring.ideal(reduced)
            restore=character_ring.hom([uvars[j] for j in character_indices],U)
            emit('FINITE_CHARACTER_REDUCED_CORE',variables=len(character_indices),ordinary_relations=len(reduced))
        cv=list(character_ring.gens());components=[]
        for choice in cartesian_product([range(o) for o in finite_orders]):
            phases=[prod(K.zeta(finite_orders[k])**(choice[k]*tags[k][j]) for k in range(len(tags))) for j in character_indices]
            twist=character_ring.hom([cv[q]/phases[q] for q in range(len(cv))],character_ring)
            components.append(character_ring.ideal([twist(f) for f in reduced_ordinary.gens()]))
        result=components[0]
        for k,next_ideal in enumerate(components[1:],2):
            emit('FINITE_CHARACTER_INTERSECTION_START',component=k,total=len(components))
            result=exact_intersection(result,next_ideal)
            emit('FINITE_CHARACTER_INTERSECTION_COMPLETE',component=k,count=len(result.gens()))
        return U.ideal([restore(f) for f in result.gens()]+character_extensions)
    # Same-degree linear dependencies are cheap exact graph simplifications.
    # In the direct tagged method only dependencies within one character
    # component are allowed. CRT components use all linear dependencies.
    buckets={}
    for j in range(n):
        key=(degrees[j],tuple(tags[k][j]%finite_orders[k] for k in range(len(tags))) if tagged else ())
        buckets.setdefault(key,[]).append(j)
    hints=list(hints)
    verified_elimination_hints=[]
    if ARGS.case==179 and forms==initial_forms(3):
        extra=json.loads((ROOT/'full_verification/179_initial4_graph_hints.json').read_text())['relations']
        extra=[U(HU(f)) for f in extra]
        evaluate=U.hom(forms,X)
        assert all(evaluate(f)==0 for f in extra),'An initial graph accelerator has nonzero image'
        hints+=extra;verified_elimination_hints=extra
        emit('INITIAL179_J4_GRAPH_ACCELERATORS_CHECKED',count=len(extra))
    if not tagged and not ARGS.direct:hints += graded_graph_hints(forms)
    for ids in buckets.values():
        if len(ids)<2:continue
        monomials=sorted(set(e for j in ids for e in forms[j].dict()))
        linear_field=QQ if all(c in QQ for j in ids for c in forms[j].coefficients()) else K
        coeff=matrix(linear_field,[[forms[j].dict().get(e,0) for j in ids] for e in monomials])
        for rel in coeff.right_kernel().basis():
            hints.append(sum(rel[q]*uvars[j] for q,j in enumerate(ids)))
    core_projection=None
    if ARGS.direct:core=list(range(n));extensions=[]
    elif ARGS.case==179 and not tagged and forms!=F:
        core,extensions,core_projection=exact_graph_core(forms,hints,tagged,with_map=True)
    else:core,extensions=exact_graph_core(forms,hints,tagged)
    if ARGS.stage=='core': return U.ideal(extensions)
    if ARGS.case==179 and not tagged and forms==F and core==list(range(6)):
        return biquadratic_base_certificate(forms,extensions)
    if ARGS.case==179 and not tagged and forms!=F and len(core)==5:
        from special_kernels import quadratic_hypersurface
        proof_hints=hints
        if core_projection is not None:
            projection=U.hom(core_projection,U)
            proof_hints=[projection(f) for f in hints[:2]]+hints
        proved=quadratic_hypersurface(forms,U,proof_hints,core,extensions,emit)
        if proved is not None:return proved
    if ARGS.case==174 and not tagged and forms==initial_forms(1):
        from special_initial174_j2 import compute_initial_kernel
        return compute_initial_kernel(forms,U,emit)
    if ARGS.case==173 and not tagged and forms==initial_forms(0):
        from special_initial173 import compute_initial_kernel
        certificate=compute_initial_kernel(a,OUT/'initial173_localization')
        assert set(certificate['core_indices'])=={j+1 for j in core}
        emit('INITIAL173_LOCALIZATION_FULL_KERNEL_PROVED',core_generators=len(certificate['relations']))
        return U.ideal([U(HU(f)) for f in certificate['relations']]+extensions)
    if ARGS.case==171 and not tagged and forms==initial_forms(0):
        from special_initial171 import compute_initial_kernel
        certificate=compute_initial_kernel(a,OUT/'initial171_localization')
        assert set(certificate['core_indices'])=={j+1 for j in core}
        emit('INITIAL171_LOCALIZATION_FULL_KERNEL_PROVED',core_generators=len(certificate['relations']))
        return U.ideal([U(HU(f)) for f in certificate['relations']]+extensions)
    if ARGS.case==171 and not tagged and forms==initial_forms(1):
        from special_initial171_j2 import compute_initial_kernel
        certificate=compute_initial_kernel(a,OUT/'initial171_j2_localization')
        assert set(certificate['core_indices'])=={j+1 for j in core}
        emit('INITIAL171_J2_LOCALIZATION_FULL_KERNEL_PROVED',core_generators=len(certificate['relations']))
        return U.ideal([U(HU(f)) for f in certificate['relations']]+extensions)
    if ARGS.case==171 and not tagged and forms==initial_forms(2):
        from special_initial171_j3 import compute_initial_kernel
        certificate=compute_initial_kernel(a,OUT/'initial171_j3_localization')
        assert set(certificate['core_indices'])=={j+1 for j in core}
        emit('INITIAL171_J3_LOCALIZATION_FULL_KERNEL_PROVED',core_generators=len(certificate['relations']))
        return U.ideal([U(HU(f)) for f in certificate['relations']]+extensions)
    if ARGS.case==161 and not tagged and forms==initial_forms(1):
        from special_initial161 import compute_initial_kernel
        certificate=compute_initial_kernel(a,OUT/'initial161_localization')
        assert certificate.get('full_generator_set') is True
        emit('INITIAL161_LOCALIZATION_FULL_KERNEL_PROVED',generators=len(certificate['relations']))
        return U.ideal([U(f) for f in certificate['relations']])
    if ARGS.case==179 and not tagged and forms==initial_forms(4):
        from special_initial179_j5 import compute_initial_kernel
        certificate=compute_initial_kernel(a,OUT/'initial179_j5_localization')
        assert certificate.get('full_generator_set') is True
        emit('INITIAL179_J5_LOCALIZATION_FULL_KERNEL_PROVED',generators=len(certificate['relations']))
        return U.ideal([U(HU(f)) for f in certificate['relations']])
    if ARGS.case==179 and not tagged and forms==initial_forms(0):
        from special_initial179 import compute_initial_kernel
        certificate=compute_initial_kernel(a,OUT/'initial179_localization')
        assert certificate.get('full_generator_set') is True
        emit('INITIAL179_LOCALIZATION_FULL_KERNEL_PROVED',generators=len(certificate['relations']))
        return U.ideal([U(HU(f)) for f in certificate['relations']])
    if ARGS.case==177 and not tagged and forms==initial_forms(1):
        from special_initial177_j2 import compute_initial_kernel
        certificate=compute_initial_kernel(a,OUT/'initial177_j2_localization')
        assert certificate.get('full_generator_set') is True
        emit('INITIAL177_J2_LOCALIZATION_FULL_KERNEL_PROVED',generators=len(certificate['relations']))
        return U.ideal([U(HU(f)) for f in certificate['relations']])
    ntag=len(finite_orders) if tagged else 0
    vnames=[f'v{j+1}' for j in range(len(core))]
    scales=[forms[j].leading_coefficient() for j in core]
    normalized=[forms[j]/scales[q] for q,j in enumerate(core)]
    rational=all(c in QQ for f in normalized for c in f.coefficients())
    core_field=QQ if rational else K
    Xcore=PolynomialRing(core_field,list(X.variable_names()))
    normalized=[Xcore(f) for f in normalized]
    if ARGS.case==179 and forms==initial_forms(4):
        # Injective monomial coordinates a=x1^2,b=x2^2,c=x1*x3,d=x2*x4.
        # Their exponent matrix has determinant four, so polynomial maps in
        # these coordinates have exactly the same kernel. Check every term.
        exponent_matrix=matrix(ZZ,[[2,0,1,0],[0,2,0,1],[0,0,1,0],[0,0,0,1]])
        assert exponent_matrix.det()!=0
        compressed=[]
        for f in normalized:
            data={}
            for e,c in f.dict().items():
                v=exponent_matrix.inverse()*vector(ZZ,e)
                assert all(q in ZZ and q>=0 for q in v),'Invalid proposed monomial compression'
                assert exponent_matrix*vector(ZZ,v)==vector(ZZ,e)
                data[tuple(map(int,v))]=c
            compressed.append(Xcore(data))
        normalized=compressed
        emit('INJECTIVE_PHYSICAL_MONOMIAL_COMPRESSION',exponent_matrix=[list(map(int,row)) for row in exponent_matrix.rows()])
    G=PolynomialRing(core_field,list(X.variable_names())+[f'c{k+1}' for k in range(ntag)]+vnames,
        order='degrevlex')
    gs=list(G.gens());xs=gs[:4];cs=gs[4:4+ntag];vs=gs[4+ntag:]
    lift=Xcore.hom(xs,G)
    graph=[cs[k]**finite_orders[k]-1 for k in range(ntag)]
    graph += [vs[q]-lift(normalized[q])*prod(cs[k]**tags[k][j] for k in range(ntag)) for q,j in enumerate(core)]
    if not tagged:
        for f in verified_elimination_hints:
            if all(all(e[j]==0 for j in range(n) if j not in core) for e in f.exponents()):
                data={(0,)*4+tuple(e[j] for j in core):c*prod(scales[q]**e[j] for q,j in enumerate(core)) for e,c in f.dict().items()}
                scalar=next(c for c in data.values() if c)
                graph.append(G({e:core_field(c/scalar) for e,c in data.items()}))
    emit('FULL_CORE_GRAPH_ELIMINATION_START',variables=len(core),tagged=tagged,coefficient_field=str(core_field))
    full=G.ideal(graph).elimination_ideal(xs+cs)
    emit('FULL_CORE_GRAPH_ELIMINATION_COMPLETE',count=len(full.gens()),tagged=tagged)
    drop=G.hom([U(0)]*(4+ntag)+[uvars[j]/scales[q] for q,j in enumerate(core)],U)
    assert all(all(e[k]==0 for k in range(4+ntag)) for f in full.gens() for e in f.exponents())
    return U.ideal([drop(f) for f in full.gens()]+extensions)

def initial_forms(k):
    if 'junior_initial_generators' in a:return [X(f) for f in a['junior_initial_generators'][k]]
    if 'junior_full_generators' not in a:return [X(f) for f in actual_valuation_maps()['junior_initial_generators'][k]]
    full=[X(f) for f in a['junior_full_generators'][k]]
    return [X({e:c for e,c in f.dict().items() if e[2]+e[3]==nu[k,j]}) for j,f in enumerate(full)]

def initial_hints(k):
    ans=[]
    for f in base_hints:
        vals={e:sum(nu[k,j]*e[j] for j in range(n)) for e in f.dict()}
        minimum=min(vals.values());ans.append(U({e:c for e,c in f.dict().items() if vals[e]==minimum}))
    return ans

def multihomogenize(ideal):
    polys=[]
    for f in ideal.gens():
        if not f:continue
        vals={e:nu*vector(ZZ,e) for e in f.dict()}
        mins=[min(v[k] for v in vals.values()) for k in range(r)]
        polys.append(P({tuple(e)+tuple(vals[e][k]-mins[k] for k in range(r)):c for e,c in f.dict().items()}))
    return P.ideal(polys)

def saturate_step(ideal,k,active_rows=None):
    """Exact Bayer saturation: positive homogeneous order, chosen t last.

    A weighted reverse-lexicographic Groebner basis divided by its maximal
    common t powers generates I:t^infinity. Positivity is checked explicitly.
    """
    if all(all(e[n+k]==0 for e in f.exponents()) for f in ideal.gens()):
        emit('SATURATION_VARIABLE_ABSENT',parameter=k+1)
        return ideal
    if ARGS.case==233:
        emit('DIRECT_IDEAL_SATURATION_START',parameter=k+1)
        result=exact_saturation(ideal,ts[k])
        emit('DIRECT_IDEAL_SATURATION_COMPLETE',parameter=k+1,generators=len(result.gens()))
        return result
    selected=list(range(r)) if active_rows is None else list(active_rows)
    invariant_order=ARGS.bayer_order if ARGS.bayer_order!='auto' else ('cyclic' if ARGS.case==179 else 'reverse')
    invariant_indices=list(range(n-1,-1,-1)) if invariant_order=='reverse' else list(range(1,n))+[0] if invariant_order=='cyclic' else list(range(n))
    other_parameters=[j for j in selected if j!=k]+[j for j in range(r) if j not in selected and j!=k]
    indices=invariant_indices+[n+j for j in other_parameters]+[n+k]
    factor=max([1]+[(sum(nu[k,j] for k in selected)+1)//degrees[j]+1 for j in range(n)])
    stage_weights=[factor*degrees[j]-sum(nu[k,j] for k in selected) for j in range(n)]+[1]*r
    assert all(w>0 for w in stage_weights)
    divisors=[1]*(n+r)
    if ARGS.parameter_compression=='orders':
        for q,order in enumerate(orders):
            if all(all(e[n+q]%order==0 for e in f.exponents()) for f in ideal.gens()):divisors[n+q]=order
    S=PolynomialRing(K,[P.variable_names()[j] for j in indices],order=TermOrder('wdegrevlex',[stage_weights[j]*divisors[j] for j in indices]))
    fs=[S({tuple(e[j]//divisors[j] for j in indices):c for e,c in f.dict().items()}) for f in ideal.gens()]
    for f in fs:
        ds={sum(e[j]*int(S.term_order().weights()[j]) for j in range(n+r)) for e in f.dict()}
        assert len(ds)<=1,('Nonhomogeneous Bayer input',k+1)
    emit('BAYER_GROEBNER_START',parameter=k+1,input_generators=len(fs),parameter_power_compression=divisors[n:])
    gb=saturation_basis(S.ideal(fs),S.gen(n+r-1),emit,keep_rational=True) if ARGS.saturation_method=='satstd' else exact_groebner_basis(S.ideal(fs))
    emit('BAYER_GROEBNER_COMPLETE',parameter=k+1,generators=len(gb))
    # Stripping creates many duplicate/redundant standard-basis elements.
    # Interreduce over the exact computation field before the expensive lift
    # to the public coefficient field and serialization of the checkpoint.
    from sage.libs.singular.function_factory import singular_function
    basis_ring=gb[0].parent();stripped=[]
    for f in gb:
        minimum=min(e[n+r-1] for e in f.dict())
        assert f.leading_monomial().exponents()[0][n+r-1]==minimum
        stripped.append(basis_ring({tuple(e[j]-(minimum if j==n+r-1 else 0) for j in range(n+r)):c for e,c in f.dict().items()}))
    stripped=list(singular_function('interred')(basis_ring.ideal(stripped)))
    emit('BAYER_STRIPPED_BASIS_INTERREDUCED',parameter=k+1,generators=len(stripped))
    sat=[]
    inverse=[indices.index(j) for j in range(n+r)]
    for f in stripped:
        sat.append(P({tuple(e[inverse[j]]*divisors[j] for j in range(n+r)):c for e,c in f.dict().items()}))
    return P.ideal(sat)

def full_hom(ideal,prefix):
    sequential=ARGS.hom_method=='sequential' or (ARGS.hom_method=='auto' and ARGS.case in [161,171,173,177,178,179,221])
    if sequential:
        default_orders={179:[4,0,3,2,1],221:[1,2,3,4,5,0],173:[1,2,0],178:[0,3,4,1,2]}
        sequence=[int(k)-1 for k in ARGS.hom_order.split(',')] if ARGS.hom_order else default_orders.get(ARGS.case,list(range(r)))
        if not ARGS.hom_order and ARGS.case==177 and prefix=='initial_1':
            sequence=[2,1,3,0]
        if not ARGS.hom_order and prefix.startswith('initial_'):
            own=int(prefix.split('_')[1])-1
            sequence=[k for k in sequence if k!=own]+[own]
        assert sorted(sequence)==list(range(r)),'Homogenization order must list each junior once'
        current=P.ideal([P({tuple(e)+(0,)*r:c for e,c in f.dict().items()}) for f in ideal.gens()])
        active=[]
        for step,k in enumerate(sequence,1):
            def homogenize_one(current=current,k=k):
                polynomials=[]
                for f in current.gens():
                    if not f:continue
                    exponents=f.exponents()
                    assert all(e[n+k]==0 for e in exponents),'A not-yet-homogenized parameter already occurs'
                    weighted={e:sum(w*int(e[j]) for j,w in nu_supports[k]) for e in exponents}
                    low=min(weighted.values());data={}
                    if all(value==low for value in weighted.values()):
                        polynomials.append(f)
                        continue
                    for e,c in f.dict().items():
                        target=list(e);target[n+k]=int(weighted[e]-low);data[tuple(target)]=c
                    polynomials.append(P(data))
                return P.ideal(polynomials)
            current=cache(prefix+f'_sequential_{step}_hom_t{k+1}',P,homogenize_one)
            active.append(k)
            current=cache(prefix+f'_sequential_{step}_saturated_t{k+1}',P,lambda current=current,k=k:saturate_step(current,k,active_rows=active))
        return current
    current=cache(prefix+'_raw',P,lambda:multihomogenize(ideal))
    for k in range(r):
        current=cache(prefix+f'_saturated_t{k+1}',P,lambda current=current,k=k:saturate_step(current,k))
    return current

if ARGS.stage=='core':
    full_kernel(F,base_hints)
    for k in ([ARGS.junior-1] if ARGS.junior else range(r)):full_kernel(initial_forms(k),initial_hints(k),True)
    emit('CORE_IDENTITIES_COMPLETE');raise SystemExit(0)
base=None;Ihom=None
if ARGS.stage in ['all','base','simultaneous']:
    ordinary_certificate=None
    use_molien=ARGS.ordinary_method=='molien' or (ARGS.ordinary_method=='auto' and ARGS.case in [171,173,177,221])
    def construct_base():
        global ordinary_certificate
        if use_molien:
            from ordinary_certificate import verify_ordinary
            result,ordinary_certificate=verify_ordinary(ARGS.case,U,X,F,OUT/'ordinary_proof',emit)
            return result
        if ARGS.case==178 and not ARGS.direct:
            from special_kernels import base178
            result,_,_=base178(F,U,base_hints,degrees,emit)
            return result
        return full_kernel(F,base_hints)
    base=cache('base_kernel',U,construct_base)
    if use_molien and ordinary_certificate is None:
        ordinary_certificate=json.loads((OUT/'ordinary_proof/ordinary_certificate.json').read_text())
        assert ordinary_certificate['ordinary_kernel_complete'] and ordinary_certificate['ordinary_invariant_generation_proved']
    emit('ORDINARY_HILBERT_SERIES_START')
    if use_molien:
        HT=PolynomialRing(QQ,'t')
        hs=HT([QQ(c) for c in ordinary_certificate['numerator']])/HT([QQ(c) for c in ordinary_certificate['denominator']])
    elif ARGS.case==178 and not ARGS.direct:
        HT=PolynomialRing(QQ,'t');ht=HT.gen()
        hs=(1-ht**8)*(1-ht**12)/prod(1-ht**d for d in degrees[:6])
    elif ARGS.case==179 and not ARGS.direct:
        HT=PolynomialRing(QQ,'t');ht=HT.gen()
        hs=(1-ht**24)**2/prod(1-ht**d for d in [2,6,8,12,12,12])
    else:hs=base.hilbert_series(grading=degrees)
    hilbert=dict(case=ARGS.case,ordinary_variable_degrees=degrees,input_hashes=HASHES,ordinary_kernel_complete=True,ordinary_kernel_characteristic=0,ordinary_invariant_generation_proved=use_molien,
        numerator=[str(c) for c in hs.numerator().list()],denominator=[str(c) for c in hs.denominator().list()],
        rational_function=str(hs),kernel_checkpoint='base_kernel.json')
    (OUT/'base_hilbert.json').write_text(json.dumps(hilbert,indent=2)+'\n')
    emit('ORDINARY_HILBERT_SERIES_COMPLETE',rational_function=str(hs))
    if ARGS.base_method=='public-saturation':
        from native_checks.public_saturation import public_presentation_fullness
        Ihom=public_presentation_fullness(m,base,U,P,nu,orders,degrees,saturate_step,emit,cache,ordinary_forms=F,image_work_directory=OUT/'public_kronecker_images')
    else:
        Ihom=full_hom(base,'base')
        MP=PolynomialRing(K,m['coordinate_order'])
        to_unit=MP.hom(list(P.gens()[:n])+[ts[k]**orders[k] for k in range(r)],P)
        public=P.ideal([to_unit(MP(s)) for s in m['equations']])
        emit('PUBLIC_PRESENTATION_EQUALITY_START')
        gpub=exact_groebner_basis(public);gfull=exact_groebner_basis(Ihom)
        assert all(f.reduce(gpub)==0 for f in Ihom.gens()),'Public presentation misses full kernel'
        assert all(f.reduce(gfull)==0 for f in public.gens()),'Public presentation has excess relations'
        emit('PUBLIC_PRESENTATION_EQUALS_FULL_KERNEL')

results=[]
if ARGS.stage in ['all','initial','simultaneous']:
    for k in ([ARGS.junior-1] if ARGS.junior else range(r)):
        beta=cache(f'initial_{k+1}_kernel',U,lambda k=k:full_kernel(initial_forms(k),initial_hints(k),True))
        if ARGS.case==174 and Ihom is not None:
            # A fresh complete target-colon calculation proves that saturating
            # every raw homogeneous initial relation preserves containment.
            # This is an exact alternative to constructing the larger Jhom.
            from native_checks.native_colons import verify_initial_target_containment
            containment=verify_initial_target_containment(beta,Ihom,nu,orders,degrees,k,emit)
            assert containment['full_homogeneous_containment'] is True
            assert containment['own_parameter_independence_checked'] is True
            assert containment['full_initial_kernel_generators']==len(beta.gens())
            (OUT/f'initial_{k+1}_target_regularity.json').write_text(json.dumps(containment,indent=2)+'\n')
            results.append(k+1)
            continue
        Jhom=full_hom(beta,f'initial_{k+1}')
        if Ihom is not None:
            if ARGS.case==179 and k in (3,4):
                # Set the unit parameter to zero and retain every component
                # of the finite-free extension in the other parameters.
                from native_checks.residue_target_membership import verify_target_containment
                import tempfile
                evidence_root=OUT/f'initial_{k+1}_residue_membership'
                evidence_root.mkdir(parents=True,exist_ok=True)
                evidence=Path(tempfile.mkdtemp(prefix='run-',dir=evidence_root))
                containment=verify_target_containment(Ihom,Jhom.gens(),nu,orders,degrees,k,emit,
                    variable_order=list(range(1,n))+[0]+list(range(n+1,n+r))+[n],
                    evidence_directory=evidence)
                assert containment['status']=='PASS' and containment['all_contained'] is True
                assert containment['checked']==len(Jhom.gens())
                assert containment['all_candidates_checked'] and containment['all_residue_components_checked']
                assert containment['candidate_reconstruction_verified']
            else:
                target=Ihom+P.ideal(ts[k]); gb=exact_groebner_basis(target)
                missing=[j for j,f in enumerate(Jhom.gens()) if f.reduce(gb)!=0]
                assert not missing,('Nonzero simultaneous remainders',k+1,missing)
            emit('FULL_SIMULTANEOUS_CONTAINMENT_ZERO',junior=k+1,full_initial_kernel_generators=len(beta.gens()),full_homogeneous_generators=len(Jhom.gens()))
        results.append(k+1)
report=dict(case=ARGS.case,stage=ARGS.stage,input_hashes=HASHES,completed_juniors=results,
    public_presentation_equals_full_kernel=Ihom is not None,
    complete_simultaneous_criterion=Ihom is not None and len(results)==r,
    elapsed_seconds=time.time()-BEGIN,
    scope='Complete kernels and valuation criterion for supplied maps. Initial invariant-ring generation and identification with actual group representations are separate requirements.')
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
emit('REQUESTED_STAGES_COMPLETE',**{k:v for k,v in report.items() if k not in ['input_hashes','case','elapsed_seconds','scope']})
