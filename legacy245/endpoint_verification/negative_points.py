"""Independent exact point/Jacobian/lattice/cone audit for six NO cases.

Coordinates and expected cones are the displayed obstruction witnesses in the manuscript.
No authors' assertions, endpoint programs, or cached results are imported.
Relations and degree matrices are read from the public normalized model inputs.
"""
from sage.all import *
from pathlib import Path
import json,time,itertools

SUPPLEMENT=Path(__file__).resolve().parent.parent
K=CyclotomicField(12,'zeta'); zeta=K.gen(); alpha=2*zeta**2-1
assert alpha**2 == -3

def point(ones,**values):
    return dict.fromkeys(ones.split(),K(1)) | {k:K(v) for k,v in values.items()}

POINTS={
138:[('P',point('u6 u14'),10,1)],
171:[('A',point('u8 u11 u20'),None,2),
     ('B',point('u11 u20 u36',e2=-QQ(7921)/8100),None,2),
     ('C',point('u5 u11 e2'),None,2),
     ('D',point('u8 u11 u21'),None,2),
     ('E',point('u11 u21 u35',e1=-QQ(7921)/8100),None,2),
     ('F',point('u5 u11 e1'),None,2)],
173:[('A',point('u2 u4 u10'),18,1),
     ('B',point('u4 u8 u9'),18,1),
     ('C',point('u7 u9 u10'),18,1),
     ('D',point('u4 u9 u14',u10=QQ(11)/6),20,1)],
178:[('A',point('u4 u6 u11 e1 e2 e5',u12=-1,u16=-1,u13=-4),13,1),
     ('B',point('u3 u5 u12 e1 e3 e4',u11=-1,u13=-1,u16=-4),13,1),
     ('C',point('u8 u10 u11 u16 e3 e4',u12=-QQ(1)/64,u13=QQ(1)/16,u18=QQ(3)/2),None,2),
     ('D',point('u7 u9 u11 e2 e5',u12=-QQ(1)/64,u13=-1,u16=-QQ(1)/16,u18=-QQ(3)/2),None,2)],
179:[('P1',point('u5 u10 e1 e2 e3',u6=-QQ(1)/4,u11=-QQ(1)/2),26,1),
     ('P2',point('u4 u5 u6 e1 e4',u9=-1,u21=QQ(16)/3,u22=9216,e5=-QQ(1)/1728),26,1),
     ('P3',point('u5 u6 u8 u12 e2',u25=-QQ(3)/4,u26=-12),26,1),
     ('P4',point('u5 u10 u25 e2 e3',u6=-QQ(1)/4,u11=-QQ(1)/2,u26=4),26,1),
     ('P5',point('u5 u6 u15 e1 e2 e3',u30=36864),26,1),
     ('P6',point('u5 u6 u10 e1 e5',u11=-QQ(1)/8,u21=9216),26,1),
     ('N0',point('u5 u6 u15 e1 e4',u22=-9216,u30=36864),27,2),
     ('N1',point('u5 u6 u10 u25 e5',u11=-QQ(1)/8,u21=9216,u26=16),27,2),
     ('N2',point('u5 u6 u12 u25 e4',u21=-QQ(64)/3,u26=16,e5=-QQ(1)/432),27,2)],
227:[('A',point('u1 u4 u8 e1',u3=alpha/3,u5=QQ(1)/18,u12=alpha/12),14,1),
     ('B',point('u1 u4 u8',u5=QQ(1)/18,u16=-QQ(1)/24),14,1),
     ('C',point('u1 u16 e2',u18=alpha/3),15,2),
     ('D',point('u4 e2 e3',u5=-QQ(1)/9,u7=alpha/3),9,2)]}

def cone(rays):
    return Polyhedron(rays=[list(v) for v in rays if any(v)],base_ring=QQ)

def poly(inequalities):
    return Polyhedron(ieqs=[[0]+list(a) for a in inequalities],base_ring=QQ)

def lattice_index(Q):
    S=Q.smith_form(transformation=False)
    return abs(prod(S[i,i] for i in range(Q.nrows())))

