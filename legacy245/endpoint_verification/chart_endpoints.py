"""Fresh chart isomorphisms, complete support covers, and Jacobian ideals."""
from common import *
from laurent_strata import check_support
from executables import singular_executable
import re

def singular_unit(R,equations,out,label,base_count=None):
    binary=singular_executable()
    source='option(noredefine);option(redSB);ring R=0,('+','.join(R.variable_names())+'),dp;'
    if base_count is None:source+='ideal bad='+','.join(map(str,equations))+';\n'
    else:
        source+='ideal I='+','.join(map(str,equations[:base_count]))+';ideal bad=I+ideal('+str(equations[-1])+');\n'
        source+='bad=bad+ideal('+','.join(map(str,equations[base_count:-1]))+');\n'
    source+='ideal B=std(bad);if(B[1]!=1){ERROR("ENDPOINT_NONUNIT");}"ENDPOINT_UNIT_PASS";quit;\n'
    source=source.replace('**','^');path=out/(label+'.sing');path.write_text(source)
    p=subprocess.run([str(binary),'-q',str(path)],capture_output=True,text=True)
    log=p.stdout+p.stderr;(out/(label+'.log')).write_text(log)
    assert p.returncode==0 and not re.search(r'^\s*\?',log,re.M) and '\nENDPOINT_UNIT_PASS\n' in '\n'+log,(label,log[-3000:])

def smooth_residual(case,index,remaining,relations,units,out):
    codim=len(remaining)-4
    assert codim>=0
    if codim==0:assert not any(relations);return {'method':'open in affine fourspace'}
    R=PolynomialRing(QQ,names=remaining+['inv']);v=R.gens();F=[R(str(f)) for f in relations if f];units=[R(str(f)) for f in units]
    if case==151:
        binary=singular_executable()
        code='LIB "primdec.lib";\nring R=0,('+','.join(remaining)+'),dp;\nideal I='+','.join(map(str,F))+';\nI=std(I);\nif(dim(I)!=4){ERROR("BAD_DIMENSION");}\nideal S=I+minor(jacob(I),'+str(codim)+');\npoly loc='+str(prod(units))+';\nS=std(sat(S,loc));\nif(S!=1){ERROR("BAD_SINGULAR_LOCUS");}\n"ENDPOINT_UNIT_PASS";quit;\n'
        path=out/f'chart_{index:02d}_smooth.sing';path.write_text(code.replace('**','^'))
        proc=subprocess.run([str(binary),'-q',str(path)],capture_output=True,text=True);log=proc.stdout+proc.stderr
        path.with_suffix('.log').write_text(log)
        assert proc.returncode==0 and not re.search(r'^\s*\?',log,re.M) and '\nENDPOINT_UNIT_PASS\n' in '\n'+log
        return {'codimension':codim,'full_localized_singular_ideal_unit':True,'fresh_dimension':4}
    J=matrix(R,[[f.derivative(x) for x in v[:-1]] for f in F])
    if case==174 and index not in [0,2,6]:
        adaptive=index in [5,10,11];file=HERE/'data/174'/f'chart_{index:02d}_{"adaptive" if adaptive else "selected_minors"}_certificate.json';c=json.loads(file.read_text())
        pairs=[(x['rows'],x['columns']) for x in c['minor_positions']] if adaptive else [([j-1 for j in x['relation_rows']],[j-1 for j in x['variable_columns']]) for x in c['selected_minors']]
        minors=[]
        for k,(rows,cols) in enumerate(pairs):
            assert len(rows)==len(cols)==codim
            m=J.matrix_from_rows_and_columns(rows,cols).det()
            if adaptive:assert m==R(c['exact_selected_minors'][k])
            minors.append(m)
    elif case==174 and index==6:
        assert codim==2;minors=J.matrix_from_rows([56,10,14,15,23,19]).minors(2)
    else:minors=J.minors(codim)
    singular_unit(R,F+minors+[v[-1]*prod(units)-1],out,f'chart_{index:02d}_smooth',base_count=len(F))
    return {'codimension':codim,'fresh_actual_jacobian_minors':len(minors),'localized_singular_ideal_unit':True}

