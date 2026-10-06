"""Exact F4 rotation invariant rings; no old log or Cox certificate is an input.

Adapted from the project's audit_rotation_ci.py. Fullness uses an injective
free module over four algebraically independent parameters and exact Molien
identity. The actual matrix representation is checked by rational conjugacy.
"""
from sage.all import (QQ,PolynomialRing,matrix,vector,identity_matrix,
                      diagonal_matrix,prod,Subsets)
from common import require,closure,molien,strings,frozen
import json


def run(source_case, record, here, out):
    R = PolynomialRing(QQ,names=['x1','x2','x3','x4'])
    x = R.gens()
    def swap(i,j):
        M = identity_matrix(QQ,4)
        M[i,i] = M[j,j] = 0
        M[i,j] = M[j,i] = 1
        return M
    f1,f2,f3 = swap(1,2),swap(2,3),diagonal_matrix(QQ,[1,1,1,-1])
    v = vector(QQ,[1,-1,-1,-1])
    f4 = identity_matrix(QQ,4)-v.column()*v.row()/2
    reflections = [f1,f2,f3,f4]
    def action(f,g):
        return R.hom(list(g*vector(R,x)),R)(f)
    sq = [y*y for y in x]
    a = sum(sq)
    b = sum(sq[i]*sq[j] for i in range(4) for j in range(i+1,4))
    c = sum(prod(sq[i] for i in indices) for indices in Subsets(range(4),3))
    d = prod(x)
    k = b-a*a/4
    c0 = c-a*b/6
    U,V = k*k+12*d*d,k**3-36*k*d*d
    delta = d*(k*k-4*d*d)
    z = prod(sq[i]-sq[j] for i in range(4) for j in range(i+1,4))
    L = delta*z
    F = [a,c0,U,V,delta,z,L]
    require([f.total_degree() for f in F] == [2,6,8,12,12,12,24], 'Wrong invariant degrees')
    require(all(f.is_homogeneous() and f != 0 for f in F),'Zero/nonhomogeneous invariant')
    I = U-3*a*c0-a**4/16
    W = V+3*a*a*U/8-a**6/128+27*c0*c0/2
    require(108*delta**2 == U**3-V**2,'First physical identity')
    require(z**2 == QQ(4)/27*(I**3-W**2),'Second physical identity')
    signs = []
    for g in reflections:
        require(all(action(f,g)==f for f in F[:4]),'A parameter is not W(F4)-invariant')
        row = []
        for f in F[4:]:
            image = action(f,g)
            require(image==f or image==-f,'Missing relative-invariant character')
            row.append(1 if image==f else -1)
        signs.append(row)
    require(signs[0][:2]==[1,-1] and signs[2][:2]==[-1,1], 'Independent reflection characters')
    require(f1*f3==f3*f1,'Character projections require commuting involutions')
    J = matrix(R,[[f.derivative(y) for y in x] for f in F[:4]])
    sample = [1,2,3,5]
    determinant = QQ(J.det()(*sample))
    require(determinant != 0,'Parameters are not proven algebraically independent')
    full = closure(reflections,1152)
    rotation_generators = [f1*f2,f1*f3,f1*f4]
    rotation = closure(rotation_generators,576)
    require(rotation=={g for g in full if g.det()==1},'Wrong determinant kernel')
    if source_case == 178:
        commutators = [g*h*g.inverse()*h.inverse() for g in rotation_generators for h in rotation_generators]
        target = closure(commutators,288)
        require(all(frozen(g*h*g.inverse()) in target for g in rotation_generators for h in target),'Commutator subgroup is not normal')
        # Exact invariance for all target generators suffices for every group element.
        require(all(action(f,g)==f for g in commutators for f in F[:6]),'Derived-group invariance failed')
        selected = F[:6]
        weights = [2,6,8,12,12,12]
        names = ['a','c0','U','V','delta','z']
    else:
        require(source_case==179,'Unsupported rotation case')
        target = rotation
        selected = F[:4]+[L]
        weights = [2,6,8,12,24]
        names = ['a','c0','U','V','L']
        require(all(action(f,g)==f for g in rotation_generators for f in selected),'Rotation-group invariance failed')
    witness = json.loads((here/'rotation_bindings.json').read_text())[str(source_case)]
    P = matrix(QQ,witness['P'])
    source = [matrix(QQ,g) for g in record['actual_generators']]
    images = [matrix(QQ,g) for g in witness['catalogue_generator_images']]
    require(P.det()!=0 and len(source)==len(images),'Invalid rational conjugacy witness')
    require(all(g*P==P*h for g,h in zip(source,images)),'Actual generator intertwining failed')
    source_group = closure(source,record['order'])
    require({frozen(P.inverse()*g*P) for g in source_group}==target,'Full actual/canonical group equality failed')
    require(closure(images,record['order'])==target,'Images fail to generate canonical group')
    T = PolynomialRing(QQ,'t')
    t = T.gen()
    K = T.fraction_field()
    denominator = (1-t**2)*(1-t**6)*(1-t**8)*(1-t**12)
    require(molien(full)==K(1)/denominator,'W(F4) parameter Molien identity')
    numerator = (1+t**12)**2 if source_case==178 else 1+t**24
    require(molien(target)==K(numerator)/denominator,'Full invariant-algebra Molien identity')
    require(molien(source_group)==molien(target),'Actual group Molien mismatch')
    S = PolynomialRing(QQ,names=names)
    aa,cc,uu,vv = S.gens()[:4]
    ii = uu-3*aa*cc-aa**4/16
    ww = vv+3*aa*aa*uu/8-aa**6/128+27*cc*cc/2
    polynomial = QQ(4)/27*(ii**3-ww**2)
    if source_case==178:
        dd,zz = S.gens()[4:]
        relations = [108*dd**2-uu**3+vv**2,zz**2-polynomial]
        basis = ['1','delta','z','delta*z']
        relation_degrees = [24,24]
        # Reduction by two monic equations gives a free module on these four
        # terms. Independent sign characters prove its physical map injective.
        require(relations[0].degree(dd)==2 and relations[0].degree(zz)==0 and
                relations[1].degree(zz)==2 and relations[1].degree(dd)==0,
                'Separate monic quadratic structure failed')
    else:
        ll = S.gens()[4]
        relations = [108*ll**2-(uu**3-vv**2)*polynomial]
        basis = ['1','L']
        relation_degrees = [48]
        require(signs[0][2]==-1 and relations[0].degree(ll)==2,'Quadratic sign-basis argument failed')
    evaluation = S.hom(selected,R)
    require(all(evaluation(f)==0 for f in relations),'Displayed relation has nonzero physical image')
    require(all(not any(sum(e)<2 for e in f.exponents()) for f in relations),'Presentation has constant or linear terms')
    require(all({sum(e[j]*weights[j] for j in range(len(weights))) for e in f.exponents()}=={degree}
                for f,degree in zip(relations,relation_degrees)),'Relation grading failed')
    hilbert = K(1)
    for degree in relation_degrees:hilbert*=1-t**degree
    for degree in weights:hilbert/=1-t**degree
    require(hilbert==molien(target),'Complete-intersection Hilbert/Molien identity failed')
    return {'method':'Exact monic free-module presentation, independent reflection characters, parameter Jacobian and complete Molien equality',
            'actual_catalogue_binding':True,'conjugator':strings(P),'actual_group_order':len(source_group),
            'canonical_full_reflection_order':len(full),'canonical_rotation_order':len(rotation),
            'full_invariant_ring':True,'complete_relation_kernel':True,'complete_intersection':True,
            'minimal_embedding':True,'embedding_dimension':len(selected),'dimension':4,
            'generator_names':names,'generator_degrees':weights,
            'physical_generators':list(map(str,selected)), 'relations':list(map(str,relations)),
            'relation_degrees':relation_degrees,'free_parameter_basis':basis,
            'parameter_jacobian_point':sample,'parameter_jacobian_determinant':str(determinant),
            'reflection_signs_delta_z_L':signs,'molien':str(molien(target)),
            'hypersurface':source_case==179}