def conditions(idx):
    d=2 if idx==138 else 5 if idx in (178,179) else 3
    x=list(identity_matrix(QQ,d).rows())
    region=x
    if idx==138: return region,[[]]
    if idx==171:
        a,b,c=x
        return region,[[a-b,2*b-c],[c-2*b,2*a-c],[a-b,c-2*a],
                       [b-a,2*a-c],[c-2*a,2*b-c],[b-a,c-2*b]]
    if idx==173:
        a,b,c=x
        return region,[[3*a-b-c],[b-3*a-c],[c-3*a-b],
                       [b+c-3*a,3*a+c-b,3*a+b-c]]
    if idx==178:
        a,b,c,d,e=x
        region=[a,2*b-c,2*c-b,2*d-e,2*e-d]
        t=3*a;U=2*(c+d);V=2*(b+e)
        return region,[[U-t,2*U-V-t],[V-t,2*V-U-t],
                       [t-V,t-2*U+V],[t-U,t-2*V+U]]
    if idx==179:
        a,x2,x3,b,c=x;s=x2+x3
        region=[b-a,2*a-b,x2,x3,c]
        c0=a-b/2;c1=b/2
        L=(-3*a+3*b+6*c)/2;U=(3*b+6*c)/4
        M=(6*a+6*c-3*b)/4;V=(9*a-6*b)/2
        return region,[[c-c0,c1-c,U-s],[s-3*b/2,s-3*c],
                       [c0-c,L-s,M-s],[c0-c,3*b+2*c-4*a,L-s],
                       [c-c1,3*b/2-s],[s-3*a/2,3*b/2-s,s-U],
                       [s-3*b/2,3*c-s],[s-L,3*a/2-s,s-V],[s-L,V-s]]
    if idx==227:
        a,b,c=x
        return region,[[3*b-a],[a-3*b+3*c,6*b-a,3*b+3*c-a],
                       [a-6*b,6*c-a],[a-3*b-3*c]]

def verify_union(region,point_conditions):
    # For homogeneous cones, finitely many strictly negative inequalities can
    # simultaneously be rescaled to <= -1. Enumerate all disjunctive failures
    # and discard empty rational polyhedra. This includes walls and the vertex.
    live=[[[0]+list(v) for v in region]]
    counts=[]
    for constraints in point_conditions:
        new=[]
        for past in live:
            for v in constraints:
                test=past+[[-1]+list(-v)]
                P=Polyhedron(ieqs=test,base_ring=QQ)
                if not P.is_empty():new.append(test)
        live=new;counts.append(len(live))
        assert len(live)<50000
    assert not live,('uncovered region',live[:1])
    return counts

def evaluate_sparse(polynomials,p):
    n=len(p); nonzero=set(i for i,v in enumerate(p) if v)
    field=p.base_ring()
    J=[];res=[]
    for f in polynomials:
        value=field(0); grad=[field(0)]*n
        for exponent,coefficient in f.dict().items():
            support=[j for j,e in enumerate(exponent) if e]
            vanishing=[j for j in support if j not in nonzero]
            if len(vanishing)>1:continue
            if not vanishing:
                term=field(coefficient)*prod(p[j]**exponent[j] for j in support)
                value+=term
                for j in support:grad[j]+=term*exponent[j]/p[j]
            else:
                j=vanishing[0]
                if exponent[j]==1:
                    grad[j]+=field(coefficient)*prod(p[k]**exponent[k] for k in support if k!=j)
        res.append(value);J.append(grad)
    assert all(v==0 for v in res),('nonzero point equations',[(i,str(v)) for i,v in enumerate(res) if v][:5])
    return matrix(field,J)

