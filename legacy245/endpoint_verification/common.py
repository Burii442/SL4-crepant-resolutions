"""Exact shared checks. Support enumeration is an outer bound, never an existence claim."""
from sage.all import *
from pathlib import Path
import json,itertools,hashlib,time,subprocess,shutil,tempfile
HERE=Path(__file__).resolve().parent
SUPPLEMENT=HERE.parent

def load_model(case):
    d=json.loads((SUPPLEMENT/str(case)/'model.json').read_text())
    K=QQ if d['coefficient_field']=='QQ' else NumberField(PolynomialRing(QQ,'zeta')(d['cyclotomic_minpoly']),'zeta')
    A=PolynomialRing(K,names=d['coordinate_order']);F=list(map(A,d['equations']))
    Q=matrix(ZZ,d['primitive_grading']);D=matrix(ZZ,d['valuation_grading'])
    assert len(F)==d['relation_count'] and len(A.gens())==Q.ncols()
    assert lattice_index(Q)==1
    change=matrix(QQ,D)*Q.transpose()*(matrix(QQ,Q)*Q.transpose()).inverse()
    assert change*Q==D and change.det()!=0 and all(c in ZZ for c in change.list())
    for f in F:assert len({tuple(Q*vector(ZZ,e)) for e in f.exponents()})==1
    return d,A,F,Q,D

def lattice_index(Q):
    S=Q.smith_form(transformation=False)
    return abs(prod(S[i,i] for i in range(Q.nrows()))) if Q.ncols()>=Q.nrows() else ZZ(0)

def boolean_supports(F,n):
    """Compile and execute the documented exact branch-and-propagate algorithm."""
    patterns=sorted({tuple(sorted(int(sum(1<<j for j,a in enumerate(e) if a)) for e in f.exponents())) for f in F},key=len)
    compiler=shutil.which('c++') or shutil.which('g++') or shutil.which('clang++')
    assert compiler,'A C++17 compiler is required for the exhaustive support check'
    with tempfile.TemporaryDirectory(prefix='cox-supports-') as folder:
        folder=Path(folder);source=HERE/'supports.cpp';exe=folder/'enumerate';inp=folder/'masks.txt'
        subprocess.run([compiler,'-std=c++17','-O3',str(source),'-o',str(exe)],check=True,capture_output=True)
        inp.write_text(f'{n} {len(patterns)}\n'+'\n'.join(str(len(p))+' '+' '.join(map(str,p)) for p in patterns)+'\n')
        proc=subprocess.run([str(exe),str(inp)],check=True,capture_output=True,text=True)
        answer=sorted(map(int,proc.stdout.split()));assert len(answer)==len(set(answer))
        assert all(0<=b<2**n for b in answer)
        print(proc.stderr.strip(),flush=True)
    return answer,{'boolean_supports':len(answer),'cube_size':2**int(n),'pattern_count':len(patterns),'enumerator':proc.stderr.strip(),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest()}

def necessary_semistable(F,Q,D,theta):
    bits,info=boolean_supports(F,Q.ncols());theta=vector(QQ,theta);cache={};answer=[]
    for b in bits:
        s=[j for j in range(Q.ncols()) if b&(1<<j)]
        rays=tuple(sorted(set(tuple(D.column(j)) for j in s if any(D.column(j)))))
        if rays not in cache:
            C=Polyhedron(rays=[list(v) for v in rays],base_ring=QQ) if rays else Polyhedron(vertices=[[0]*D.nrows()],base_ring=QQ)
            member=C.contains(theta)
            cache[rays]=(member,C.interior_contains(theta) if member else False)
        member,interior=cache[rays]
        if not member:continue
        assert interior,('non-generic character support',s)
        assert lattice_index(Q[:,s])==1,('non-free necessary semistable support',s)
        answer.append(s)
    info.update(semistable_supports=len(answer),distinct_orbit_cones=len(cache),all_semistable_stable_and_free=True)
    return answer,info

def admissibility(case,F,D,theta):
    theta=vector(QQ,theta);r=D.nrows();n=D.ncols();nu=n-r
    assert all(x<0 for x in theta)
    for k in range(nu,n):
        C=Polyhedron(rays=[list(D.column(j)) for j in range(n) if j!=k and any(D.column(j))],base_ring=QQ)
        assert C.interior_contains(theta),('exceptional omission boundary',k)
    a=json.loads((SUPPLEMENT/str(case)/'invariants.json').read_text())
    K=NumberField(PolynomialRing(QQ,'zeta')(a['cyclotomic_minpoly']),'zeta') if a.get('cyclotomic_minpoly') else QQ;Y=PolynomialRing(K,names=a['polynomial_coordinate_order']);inv=[Y(f) for f in a['generator_polynomials']]
    assert len(inv)==nu
    # The toric231 schema records the literal generators without a separate
    # degree list; their ordinary degrees are determined directly from them.
    recorded_degrees=a.get('polynomial_degrees',[int(f.total_degree()) for f in inv])
    scalar=vector(ZZ,recorded_degrees+[0]*r)
    assert len(scalar)==n and all(t>0 for t in scalar[:nu])
    assert [f.total_degree() for f in inv]==list(recorded_degrees)
    assert all(len({scalar*vector(ZZ,e) for e in f.exponents()})==1 for f in F)
    assert D[:,nu:]==diagonal_matrix(ZZ,a['junior_orders'])
    for i,row in enumerate(a['valuation_matrix']):
        assert list(-D.row(i)[:nu])==row
        selected=sorted([f for f,v in zip(inv,row) if v>0],key=lambda f:(f.total_degree(),len(f.monomials())))
        g=selected[0]
        for f in selected[1:]:
            g=gcd(g,f)
            if g.is_constant():break
        assert g.is_constant()
        print(case,'admissibility gcd',i+1,'PASS',flush=True)
    return {'negative_raw_character':True,'strict_exceptional_omissions':r,'divisor_gcd_tests':r,'positive_scalar_homogeneity':True}
