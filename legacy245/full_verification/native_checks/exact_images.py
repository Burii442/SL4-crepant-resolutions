"""Fresh exact polynomial images in characteristic zero.

This is a transport for polynomial homomorphisms, not a completeness test.
The caller must separately prove that its ordinary kernel is complete before
using zero images to identify membership in that kernel. No saved values,
modular reductions, or numerical evaluations enter this calculation.
"""
def verify_zero_images(polynomials, images, emit=lambda *a, **k: None):
    from sage.all import QQ, PolynomialRing
    from sage.env import SINGULAR_BIN
    import hashlib, re, subprocess, tempfile
    from pathlib import Path
    polynomials=list(polynomials);images=list(images)
    assert images and polynomials, 'Nonempty typed inputs are required'
    U=polynomials[0].parent();X=images[0].parent()
    assert U.ngens()==len(images), 'A polynomial image is missing'
    assert all(f.parent() is U for f in polynomials)
    assert all(f.parent() is X for f in images)
    for R in [U,X]:
        K=R.base_ring()
        assert K.is_field() and K.is_exact() and K.characteristic()==0, 'An exact field of characteristic zero is required'
    assert all(c in QQ for f in polynomials+images for c in f.coefficients()), 'This native image transport requires rational coefficients'
    # Rename variables positionally, avoiding collisions with protocol names
    # and transporting exact coefficient dictionaries rather than raw input.
    V=PolynomialRing(QQ,['source'+str(j+1) for j in range(U.ngens())])
    Y=PolynomialRing(QQ,['target'+str(j+1) for j in range(X.ngens())])
    def exponent_tuple(e):
        return tuple(e) if hasattr(e,'__iter__') else (int(e),)
    def convert(f,R):
        if R.ngens()==1:
            return R(sum(QQ(c)*R.gen()**exponent_tuple(e)[0] for e,c in f.dict().items()))
        return R({exponent_tuple(e):QQ(c) for e,c in f.dict().items()})
    inputs=[convert(f,V) for f in polynomials]
    targets=[convert(f,Y) for f in images]
    source='option(noredefine);ring Input=0,('+','.join(V.variable_names())+'),dp;\n'
    source+='ideal relations='+','.join(map(str,inputs))+';\n'
    source+='ring Physical=0,('+','.join(Y.variable_names())+'),dp;\n'
    source+='map physical=Input,'+','.join(map(str,targets))+';\n'
    source+='int j;poly value;\n'
    source+='for(j=1;j<='+str(len(inputs))+';j++){setring Input;poly relation=relations[j];setring Physical;value=physical(relation);if(value!=0){print("PHYSICAL_NONZERO_"+string(j));quit;}print("PHYSICAL_EXACT_ZERO_"+string(j));}\n'
    source+='print("PHYSICAL_BATCH_COMPLETE");quit;\n'
    emit('NATIVE_EXACT_IMAGES_START',count=len(inputs),characteristic=0,generated_program_sha256=hashlib.sha256(source.encode()).hexdigest())
    lines=[];markers=[]
    with tempfile.TemporaryDirectory(prefix='exact_polynomial_images_') as work:
        path=Path(work)/'verify.sing';path.write_text(source)
        process=subprocess.Popen([SINGULAR_BIN,'-q',str(path)],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
        try:
            for line in process.stdout:
                lines.append(line)
                match=re.fullmatch(r'PHYSICAL_EXACT_ZERO_([0-9]+)\n?',line)
                if match:
                    markers.append(int(match[1]))
                    if len(markers)%100==0:emit('NATIVE_EXACT_IMAGES_PROGRESS',count=len(markers),total=len(inputs))
            returncode=process.wait()
        except BaseException:
            process.terminate()
            try:process.wait(timeout=5)
            except subprocess.TimeoutExpired:process.kill();process.wait()
            raise
    output=''.join(lines)
    assert returncode==0 and '?' not in output and 'PHYSICAL_NONZERO_' not in output, 'Exact native polynomial image failed: '+output[-3000:]
    assert markers==list(range(1,len(inputs)+1)), 'Incomplete exact image coverage'
    assert output.splitlines().count('PHYSICAL_BATCH_COMPLETE')==1, 'Missing or repeated exact image completion marker'
    emit('NATIVE_EXACT_IMAGES_COMPLETE',count=len(markers),characteristic=0,native_output_sha256=hashlib.sha256(output.encode()).hexdigest())
    return {'all_zero':True,'checked':len(markers),'characteristic':0,'coefficient_field':'QQ'}
