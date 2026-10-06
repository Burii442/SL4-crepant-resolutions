#!/usr/bin/env sage -python
"""Exact binding of a normalized Cox input to its finite matrix group.

API: verify_case(case, output=None). CLI: --case N --output PATH.
Verifies group conjugacy, every junior class and order, all generator
invariances under the commutator, exact valuations and character grading.
It computes Molien but does not by itself prove generation of invariants.
"""
from pathlib import Path
import argparse
import hashlib
from itertools import combinations
import json
import sys
import time
from sage.all import (QQ, ZZ, CyclotomicField, PolynomialRing, matrix,
                      identity_matrix, vector, diagonal_matrix, block_matrix,
                      cyclotomic_polynomial, divisors, lcm, sage_eval)
HERE=Path(__file__).resolve().parent
SUPPLEMENT=HERE.parent

def require(condition, message):
    if not condition:
        raise ValueError(message)

def immutable(m):
    m.set_immutable()
    return m

def close(generators, identity, bound):
    found={immutable(identity)};todo=list(found)
    for a in todo:
        for b in generators:
            c=immutable(a*b)
            if c not in found:
                found.add(c);todo.append(c)
                require(len(found)<=bound,'Matrix closure exceeded the asserted finite order')
    return found

def minimal_subgroup(elements, identity, bound):
    result={immutable(identity)};gens=[]
    # Prefer sparse exact substitutions; whole-subgroup closure still proves
    # that the selected generators generate precisely the required subgroup.
    for g in sorted(elements,key=lambda h:(sum(c!=0 for c in h.list()),sum(len(str(c)) for c in h.list()),h)):
        if g not in result:
            gens.append(g);result=close(gens,identity,bound)
    return result,gens

def finite_degree_kernel(degrees, orders, n):
    A=matrix(ZZ,degrees);require(A.ncols()==n and A.nrows()==len(orders),'Degree matrix shape')
    D=diagonal_matrix(ZZ,orders)
    return block_matrix(ZZ,[[A,-D]]).right_kernel().basis_matrix()[:,:n].row_module()

