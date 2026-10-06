"""Prove parameter saturation by exact first-colon equalities.

If I:x=I, induction gives I:x^m=I for every m, and therefore I:x^infinity=I.
The complete colon is obtained either by exact ideal quotient or by proving
that no leading monomial in a fresh complete standard basis uses the parameter.
Rational field descent and parameter-power extension are faithfully flat.
Injectivity of multiplication by e_k=t_k^r_k implies injectivity by t_k.
"""
def verify_parameter_colons(ideal, nu, orders, degrees, last_parameter,
                            emit=lambda *a,**k:None, variable_order=None,
                            membership_polynomials=()):
    from sage.all import QQ,ZZ,PolynomialRing,TermOrder
    from sage.env import SINGULAR_BIN
    from pathlib import Path
    import hashlib,re,subprocess,tempfile,time
    started=time.monotonic();P=ideal.ring();K=P.base_ring()
    assert K.is_field() and K.is_exact() and K.characteristic()==0, 'An exact field of characteristic zero is required'
    assert all(v in ZZ for v in list(orders)+list(degrees)+list(nu.list()))
    assert last_parameter in ZZ, 'Last parameter must be an integer index'
    last_parameter=int(last_parameter)
    orders=list(map(int,orders));degrees=list(map(int,degrees));n=len(degrees);r=len(orders)
    assert n>0 and r>0 and P.ngens()==n+r and 0<=last_parameter<r
    assert nu.nrows()==r and nu.ncols()==n
    assert all(v>0 for v in degrees+orders)
    factor=max([1]+[(sum(int(nu[k,j]) for k in range(r))+1)//degrees[j]+1 for j in range(n)])
    weights=[factor*degrees[j]-sum(int(nu[k,j]) for k in range(r)) for j in range(n)]+orders
    assert all(w>0 for w in weights)
    if variable_order is None:
        ids=list(range(n-1,-1,-1))+[n+k for k in range(r) if k!=last_parameter]+[n+last_parameter]
    else:
        assert all(j in ZZ for j in variable_order)
        ids=list(map(int,variable_order))
        assert len(ids)==n+r and set(ids)==set(range(n+r)), 'Variable order must be a complete permutation of zero-based indices'
    # Fresh names avoid collisions with native protocol identifiers.
    names=['q'+str(j+1) for j in ids]
    ordered_weights=[weights[j] for j in ids]
    Q=PolynomialRing(QQ,names,order=TermOrder('wdegrevlex',ordered_weights))
    divisors=[1]*n+orders
    def descend(f):
        if not f:return Q.zero()
        scale=f.leading_coefficient();data={}
        for e,c in f.dict().items():
            coefficient=c/scale
            assert coefficient in QQ, 'Every monic coefficient must be rational'
            assert all(int(e[j])%divisors[j]==0 for j in range(n+r)), 'Every parameter exponent must descend exactly'
            data[tuple(int(e[j])//divisors[j] for j in ids)]=QQ(coefficient)
        return Q(data)
    emit('NATIVE_PARAMETER_COLONS_DESCENT_START',parameters=r,source_generators=len(ideal.gens()))
    source_polynomials=[descend(f) for f in ideal.gens()]
    membership_polynomials=list(membership_polynomials)
    assert all(f.parent() is P for f in membership_polynomials), 'Membership polynomials must belong to the supplied ideal ring'
    candidates=[descend(f) for f in membership_polynomials]
    source='option(noredefine);ring R=0,('+','.join(names)+'),wp('+','.join(map(str,ordered_weights))+');\n'
    source+='ideal sourceIdeal='+(','.join(map(str,source_polynomials)) or '0')+';\n'
    source+='ideal basis=std(sourceIdeal);print("PARAMETER_COLON_BASIS_"+string(size(basis)));\n'
    source+='ideal candidates='+(','.join(map(str,candidates)) or '0')+';\n'
    source+='ideal parameters='+','.join('q'+str(n+k+1) for k in range(r))+';\n'
    source+='intvec parameterPositions='+','.join(str(ids.index(n+k)+1) for k in range(r))+';\n'
    source+='int k;int j;int regular;intvec leadExponents;poly value;ideal colonIdeal;\n'
    source+='for(j=1;j<='+str(len(candidates))+';j++){value=reduce(candidates[j],basis);if(value!=0){print("PARAMETER_MEMBERSHIP_NONZERO_"+string(j));quit;}print("PARAMETER_MEMBERSHIP_ZERO_"+string(j));}\n'
    source+='for(k=1;k<='+str(r)+';k++){regular=1;for(j=1;j<=size(basis);j++){leadExponents=leadexp(basis[j]);if(leadExponents[parameterPositions[k]]!=0){regular=0;}}if(regular){colonIdeal=basis;print("PARAMETER_COLON_LEADING_"+string(k)+"_"+string(size(basis)));}else{colonIdeal=quotient(basis,ideal(parameters[k]));print("PARAMETER_COLON_QUOTIENT_"+string(k));}print("PARAMETER_COLON_COUNT_"+string(k)+"_"+string(size(colonIdeal)));for(j=1;j<=size(colonIdeal);j++){value=reduce(colonIdeal[j],basis);if(value!=0){print("PARAMETER_COLON_NONZERO_"+string(k)+"_"+string(j));quit;}print("PARAMETER_COLON_ZERO_"+string(k)+"_"+string(j));}}\n'
    source+='print("ALL_PARAMETER_COLONS_COMPLETE");quit;\n'
    program_sha=hashlib.sha256(source.encode()).hexdigest()
    emit('NATIVE_PARAMETER_COLONS_START',parameters=r,generated_program_sha256=program_sha)
    lines=[];markers=[];counts=[];basis_counts=[];leading_checks=[];quotient_checks=[];membership_checks=[]
    with tempfile.TemporaryDirectory(prefix='exact_parameter_colons_') as directory:
        path=Path(directory)/'verify.sing';path.write_text(source)
        process=subprocess.Popen([SINGULAR_BIN,'-q',str(path)],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
        try:
            for line in process.stdout:
                lines.append(line)
                match=re.fullmatch(r'PARAMETER_COLON_BASIS_([0-9]+)\n?',line)
                if match:basis_counts.append(int(match[1]))
                match=re.fullmatch(r'PARAMETER_MEMBERSHIP_ZERO_([0-9]+)\n?',line)
                if match:membership_checks.append(int(match[1]))
                match=re.fullmatch(r'PARAMETER_COLON_LEADING_([0-9]+)_([0-9]+)\n?',line)
                if match:leading_checks.append((int(match[1]),int(match[2])))
                match=re.fullmatch(r'PARAMETER_COLON_QUOTIENT_([0-9]+)\n?',line)
                if match:quotient_checks.append(int(match[1]))
                match=re.fullmatch(r'PARAMETER_COLON_COUNT_([0-9]+)_([0-9]+)\n?',line)
                if match:
                    counts.append((int(match[1]),int(match[2])))
                    emit('NATIVE_PARAMETER_COLON_COMPUTED',parameter=int(match[1]),complete_generators=int(match[2]))
                match=re.fullmatch(r'PARAMETER_COLON_ZERO_([0-9]+)_([0-9]+)\n?',line)
                if match:markers.append((int(match[1]),int(match[2])))
            code=process.wait()
        except BaseException:
            process.terminate()
            try:process.wait(timeout=5)
            except subprocess.TimeoutExpired:process.kill();process.wait()
            raise
    output=''.join(lines)
    assert code==0 and '?' not in output and 'NONZERO_' not in output, 'Exact parameter-colon verification failed: '+output[-2500:]
    assert len(basis_counts)==1, 'Missing or repeated complete basis marker'
    assert membership_checks==list(range(1,len(candidates)+1)), 'Incomplete or repeated supplied polynomial coverage'
    assert sorted([k for k,count in leading_checks]+quotient_checks)==list(range(1,r+1)), 'Incomplete or repeated proof-method coverage'
    assert all(count==basis_counts[0] for k,count in leading_checks), 'Not all complete-basis leading monomials were checked'
    assert [k for k,count in counts]==list(range(1,r+1)), 'Incomplete or repeated parameter coverage'
    assert markers==[(k,j) for k,count in counts for j in range(1,count+1)], 'Incomplete first-colon generator coverage'
    assert output.splitlines().count('ALL_PARAMETER_COLONS_COMPLETE')==1, 'Missing or repeated full completion marker'
    result=dict(all_parameter_colons_equal=True,all_parameter_saturations_equal=True,
        characteristic=0,coefficient_field='QQ',parameters=list(range(1,r+1)),
        parameter_orders=orders,variable_order=[j+1 for j in ids],source_generators=len(ideal.gens()),
        complete_standard_basis_generators=basis_counts[0],
        complete_colon_generator_counts=[dict(parameter=k,generators=count) for k,count in counts],
        leading_monomial_regularity=[dict(parameter=k,complete_basis_leading_monomials_checked=count) for k,count in leading_checks],
        explicit_ideal_quotient_parameters=quotient_checks,
        checked_generator_memberships=len(markers),generated_program_sha256=program_sha,
        checked_supplied_memberships=len(membership_checks),
        native_output_sha256=hashlib.sha256(output.encode()).hexdigest())
    emit('NATIVE_ALL_PARAMETER_COLONS_EQUAL',native_elapsed_seconds=time.monotonic()-started,**result)
    return result


def verify_initial_target_containment(ordinary_initial, full_public, nu, orders,
                                      degrees, junior, emit=lambda *a,**k:None):
    """Prove the full simultaneous containment by target regularity.

    The caller supplies a proved complete ordinary initial kernel and a proved
    full public homogenized kernel. This function freshly homogenizes every
    ordinary initial generator. It requires independence of the own parameter,
    checks every resulting generator after setting that parameter to zero, and
    proves that the target quotient is saturated at every remaining parameter.
    Saturating the raw generators therefore preserves their containment. Since
    the raw ideal and its remaining saturation extend from the ring without
    the own parameter, that last parameter introduces no further saturation.
    """
    from sage.all import PolynomialRing,ZZ,matrix
    U=ordinary_initial.ring();P=full_public.ring();n=U.ngens();r=len(orders)
    assert junior in ZZ and 0<=junior<r, 'Junior must be a zero-based parameter index'
    junior=int(junior)
    assert r>=2 and P.ngens()==n+r and nu.nrows()==r and nu.ncols()==n
    assert len(degrees)==n and U.base_ring()==P.base_ring()
    assert all(value in ZZ for value in list(nu.list())+list(orders)+list(degrees))
    assert all(value>0 for value in list(orders)+list(degrees)), 'All parameter orders and ordinary degrees must be positive'
    remaining=[k for k in range(r) if k!=junior]
    # Canonical fresh names are positional: public input names are irrelevant.
    Q=PolynomialRing(P.base_ring(),['a'+str(j+1) for j in range(n+r-1)])
    target=[]
    for f in full_public.gens():
        data={}
        for e,c in f.dict().items():
            if int(e[n+junior])==0:
                data[tuple(e[:n])+tuple(int(e[n+k]) for k in remaining)]=c
        target.append(Q(data))
    raw=[]
    for f in ordinary_initial.gens():
        if not f:
            raw.append(Q.zero());continue
        weighted={e:tuple(sum(int(e[j])*int(nu[k,j]) for j in range(n)) for k in range(r)) for e in f.dict()}
        minima=[min(v[k] for v in weighted.values()) for k in range(r)]
        assert all(v[junior]==minima[junior] for v in weighted.values()), 'Raw initial homogenization must be independent of its own parameter'
        raw.append(Q({tuple(e)+tuple(weighted[e][k]-minima[k] for k in remaining):c for e,c in f.dict().items()}))
    emit('INITIAL_TARGET_REGULARITY_START',junior=junior+1,full_initial_kernel_generators=len(raw),remaining_parameters=[k+1 for k in remaining])
    report=verify_parameter_colons(Q.ideal(target),matrix(ZZ,[list(nu.row(k)) for k in remaining]),
        [orders[k] for k in remaining],degrees,0,emit,membership_polynomials=raw)
    assert report['checked_supplied_memberships']==len(raw) and report['all_parameter_saturations_equal'] is True
    result=dict(junior=junior+1,full_initial_kernel_generators=len(raw),
        full_homogeneous_containment=True,own_parameter_independence_checked=True,
        raw_homogeneous_generators_recomputed=len(raw),remaining_parameters=[k+1 for k in remaining],
        target_colon_certificate=report,
        method='raw homogeneous containment and complete target first-colon equalities')
    emit('FULL_SIMULTANEOUS_CONTAINMENT_ZERO',**result)
    return result
