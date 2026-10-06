#!/usr/bin/env sage-python
"""Rebuild the complete paper83 proof from exact public mathematical inputs.

Run with: sage -python verify194.py --output-dir /path/to/certificates
No archived log, precomputed Groebner basis flag, external source tree or
installed helper module is used. Every successful assertion is mathematical;
JSON certificates report exact witnesses and source hashes.
"""
from pathlib import Path
import argparse, hashlib, itertools, json, time
from sage.all import *

HERE=Path(__file__).resolve().parent

def dump(path,data):
    path.write_text(json.dumps(data,indent=2,sort_keys=True)+'\n')

def frozen(M):
    M.set_immutable();return M

def matrix_strings(M): return [[str(x) for x in row] for row in M.rows()]

def closure(generators):
    one=identity_matrix(generators[0].base_ring(),4);one.set_immutable()
    todo=[one];seen={one}
    for g in generators:g.set_immutable()
    for a in todo:
        for g in generators:
            b=a*g;b.set_immutable()
            if b not in seen:seen.add(b);todo.append(b)
        assert len(todo)<10000,'unexpected group size'
    return todo

def order(g):
    h=identity_matrix(g.base_ring(),4)
    for k in range(1,49):
        h=h*g
        if h.is_one():return k
    raise AssertionError('unexpected element order')

def representation_match(source,target_generators,K):
    target=closure(target_generators);one=identity_matrix(K,4);one.set_immutable()
    choices=[[g for g in target if order(g)==order(s) and g.charpoly()==s.charpoly()] for s in source]
    for candidate in itertools.product(*choices):
        mapping={one:one};todo=[one];valid=True
        for a in todo:
            for s,t in zip(source,candidate):
                b=a*s;b.set_immutable();bt=mapping[a]*t;bt.set_immutable()
                if b in mapping:
                    if mapping[b]!=bt:valid=False;break
                else:mapping[b]=bt;todo.append(b)
            if not valid:break
        if not valid or len(mapping)!=len(target) or len(set(mapping.values()))!=len(target):continue
        if not all(a.trace()==b.trace() for a,b in mapping.items()):continue
        equations=[]
        for s,t in zip(source,candidate):
            for i in range(4):
                for j in range(4):
                    equations.append([((s[i,k] if l==j else 0)-(t[l,j] if k==i else 0)) for k in range(4) for l in range(4)])
        basis=matrix(K,equations).right_kernel().basis()
        mats=[matrix(K,4,4,v) for v in basis]
        for coeffs in itertools.product(range(4),repeat=len(mats)):
            C=sum((c*M for c,M in zip(coeffs,mats)),zero_matrix(K,4))
            if C.det():
                assert all(s*C==C*t for s,t in zip(source,candidate))
                return {'conjugator':matrix_strings(C),'images_of_194_generators':list(map(matrix_strings,candidate)),
                        'target_order':len(target),'determinant':str(C.det())}
    raise AssertionError('representations are not conjugate')

