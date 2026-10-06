#!/usr/bin/env python3
"""Construct exact witnesses for the four non-rational polynomial-coordinate models.

The generated JSON contains matrices, not stored assertions. Every claimed group
identity is checked before writing it. The general binding validator independently
checks these witnesses against the public catalogue and invariant polynomials.
"""
from sage.all import *
from pathlib import Path
from itertools import product
import argparse,json
ROOT=Path(__file__).resolve().parents[1]
def key(A):return tuple(A.list())
def closure(gens,K):
    I=identity_matrix(K,4);found={key(I):I};todo=[I]
    for g in todo:
        for h in gens:
            gh=g*h;k=key(gh)
            if k not in found:found[k]=gh;todo.append(gh)
    return todo

def intertwiner(actual,canonical,K):
    I=identity_matrix(K,4)
    equations=matrix(K,0,16)
    for a,b in zip(actual,canonical):equations=equations.stack(a.tensor_product(I)-I.tensor_product(b.transpose()))
    basis=[matrix(K,4,4,v) for v in equations.right_kernel().basis()]
    for P in basis:
        if P.det():return P
    for coeff in product([0,1,-1],repeat=len(basis)):
        P=sum((c*b for c,b in zip(coeff,basis)),zero_matrix(K,4))
        if P.det():return P
    return None

def encoded(M):return [[str(v) for v in row] for row in M.rows()]
def make(case,catalogue):
    order={114:8,138:12,231:5,233:5}[case];K=CyclotomicField(order,names='zeta');z=K.gen();I=identity_matrix(K,4)
    supplied=json.loads((ROOT/str(case)/'invariants.json').read_text())
    G=closure([matrix(K,g) for g in catalogue[case-1]['actual_generators']],K)
    assert len(G)==catalogue[case-1]['order']
    jr=[g for g in G if (g-I).rank()==2]
    if case in [114,138]:
        Bs=[matrix(K,[[K(x) for x in row] for row in B]) for B in supplied['junior_eigenbases']]
        juniors=[B*diagonal_matrix(K,[1,1,-1,-1])*B.inverse() for B in Bs]
        target=closure(juniors,K);assert len(target)==len(G)
        P=None
        for a in jr:
            for b in jr:
                if (a*b).trace()!=(juniors[0]*juniors[1]).trace():continue
                if len(closure([a,b],K))!=len(G):continue
                P=intertwiner([a,b],juniors,K)
                if P is not None:break
            if P is not None:break
        assert P is not None
        generators=juniors
    else:
        rotation=next(g for g in G if g!=I and g**5==I)
        reflection=next(g for g in jr if g*g==I and g*rotation*g==rotation.inverse())
        v1=(rotation-z*I).right_kernel().basis()[0]
        v2=(rotation-z*z*I).right_kernel().basis()[0]
        P=matrix(K,[v1,v2,reflection*v2,reflection*v1]).transpose()
        canonical_rotation=diagonal_matrix(K,[z,z*z,z**3,z**4]);S=matrix(K,[[0,0,0,1],[0,0,1,0],[0,1,0,0],[1,0,0,0]])
        generators=[canonical_rotation,S]+([-I] if case==233 else [])
        juniors=[S] if case==231 else [S,-S]
        target=closure(generators,K)
        assert P.inverse()*rotation*P==canonical_rotation
        assert P.inverse()*reflection*P==S
    assert P.det()!=0
    target_keys={key(g) for g in target}
    assert {key(P.inverse()*g*P) for g in G}==target_keys
    assert all(key(j) in target_keys and (j-I).rank()==2 for j in juniors)
    all_junior_keys={key(g) for g in target if (g-I).rank()==2}
    classes=[{key(g*j*g.inverse()) for g in target} for j in juniors]
    assert len(classes)==len(supplied['valuation_matrix'])
    assert set.union(*classes)==all_junior_keys
    assert all(not (classes[a]&classes[b]) for a in range(len(classes)) for b in range(a))
    result={'cyclotomic_order':order,'P':encoded(P),'convention':'P^-1 G_catalogue P = G_polynomial','group_generators_in_coordinates':[encoded(g) for g in generators],'junior_matrices':[encoded(j) for j in juniors]}
    print('SPECIAL_GROUP',case,'order',len(G),'junior_class_sizes',list(map(len,classes)),'det(P)',P.det(),flush=True)
    return result

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,default=Path(__file__).with_name('special_groups.json'));args=ap.parse_args()
    catalogue=json.loads((ROOT/'catalogue.json').read_text());records={str(i):make(i,catalogue) for i in [114,138,231,233]}
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(records,indent=2)+'\n')
    print('ALL_FOUR_SPECIAL_GROUP_WITNESSES_CONSTRUCTED',flush=True)
if __name__=='__main__':main()