def simple_chart(A,F,support,gauge):
    v=list(A.gens());sub={v[j]:A.one() for j in gauge};current=[f.subs(sub) for f in F];remaining=[x for j,x in enumerate(v) if j not in gauge]
    loc=prod(v[j] for j in support if j not in gauge);steps=[]
    while True:
        possible=[]
        for i,f in enumerate(current):
            if not f:continue
            for x in remaining:
                c=f.derivative(x)
                if c and c.is_constant():
                    expr=x-f/c;possible.append((len(expr.monomials()),str(x),i,x,c,expr))
        if not possible:break
        _,_,i,x,c,expr=min(possible,key=lambda a:a[:3]);assert current[i]==c*(x-expr)
        current=[f.subs({x:expr}) for f in current];loc=loc.subs({x:expr});remaining.remove(x);steps.append((str(x),str(expr)))
    assert loc
    return list(map(str,remaining)),[f for f in current if f],[loc],steps

def chart151(A,F,rec):
    v=list(A.gens());gauge=[j-1 for j in rec['pivot']];support=[j-1 for j in rec['support']]
    current=[f.subs({v[j]:A.one() for j in gauge}) for f in F];left=[x for j,x in enumerate(v) if j not in gauge];loc=prod(v[j] for j in support if j not in gauge)
    norm=lambda fs:{f/f.lc() for f in fs if f}
    for step in rec['eliminations']:
        x=A(step['variable']);f=A(step['source_polynomial']);expr=A(step['expression']);c=QQ(step['coefficient'])
        assert c and x in left and expr.degree(x)==0 and f==c*(x-expr) and f/f.lc() in norm(current)
        current=[f.subs({x:expr}) for f in current];loc=loc.subs({x:expr});left.remove(x)
    assert list(map(str,left))==rec['remaining_variables'] and norm(current)==norm(list(map(A,rec['residual_equations'])))
    assert loc==A(rec['localization']) and loc
    return list(map(str,left)),list(map(A,rec['residual_equations'])),[loc],rec['eliminations']

def rational_substitution(f,j,expression):
    """Substitute with one denominator clearing, then one final cancellation.

    Horner's polynomial identity equals den^degree * f(x=num/den), avoiding
    repeated rational gcd computations after every monomial addition.
    """
    A=f.parent();K=A.fraction_field();num=A(expression.numerator());den=A(expression.denominator())
    if not f:return K.zero()
    blocks={}
    for e,c in f.dict().items():
        k=e[j];ee=tuple(e[:j])+(0,)+tuple(e[j+1:]);blocks.setdefault(k,{})[ee]=c
    degree=max(blocks);result=A.zero()
    for k in range(degree,-1,-1):result=result*num+A(blocks.get(k,{}))*den**(degree-k)
    return K(result)/den**degree

