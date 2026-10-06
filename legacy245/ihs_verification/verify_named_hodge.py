"""New exact implementation of the fixed-sector formula; no stored Hodge output."""
from sage.all import ZZ, QQ, matrix, identity_matrix, MatrixGroup, PolynomialRing, vector
from pathlib import Path
from itertools import product
import json,argparse

ROOT = Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args()
catalogue = json.loads((ROOT/'catalogue.json').read_text())
R = PolynomialRing(QQ, names=('u','v'))
u,v = R.gens()
I4 = identity_matrix(ZZ,4)

def profile(index):
    G=MatrixGroup([matrix(ZZ,g) for g in catalogue[index-1]['actual_generators']])
    elements=[matrix(ZZ,g.matrix()) for g in G]
    remaining=set(tuple(g.list()) for g in elements)
    lookup={tuple(g.list()):g for g in elements}
    sectors=[];total=R.zero()
    while remaining:
        key=min(remaining);g=lookup[key]
        conjugates={tuple((h*g*h.inverse()).list()) for h in elements}
        assert conjugates<=remaining
        remaining-=conjugates
        centralizer=[h for h in elements if h*g==g*h]
        assert len(conjugates)*len(centralizer)==len(elements)
        M=g-I4;rank=M.rank();assert rank%2==0;age=rank//2
        D,U,V=M.smith_form()
        assert D==U*M*V and abs(U.det())==abs(V.det())==1
        orders=[abs(ZZ(D[i,i])) for i in range(rank)]
        assert all(d for d in orders)
        tors=list(product(*(range(d) for d in orders)))
        W=M.change_ring(QQ).right_kernel()
        base=list(W.basis())
        sector=R.zero();marks=[]
        for h in centralizer:
            action=U*h*U.inverse()
            assert all(action[i,j]==0 for i in range(rank,4) for j in range(rank))
            fixed=0
            for x in tors:
                y=action*vector(ZZ,list(x)+[0]*(4-rank))
                if all((y[i]-x[i])%orders[i]==0 for i in range(rank)):
                    fixed+=1
            hw=matrix(QQ,[W.coordinate_vector(h*b) for b in base]) if base else matrix(QQ,0,0)
            extu=(identity_matrix(R,len(base))+u*hw).det()
            extv=(identity_matrix(R,len(base))+v*hw).det()
            sector+=fixed**2*extu*extv
            marks.append(fixed)
        sector=(u*v)**age*sector/len(centralizer)
        assert all(a in ZZ for a in sector.coefficients())
        assert all(a>=0 for a in sector.coefficients())
        total+=sector
        sectors.append({'representative':list(key),'class_size':len(conjugates),'centralizer_order':len(centralizer),'age':age,'torsion_orders':list(map(int,orders)),'fixed_counts':marks,'hodge_polynomial':str(sector)})
    H=[[int(total.monomial_coefficient(u**p*v**q)) for q in range(5)] for p in range(5)]
    assert all(H[p][q]==H[q][p]==H[4-p][4-q] for p in range(5) for q in range(5))
    betti=[sum(H[p][k-p] for p in range(5) if 0<=k-p<5) for k in range(9)]
    euler=sum((-1)**k*b for k,b in enumerate(betti))
    # Separate checksum: Euler characteristic from all commuting pairs.
    # The common fixed torus has Euler zero in positive dimension; otherwise
    # Smith divisors of the stacked 8x4 matrix give its number of points.
    pair_sum=ZZ.zero();commuting_count=0
    for g in elements:
        for h in elements:
            if g*h!=h*g:
                continue
            commuting_count+=1
            stacked=(g-I4).stack(h-I4)
            if stacked.rank()!=4:
                continue
            divisors=[d for d in stacked.elementary_divisors() if d]
            assert len(divisors)==4
            fixed=ZZ.one()
            for d in divisors:
                fixed*=d
            pair_sum+=fixed**2
    assert pair_sum%len(elements)==0
    euler_pairs=pair_sum//len(elements)
    assert euler_pairs==euler
    result={'index':index,'group_order':len(elements),'hodge_matrix_rows_p_columns_q':H,'betti':betti,'euler':euler,'euler_commuting_pairs':euler_pairs,'commuting_pair_count':commuting_count,'polynomial':str(total),'sectors':sectors}
    print('INDEX',index,'order',len(elements),'HODGE',H,'BETTI',betti,'EULER',euler,flush=True)
    print('COMMUTING_PAIR_EULER',index,'pairs',commuting_count,'sum',pair_sum,'divisor',len(elements),'result',euler_pairs,'PASS',flush=True)
    return result

records=[profile(i) for i in [98,99,211,41,42,43,61,150,199,226]]
for d in records[:3]:
    expected=[[1,0,1,0,1],[0,14,0,14,0],[1,0,176,0,1],[0,14,0,14,0],[1,0,1,0,1]]
    assert d['hodge_matrix_rows_p_columns_q']==expected
    assert d['betti']==[1,0,16,0,206,0,16,0,1]
for d in records[3:6]:
    assert d['betti']==[1,0,7,8,108,8,7,0,1]
    assert d['hodge_matrix_rows_p_columns_q'][2][2]==96
for d in records[6:]:
    assert d['betti']==[1,0,23,0,276,0,23,0,1]
    assert d['hodge_matrix_rows_p_columns_q'][2][2]==232
args.output.parent.mkdir(parents=True,exist_ok=True)
args.output.write_text(json.dumps(records,indent=2,default=int)+'\n')
print('ALL_10_NAMED_HODGE_PROFILES_PASSED',flush=True)
