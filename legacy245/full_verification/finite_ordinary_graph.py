"""Complete finite-tag kernel from an already proved ordinary kernel.

In K[u,c]/(c_k^r_k-1), u_j -> u_j product(c_k^tag_kj) is an
automorphism. Apply its inverse to the entire ordinary ideal and contract
by a full elimination of the finite variables. This computes the kernel of
u_j -> F_j product(c_k^tag_kj). The ordinary ideal must be supplied by a live
complete-kernel computation; no saved claim of completeness is accepted here.
"""
from sage.all import QQ,ZZ,PolynomialRing,TermOrder
from exact_algebra import rational_model,power_subfield_models

def tagged_kernel(ordinary,tags,orders,emit=lambda *a,**k:None):
    U=ordinary.ring();K=U.base_ring();n=U.ngens()
    assert K.is_field() and K.is_exact() and K.characteristic()==0
    orders=list(orders);tags=[list(row) for row in tags]
    assert all(q in ZZ for q in orders) and all(q in ZZ for row in tags for q in row)
    orders=list(map(int,orders));tags=[list(map(int,row)) for row in tags]
    assert len(tags)==len(orders)>0 and all(len(row)==n for row in tags)
    assert all(r>0 for r in orders)
    rational=rational_model(ordinary)
    if rational is not None:
        source=rational;embedding=lambda c:K(c)
    else:
        result=power_subfield_models([ordinary])
        if result is None:
            source=ordinary;embedding=lambda c:c
        else:
            sources,embedding=result;source=sources[0]
    S=source.ring();L=S.base_ring();r=len(orders)
    auxiliary=['tag_aux'+str(k+1) for k in range(r)]
    assert set(auxiliary).isdisjoint(S.variable_names())
    G=PolynomialRing(L,auxiliary+list(S.variable_names()),order=TermOrder('lex',r)+S.term_order())
    relations=[]
    for f in source.gens():
        coefficients={}
        for e,c in f.dict().items():
            finite=tuple((-sum(int(e[j])*tags[k][j] for j in range(n)))%orders[k] for k in range(r))
            coefficients[finite+tuple(e)]=c
        relations.append(G(coefficients))
    relations += [G.gen(k)**orders[k]-1 for k in range(r)]
    emit('COMPLETE_ORDINARY_FINITE_GRAPH_START',ordinary_generators=len(source.gens()),finite_orders=orders,coefficient_field=str(L))
    eliminated=G.ideal(relations).elimination_ideal(list(G.gens()[:r]))
    output=[]
    for f in eliminated.gens():
        assert all(all(e[k]==0 for k in range(r)) for e in f.exponents())
        g=U({tuple(e[r:]):embedding(c) for e,c in f.dict().items()})
        characters={tuple(sum(int(e[j])*tags[k][j] for j in range(n))%orders[k] for k in range(r)) for e in g.exponents()}
        assert len(characters)<=1
        output.append(g)
    emit('COMPLETE_ORDINARY_FINITE_GRAPH_FINISHED',generators=len(output),full_elimination=True)
    return U.ideal(output)
