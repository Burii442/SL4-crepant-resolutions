#!/usr/bin/env sage -python
"""Fresh Case 233 endpoint from the complete public Cox ideal.

All simplicial semistable opens are enumerated over QQ. Twelve unimodular
slices are proved smooth by exact elimination and the Jacobian criterion;
unit ideals prove that they cover every other simplicial semistable open.
No historical chart, saturation, log or saved assertion is an input.
The full Cox identification is the separate algebra verification step.
"""
from pathlib import Path
import argparse,hashlib,json,os,re,shutil,subprocess,time
from itertools import combinations
from sage.all import QQ,ZZ,PolynomialRing,matrix,vector,gcd,sage_eval
HERE=Path(__file__).resolve().parent
SUPPLEMENT=HERE.parents[1]
GOOD={(5,7),(6,7),(7,13),(5,8),(6,8),(8,14),(5,9),(9,11),(9,13),(6,10),(10,12),(10,14)}
def require(ok,msg):
    if not ok:raise ValueError(msg)
def verify(output_dir):
    started=time.monotonic();out=Path(output_dir).resolve();out.mkdir(parents=True,exist_ok=True)
    model_path=SUPPLEMENT/'233/model.json';inv_path=SUPPLEMENT/'233/invariants.json'
    m=json.loads(model_path.read_text());a=json.loads(inv_path.read_text())
    require(m['case']==233 and m['coefficient_field']=='QQ','Expected rational Case 233 model')
    Q=matrix(ZZ,m['primitive_grading']);D=matrix(ZZ,m['valuation_grading']);chi=vector(QQ,[-1,-2]);n=Q.ncols()
    require(n==16 and Q==D and Q.rank()==2,'Ordered class grading')
    require(gcd([abs(Q.matrix_from_columns(pair).det()) for pair in combinations(range(n),2)])==1,'Primitive full class lattice')
    pairs=[];determinants={}
    for j in range(n):
        col=Q.column(j)
        require(matrix(QQ,[col,chi]).rank()==2 or col==0 or col.dot_product(chi)<=0,'Character lies on a degree ray')
    for pair in combinations(range(n),2):
        P=Q.matrix_from_columns(pair)
        if P.det()==0:continue
        coefficients=P.solve_right(chi)
        if all(c>=0 for c in coefficients):
            require(all(c>0 for c in coefficients),'Character on a wall')
            pair=tuple(j+1 for j in pair);pairs.append(pair);determinants[pair]=int(P.det())
    require(len(pairs)==26 and GOOD<=set(pairs),'Complete simplicial cover enumeration')
    require(all(abs(determinants[p])==1 for p in GOOD),'Every smooth gauge must be unimodular')
    # chi is a strictly negative invariant-lift class: D_5+D_7.
    require(D.column(4)+D.column(6)==chi and all(c<0 for c in chi),'Admissibility character')
    R=PolynomialRing(QQ,a['polynomial_coordinate_order']);loc=dict(zip(a['polynomial_coordinate_order'],R.gens()))
    F=[R(sage_eval(s,locals=loc)) for s in a['generator_polynomials']]
    for row in a['valuation_matrix']:
        require(gcd([f for f,v in zip(F,row) if v>0])==1,'Divisorial gcd condition')
    singular=shutil.which('Singular')
    require(singular is not None,'Singular executable required')
    source='option(noredefine);\nLIB "presolve.lib";\nring Full=0,('+','.join(m['coordinate_order'])+'),dp;\nideal FullIdeal='+',\n'.join(m['equations'])+';\n'
    (out/'full_model.sing').write_text(source)
    records=[]
    for pair in pairs:
        label='_'.join(map(str,pair));stem=('smooth_' if pair in GOOD else 'cover_')+label
        images=[];index={};pos=0
        for j in range(1,n+1):
            if j in pair:images.append('1');index[j]='1'
            else:pos+=1;images.append(f'z({pos})');index[j]=images[-1]
        code='execute(read("full_model.sing"));\nring Slice=0,z(1..14),dp;\nmap gauge=Full,'+','.join(images)+';\nideal I=gauge(FullIdeal);\n'
        if pair in GOOD:
            code+='''
I=std(I);
"SLICE_DIMENSION";dim(I);
ideal J=mstd(I)[2];
"MINIMAL_IDEAL_EQUALITY_1";size(simplify(reduce(I,std(J)),2));
"MINIMAL_IDEAL_EQUALITY_2";size(simplify(reduce(J,I),2));
list E=elimpart(J);
ideal K=std(E[1]);
map retract=Slice,E[5];
ideal certificate=std(K+E[3]);
"ELIMINATION_EQUALITY_1";size(simplify(reduce(J,certificate),2));
"ELIMINATION_EQUALITY_2";size(simplify(reduce(certificate,I),2));
"RETRACTION_CHECK";size(simplify(reduce(retract(J),K),2));
ideal inverseExpressions=E[5];
ideal doubleRetraction=retract(inverseExpressions);
ideal retractionDifferences;
for(int q=1;q<=nvars(basering);q++){retractionDifferences[q]=doubleRetraction[q]-inverseExpressions[q];}
"RETRACTION_IDEMPOTENT";size(simplify(retractionDifferences,2));
"REMAINING_COORDINATES";E[4];
"INVERSE_EXPRESSIONS";E[5];
"REDUCED_IDEAL";K;
int codimension=nvars(basering)-dim(K);
ideal SingularLocus;
if(codimension==0){SingularLocus=1;}
else{SingularLocus=std(K+minor(jacob(K),codimension));}
"JACOBIAN_UNIT_IDEAL";(SingularLocus==1);
"DONE";quit;
'''
            expected={'SLICE_DIMENSION':4,'MINIMAL_IDEAL_EQUALITY_1':0,'MINIMAL_IDEAL_EQUALITY_2':0,'ELIMINATION_EQUALITY_1':0,'ELIMINATION_EQUALITY_2':0,'RETRACTION_CHECK':0,'RETRACTION_IDEMPOTENT':0,'JACOBIAN_UNIT_IDEAL':1}
        else:
            monomials=','.join(index[j]+'*'+index[k] for j,k in sorted(GOOD))
            code+='ideal CoverMonomials='+monomials+';\nideal Uncovered=std(I+CoverMonomials);\n"COVER_UNIT_IDEAL";(Uncovered==1);\n"DONE";quit;\n'
            expected={'COVER_UNIT_IDEAL':1}
        script=out/(stem+'.sing');script.write_text(code);log=out/(stem+'.log')
        print(f'233: starting {stem}',flush=True);t=time.monotonic()
        with log.open('w') as handle:
            p=subprocess.run([singular,'-q',script.name],cwd=out,stdout=handle,stderr=subprocess.STDOUT)
        text=log.read_text()
        require(p.returncode==0 and not re.search(r'^\s*\?',text,re.M) and '\nDONE\n' in '\n'+text,stem+': Singular error or incomplete execution')
        for marker,value in expected.items():
            found=re.findall(r'^'+marker+r'\n(-?\d+)\s*$',text,re.M)
            require(found==[str(value)],f'{stem}: {marker}: {found} != {value}')
        record={'pair':list(pair),'gauge_determinant':determinants[pair],'kind':'smooth' if pair in GOOD else 'covered','checks':expected,'seconds':round(time.monotonic()-t,3),'log':log.name,'log_sha256':hashlib.sha256(log.read_bytes()).hexdigest()};records.append(record)
        (out/'progress.json').write_text(json.dumps(records,indent=2)+'\n');print(f'233: PASS {stem}',flush=True)
    result={'status':'PASS','case':233,'character':list(map(int,chi)),'simplicial_opens':len(pairs),'smooth_unimodular_slices':len(GOOD),'complementary_unit_ideal_checks':len(pairs)-len(GOOD),'complete_cover':True,'admissibility_gcd_checks':2,'records':records,'inputs':{str(p.relative_to(SUPPLEMENT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [model_path,inv_path,Path(__file__).resolve()]},'seconds':round(time.monotonic()-started,3),'scope':'Complete geometric endpoint conditional on the separately verified full Cox ring identification; all ideals here come directly from public model.json.'}
    (out/'certificate.json').write_text(json.dumps(result,indent=2)+'\n');print('CASE233_ALL_ENDPOINT_CHECKS_PASS',flush=True);return result
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output-dir',type=Path,required=True);args=p.parse_args();verify(args.output_dir)
