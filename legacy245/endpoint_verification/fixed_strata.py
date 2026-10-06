"""Exhaustively reconstruct scalar-fixed supports and every full ambient Jacobian.

The JSON records supply identities to check; their status strings are never
accepted as evidence. The source Cox polynomials and gradings come directly
from the public per-case model. All stratum Groebner bases are recomputed.
"""
from common import *

def run(case,out):
    start=time.monotonic();out=Path(out);out.mkdir(parents=True,exist_ok=True)
    H=HERE/'data'/str(case);conf=json.loads((H/'geometry.json').read_text())
    assert conf['model_sha256']==hashlib.sha256((SUPPLEMENT/str(case)/'model.json').read_bytes()).hexdigest()
    d,A,polys,Q,D=load_model(case);n=Q.ncols();r=Q.nrows();required=n-d['dimension']
    ss,enumeration=necessary_semistable(polys,Q,D,conf['theta_raw'])
    inv=json.loads((SUPPLEMENT/str(case)/'invariants.json').read_text());degrees=vector(ZZ,inv['polynomial_degrees']+[0]*r)
    for f in polys:assert len({degrees*vector(ZZ,e) for e in f.exponents()})==1
    M=Q.stack(matrix(ZZ,[degrees]));fixed=[s for s in ss if M[:,s].rank()==r]
    assert {tuple(j+1 for j in s) for s in fixed}=={tuple(s) for s in conf['supports']}
    print(case,'fresh exhaustive enumeration',enumeration,'fixed',len(fixed),flush=True)
    admissible=admissibility(case,polys,D,conf['theta_raw']);records=[]
    for idx,entry in enumerate(conf['supports']):
        p=H/f'fixed_{idx:03d}.json';rec=json.loads(p.read_text())
        assert rec['support']==entry and rec['required_jacobian_rank']==required
        support=[j-1 for j in entry];gauge=[j-1 for j in rec['gauge']];free=[j for j in support if j not in gauge]
        assert set(gauge)<=set(support) and Q[:,gauge].det()!=0
        names=[d['coordinate_order'][j] for j in free]+['zzloc'];assert names==rec['ring_variables']
        R=PolynomialRing(QQ,len(names),names=names,order='degrevlex');v=R.gens();images=[R.zero()]*n
        for j in gauge:images[j]=R.one()
        for j,x in zip(free,v):images[j]=x
        phi=A.hom(images,R);I=[phi(f) for f in polys]+[v[-1]*prod(v[:-1])-1]
        fresh=list(R.ideal(I).groebner_basis());GB=list(map(R,rec['stratum_groebner_basis']))
        assert list(R.ideal(GB).groebner_basis())==fresh;nf=lambda f:R(f).reduce(fresh)
        if fresh==[R.one()]:
            records.append(dict(index=idx,status='EMPTY_PASS'));print(case,idx,'EMPTY',flush=True);continue
        rows=[]
        for f in polys:
            row={j:nf(phi(f.derivative(A.gen(j)))) for j in range(n)}
            row={j:x for j,x in row.items() if x}
            if row:rows.append(row)
        for step in rec['pivots']:
            i,j=step['row'],step['column'];pivot=R(step['pivot']);inverse=R(step['inverse'])
            assert rows[i][j]==pivot and nf(pivot*inverse-1)==0
            normalized={k:nf(x*inverse) for k,x in rows[i].items()};assert normalized[j]==1;result=[]
            for k,row in enumerate(rows):
                if k==i:continue
                coefficient=row.get(j,R.zero())
                if not coefficient:result.append(row);continue
                new={l:nf(row.get(l,0)-coefficient*normalized.get(l,0)) for l in row.keys()|normalized.keys() if l!=j}
                new={l:x for l,x in new.items() if x}
                if new:result.append(new)
            rows=result
        rank=len(rec['pivots'])
        if rank==required:method='full rank by exact globally invertible pivots'
        elif case==161 and idx==20:
            mc=json.loads(p.with_name(p.stem+'_blocks.json').read_text());assert rank==required-4 and len(mc['blocks'])==4
            used_rows=set();used_cols=set()
            for block in mc['blocks']:
                rr=set(block['row_indices']);cc=set(block['columns'])
                assert not used_rows&rr and not used_cols&cc;used_rows|=rr;used_cols|=cc
                assert all(set(rows[i])<=cc for i in rr)
                entries=list(map(R,block['selected_entries']));assert len(entries)==len(block['entry_positions'])
                for f,(i,j) in zip(entries,block['entry_positions']):assert i in rr and j in cc and rows[i][j]==f
                co=list(map(R,block['unit_identity_coefficients']))
                assert len(co)==len(GB)+len(entries) and sum(c*f for c,f in zip(co,GB+entries))==1
            method='11 exact pivots plus 4 disjoint unit-ideal residual blocks'
        else:
            assert rank==required-1
            mc=json.loads(p.with_name(p.stem+'_minors.json').read_text())
            assert mc['required_residual_rank']==1
            available={x/x.lc() for row in rows for x in row.values() if x};minors=list(map(R,mc['normalized_minors']))
            assert all(f in available for f in minors)
            co=list(map(R,mc['unit_ideal_identity_coefficients']))
            assert len(co)==len(GB)+len(minors) and sum(c*f for c,f in zip(co,GB+minors))==1
            method='exact pivots and unit identity in actual residual Jacobian entries'
        records.append(dict(index=idx,status='SMOOTH_PASS',method=method,gauge_determinant=int(abs(Q[:,gauge].det()))))
        print(case,idx,'SMOOTH',rank,flush=True)
    result=dict(case=case,status='PASS',complete=True,exhaustive_support_enumeration=enumeration,
                fixed_supports=len(fixed),admissibility=admissible,records=records,seconds=time.monotonic()-start)
    (out/'certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    return result
