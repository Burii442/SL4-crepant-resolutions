"""Exact saturation equalities from complete homogeneous reverse-lex bases.

For a positive weighted homogeneous ideal, put the selected parameter last
in weighted degree reverse lexicographic order. Dividing every element of a
complete Groebner basis by its maximal power of that parameter gives a
Groebner basis of the full parameter saturation (Bayer's saturation argument).
Here every divided element is reduced in the original complete basis.
All zero remainders prove equality with the full saturation.

Individual nonzero scalar normalization descends the supplied ideal to QQ.
Field extension is faithfully flat. The extension e_k = t_k**r_k is finite
free; regularity of multiplication by e_k implies regularity by t_k.
"""

def verify_parameter_saturations(ideal, nu, orders, degrees,
                                 emit=lambda *a, **k: None,
                                 invariant_order=None):
    from sage.all import QQ, ZZ, PolynomialRing
    from sage.env import SINGULAR_BIN
    from pathlib import Path
    import hashlib, re, subprocess, tempfile, time
    started = time.monotonic()
    P = ideal.ring()
    K = P.base_ring()
    assert K.is_field() and K.is_exact() and K.characteristic() == 0, 'An exact field of characteristic zero is required'
    assert all(v in ZZ for v in list(orders) + list(degrees) + list(nu.list()))
    orders = list(map(int, orders))
    degrees = list(map(int, degrees))
    n, r = len(degrees), len(orders)
    assert n > 0 and r > 0 and P.ngens() == n + r
    assert nu.nrows() == r and nu.ncols() == n
    assert all(v > 0 for v in degrees + orders)
    factor = max([1] + [(sum(int(nu[k,j]) for k in range(r)) + 1) // degrees[j] + 1 for j in range(n)])
    weights = [factor * degrees[j] - sum(int(nu[k,j]) for k in range(r)) for j in range(n)] + orders
    assert all(w > 0 for w in weights)
    if invariant_order is None:
        invariant_ids = list(range(n - 1, -1, -1))
    else:
        assert all(j in ZZ for j in invariant_order)
        invariant_ids = list(map(int, invariant_order))
        assert len(invariant_ids) == n and set(invariant_ids) == set(range(n)), 'Invariant order must be a complete zero-based permutation'
    natural = ['q' + str(j + 1) for j in range(n + r)]
    Q = PolynomialRing(QQ, names=natural)
    divisors = [1] * n + orders

    def descend(f):
        if not f:
            return Q.zero()
        scale = f.leading_coefficient()
        data = {}
        for e, c in f.dict().items():
            coefficient = c / scale
            assert coefficient in QQ, 'Every monic coefficient must be rational'
            assert all(int(e[j]) % divisors[j] == 0 for j in range(n + r)), 'Every parameter exponent must descend exactly'
            exponent = tuple(int(e[j]) // divisors[j] for j in range(n + r))
            data[exponent] = QQ(coefficient)
        assert len({sum(e[j] * weights[j] for j in range(n + r)) for e in data}) <= 1, 'Positive weighted homogeneity is required for Bayer saturation'
        return Q(data)

    emit('NATIVE_BAYER_DESCENT_START', parameters=r, source_generators=len(ideal.gens()))
    polynomials = [descend(f) for f in ideal.gens()]
    source = 'option(noredefine);\n'
    variable_orders = []
    for k in range(r):
        ids = invariant_ids + [n + j for j in range(r) if j != k] + [n + k]
        variable_orders.append([j + 1 for j in ids])
        source += 'ring R' + str(k) + '=0,(' + ','.join(natural[j] for j in ids) + '),wp(' + ','.join(str(weights[j]) for j in ids) + ');\n'
        if k == 0:
            source += 'ideal sourceIdeal=' + (','.join(map(str, polynomials)) or '0') + ';\n'
        else:
            source += 'ideal sourceIdeal=imap(R0,sourceIdeal);\n'
        source += 'print("BAYER_BASIS_START_' + str(k + 1) + '");ideal basis=std(sourceIdeal);print("BAYER_BASIS_COUNT_' + str(k + 1) + '_"+string(size(basis)));\n'
        source += 'int j;int l;int minimum;intvec leading;intvec exponents;poly value;\n'
        source += 'for(j=1;j<=size(basis);j++){leading=leadexp(basis[j]);minimum=leading[nvars(basering)];for(l=1;l<=size(basis[j]);l++){exponents=leadexp(basis[j][l]);if(exponents[nvars(basering)]<minimum){print("BAYER_MINIMUM_FAILED");quit;}}value=basis[j]/' + natural[n + k] + '^minimum;if(reduce(value,basis)!=0){print("BAYER_NONZERO_' + str(k + 1) + '_"+string(j));quit;}print("BAYER_ZERO_' + str(k + 1) + '_"+string(j));}\n'
    source += 'print("ALL_BAYER_SATURATIONS_COMPLETE");quit;\n'
    program_sha = hashlib.sha256(source.encode()).hexdigest()
    emit('NATIVE_BAYER_START', parameters=r, generated_program_sha256=program_sha)
    lines, starts, counts, zeros = [], [], [], []
    with tempfile.TemporaryDirectory(prefix='exact_bayer_saturation_') as directory:
        path = Path(directory) / 'verify.sing'
        path.write_text(source)
        process = subprocess.Popen([SINGULAR_BIN, '-q', str(path)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        try:
            for line in process.stdout:
                lines.append(line)
                match = re.fullmatch(r'BAYER_BASIS_START_([0-9]+)\n?', line)
                if match:
                    starts.append(int(match[1]))
                    emit('NATIVE_BAYER_PARAMETER_START', parameter=int(match[1]))
                match = re.fullmatch(r'BAYER_BASIS_COUNT_([0-9]+)_([0-9]+)\n?', line)
                if match:
                    counts.append((int(match[1]), int(match[2])))
                    emit('NATIVE_BAYER_BASIS_COMPUTED', parameter=int(match[1]), complete_generators=int(match[2]))
                match = re.fullmatch(r'BAYER_ZERO_([0-9]+)_([0-9]+)\n?', line)
                if match:
                    zeros.append((int(match[1]), int(match[2])))
            code = process.wait()
        except BaseException:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
            raise
    output = ''.join(lines)
    assert code == 0 and '?' not in output and 'BAYER_NONZERO_' not in output and 'BAYER_MINIMUM_FAILED' not in output, 'Exact Bayer verification failed: ' + output[-2500:]
    assert starts == list(range(1, r + 1)), 'Missing or repeated parameter start'
    assert [k for k, count in counts] == list(range(1, r + 1)), 'Missing or repeated complete basis'
    assert zeros == [(k, j) for k, count in counts for j in range(1, count + 1)], 'Incomplete divided-basis generator coverage'
    assert output.splitlines().count('ALL_BAYER_SATURATIONS_COMPLETE') == 1, 'Missing or repeated full completion marker'
    result = dict(all_parameter_saturations_equal=True, characteristic=0,
                  coefficient_field='QQ', parameter_orders=orders,
                  parameters=list(range(1, r + 1)), weighted_homogeneity_checked=True,
                  variable_orders=variable_orders, source_generators=len(ideal.gens()),
                  complete_standard_basis_counts=[dict(parameter=k, generators=count) for k, count in counts],
                  checked_generator_memberships=len(zeros),
                  generated_program_sha256=program_sha,
                  native_output_sha256=hashlib.sha256(output.encode()).hexdigest())
    emit('NATIVE_ALL_BAYER_SATURATIONS_EQUAL', native_elapsed_seconds=time.monotonic() - started, **result)
    return result
