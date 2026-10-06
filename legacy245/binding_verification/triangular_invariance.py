"""Exact invariance through checked monic triangular coordinate identities."""

def triangular_core(forms,relation_strings,core_size=6,emit=print):
    """Express each later F_j as a polynomial in earlier F_i, exactly.

    No elimination or supplied completeness claim is needed here. A checked
    identity F_j=P_j(F_1,...,F_{j-1}) and induction imply that invariance of the
    first core_size polynomials implies invariance of every polynomial. Each
    identity is evaluated in the actual four-variable polynomial ring.
    """
    from sage.all import PolynomialRing,QQ
    X=forms[0].parent();n=len(forms);K=X.base_ring()
    input_field=QQ if all('zeta' not in s for s in relation_strings) else K
    U=PolynomialRing(input_field,[f'u{i+1}' for i in range(n)]);u=U.gens()
    relations=[U(s) for s in relation_strings]
    # Constant-field descent is exact; it avoids arithmetic in an irrelevant
    # cyclotomic extension when every coordinate has rational coefficients.
    if all(c in QQ for f in forms for c in f.coefficients()):
        Y=PolynomialRing(QQ,X.variable_names())
        coordinates=[Y({e:QQ(c) for e,c in f.dict().items()}) for f in forms]
    else:Y=X;coordinates=forms
    evaluate=U.hom(coordinates,Y)
    checked=[]
    for j in range(core_size,n):
        candidates=[]
        for number,relation in enumerate(relations,1):
            coefficient=relation.monomial_coefficient(u[j])
            if not coefficient:continue
            rest=relation-coefficient*u[j]
            if all(all(e[k]==0 for k in range(j,n)) for e in rest.dict()):
                candidates.append((len(relation.dict()),number,relation/coefficient))
        if not candidates:raise ValueError(f'No monic triangular definition for F{j+1}')
        _,number,relation=min(candidates,key=lambda item:item[:2])
        if evaluate(relation)!=0:raise ValueError(f'False triangular identity for F{j+1}, source relation {number}')
        checked.append({'generator':j+1,'source_relation':number,'identity':str(relation)})
        emit(f'exact triangular invariance identity {len(checked)}/{n-core_size}, F{j+1}')
    return list(range(core_size)),checked

def transform_with_identities(forms,matrix,core,identities):
    """Apply a linear substitution through the already checked identities.

    Substitution is a ring homomorphism, hence preserves each proved identity.
    All returned polynomials are complete expanded coordinate expressions.
    """
    from sage.all import PolynomialRing,QQ,vector
    X=forms[0].parent();n=len(forms)
    rational=all(c in QQ for c in matrix.list()) and all(c in QQ for f in forms for c in f.coefficients())
    Y=PolynomialRing(QQ,X.variable_names()) if rational else X
    coordinates=[Y({e:QQ(c) if rational else c for e,c in f.dict().items()}) for f in forms]
    images=[sum(Y(QQ(matrix[i,j]) if rational else matrix[i,j])*Y.gen(j) for j in range(Y.ngens())) for i in range(Y.ngens())]
    transformed=[Y(0)]*n
    for j in core:transformed[j]=coordinates[j](*images)
    U=PolynomialRing(QQ,[f'u{i+1}' for i in range(n)]);u=U.gens()
    done=set(core)
    for item in identities:
        j=item['generator']-1;relation=U(item['identity'])
        if relation.monomial_coefficient(u[j])!=1:raise ValueError('The checked definition is not monic')
        rest=relation-u[j]
        if any(e[k] for e in rest.dict() for k in range(n) if k not in done):raise ValueError('The checked definitions are not triangular')
        transformed[j]=-U.hom(transformed,Y)(rest)
        done.add(j)
    if done!=set(range(n)):raise ValueError('Incomplete transformed generator list')
    return [X({e:c for e,c in f.dict().items()}) for f in transformed]
