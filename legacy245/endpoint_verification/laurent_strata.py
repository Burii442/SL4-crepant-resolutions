"""Fresh full-Jacobian rank calculations on exact support strata."""
from common import *

def check_support(F,Q,support,gauge,required):
    n=Q.ncols();support=list(support);gauge=list(gauge);free=[j for j in support if j not in gauge]
    assert len(gauge)==0 or Q[:,gauge].det()!=0
    if not free:
        point=[F[0].base_ring()(1 if j in gauge else 0) for j in range(n)]
        if any(f(*point) for f in F):return {'status':'EMPTY','unit_pivot_rank':0}
        rank=int(matrix(F[0].base_ring(),[[f.derivative(x)(*point) for x in f.parent().gens()] for f in F]).rank())
        return {'status':'SMOOTH' if rank>=required else 'INCONCLUSIVE','unit_pivot_rank':rank}
    L=LaurentPolynomialRing(F[0].base_ring(),len(free),names=[f'z{j+1}' for j in free]);off=set(range(n))-set(support)
    def specialize(f):
        terms={}
        for e,c in f.dict().items():
            if any(e[j] for j in off):continue
            ef=tuple(e[j] for j in free);terms[ef]=terms.get(ef,0)+c
        return L(terms)
    variables=F[0].parent().gens()
    # Derivative always taken in the full ambient space, before specialization.
    rows=[[specialize(f.derivative(v)) for j,v in enumerate(variables)] for f in F]
    rows=[row for row in rows if any(row)];columns=list(reversed(range(n)));rank=0
    while rank<required:
        found=next(((i,j) for i,row in enumerate(rows) for j in columns if row[j] and len(row[j].dict())==1),None)
        if found is None:break
        i,j=found;row=rows.pop(i);unit=row[j];row=[v/unit for v in row];assert row[j]==1;columns.remove(j)
        for other in rows:
            factor=other[j]
            if factor:
                for k in columns:other[k]-=factor*row[k]
                other[j]=L.zero()
        rows=[row for row in rows if any(row[k] for k in columns)];rank+=1
    if rank==required:return {'status':'SMOOTH','unit_pivot_rank':rank}
    R=PolynomialRing(F[0].base_ring(),len(free),names=[f'z{j+1}' for j in free]);rv=R.gens()
    def clear(f):
        if not f:return R.zero()
        terms=f.dict();minima=[min(0,min(e[j] for e in terms)) for j in range(len(free))]
        return R({tuple(e[j]-minima[j] for j in range(len(free))):c for e,c in terms.items()})
    equations=[clear(specialize(f)) for f in F]
    def localized_unit(polys):
        # First reduce the equations in the smaller polynomial ring, then
        # saturate by the Laurent units. This is the same localization and
        # avoids an initially high-degree inverse-product equation.
        GB=list(R.ideal(polys).groebner_basis(algorithm='libsingular:std'))
        if GB==[R.one()]:return True
        return R.ideal(GB).saturation(R.ideal(prod(rv)))[0].is_one()
    print('residual Laurent rank',rank,'free variables',len(free),flush=True)
    if rank==required-1:
        entries=[clear(row[j]) for row in rows for j in columns if row[j]]
        if localized_unit(equations+entries):return {'status':'SMOOTH','unit_pivot_rank':rank,'residual_unit_ideal':True}
    if localized_unit(equations):return {'status':'EMPTY','unit_pivot_rank':rank}
    return {'status':'INCONCLUSIVE','unit_pivot_rank':rank}