def chart174(A,F,rec):
    v=A.gens();K=A.fraction_field();pivot=[i-1 for i in rec['unimodular_pivot']];support=[i-1 for i in rec['support']]
    unique=lambda fs:list(dict.fromkeys(fs));norm=lambda fs:unique(f/f.lc() for f in fs if f);normunit=lambda fs:unique(f/f.lc() for f in fs if f and not f.is_constant())
    phi=A.hom([A.one() if i in pivot else v[i] for i in range(len(v))],A);I=[phi(f) for f in F];units=[v[i] for i in support if i not in pivot];remaining=[i for i in range(len(v)) if i not in pivot]
    for step in rec['steps']:
        I=norm(I);assert not any(f.is_constant() for f in I) and all(units);units=normunit(units);P=prod(units,A.one());j=list(A.variable_names()).index(step['variable']);assert j in remaining
        source=A(step['source_equation']);c=A(step['unit_coefficient']);expr=K(step['expression'])
        assert source.degree(v[j])==1 and source.derivative(v[j])==c and K(source)==c*(K(v[j])-expr) and c.degree(v[j])==0
        if source not in I:
            remainder=source.reduce(I)
            if remainder:assert source.reduce(A.ideal(I).groebner_basis())==0
        h=c
        while not h.is_constant():
            divisor=gcd(h,P);assert not divisor.is_constant();h=h//divisor
        assert h
        if expr.denominator().is_constant():
            values=list(v);values[j]=A(expr);phi=A.hom(values,A);I=[f.subs({v[j]:A(expr)}) for f in I];units=[f.subs({v[j]:A(expr)}) for f in units]+[c]
        else:
            values=list(map(K,v));values[j]=expr;phi=A.hom(values,K);ii=[rational_substitution(f,j,expr) for f in I];uu=[rational_substitution(f,j,expr) for f in units];I=[A(f.numerator()) for f in ii];units=[A(f.numerator()) for f in uu]+[A(f.denominator()) for f in ii+uu if f.denominator()!=1]+[c]
        expected_units=list(map(A,step['new_nonzero_conditions']))
        assert all(units) and all(expected_units)
        # Rational arithmetic may choose different nonzero scalar multiples
        # or powers of denominators. Prove equality of the principal opens.
        if set(normunit(units))!=set(normunit(expected_units)):
            for source_units,target_units in [(units,expected_units),(expected_units,units)]:
                product=prod(target_units,A.one())
                for element in source_units:
                    while not element.is_constant():
                        divisor=gcd(element,product);assert not divisor.is_constant()
                        element=element//divisor
                    assert element
        units=expected_units;remaining.remove(j)
        print(174,'verified elimination',step['variable'],flush=True)
    assert [str(v[i]) for i in remaining]==rec['remaining_variables'] and normunit(units)==list(map(A,rec['nonzero_conditions']))
    expected=list(map(A,rec['residual_relations']))
    if set(norm(I))!=set(expected):assert list(A.ideal(I).groebner_basis())==list(A.ideal(expected).groebner_basis())
    return rec['remaining_variables'],list(map(A,rec['residual_relations'])),list(map(A,rec['nonzero_conditions'])),rec['steps']

