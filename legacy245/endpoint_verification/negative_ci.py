"""Two actual points and an exact closed-cone cover for each of 140 and 243."""
from common import *
from negative_points import evaluate_sparse,cone,poly,verify_union

def run(case,out):
    d,A,F,Q,D=load_model(case);out=Path(out);out.mkdir(parents=True,exist_ok=True)
    K=QuadraticField(3,'sqrt3');sqrt3=K.gen();a,b,c,e=identity_matrix(QQ,4).rows()
    if case==140:
        pts=[[0,0,1,1,1,1,0,-27,1,0],[0,0,1,1,1,1,1,0,0,1]];v=a+e-b-c
    else:
        assert case==243
        pts=[[1,1,0,0,1,6*sqrt3,0,1,0,-4],[1,1,0,0,1,6*sqrt3,1,0,1,0]];v=a+c-b-e
    region=list(identity_matrix(QQ,4).rows());necessary=poly(region);omission=None
    for k in range(6,10):
        C=cone(-Q.column(j) for j in range(10) if j!=k)
        omission=C if omission is None else omission.intersection(C)
    assert omission==necessary
    results=[]
    for name,pt,rank,index,condition in zip(['p','q'],pts,[2,1],[2,1],[v,-v]):
        pt=vector(K,pt);J=evaluate_sparse(F,pt);assert J.rank()==rank
        support=[j for j,x in enumerate(pt) if x];assert lattice_index(Q[:,support])==index
        assert cone(-Q.column(j) for j in support).intersection(necessary)==poly(region+[condition])
        result={'point':name,'coordinates':list(map(str,pt)),'equations_zero':True,'jacobian_rank':rank,'support_index':index,'closed_support_cone_exact':True,
                'support':[d['coordinate_order'][j] for j in support],
                'cone_inequalities_in_negative_primitive_coordinates':[list(map(str,condition))]}
        if index==2:
            signs=matrix(GF(2),Q[:,support].transpose()).right_kernel()
            assert signs.dimension()==1
            character=signs.basis()[0]
            parity=[sum(int(character[i])*Q[i,j] for i in range(Q.nrows()))%2 for j in range(Q.ncols())]
            plus=[j for j in range(Q.ncols()) if parity[j]==0]
            minus=[j for j in range(Q.ncols()) if parity[j]==1]
            dimensions=[len(plus)-J[:,plus].rank(),len(minus)-J[:,minus].rank()]
            assert dimensions==[4,4]
            orbit=diagonal_matrix(pt)*Q.transpose()
            assert orbit.rank()==4 and J*orbit==0
            result.update(stabilizer_sign_exponents=list(map(int,character)),
                          tangent_sign_dimensions=list(map(int,dimensions)),
                          quotient_slice_sign_dimensions=[0,4])
        results.append(result)
    verify_union(region,[[v],[-v]])
    result={'case':case,'status':'PASS','complete':True,'points':results,'exceptional_omission_exact':True,'complete_closed_region_covered':True,
            'coordinate_order':d['coordinate_order'],'primitive_grading':[list(map(int,row)) for row in Q.rows()],
            'region_inequalities_in_negative_primitive_coordinates':[list(map(str,row)) for row in region]}
    (out/'certificate.json').write_text(json.dumps(result,indent=2)+'\n');return result