def verify_case(case, output=None):
    case=int(case);start=time.time()
    model_path=SUPPLEMENT/str(case)/'model.json'
    invariants_path=SUPPLEMENT/str(case)/'invariants.json'
    m=json.loads(model_path.read_text());a=json.loads(invariants_path.read_text())
    catalogue_path=SUPPLEMENT/'catalogue.json'
    record=next(r for r in json.loads(catalogue_path.read_text()) if r['index']==case)
    witness_path=HERE/('special_groups.json' if case in [114,138,231,233] else 'standard_groups.json')
    witness=json.loads(witness_path.read_text())[str(case)]
    initial_bases_path=HERE/f'{case}_initial_bases.json'
    initial_bases=json.loads(initial_bases_path.read_text()) if initial_bases_path.exists() else None
    order=int(witness['cyclotomic_order']);K=CyclotomicField(order,'zeta');zeta=K.gen()
    T=PolynomialRing(QQ,'zeta');mini=a.get('cyclotomic_minpoly')
    input_order=next(n for n in range(1,97) if T(cyclotomic_polynomial(n))==T(mini)) if mini else 1
    require(order%input_order==0,'Coefficient-field embedding')
    oldzeta=zeta**(order//input_order)
    def scalar(x,root):return K(sage_eval(str(x),locals={'zeta':root}))
    def mat(raw,root=zeta):return immutable(matrix(K,[[scalar(x,root) for x in row] for row in raw]))
    I=identity_matrix(K,4)
    P=mat(witness['P']);require(P.nrows()==P.ncols()==4 and P.det()!=0,'Singular coordinate change')
    Pi=P.inverse()
    actual_gens=[mat(raw) for raw in record['actual_generators']]
    actual=close(actual_gens,I,record['order'])
    require(len(actual)==record['order'],'Catalogue group order')
    poly_gens=[immutable(Pi*g*P) for g in actual_gens]
    group=close(poly_gens,I,record['order'])
    require(group=={immutable(Pi*g*P) for g in actual},'Whole-group conjugacy')
    require(all(g.det()==1 for g in group),'Determinant-one group')
    if 'group_generators_in_coordinates' in witness:
        supplied=close([mat(raw) for raw in witness['group_generators_in_coordinates']],I,record['order'])
        require(supplied==group,'Canonical generator group differs from the catalogue group')
    raw_juniors=a.get('canonical_juniors',a.get('junior_representatives_in_coordinates'))
    juniors=[mat(raw,oldzeta) for raw in raw_juniors] if raw_juniors is not None else [mat(raw) for raw in witness['junior_matrices']]
    require(len(juniors)==len(a['junior_orders'])==record['junior_classes'],'Junior-list size')
    rank_two={g for g in group if (g-I).rank()==2};covered=set();class_sizes=[]
    for j,r in zip(juniors,a['junior_orders']):
        require(j in group and j**r==I and all(j**d!=I for d in divisors(r) if d<r),'Junior matrix/order does not belong to group')
        orbit={immutable(g*j*g.inverse()) for g in group}
        require(orbit<=rank_two and not orbit&covered,'Duplicate or nonjunior conjugacy class')
        covered.update(orbit);class_sizes.append(len(orbit))
    require(covered==rank_two,'Junior representatives do not cover all junior classes')
    junior_group,_=minimal_subgroup(rank_two,I,len(group))
    require(junior_group==group,'Group not generated by all juniors')
    commutators={immutable(g*s*g.inverse()*s.inverse()) for g in group for s in poly_gens}
    derived,derived_gens=minimal_subgroup(commutators,I,len(group))
    require(all(immutable(g*h*g.inverse()) in derived for g in poly_gens for h in derived_gens),'Derived subgroup normality')
    print(f'{case}: complete group and junior binding; |G|={len(group)}, |[G,G]|={len(derived)}',flush=True)
    R=PolynomialRing(K,a['polynomial_coordinate_order']);X=R.gens();loc=dict(zip(a['polynomial_coordinate_order'],X));loc['zeta']=oldzeta
    generators=[R(sage_eval(f,locals=loc)) for f in a['generator_polynomials']]
    require(len(generators)==m['invariant_generator_count'],'Invariant generator count')
    require(all(f and f.is_homogeneous() for f in generators),'Nonzero homogeneous generators required')
    actual_degrees=[int(f.total_degree()) for f in generators]
    given_degrees=a.get('polynomial_degrees',a.get('homogeneous_generator_degrees'))
    if given_degrees is not None:require(actual_degrees==given_degrees,'Polynomial degrees')
    invariant_checks=0;direct_invariant_checks=0;invariance_core=list(range(len(generators)));triangular_identities=[]
    if case==179:
        if str(HERE) not in sys.path:sys.path.insert(0,str(HERE))
        from triangular_invariance import triangular_core
        invariance_core,triangular_identities=triangular_core(generators,a['base_relations'],6,
            emit=lambda message:print(f'{case}: {message}',flush=True))
        require(len(generators)==31 and len(triangular_identities)==25,'Incomplete triangular invariance reduction')
    for hno,h in enumerate(derived_gens,1):
        images=list(h*vector(R,X))
        for index in invariance_core:
            fno=index+1;f=generators[index]
            require(f(*images)==f,f'{case}: F{fno} is not invariant under commutator generator {hno}')
            direct_invariant_checks+=1
        # Checked monic triangular identities imply the same equality for
        # every remaining generator, by induction on its index.
        invariant_checks+=len(generators)
        print(f'{case}: exact invariance under commutator generator {hno}/{len(derived_gens)}',flush=True)
    valuations=[];character_checks=0;initial_checks=0;full_form_checks=0
    for jno,(j,r) in enumerate(zip(juniors,a['junior_orders'])):
        require(r==2 or order%r==0,'Cyclotomic field misses a junior eigenvalue')
        root=K(-1) if r==2 else zeta**(order//r)
        if initial_bases is not None or 'junior_eigenbases' in a:
            if initial_bases is not None:
                require(initial_bases['case']==case and initial_bases['cyclotomic_order']==order,'Initial-basis coefficient convention')
                B=mat(initial_bases['junior_eigenbases'][jno],zeta)
            else:B=mat(a['junior_eigenbases'][jno],oldzeta)
            diagonal=B.inverse()*j*B
            require(diagonal.is_diagonal(),'Supplied junior eigenbasis')
            weights=[next(e for e in range(r) if root**e==diagonal[q,q]) for q in range(4)]
        else:
            basis=[];weights=[]
            for e in range(r):
                b=(j-root**e*I).right_kernel().basis();basis.extend(b);weights.extend([e]*len(b))
            B=matrix(K,basis).transpose()
        require(B.det()!=0 and sum(weights)==r,'Junior eigenbasis/age')
        images=list(B*vector(R,X));row=[]
        for fno,f in enumerate(generators):
            transformed=f(*images)
            degrees=[sum(e*w for e,w in zip(ex,weights)) for ex in transformed.exponents()]
            value=int(min(degrees));row.append(value)
            require(all((d-value)%r==0 for d in degrees),'Generator is not homogeneous for the actual junior character')
            character_checks+=1
            if 'junior_initial_generators' in a:
                initial=R({e:c for e,c in transformed.dict().items() if sum(v*w for v,w in zip(e,weights))==value})
                given=R(sage_eval(a['junior_initial_generators'][jno][fno],locals=loc))
                require(initial==given,f'{case}: incorrect initial form for junior {jno+1}, generator {fno+1}')
                initial_checks+=1
            if 'junior_full_generators' in a:
                given=R(sage_eval(a['junior_full_generators'][jno][fno],locals=loc))
                require(transformed==given,f'{case}: incorrect eigenbasis expression for junior {jno+1}, generator {fno+1}')
                full_form_checks+=1
        require(row==a['valuation_matrix'][jno],f'{case}: valuation row {jno+1}')
        valuations.append(row)
        print(f'{case}: exact valuation row {jno+1}/{len(juniors)}',flush=True)
    # The finite tags must induce exactly the same equivalence of generator
    # characters as evaluation on the complete list of junior classes.
    n=len(generators);valuation_lattice=finite_degree_kernel(valuations,a['junior_orders'],n)
    tags=a.get('finite_degree_matrix',valuations);tag_orders=a.get('finite_degree_orders',a['junior_orders'])
    tag_lattice=finite_degree_kernel(tags,tag_orders,n)
    require(valuation_lattice==tag_lattice,'Finite tags do not identify the actual generator characters')
    character_index=int(abs(valuation_lattice.basis_matrix().det()))
    require(character_index==len(group)//len(derived),'Generator characters do not span the character group')
    # Molien is recomputed from every commutator element. No saved series is read.
    U=PolynomialRing(K,'t');t=U.gen();FF=U.fraction_field();denominators={}
    for h in derived:
        d=U((identity_matrix(U,4)-t*h).det());denominators[d]=denominators.get(d,0)+1
    molien=sum(FF(c)/d for d,c in denominators.items())/len(derived)
    require(all(c in QQ for c in molien.numerator().list()+molien.denominator().list()),'Nonrational Molien series')
    result={'status':'PASS','case':case,'group_order':len(group),'derived_order':len(derived),
        'junior_class_sizes':class_sizes,'all_junior_classes_covered':True,
        'invariant_generators':n,'exact_invariance_checks':invariant_checks,
        'direct_invariance_substitutions':direct_invariant_checks,
        'invariance_method':'Exact core substitutions and checked monic triangular identities' if triangular_identities else 'Exact substitutions for every generator',
        'invariance_core_indices':[i+1 for i in invariance_core],
        'triangular_invariance_identities':triangular_identities,
        'valuations_checked':sum(map(len,valuations)),'actual_character_checks':character_checks,
        'stored_initial_forms_checked':initial_checks,'stored_full_eigenbasis_expressions_checked':full_form_checks,
        'finite_character_index':character_index,'polynomial_degrees':actual_degrees,
        'molien_numerator':[str(QQ(c)) for c in molien.numerator().list()],
        'molien_denominator':[str(QQ(c)) for c in molien.denominator().list()],
        'inputs':{str(p.relative_to(SUPPLEMENT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [catalogue_path,model_path,invariants_path,witness_path,Path(__file__).resolve()]+([initial_bases_path] if initial_bases is not None else [])+([HERE/'triangular_invariance.py'] if case==179 else [])},
        'elapsed_seconds':round(time.time()-start,3),
        'scope':'Complete group/junior binding, exact commutator invariance, valuations and finite character grading. Full generation of ordinary invariants requires the separate generation or full-kernel/Hilbert comparison.'}
    if output is not None:
        output=Path(output);output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2),flush=True)
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--case',type=int,required=True);p.add_argument('--output',type=Path)
    args=p.parse_args();verify_case(args.case,args.output or HERE/'verification'/f'{args.case}.json')
if __name__=='__main__':main()
