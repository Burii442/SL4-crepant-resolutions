"""Exact characteristic-zero ideal membership in a fresh native Singular ring.

All input polynomials are supplied by the live caller. A complete standard
basis is computed afresh; no saved basis or PASS assertion is accepted.
Rational descent is faithfully flat. The optional parameter substitution
z_k = t_k^r_k is finite free, hence also faithfully flat, so containment of
ideals and membership of descended polynomials are reflected exactly.
"""

def contains_all(ideal, polynomials, nu, orders, degrees, last_parameter, emit=lambda *a, **k: None):
    """Prove membership of every polynomial, or raise an exception.

    ``last_parameter`` is zero based. Invariant variables are ordered in
    reverse, followed by the other parameters and then the selected one.
    Every coefficient and every exponent is checked before field/power
    descent. Unsupported inputs fail explicitly rather than weakening the
    calculation. The caller can choose its separate general fallback.
    """
    from sage.all import QQ, ZZ, PolynomialRing, TermOrder
    from sage.env import SINGULAR_BIN
    import hashlib, re, subprocess, tempfile, time
    from pathlib import Path
    begin=time.time();P=ideal.ring();polynomials=list(polynomials)
    assert P.base_ring().is_field(), 'Native rational descent requires a coefficient field'
    assert P.base_ring().is_exact(), 'Native rational descent requires exact coefficients'
    assert P.base_ring().characteristic()==0, 'Native rational descent requires characteristic zero'
    assert all(v in ZZ for v in list(orders)+list(degrees)+list(nu.list()))
    orders=list(map(int,orders));degrees=list(map(int,degrees));n=len(degrees);r=len(orders)
    assert P.ngens()==n+r and r>0 and 0<=last_parameter<r
    assert nu.nrows()==r and nu.ncols()==n
    assert all(d>0 for d in degrees) and all(o>0 for o in orders)
    assert all(f.parent() is P for f in polynomials)
    source=list(ideal.gens())
    factor=max([1]+[(sum(int(nu[k,j]) for k in range(r))+1)//degrees[j]+1 for j in range(n)])
    weights=[factor*degrees[j]-sum(int(nu[k,j]) for k in range(r)) for j in range(n)]+orders
    assert all(w>0 for w in weights)
    ids=list(range(n-1,-1,-1))+[n+k for k in range(r) if k!=last_parameter]+[n+last_parameter]
    names=[P.variable_names()[j] for j in ids];ordered_weights=[weights[j] for j in ids]
    Q=PolynomialRing(QQ,names,order=TermOrder('wdegrevlex',ordered_weights))
    divisors=[1]*n+orders
    def descend(f):
        if not f:return Q.zero()
        # Multiplication by a nonzero field scalar does not change an ideal
        # generator or its membership. Monic normalization also handles a
        # common nonrational scalar on otherwise rational equations.
        coefficient=f.leading_coefficient()
        data={}
        for e,c in f.dict().items():
            c=c/coefficient
            assert c in QQ, 'Native membership requires rational monic coefficients'
            assert all(int(e[j])%divisors[j]==0 for j in range(n+r)), 'Parameter exponent does not descend exactly'
            target=tuple(int(e[j])//divisors[j] for j in ids)
            data[target]=QQ(c)
        return Q(data)
    emit('NATIVE_MEMBERSHIP_EXACT_DESCENT_START',source_generators=len(source),candidates=len(polynomials))
    descended_source=[descend(f) for f in source];descended_candidates=[descend(f) for f in polynomials]
    source_code='option(noredefine);ring R=0,('+','.join(names)+'),wp('+','.join(map(str,ordered_weights))+');\n'
    source_code+='ideal sourceIdeal='+(','.join(map(str,descended_source)) or '0')+';\n'
    source_code+='ideal candidates='+(','.join(map(str,descended_candidates)) or '0')+';\n'
    source_code+='ideal basis=std(sourceIdeal);print("NATIVE_MEMBERSHIP_BASIS_"+string(size(basis)));int j;poly value;\n'
    source_code+='for(j=1;j<='+str(len(polynomials))+';j++){value=reduce(candidates[j],basis);if(value!=0){print("NATIVE_MEMBERSHIP_NONZERO_"+string(j));quit;}print("NATIVE_MEMBERSHIP_ZERO_"+string(j));}\n'
    source_code+='print("NATIVE_MEMBERSHIP_COMPLETE");quit;\n'
    program_sha=hashlib.sha256(source_code.encode()).hexdigest()
    emit('NATIVE_MEMBERSHIP_BATCH_START',candidates=len(polynomials),generated_program_sha256=program_sha,parameter_power_descent=orders,last_parameter=last_parameter+1)
    lines=[];markers=[];basis_counts=[]
    with tempfile.TemporaryDirectory(prefix='exact_native_membership_') as directory:
        path=Path(directory)/'check.sing';path.write_text(source_code)
        process=subprocess.Popen([SINGULAR_BIN,'-q',str(path)],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
        for line in process.stdout:
            lines.append(line)
            match=re.fullmatch(r'NATIVE_MEMBERSHIP_ZERO_([0-9]+)\n?',line)
            if match:
                markers.append(int(match[1]))
                if len(markers)%200==0:emit('NATIVE_MEMBERSHIP_PROGRESS',count=len(markers),total=len(polynomials))
            match=re.fullmatch(r'NATIVE_MEMBERSHIP_BASIS_([0-9]+)\n?',line)
            if match:basis_counts.append(int(match[1]))
        code=process.wait()
    output=''.join(lines)
    assert code==0 and '?' not in output and 'NATIVE_MEMBERSHIP_NONZERO_' not in output, 'Native exact membership failed: '+output[-3000:]
    assert markers==list(range(1,len(polynomials)+1)), 'Incomplete or misnumbered native membership coverage'
    assert len(basis_counts)==1 and sum(line.strip()=='NATIVE_MEMBERSHIP_COMPLETE' for line in lines)==1, 'Missing native completion or basis marker'
    report={'all_contained':True,'characteristic':0,'checked':len(markers),'source_generators':len(source),'complete_standard_basis_generators':basis_counts[0],'parameter_power_descent':orders,'last_parameter':last_parameter+1,'generated_program_sha256':program_sha,'native_output_sha256':hashlib.sha256(output.encode()).hexdigest(),'elapsed_seconds':time.time()-begin}
    # The main verifier owns the event's global elapsed_seconds field.
    # Keep the local duration distinct when emitting into that event stream.
    event_report={key:value for key,value in report.items() if key!='elapsed_seconds'}
    emit('NATIVE_MEMBERSHIP_ALL_ZERO',native_elapsed_seconds=report['elapsed_seconds'],**event_report)
    return report
