"""An exact quotient presentation obtained from literal monic definitions.

The input ideal must already be the proved complete ordinary kernel. No saved
kernel, list of chosen core equations, or assertion of completeness is read.
Every input generator is imposed in the smaller quotient. The coefficient
ring must be an exact field of characteristic zero.
"""
def quotient_lift(value,ring):
    # Sage simplifies a quotient by the zero ideal to the covering ring.
    return value if value.parent() is ring else value.lift()

class ExactTriangularQuotient:
    def __init__(self,evaluate,core_ring,core_ideal,images):
        self.evaluate=evaluate
        self.core_ring=core_ring
        self.core_ideal=core_ideal
        self.images=images
    def __call__(self,f):return self.evaluate(f)
    def verify_zero_batch(self,polynomials,emit=lambda *a,**k:None):
        """Check every polynomial in a fresh native characteristic-zero qring.

        A qring map does not itself normalize its displayed representatives.
        Therefore every image is explicitly reduced by std(ideal(0)) in that
        quotient; a numbered zero marker is required for every input.
        """
        from sage.all import QQ
        from sage.env import SINGULAR_BIN
        import hashlib,re,subprocess,tempfile
        from pathlib import Path
        U=self.evaluate.domain();R=self.core_ring
        assert R.base_ring() is QQ, 'Native batch currently requires rational coefficients'
        polynomials=list(polynomials)
        assert all(f.parent() is U for f in polynomials)
        equations=','.join(str(f) for f in polynomials) or '0'
        core_basis=self.core_ideal.groebner_basis()
        source='option(noredefine);ring Input=0,('+','.join(U.variable_names())+'),dp;\n'
        source+='ideal relations='+equations+';\n'
        source+='ring Core=0,('+','.join(R.variable_names())+'),lp;\n'
        source+='ideal coreKernel='+(','.join(str(g) for g in core_basis) or '0')+';\n'
        source+='qring Quotient=std(coreKernel);ideal quotientZero=std(ideal(0));\n'
        source+='map substitute=Input,'+','.join(str(quotient_lift(v,R)) for v in self.images)+';\n'
        source+='int j;poly value;\n'
        source+='for(j=1;j<='+str(len(polynomials))+';j++){setring Input;poly relation=relations[j];setring Quotient;value=reduce(substitute(relation),quotientZero);if(value!=0){print("TRIANGULAR_NONZERO_"+string(j));quit;}print("TRIANGULAR_EXACT_ZERO_"+string(j));}\n'
        source+='print("TRIANGULAR_BATCH_COMPLETE");quit;\n'
        emit('TRIANGULAR_NATIVE_BATCH_START',count=len(polynomials),generated_program_sha256=hashlib.sha256(source.encode()).hexdigest())
        lines=[];markers=[]
        with tempfile.TemporaryDirectory(prefix='exact_triangular_quotient_') as work:
            path=Path(work)/'verify.sing';path.write_text(source)
            process=subprocess.Popen([SINGULAR_BIN,'-q',str(path)],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
            for line in process.stdout:
                lines.append(line)
                match=re.fullmatch(r'TRIANGULAR_EXACT_ZERO_([0-9]+)\n?',line)
                if match:
                    markers.append(int(match[1]))
                    if len(markers)%200==0:emit('TRIANGULAR_NATIVE_BATCH_PROGRESS',count=len(markers),total=len(polynomials))
            returncode=process.wait()
        output=''.join(lines)
        assert returncode==0 and '?' not in output and 'TRIANGULAR_NONZERO_' not in output, 'Native core quotient failed: '+output[-3000:]
        assert markers==list(range(1,len(polynomials)+1)) and output.splitlines().count('TRIANGULAR_BATCH_COMPLETE')==1, 'Incomplete native relation coverage: '+output[-3000:]
        emit('TRIANGULAR_NATIVE_BATCH_COMPLETE',count=len(markers),native_output_sha256=hashlib.sha256(output.encode()).hexdigest(),explicit_qring_normal_forms=True)
        return len(markers)

def triangular_quotient_map(kernel, core_indices, emit=lambda *a,**k:None):
    from sage.all import PolynomialRing
    U=kernel.ring();n=U.ngens();u=list(U.gens())
    K=U.base_ring()
    assert K.is_field() and K.is_exact() and K.characteristic()==0, 'An exact coefficient field of characteristic zero is required'
    core=list(core_indices)
    assert len(set(core))==len(core) and all(0<=j<n for j in core)
    generators=list(kernel.gens())
    known=set(core);definitions=[]
    while len(known)<n:
        choices=[]
        for j in range(n):
            if j in known:continue
            for index,f in enumerate(generators):
                coefficient=f.monomial_coefficient(u[j])
                if not coefficient:continue
                rest=f-coefficient*u[j]
                if all(all(not e[k] or k in known for k in range(n)) for e in rest.dict()):
                    choices.append((j,len(rest.dict()),index,rest/coefficient))
        assert choices, 'Complete kernel has no remaining literal monic triangular definition'
        j,_,index,rest=min(choices,key=lambda c:c[:3])
        definitions.append((j,index,rest));known.add(j)
    # Core-only relations are used immediately to prevent expression swell.
    # They are just a subset of the input, not an assumed complete core kernel.
    core_set=set(core)
    R=PolynomialRing(U.base_ring(),[U.variable_names()[j] for j in reversed(core)],order='lex')
    positions={j:len(core)-1-k for k,j in enumerate(core)}
    def core_convert(f):
        return R({tuple(e[j] for j in reversed(core)):c for e,c in f.dict().items()})
    core_only=[core_convert(f) for f in generators if all(all(not e[k] or k in core_set for k in range(n)) for e in f.dict())]
    J0=R.ideal(core_only);Q0=R.quotient(J0)
    values=[Q0(0)]*n
    for j in core:values[j]=Q0(R.gen(positions[j]))
    emit('TRIANGULAR_QUOTIENT_START',core_indices=[j+1 for j in core],initial_core_relations=len(core_only),definitions=len(definitions))
    for j,index,rest in definitions:
        values[j]=-U.hom(values,Q0)(rest)
        emit('TRIANGULAR_QUOTIENT_RECOVERY',generator=j+1,source_kernel_generator=index+1)
    evaluate0=U.hom(values,Q0)
    all_images=[quotient_lift(evaluate0(f),R) for f in generators]
    J=R.ideal(list(J0.gens())+all_images)
    Q=R.quotient(J)
    final_values=[Q(quotient_lift(v,R)) for v in values]
    evaluate=U.hom(final_values,Q)
    assert all(evaluate(f)==0 for f in generators), 'A complete ordinary kernel generator was omitted'
    metadata=dict(core_indices=[j+1 for j in core],monic_definitions=len(definitions),
        kernel_generators_imposed=len(generators),initial_core_generators=len(core_only),
        additional_nonzero_core_images=sum(bool(f) for f in all_images),
        method='literal monic elimination; all complete ordinary-kernel generators imposed in the core quotient')
    emit('TRIANGULAR_QUOTIENT_COMPLETE',**metadata)
    return ExactTriangularQuotient(evaluate,R,J,final_values),metadata