def run(cases,OUT):
    OUT=Path(OUT); OUT.mkdir(parents=True,exist_ok=True)
    allresults=[];started=time.time()
    for idx,points in POINTS.items():
        if idx not in cases:continue
        d=json.loads((SUPPLEMENT/f'{idx}/model.json').read_text())
        field=K if idx in (138,227) else QQ
        names=d['coordinate_order'];R=PolynomialRing(field,names)
        print('parsing',idx,'equations',len(d['equations']),flush=True)
        equations=[R(s) for s in d['equations']]
        assert len(equations)==d['relation_count']
        D=matrix(ZZ,d['valuation_grading']);Q=matrix(ZZ,d['primitive_grading'])
        r=Q.nrows();n=Q.ncols()
        assert lattice_index(Q)==1
        change=matrix(QQ,D)*Q.transpose()*(matrix(QQ,Q)*Q.transpose()).inverse()
        assert change*Q==D and change.det()!=0 and all(c in ZZ for c in change.list())
        for f in equations:
            assert len({tuple(Q*vector(ZZ,e)) for e in f.exponents()})==1
        raw_index=int(lattice_index(D))
        assert raw_index=={138:1,171:2,173:9,178:18,179:72,227:3}[idx]
        region,point_conditions=conditions(idx)
        necessary=poly(region)
        omission=None
        for k in range(d['invariant_generator_count'],n):
            C=cone(-D.column(j) for j in range(n) if j!=k)
            omission=C if omission is None else omission.intersection(C)
        assert omission==necessary,('necessary region',idx)
        output=dict(case=idx,variables=n,equations=len(equations),model_dimension=d['dimension'],
                    raw_lattice_index=raw_index,full_lattice_index=1,necessary_region_exact=True,points=[],
                    coordinate_order=names,
                    region_inequalities_in_negative_valuation_coordinates=[list(map(str,v)) for v in region],
                    valuation_to_primitive_lattice_change=[list(map(str,v)) for v in change.rows()],
                    relation_multihomogeneity_checked=True)
        for position,(name,pdict,expected_rank,expected_index) in enumerate(points):
            p=vector(field,[pdict.get(v,0) for v in names])
            J=evaluate_sparse(equations,p)
            rank=int(J.rank())
            if expected_rank is not None:assert rank==expected_rank,(idx,name,'Jacobian',rank,expected_rank)
            support=[j for j,v in enumerate(p) if v]
            Qs=Q.matrix_from_columns(support)
            assert Qs.rank()==r
            index=int(lattice_index(Qs));assert index==expected_index,(idx,name,'support index',index)
            Cp=cone(-D.column(j) for j in support)
            assert Cp.intersection(necessary)==poly(region+point_conditions[position]),('point cone',idx,name)
            result=dict(name=name,equations_zero=len(equations),jacobian_rank=rank,
                expected_smooth_rank=n-d['dimension'],support_index=index,
                support=[names[j] for j in support],cone_exact=True,
                coordinates=list(map(str,p)),
                cone_inequalities_in_negative_valuation_coordinates=[list(map(str,v)) for v in point_conditions[position]])
            if index==2:
                signker=matrix(GF(2),Qs.transpose()).right_kernel()
                assert signker.dimension()==1
                t=signker.basis()[0]
                signs=[sum(int(t[i])*Q[i,j] for i in range(r))%2 for j in range(n)]
                assert all(signs[j]==0 for j in support)
                result['stabilizer_sign_exponents']=list(map(int,t))
                plus=[j for j in range(n) if signs[j]==0];minus=[j for j in range(n) if signs[j]==1]
                plusdim=len(plus)-int(J.matrix_from_columns(plus).rank())
                minusdim=len(minus)-int(J.matrix_from_columns(minus).rank())
                assert plusdim+minusdim==n-rank
                result['tangent_sign_dimensions']=[plusdim,minusdim]
                orbit=diagonal_matrix(p)*Q.transpose()
                assert orbit.rank()==r and J*orbit==0
                if idx==179 and name.startswith('N'):
                    assert (plusdim,minusdim)==(5,4)
                if idx==171:assert list(map(int,t))==[1,1,0]
            output['points'].append(result)
            print(idx,name,'all equations zero; rank',rank,'index',index,'cone exact;',round(time.time()-started,1),'s',flush=True)
        output['uncovered_branch_counts']=verify_union(region,point_conditions)
        output['complete_closed_region_covered']=True
        allresults.append(output)
        (OUT/'catalogue_cox_points_results.json').write_text(json.dumps(allresults,indent=2)+'\n')
        print(idx,'FULL POINT/GRADING/OMISSION/COVER AUDIT PASS',flush=True)
    return allresults