def run(case,out):
    start=time.time();out=Path(out);out.mkdir(parents=True,exist_ok=True);d,A,F,Q,D=load_model(case)
    conf=json.loads((HERE/'data'/str(case)/'geometry.json').read_text());theta=conf['theta_raw']
    ss,enumeration=necessary_semistable(F,Q,D,theta);print(case,'support enumeration done',enumeration,flush=True)
    adm=admissibility(case,F,D,theta);records=[]
    if case==174:
        minimal=json.loads((HERE/'data/174/minimal_equations.json').read_text())
        M=list(map(A,minimal['equations']));given={f/f.lc() for f in F}
        assert all(f/f.lc() in given for f in M) # One inclusion by literal generators.
        B=PolynomialRing(QQ,names=minimal['weighted_order_names'],order=TermOrder('wdegrevlex',minimal['weighted_order_weights']))
        GB=list(B.ideal([B(str(f)) for f in M]).groebner_basis())
        assert all(B(str(f)).reduce(GB)==0 for f in F) # Reverse inclusion, fresh GB.
        print(174,'185 reduced generators equal all 589 public relations in both directions',len(GB),flush=True)
        F=M
    if case==143:
        for k in conf['smooth_coordinate_opens']:
            remaining,rels,units,steps=simple_chart(A,F,[k-1],[k-1]);assert not rels and len(remaining)==d['dimension']-1
            records.append({'coordinate_open':k,'eliminations':len(steps),'smooth_affine_slice':True})
        rest=[s for s in ss if not any(k-1 in s for k in conf['smooth_coordinate_opens'])]
        # Refine using a fresh Groebner basis of the six-zero complement.
        G=list(A.ideal(F+[A.gen(k-1) for k in conf['smooth_coordinate_opens']]).groebner_basis())
        patterns=[[int(sum(1<<j for j,a in enumerate(e) if a)) for e in f.exponents()] for f in G]
        rest=[s for s in rest if all(sum(m&sum(1<<j for j in s)==m for m in p)!=1 for p in patterns)]
        assert {tuple(j+1 for j in s) for s in rest}=={tuple(s) for s in conf['residual_supports']}
        for j,s in enumerate(rest):
            result=check_support(F,Q,s,[],Q.ncols()-d['dimension']);assert result['status'] in ['SMOOTH','EMPTY'];records.append({'residual_support':[k+1 for k in s],**result})
    elif case==222:
        inv=json.loads((SUPPLEMENT/'222/invariants.json').read_text())
        scalar=vector(ZZ,inv['polynomial_degrees']+[0]*Q.nrows())
        assert all(t>0 for t in scalar[:len(inv['polynomial_degrees'])])
        scalar_matrix=Q.stack(matrix(ZZ,[scalar]))
        fixed=[s for s in ss if scalar_matrix[:,s].rank()==Q.nrows()]
        assert len(fixed)==32
        for j,s in enumerate(fixed):
            charts=[c for c in conf['charts'] if set(k-1 for k in c['support'])<=set(s)]
            gauge=[k-1 for k in charts[0]['pivot']] if charts else list(Q[:,s].pivots())
            if not charts:gauge=[s[k] for k in gauge]
            assert len(gauge)==Q.nrows() and Q[:,gauge].det()!=0
            result=check_support(F,Q,s,gauge,Q.ncols()-d['dimension'])
            if result['status']=='INCONCLUSIVE':result=check_support(F,Q,s,[],Q.ncols()-d['dimension'])
            assert result['status'] in ['SMOOTH','EMPTY'],(j,s,result)
            records.append({'support':[k+1 for k in s],**result});print(case,j,result,flush=True)
    elif case in [151,174,206]:
        charts=conf['charts'];assert all(any(set(j-1 for j in row['support'])<=set(s) for row in charts) for s in ss)
        for j,row in enumerate(charts):
            if case==151:rec=json.loads((HERE/'data/151'/f'chart_{j:02d}.json').read_text());pivot=rec['pivot']
            elif case==174:rec=json.loads((HERE/'data/174'/f'chart_{j:02d}_localized.json').read_text());pivot=rec['unimodular_pivot']
            else:pivot=row['pivot']
            if case in [151,174]:assert rec['support']==row['support']
            assert set(pivot)<=set(row['support']) and abs(Q[:,[k-1 for k in pivot]].det())==1
            if case==151:remaining,rels,units,steps=chart151(A,F,rec)
            elif case==174:remaining,rels,units,steps=chart174(A,F,rec)
            else:remaining,rels,units,steps=simple_chart(A,F,[k-1 for k in row['support']],[k-1 for k in pivot])
            result=smooth_residual(case,j,remaining,rels,units,out);records.append({'chart':j,'eliminations':len(steps),**result});print(case,j,'CHART_PASS',flush=True)
    else:raise AssertionError(('unsupported endpoint',case))
    result={'case':case,'status':'PASS','complete':True,'support_enumeration':enumeration,'admissibility':adm,'records':records,'seconds':time.time()-start}
    if case==222:result['scalar_fixed_reduction']={'positive_invariant_degrees':True,'fixed_supports':len(fixed),'all_fixed_supports_checked':True,'semistable_supports':len(ss)}
    if case==174:result['public_ideal_equals_minimal_presentation']={'public_generators':d['relation_count'],'smaller_generators':len(M),'fresh_weighted_groebner_basis':len(GB),'both_inclusions':True}
    (out/'certificate.json').write_text(json.dumps(result,indent=2)+'\n');return result
