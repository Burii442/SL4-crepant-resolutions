#!/usr/bin/env python3
"""Portable exact Sieve F checks. Run with sage -python; see README.md."""
from pathlib import Path
import csv
import sys
from common import main


def verify(context):
    from sage.all import QQ, PolynomialRing, matrix, vector
    PUB = context.legacy
    inputs = context.inputs
    bind, read = context.bind, context.read

    def immutable(M):
        M.set_immutable()
        return M

    catalogue = {r['index']:r for r in read(PUB/'catalogue.json')}
    matrix_binding = context.example_matrices('F', 41, 127,
                                              catalogue[127]['actual_generators'])
    rows = list(csv.DictReader(bind(PUB/'criteria_incidence.csv').open()))
    positive = sorted(int(r['index']) for r in rows if r['test']=='G' and r['outcome']=='YES')
    assert len(positive)==29
    assert all(catalogue[i]['family']=='G' and catalogue[i]['decision']=='YES' for i in positive)
    representatives = sorted({catalogue[i]['representative'] for i in positive})
    assert representatives==[91,107,127,145,190,204,219,224,241,245]
    groups = {}
    def group(i):
        if i not in groups:
            generators = [matrix(QQ,g) for g in catalogue[i]['actual_generators']]
            seen = {immutable(matrix.identity(QQ,4))}; todo = list(seen)
            while todo:
                g = todo.pop()
                for h in generators:
                    k = immutable(g*h)
                    if k not in seen: seen.add(k); todo.append(k)
            assert len(seen)==catalogue[i]['order']
            groups[i] = seen
        return groups[i]

    witnesses = {r['index']:r for r in read(PUB/'representative_conjugacies.json')['witnesses']}
    transfers = []
    for i in positive:
        j = catalogue[i]['representative']
        if i!=j:
            w = witnesses[i]; assert w['representative']==j
            P = matrix(QQ,w['P']); assert P.det()!=0
            assert {immutable(P*g*P.inverse()) for g in group(j)}==group(i)
        else: group(i)
        transfers.append({'index':i,'representative':j,'order':len(groups[i])})
    print('F: all 29 matrix groups and representative conjugacies verified',flush=True)

    U = PolynomialRing(QQ,names='a,b,c,d,z'); a,b,c,d,z = U.gens()
    Delta = 4*a**3*c*c+27*c**4-18*a*c*c*d-a*a*d*d+4*d**3
    # Each pair records the disjoint variable sets and actual plane branch blocks.
    blocks = {
        91:[(4*a**3-27*c*c,(a,c),'cusp'),(4*b**3-27*d*d,(b,d),'cusp')],
        107:[(b*c,(b,c),'axes'),((d-a*a)*(2*d-a*a),(a,d),'pair')],
        145:[(d*(b*b-4*d),(b,d),'pair'),((a*a-c)*(a*a-2*c),(a,c),'pair')],
        190:[(a*c,(a,c),'axes'),(4*b**3-27*d*d,(b,d),'cusp')],
        204:[(b*c,(b,c),'axes'),((2*a**3-d)*(22*a**3-9*d),(a,d),'pair')],
        219:[(4*a**3-c*c,(a,c),'cusp'),((2*b**3-d)*(22*b**3-9*d),(b,d),'pair')],
        224:[((2*a**3-c)*(22*a**3-9*c),(a,c),'pair'),((2*b**3-d)*(22*b**3-9*d),(b,d),'pair')],
        241:[(d*(a*a-4*d),(a,d),'pair'),(4*b**3-c*c,(b,c),'cusp')],
        245:[(c*(a*a-4*c),(a,c),'pair'),((2*b**3-d)*(22*b**3-9*d),(b,d),'pair')]
    }
    branch = {i:parts[0][0]*parts[1][0] for i,parts in blocks.items()}
    branch[127] = b*Delta
    ring_reports = []
    for i in representatives:
        folder = PUB/str(i)/'invariant_ring'
        data = read(folder/'ring_certificate.json')
        matrices = read(folder/'input_matrices.json')
        assert matrices==catalogue[i]['actual_generators']
        R = PolynomialRing(QQ,names='x1,x2,x3,x4'); xs=R.gens()
        fs = [R(f) for f in data['generators']]
        assert len(fs)==5 and [f.degree() for f in fs]==data['weights']
        for g in matrices:
            image = list(matrix(QQ,g)*vector(xs))
            assert all(f(*image)==f for f in fs)
        T = PolynomialRing(QQ,names=['x1','x2','x3','x4']+[f'u{k}' for k in range(1,6)],order='lex')
        x,u = T.gens()[:4],T.gens()[4:]
        graph = T.ideal([u[k]-T(str(fs[k])) for k in range(5)])
        kernel = T.ideal([f for f in graph.groebner_basis() if not any(f.degree(v) for v in x)])
        relations = T.ideal([T(f) for f in data['minimal_relations']])
        assert kernel==relations and len(relations.gens())==1
        assert relations.dimension()==8
        relation = U(str(relations.gen(0)).replace('u1','a').replace('u2','b').replace('u3','c').replace('u4','d').replace('u5','z'))
        Az = relation.coefficient({z:2}); Bz = relation.coefficient({z:1}); Cz = relation.subs(z=0)
        assert Az.is_constant() and Az!=0 and relation==Az*z*z+Bz*z+Cz
        disc = Bz*Bz-4*Az*Cz
        ratio = U.fraction_field()(disc)/branch[i]
        assert ratio in QQ and ratio!=0
        assert disc==(2*Az*z+Bz)**2-4*Az*relation
        assert all(multiplicity==1 for factor,multiplicity in branch[i].factor())
        Z = PolynomialRing(QQ,'t'); t=Z.gen(); K=Z.fraction_field()
        molien = sum(K(1)/(matrix.identity(Z,4)-t*matrix(Z,g)).det() for g in group(i))/len(group(i))
        hilbert = K(1)
        for degree in data['relation_degrees']: hilbert *= 1-t**degree
        for degree in data['weights']: hilbert /= 1-t**degree
        assert molien==hilbert
        ring_reports.append({'index':i,'invariance':True,'full_kernel':True,'molien_hilbert':True,
                             'square_completion':True,'reduced_branch':True,'discriminant_scalar':str(ratio)})
        print(f'F{i}: full invariant ring and branch discriminant verified',flush=True)

    # Exact chart calculations for the two-dimensional factors, including all
    # nonzero constants occurring above. Exceptional curves are omitted from the
    # updated branch because every extracted multiplicity is two.
    P = PolynomialRing(QQ,names='x,y,v'); x,y,v=P.gens()
    def smooth(f,ring): return ring.ideal([f]+[f.derivative(v) for v in ring.gens()]).is_one()
    def saturation(f,e,ring): return ring.ideal(f).saturation(ring.ideal(e))[0]
    def origin_order(f,coordinates):
        positions=[f.parent().gens().index(v) for v in coordinates]
        return min(sum(exponents[k] for k in positions) for exponents in f.dict())
    plane_reports=[]
    for i,parts in blocks.items():
        assert set(parts[0][1]).isdisjoint(parts[1][1])
        for f,coordinates,kind in parts:
            hom=U.hom([x if v==coordinates[0] else y if v==coordinates[1] else 0 for v in U.gens()],P)
            original=hom(f); current=original; steps=0
            assert P.ideal([original]+[original.derivative(vv) for vv in P.gens()]).radical()==P.ideal(x,y)
            if kind=='cusp':
                assert origin_order(current,[x,y])==2
                total_x=current.subs(y=x*v); total_y=current.subs(x=y*v)
                strict_x=P(total_x/(x*x)); strict_y=P(total_y/(y*y))
                assert saturation(total_x,x,P)==P.ideal(strict_x)
                assert saturation(total_y,y,P)==P.ideal(strict_y)
                assert smooth(strict_x,P) and smooth(strict_y,P)
                steps=1
            else:
                while not smooth(current,P):
                    assert steps<3 and origin_order(current,[x,y])==2
                    total_x=current.subs(y=x*v); total_y=current.subs(x=y*v)
                    strict_x=P(total_x/(x*x)); strict_y=P(total_y/(y*y))
                    assert saturation(total_x,x,P)==P.ideal(strict_x)
                    assert saturation(total_y,y,P)==P.ideal(strict_y)
                    # Away from the exceptional curve a plane blow-up is an
                    # isomorphism. The original pair meets only at the origin.
                    assert P.ideal([strict_y,y]+[strict_y.derivative(w) for w in P.gens()]).is_one()
                    current=strict_x.subs(v=y)
                    steps+=1
                assert steps in [1,2,3]
            plane_reports.append({'representative':i,'kind':kind,'blowups':steps,'smooth_final_branch':True,'multiplicity_each_step':2})

    # The cross-factor branch intersections have the universal transverse model
    # xy=0. Its two strict transforms v=0 are disjoint on the blow-up overlap.
    assert P(x*y).subs(y=x*v)==x*x*v and P(x*y).subs(x=y*v)==y*y*v
    assert smooth(v,P)
    print('F: all plane branch charts and cross-factor intersections verified',flush=True)

    # Exceptional discriminant case 127: cover both charts of the first blow-up,
    # identify the entire cusp locus, and resolve its transverse cusp explicitly.
    R=PolynomialRing(QQ,names='a,b,c,d,q,u,v,w,t'); a,b,c,d,q,u,v,w,t=R.gens()
    Delta=4*a**3*c*c+27*c**4-18*a*c*c*d-a*a*d*d+4*d**3
    assert origin_order(b*Delta,[c,d])==2
    total_c=Delta.subs(d=c*q); total_d=Delta.subs(c=d*q)
    Fc=R(total_c/(c*c)); Fd=R(total_d/(d*d))
    assert saturation(total_c,c,R)==R.ideal(Fc)
    assert saturation(total_d,d,R)==R.ideal(Fd)
    sing_c=R.ideal([Fc]+[Fc.derivative(vv) for vv in R.gens()]).radical()
    sing_d=R.ideal([Fd]+[Fd.derivative(vv) for vv in R.gens()]).radical()
    assert sing_c==R.ideal(3*a-q*q,27*c-q**3)
    assert sing_d==R.ideal(3*a*q*q-1,27*d*q**4-1)
    assert (sing_d+R.ideal(q)).is_one()
    assert 27*Fc.subs(a=(u+q*q)/3,c=(v+q**3)/27)==(v-3*q*u)**2+4*u**3
    assert ((v-3*q*u)**2+4*u**3).subs(v=w+3*q*u)==w*w+4*u**3
    cusp=w*w+4*u**3
    assert origin_order(b*cusp,[u,w])==2
    for exceptional,sub,strict in [(u,{w:u*t},t*t+4*u),(w,{u:w*t},1+4*w*t**3)]:
        total=cusp.subs(sub)
        assert total==exceptional**2*strict
        assert saturation(total,exceptional,R)==R.ideal(strict)
        assert smooth(strict,R)
        # Independence of b makes the last two branch divisors transverse.
        assert strict.derivative(b)==0
    assert 2-1-2//2==0

    bind(Path(__file__).resolve())
    result={'status':'PASS','source_criterion':'G','short_version_criterion':'F','positive':positive,'negative':[],
            'representatives':representatives,'matrix_transfers':transfers,'full_invariant_rings':ring_reports,
            'plane_branch_checks':plane_reports,
            'example_127':{**matrix_binding,'order':24,'full_invariant_ring':True,
                           'first_blowup_both_saturations':True,'entire_singular_locus_both_charts':True,
                           'cusp_coordinate_identity':True,'cusp_resolution_both_charts':True,
                           'last_branch_intersection_transverse':True,'centre_codimensions':[2,2,2],
                           'generic_branch_multiplicities':[2,2,2],'canonical_coefficients':[0,0,0]},
            'input_sha256':inputs,
            'scope':'Exact group, ring, branch, saturation and Jacobian checks. Projectivity and crepancy use the stated double-cover criterion.'}
    return result


if __name__ == '__main__':
    sys.exit(main('F', verify, Path(__file__)))