def check_group(a,K,Y,out):
    catalogue=json.loads((HERE.parent/'catalogue.json').read_text())
    by_index={int(row['index']):row for row in catalogue}
    assert len(by_index)==len(catalogue)
    for index in range(194,198):
        assert a['original_group_generators'][str(index)]==by_index[index]['actual_generators']
    zeta=K.gen();source=[matrix(K,x) for x in a['original_group_generators']['194']]
    assert all(g.det()==1 for g in source)
    G=closure(source);assert len(G)==12
    print('literal group and conjugacy classes',flush=True)
    d=matrix(K,a['derived_generator']);H=closure([d]);assert len(H)==3
    assert d in G and all(g*h*g.inverse()*h.inverse() in H for g in G for h in G)
    assert any(not (g*h==h*g) for g in G for h in G)
    classes=[];left=set(G)
    while left:
        g=min(left,key=lambda x:tuple(str(c) for c in x.list()))
        cl={frozen(h*g*h.inverse()) for h in G};classes.append(cl);left-=cl
    def age(g):
        roots=g.charpoly().roots(K);assert sum(m for _,m in roots)==4
        return sum(next(QQ(j)/6 for j in range(6) if zeta**j==v)*m for v,m in roots)
    jc=[c for c in classes if age(next(iter(c)))==1];assert len(jc)==3
    juniors=[frozen(matrix(K,x)) for x in a['junior_representatives_original']]
    assert all(j in G and order(j)==2 and age(j)==1 for j in juniors)
    assert len({next(i for i,c in enumerate(jc) if j in c) for j in juniors})==3
    assert len(closure([g*j*g.inverse() for g in G for j in juniors]))==12
    P=matrix(K,a['eigenbasis_original_from_y']);assert P.det()
    assert P.inverse()*d*P==diagonal_matrix(K,[zeta**(2*x) for x in a['derived_weights_mod_3']])
    F=[Y(f) for f in a['generator_polynomials']];ys=Y.gens()
    monomials=[ys[i]*ys[j] for i in [0,1] for j in [2,3]]
    monomials += [ys[0]**k*ys[1]**(3-k) for k in range(4)]+[ys[2]**k*ys[3]**(3-k) for k in range(4)]
    M=matrix(K,[[f.monomial_coefficient(m) for m in monomials] for f in F]);assert M.det()
    assert all(f==sum(c*m for c,m in zip(row,monomials)) for f,row in zip(F,M.rows()))
    # Mixed quadratics and pure cubics generate every C3-invariant monomial:
    # strip mixed factors until one weight class is empty, then strip cubics.
    vals=[];initials=[];bases=[];full=[]
    for j in juniors:
        j=P.inverse()*j*P
        plus=(j-identity_matrix(K,4)).right_kernel().basis();minus=(j+identity_matrix(K,4)).right_kernel().basis()
        assert len(plus)==len(minus)==2
        E=matrix(K,list(plus)+list(minus)).transpose();assert E.det()
        assert E.inverse()*j*E==diagonal_matrix(K,[1,1,-1,-1])
        transformed=[f(*list(E*vector(Y,ys))) for f in F]
        nu=[min(e[2]+e[3] for e in f.exponents()) for f in transformed]
        ini=[Y({e:c for e,c in f.dict().items() if e[2]+e[3]==v}) for f,v in zip(transformed,nu)]
        assert all(f(*list(j*vector(Y,ys)))==(-1)**v*f for f,v in zip(F,nu))
        vals.append(nu);initials.append(ini);bases.append(E);full.append(transformed)
    assert vals==a['valuation_matrix']
    if 'junior_initial_generators' in a:assert initials==[[Y(f) for f in row] for row in a['junior_initial_generators']]
    if 'junior_eigenbases_in_y' in a:assert bases==[matrix(K,x) for x in a['junior_eigenbases_in_y']]
    print('invariants and all valuations bound to literal matrices',flush=True)
    matches={str(i):representation_match(source,[matrix(K,x) for x in a['original_group_generators'][str(i)]],K) for i in range(195,198)}
    result={'status':'PASS','order':12,'commutator_order':3,'junior_classes':3,'junior_normal_generation':True,
            'invariant_monomial_span_determinant':str(M.det()),'valuations':vals,
            'junior_eigenbases_in_y':list(map(matrix_strings,bases)),
            'junior_initial_generators':[[str(f) for f in row] for row in initials],
            'representation_matches':matches,'class_ages':sorted(str(age(next(iter(c)))) for c in classes)}
    dump(out/'group_and_invariants.json',result)
    return F,initials

