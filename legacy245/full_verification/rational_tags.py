"""Recover independent finite characters as ratios of equal physical forms.

If the character differences of two equal-form ratios generate the finite
character group, inverting their denominators reconstructs the entire finite
coefficient algebra. Untwisting a complete ordinary kernel and adjoining the
ratio-order equations gives the complete localized tagged kernel. Saturation
contracts it, since every denominator is nonzero in every target component.
"""
from sage.all import *
from exact_algebra import saturation_basis

def recovered_tag_kernel(ordinary,forms,U,tags,finite_orders,pairs,degrees,emit):
    n=U.ngens();u=list(U.gens());s=len(finite_orders)
    assert len(pairs)==s and len(set(finite_orders))==1
    order=finite_orders[0];assert is_prime(order)
    B=matrix(GF(order),[[tags[k][p]-tags[k][q] for p,q in pairs] for k in range(s)])
    assert B.is_invertible(),'Ratio characters do not generate the finite character group'
    assert all(forms[p]==forms[q] and forms[q]!=0 for p,q in pairs)
    inverse=B.inverse()
    powers=[list(map(int,inverse*vector(GF(order),[tags[k][j] for k in range(s)]))) for j in range(n)]
    relations=[]
    for f in ordinary.gens():
        terms={}
        for e,c in f.dict().items():
            v=list(e)
            for b,(p,q) in enumerate(pairs):
                # In the localized presentation each recovered ratio has
                # order ``order`` (the equations below are adjoined).
                # Reducing an exponent modulo that order changes a Laurent
                # relation only by multiples of these order equations.
                # This preserves the full localized ideal while avoiding
                # unnecessarily large denominator powers.
                power=sum(int(e[j])*powers[j][b] for j in range(n))%order
                v[p]-=power;v[q]+=power
            v=tuple(v);terms[v]=terms.get(v,0)+c
        minima=[min(0,min(e[j] for e in terms)) for j in range(n)]
        relations.append(U({tuple(e[j]-minima[j] for j in range(n)):c for e,c in terms.items()}))
    relations += [u[p]**order-u[q]**order for p,q in pairs]
    # Target u_j has finite character tags[:,j]. Each relation is checked
    # before computing the exact contraction to the original polynomial ring.
    for f in relations:
        assert len({tuple(sum(e[j]*tags[k][j] for j in range(n))%finite_orders[k] for k in range(s)) for e in f.exponents()})<=1
    emit('RATIONAL_CHARACTER_RECOVERY_PROVED',pairs=[[p+1,q+1] for p,q in pairs],relations=len(relations))
    I=U.ideal(relations);denominators=sorted(set(q for _,q in pairs))
    # It is safe to allow divisions by ALL final denominators at every step.
    # Write T=I:S^infinity and P_k for the first k denominator variables.
    # Inductively I:P_(k-1)^infinity <= I_(k-1) <= T. satstd produces
    # I_(k-1) <= J <= T, and Bayer gives I_k=J:t_k^infinity, hence
    # I:P_k^infinity <= I_k <= T. After all variables the lower bound is T.
    # This sandwich does not assume preservation of intermediate saturations.
    for q in denominators:
        ids=[j for j in range(n) if j!=q]+[q]
        R=PolynomialRing(U.base_ring(),[str(u[j]) for j in ids],order=TermOrder('wdegrevlex',[degrees[j] for j in ids]))
        gens=[R({tuple(e[j] for j in ids):c for e,c in f.dict().items()}) for f in I.gens()]
        # All divisions below concern the final localization denominators.
        variables=[R.gen(ids.index(j)) for j in denominators]
        emit('RATIONAL_CHARACTER_CONTRACTION_START',variable=q+1,inputs=len(gens))
        gb=saturation_basis(R.ideal(gens),variables,emit)
        inv=[ids.index(j) for j in range(n)];result=[]
        for f in gb:
            low=min(e[n-1] for e in f.exponents())
            assert f.leading_monomial().exponents()[0][n-1]==low
            result.append(U({tuple(e[inv[j]]-(low if j==q else 0) for j in range(n)):c for e,c in f.dict().items()}))
        I=U.ideal(result)
        emit('RATIONAL_CHARACTER_CONTRACTION_COMPLETE',variable=q+1,generators=len(result))
    return I