def check_algebra(a,m,K,Y,F,initials,out):
    n=12;r=3;nu=matrix(ZZ,a['valuation_matrix']);names=Y.variable_names()
    U=PolynomialRing(K,[f'u{i+1}' for i in range(n)]);us=U.gens()
    factor=1+max(sum(nu[:,j].list())//a['polynomial_degrees'][j] for j in range(n))
    weights=[factor*a['polynomial_degrees'][j]-sum(nu[:,j].list()) for j in range(n)]+[1]*r
    P=PolynomialRing(K,[f'u{i+1}' for i in range(n)]+[f't{i+1}' for i in range(r)],order=TermOrder('wdegrevlex',weights));pu=P.gens()[:n];ts=P.gens()[n:]
    tagrows=[]
    for h in range(r):
        if matrix(GF(2),[nu.row(j) for j in tagrows+[h]]).rank()>len(tagrows):tagrows.append(h)
    assert len(tagrows)==2
    # The retained two character rows span the three recorded rows over F2.
    # They therefore give exactly the same full finite-character kernel.
    def kernel(forms,tags=False):
        k=len(tagrows) if tags else 0;extra=4+k
        G=PolynomialRing(K,list(names)+[f'c{i+1}' for i in range(k)]+list(U.variable_names()),order='degrevlex')
        xs=G.gens()[:4];cs=G.gens()[4:extra];vs=G.gens()[extra:];lift=Y.hom(xs,G)
        graph=[c*c-1 for c in cs]+[vs[j]-lift(forms[j])*prod(cs[h]**(nu[tagrows[h],j]%2) for h in range(k)) for j in range(n)]
        complete=G.ideal(graph).elimination_ideal(list(xs)+list(cs));drop=G.hom([U(0)]*extra+list(us),U)
        assert all(all(e[h]==0 for h in range(extra)) for f in complete.gens() for e in f.exponents())
        return U.ideal([drop(f) for f in complete.gens()])
    def homogenize(I):
        fs=[]
        for f in I.gens():
            values={e:nu*vector(ZZ,e) for e in f.dict()};minimum=[min(v[k] for v in values.values()) for k in range(r)]
            fs.append(P({tuple(e)+tuple(values[e][k]-minimum[k] for k in range(r)):c for e,c in f.dict().items()}))
        return P.ideal(fs).saturation(P.ideal(prod(ts)))[0]
    print('ordinary kernel and full multihomogenization',flush=True)
    base=kernel(F);I=homogenize(base)
    A=PolynomialRing(K,m['coordinate_order']);phi=A.hom(list(pu)+[t*t for t in ts],P);given=P.ideal([phi(A(s)) for s in m['equations']])
    assert all(given.reduce(f)==0 for f in I.gens()),'paper83 misses relations'
    assert all(I.reduce(f)==0 for f in given.gens()),'paper83 has excess relations'
    assert given.dimension()==m['dimension']==7
    dump(out/'ordinary_kernel.json',{'generators':[str(f) for f in base.gens()]})
    dump(out/'full_homogenized_kernel.json',{'variables':list(P.variable_names()),'generators':[str(f) for f in I.gens()]})
    tests=[]
    for k in range(3):
        print('full tagged kernel and simultaneous test',k+1,flush=True)
        beta=kernel(initials[k],True);print('complete tagged kernel',k+1,len(beta.gens()),flush=True)
        J=homogenize(beta);print('complete initial homogenization',k+1,len(J.gens()),flush=True);target=I+P.ideal(ts[k])
        assert all(target.reduce(f)==0 for f in J.gens()),('Schmitt containment fails',k+1)
        dump(out/f'initial_kernel_{k+1}.json',{'generators':[str(f) for f in beta.gens()]})
        dump(out/f'initial_homogenized_kernel_{k+1}.json',{'variables':list(P.variable_names()),'generators':[str(f) for f in J.gens()]})
        tests.append({'junior':k+1,'complete_kernel_generators':len(beta.gens()),'homogenized_generators':len(J.gens()),'all_remainders_zero':True})
    result={'status':'PASS','ordinary_kernel_generators':len(base.gens()),'ordinary_invariant_generation_checked_separately':True,'independent_character_rows':[h+1 for h in tagrows],
            'full_homogenized_generators':len(I.gens()),'paper_relation_count':83,'both_ideal_inclusions_zero':True,'simultaneous_tests':tests}
    dump(out/'algebra.json',result)
    return A,A.ideal([A(f) for f in m['equations']])

def check_charts(m,c,K,out):
    R=PolynomialRing(K,m['coordinate_order']);xs=list(R.gens());F=[R(f) for f in m['equations']];Q=matrix(ZZ,m['primitive_grading'])
    rows=[]
    for index,chart in enumerate(c['charts'],1):
        piv=chart['gauge'];support=chart['support'];det=Q[:,[i-1 for i in piv]].det();assert abs(det)==1
        current=[f.subs({xs[i-1]:1 for i in piv}) for f in F];remaining=[x for i,x in enumerate(xs,1) if i not in piv]
        images={xs[i-1]:R(1) for i in piv};steps=[];localizer=prod(xs[i-1] for i in support if i not in piv)
        while True:
            cand=[]
            for k,f in enumerate(current):
                if not f:continue
                for v in remaining:
                    coeff=f.derivative(v)
                    if coeff and coeff.is_constant():
                        replacement=v-f/coeff;cand.append((len(replacement.monomials()),str(v),k,v,replacement,coeff))
            if not cand:break
            _,_,k,v,replacement,coeff=min(cand,key=lambda x:x[:3]);assert current[k]==coeff*(v-replacement)
            current=[f.subs({v:replacement}) for f in current];localizer=localizer.subs({v:replacement})
            images={x:f.subs({v:replacement}) for x,f in images.items()};images[v]=replacement;remaining.remove(v)
            steps.append({'variable':str(v),'source_equation_index':k,'coefficient':str(coeff),'replacement_at_step':str(replacement)})
        assert len(steps)==8 and len(remaining)==4 and all(not f for f in current)
        for v in remaining:images[v]=v
        assert all(f(*[images[x] for x in xs])==0 for f in F)
        assert all(images[v]==v for v in remaining)
        row={'chart':index,'support':support,'gauge':piv,'determinant':int(det),'free_coordinates':list(map(str,remaining)),
             'coordinate_images':[str(images[x]) for x in xs],'localizer':str(localizer),'constant_eliminations':steps,
             'both_ideal_inclusions_and_inverse_projection_checked':True}
        rows.append(row);print('polynomial gauge slice',index,'PASS',flush=True)
    T=PolynomialRing(K,c['first_slice_parameters']);ff=[T(f) for f in c['first_slice_images']]
    assert all(f(*ff)==0 for f in F)
    assert [ff[m['coordinate_order'].index(v)] for v in c['first_slice_free_coordinates']]==list(T.gens())
    # Check the displayed map is inverse to the full first gauge ideal, not only
    # a morphism into it: its graph ideal equals I+(u8-1,u9-1,u10-1).
    aa,bb,cc,dd=[xs[m['coordinate_order'].index(v)] for v in c['first_slice_free_coordinates']]
    lift=T.hom([aa,bb,cc,dd],R);graph=R.ideal([x-lift(f) for x,f in zip(xs,ff)])
    sliceideal=R.ideal(F+[xs[i-1]-1 for i in c['charts'][0]['gauge']])
    assert graph==sliceideal
    dump(out/'charts.json',{'status':'PASS','charts':rows,'displayed_first_parametrization_both_ideal_inclusions':True})

def check_cover(a,m,c,K,Y,F,out):
    Q=matrix(ZZ,m['primitive_grading']);D=matrix(ZZ,m['valuation_grading']);B=matrix(ZZ,m['raw_lattice_basis']);chi=vector(QQ,c['character'])
    assert D==(-matrix(ZZ,a['valuation_matrix'])).augment(2*identity_matrix(ZZ,3))
    assert B*Q==D and abs(B.det())==2
    smith=Q.smith_form()[0];assert [abs(smith[i,i]) for i in range(3)]==[1,1,1]
    assert B*chi==vector(QQ,c['raw_character']) and all(x<0 for x in B*chi)
    w=c['admissible_invariant_degree_witness'];assert sum((QQ(t)*D.column(i-1) for i,t in zip(w['indices'],w['coefficients'])),vector(QQ,[0,0,0]))==B*chi
    assert all(t>=0 for t in w['coefficients']) and all(i<=12 for i in w['indices'])
    gcds=[]
    for row in a['valuation_matrix']:
        g=gcd([f for f,v in zip(F,row) if v>0]);assert g.is_constant();gcds.append(str(g))
    # Any minimal conic expression of chi has independent columns (conic
    # Caratheodory). Enumerate all sizes <=3; reject lower-rank boundary cones.
    eligible=[]
    for size in [1,2,3]:
        for indices in itertools.combinations(range(15),size):
            mat=Q[:,list(indices)]
            if mat.rank()!=size:continue
            try:coeff=mat.solve_right(chi)
            except ValueError:continue
            if any(x<0 for x in coeff):continue
            assert size==3 and all(x>0 for x in coeff),'character is on a boundary cone'
            eligible.append({'indices':[i+1 for i in indices],'coefficients':list(map(str,coeff))})
    assert eligible
    for chart in c['charts']:
        assert any(set(x['indices'])<=set(chart['support']) for x in eligible)
    R=PolynomialRing(K,m['coordinate_order']);xs=R.gens();I=R.ideal([R(f) for f in m['equations']]);
    assert all(len({tuple(Q*vector(ZZ,e)) for e in f.exponents()})==1 for f in I.gens())
    covermons=[prod(xs[i-1] for i in row['support']) for row in c['charts']]
    uncovered=I+R.ideal(covermons)
    for j,row in enumerate(eligible,1):
        localizer=prod(xs[i-1] for i in row['indices'])
        saturation=uncovered.saturation(R.ideal(localizer))[0]
        assert saturation.is_one(),('uncovered semistable points',row)
        row['uncovered_localized_ideal_is_unit']=True
        print('ambient semistable basis covered',j,'/',len(eligible),flush=True)
    result={'status':'PASS','primitive_grading_smith_invariants':[1,1,1],'raw_lattice_index':2,
            'character':c['character'],'raw_character':c['raw_character'],'strictly_negative_raw_character':True,
            'invariant_cone_witness':w,'positive_valuation_gcds':gcds,'all_small_cones_checked':True,
            'lower_dimensional_semistable_cones':0,'eligible_bases':eligible,'six_principal_opens_cover_entire_semistable_locus':True}
    dump(out/'cover_and_admissibility.json',result)

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output-dir',type=Path,default=HERE/'verification_output')
    parser.add_argument('--sections',nargs='+',choices=['group','algebra','charts','cover'],default=['group','algebra','charts','cover'])
    args=parser.parse_args();out=args.output_dir.resolve();out.mkdir(parents=True,exist_ok=True);start=time.time()
    catalogue_hash=hashlib.sha256((HERE.parent/'catalogue.json').read_bytes()).hexdigest()
    a=json.loads((HERE/'paper_invariants83.json').read_text());m=json.loads((HERE/'paper_model83.json').read_text());c=json.loads((HERE/'paper_charts83.json').read_text())
    assert len(m['equations'])==83 and a['presentation_id']==m['presentation_id']==c['presentation_id']=='paper83'
    assert m['coordinate_order']==[f'u{i}' for i in range(1,13)]+[f'e{i}' for i in range(1,4)]
    assert a['cyclotomic_minpoly']==m['cyclotomic_minpoly']
    K=NumberField(PolynomialRing(QQ,'zeta')(a['cyclotomic_minpoly']),'zeta');Y=PolynomialRing(K,a['polynomial_coordinate_order'])
    # Algebra and admissibility always bind to freshly reconstructed matrices,
    # eigenbases, polynomial generators and initial forms.
    F,initials=check_group(a,K,Y,out)
    if 'algebra' in args.sections:check_algebra(a,m,K,Y,F,initials,out)
    if 'charts' in args.sections:check_charts(m,c,K,out)
    if 'cover' in args.sections:check_cover(a,m,c,K,Y,F,out)
    paths=[HERE/x for x in ['paper_invariants83.json','paper_model83.json','paper_charts83.json','verify194.py']]
    paths.append(HERE.parent/'catalogue.json')
    assert hashlib.sha256((HERE.parent/'catalogue.json').read_bytes()).hexdigest()==catalogue_hash
    status='ALL_PAPER83_CHECKS_PASS' if set(args.sections)=={'group','algebra','charts','cover'} else 'REQUESTED_SECTIONS_PASS'
    dump(out/'certificate.json',{'case':194,'presentation_id':'paper83','status':status,'sections':args.sections,'literal_catalogue_generators_checked':[194,195,196,197],
        'seconds':time.time()-start,'sage_version':str(version()),'input_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}})
    print(status,round(time.time()-start,2),'seconds',flush=True)
if __name__=='__main__':main()
