#!/usr/bin/env sage -python
"""Complete Case 114 chart proof from the full public Cox ideal.

Enumerates every simplicial semistable open for both stated characters.
Checks one exact smooth slice and all 35 remaining candidate fixed supports.
The index-two gauges also require an empty residual fixed locus.
"""
from pathlib import Path
import argparse,hashlib,json,re,shutil,subprocess,time
from itertools import combinations
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from laurent_strata import check_support
from strata import point_values_and_jacobian,finite_stratum
from sage.all import QQ,ZZ,GF,NumberField,PolynomialRing,matrix,vector,gcd,sage_eval
HERE=Path(__file__).resolve().parent;SUPPLEMENT=HERE.parents[1]
GOOD=[(5,9)]
RETAIN={(5,9):[10,11,12,13,14],(5,12):[2,8,9,14,16],(5,13):[1,2,6,8,9,14,15],(9,14):[5,8,10,11,12,13],(12,14):[2,5,8,9,13,16]}
def require(ok,msg):
    if not ok:raise ValueError(msg)
def verify(output_dir):
    start=time.monotonic();out=Path(output_dir).resolve();out.mkdir(parents=True,exist_ok=True)
    mp=SUPPLEMENT/'114/model.json';ip=SUPPLEMENT/'114/invariants.json'
    m=json.loads(mp.read_text());a=json.loads(ip.read_text());Q=matrix(ZZ,m['primitive_grading']);D=matrix(ZZ,m['valuation_grading']);n=Q.ncols()
    require(m['case']==114 and n==16 and Q==D and Q.rank()==2,'Ordered group grading')
    require(gcd([abs(Q.matrix_from_columns(p).det()) for p in combinations(range(n),2)])==1,'Primitive class lattice')
    characters=[vector(QQ,[-2,-1]),vector(QQ,[-1,-2])];covers=[];pairs=set();determinants={}
    for chi in characters:
        for col in Q.columns():require(matrix(QQ,[col,chi]).rank()==2 or col==0 or col.dot_product(chi)<=0,'Nongeneric character')
        selected=[]
        for p in combinations(range(n),2):
            P=Q.matrix_from_columns(p)
            if P.det()==0:continue
            c=P.solve_right(chi)
            if all(v>=0 for v in c):
                require(all(v>0 for v in c),'Character on a wall')
                p=tuple(j+1 for j in p);selected.append(p);pairs.add(p);determinants[p]=int(P.det())
        require(len(selected)==26,'26 simplicial opens for each character');covers.append(selected)
    require(len(pairs)==36,'36 distinct gauges for both characters')
    K=NumberField(PolynomialRing(QQ,'zeta')(a['cyclotomic_minpoly']),'zeta')
    R=PolynomialRing(K,a['polynomial_coordinate_order']);loc=dict(zip(a['polynomial_coordinate_order'],R.gens()));loc['zeta']=K.gen()
    F=[R(sage_eval(f,locals=loc)) for f in a['generator_polynomials']]
    require(D.column(8)+D.column(12)==characters[0] and D.column(4)+D.column(12)==characters[1],'Admissible negative invariant-lift characters')
    require(all(gcd([f for f,v in zip(F,row) if v>0])==1 for row in a['valuation_matrix']),'Divisorial gcd check')
    singular=shutil.which('Singular');require(singular is not None,'Singular required')
    source='option(noredefine);\nLIB "presolve.lib";\nring Full=(0,zeta),('+','.join(m['coordinate_order'])+'),dp;\nminpoly='+m['cyclotomic_minpoly']+';\nideal FullIdeal='+',\n'.join(m['equations'])+';\n'
    (out/'full_model.sing').write_text(source);records=[]
    for pair in GOOD:
        stem='slice_'+'_'.join(map(str,pair))
        coordinate_order=[j for j in range(1,n+1) if j not in pair and j not in RETAIN[pair]]+RETAIN[pair]
        require(len(coordinate_order)==14 and len(set(coordinate_order))==14,'Slice coordinate permutation')
        index={j:f'z({q+1})' for q,j in enumerate(coordinate_order)};index.update({j:'1' for j in pair})
        images=[index[j] for j in range(1,n+1)]
        code='execute(read("full_model.sing"));\nring Slice=(0,zeta),z(1..14),dp;\nminpoly='+m['cyclotomic_minpoly']+';\nmap gauge=Full,'+','.join(images)+';\nideal I=std(gauge(FullIdeal));\n'
        code+='int eliminateCount='+str(14-len(RETAIN[pair]))+';\n'
        code+='''
"SLICE_DIMENSION";dim(I);
ideal J=mstd(I)[2];
"MINIMAL_IDEAL_EQUALITY_1";size(simplify(reduce(I,std(J)),2));
"MINIMAL_IDEAL_EQUALITY_2";size(simplify(reduce(J,I),2));
list E=elimpart(J,eliminateCount);
ideal K=std(E[1]);
map retract=Slice,E[5];
ideal certificate=std(K+E[3]);
"ELIMINATION_EQUALITY_1";size(simplify(reduce(J,certificate),2));
"ELIMINATION_EQUALITY_2";size(simplify(reduce(certificate,I),2));
"RETRACTION_CHECK";size(simplify(reduce(retract(J),K),2));
ideal inverseExpressions=E[5];
ideal doubleRetraction=retract(inverseExpressions);
ideal differences;
for(int q=1;q<=nvars(basering);q++){differences[q]=doubleRetraction[q]-inverseExpressions[q];}
"RETRACTION_IDEMPOTENT";size(simplify(differences,2));
"REMAINING_COORDINATES";E[4];
"INVERSE_EXPRESSIONS";E[5];
"REDUCED_IDEAL";K;
int eliminationFailure=0;
for(int step=1;step<=14;step++){
  list Next=elimpart(interred(K),eliminateCount);
  if(size(simplify(Next[2],2))==0){break;}
  ideal Kprevious=K;
  K=std(Next[1]);
  ideal stepCertificate=std(K+Next[3]);
  eliminationFailure=eliminationFailure+size(simplify(reduce(Kprevious,stepCertificate),2));
  eliminationFailure=eliminationFailure+size(simplify(reduce(stepCertificate,Kprevious),2));
  map stepRetraction=Slice,Next[5];
  eliminationFailure=eliminationFailure+size(simplify(reduce(stepRetraction(Kprevious),K),2));
  "STEP_INVERSE_EXPRESSIONS";Next[5];
}
"ITERATED_ELIMINATION_EQUALITIES";eliminationFailure;
"FINAL_REDUCED_IDEAL";K;
int codimension=nvars(basering)-dim(K);
"REDUCED_CODIMENSION";codimension;
ideal SingularLocus;
if(codimension==0){SingularLocus=1;}
else{
  ideal Ksmall=mstd(K)[2];
  matrix allJacobian=jacob(Ksmall);
  intvec activeColumns;
  int activeCount=0;
  for(int col=1;col<=ncols(allJacobian);col++){
    for(int row=1;row<=nrows(allJacobian);row++){
      if(allJacobian[row,col]!=0){activeCount++;activeColumns[activeCount]=col;break;}
    }
  }
  matrix Jacob[nrows(allJacobian)][activeCount];
  for(col=1;col<=activeCount;col++){
    for(row=1;row<=nrows(allJacobian);row++){Jacob[row,col]=allJacobian[row,activeColumns[col]];}
  }
  SingularLocus=K;
  int seed=7919;int attempt=0;int index;int used;int count;int k;
  matrix block[codimension][codimension];
  intvec rows;intvec columns;
  // A unit ideal from ANY subset of codimension minors proves smoothness.
  // Deterministic small minors are tried first; exhaustive minors are the fallback.
  while((SingularLocus!=1)&&(attempt<256)){
    attempt++;rows=0;columns=0;
    count=0;
    while(count<codimension){
      seed=(25173*seed+13849)%65521;index=1+seed%nrows(Jacob);used=0;
      for(k=1;k<=count;k++){if(rows[k]==index){used=1;}}
      if(used==0){count++;rows[count]=index;}
    }
    count=0;
    while(count<codimension){
      seed=(25173*seed+13849)%65521;index=1+seed%ncols(Jacob);used=0;
      for(k=1;k<=count;k++){if(columns[k]==index){used=1;}}
      if(used==0){count++;columns[count]=index;}
    }
    for(row=1;row<=codimension;row++){
      for(col=1;col<=codimension;col++){block[row,col]=Jacob[rows[row],columns[col]];}
    }
    SingularLocus=std(SingularLocus+det(block));
  }
  "SELECTED_MINOR_COUNT";attempt;
  if(SingularLocus!=1){SingularLocus=std(K+minor(Jacob,codimension));}
}
"JACOBIAN_UNIT_IDEAL";(SingularLocus==1);
'''
        expected={'SLICE_DIMENSION':4,'MINIMAL_IDEAL_EQUALITY_1':0,'MINIMAL_IDEAL_EQUALITY_2':0,'ELIMINATION_EQUALITY_1':0,'ELIMINATION_EQUALITY_2':0,'RETRACTION_CHECK':0,'RETRACTION_IDEMPOTENT':0,'JACOBIAN_UNIT_IDEAL':1,'ITERATED_ELIMINATION_EQUALITIES':0}
        fixed_variables=[]
        if abs(determinants[pair])==2:
            P=Q.matrix_from_columns([j-1 for j in pair]);kernel=matrix(GF(2),P.transpose()).right_kernel();require(kernel.dimension()==1,'Residual stabilizer must be exactly mu2')
            action=kernel.basis()[0];fixed_variables=[j+1 for j in range(n) if vector(GF(2),Q.column(j)).dot_product(action)!=0]
            code+='ideal FixedCoordinates='+','.join(index[j] for j in fixed_variables)+';\nideal FixedLocus=std(I+FixedCoordinates);\n"RESIDUAL_ACTION_FREE";(FixedLocus==1);\n'
            expected['RESIDUAL_ACTION_FREE']=1
        else:require(abs(determinants[pair])==1,'Unhandled finite gauge')
        code+='"DONE";quit;\n';script=out/(stem+'.sing');script.write_text(code);log=out/(stem+'.log');t=time.monotonic()
        print('114: starting '+stem,flush=True)
        with log.open('w') as handle:p=subprocess.run([singular,'-q',script.name],cwd=out,stdout=handle,stderr=subprocess.STDOUT)
        text=log.read_text();require(p.returncode==0 and not re.search(r'^\s*\?',text,re.M) and '\nDONE\n' in '\n'+text,stem+': Singular error or incomplete execution')
        for marker,value in expected.items():require(re.findall(r'^'+marker+r'\n(-?\d+)\s*$',text,re.M)==[str(value)],stem+': '+marker)
        records.append({'pair':list(pair),'determinant':determinants[pair],'residual_fixed_coordinates':fixed_variables,'checks':expected,'seconds':round(time.monotonic()-t,3),'log':log.name,'log_sha256':hashlib.sha256(log.read_bytes()).hexdigest()})
        (out/'progress.json').write_text(json.dumps(records,indent=2)+'\n');print('114: PASS '+stem,flush=True)
    # Scalar-fixed profiles are derived from ALL simplicial degree pairs.
    # The full ambient slice Jacobian is retained before support equations.
    polyring=PolynomialRing(K,m['coordinate_order']);Z=polyring.gens()
    relations=[polyring(f) for f in m['equations']]
    scalar_degrees=vector(QQ,[f.total_degree() for f in F]+[0,0])
    profiles={}
    for pair in pairs:
        ids=[j-1 for j in pair];lam=Q.matrix_from_columns(ids).transpose().solve_right(vector(QQ,[scalar_degrees[j] for j in ids]))
        support=tuple(j+1 for j in range(n) if lam.dot_product(Q.column(j))==scalar_degrees[j])
        profiles[tuple(lam)]=support
    require(len(profiles)==6,'Complete six scalar-fixed profiles')
    require(all(len({scalar_degrees*vector(QQ,e) for e in f.exponents()})<=1 for f in relations),'Scalar action preserves full equations')
    fixed_records=[];residual_checks=[]
    for pair in sorted(pairs):
        if abs(determinants[pair])!=2:continue
        P=Q.matrix_from_columns([j-1 for j in pair]);action=matrix(GF(2),P.transpose()).right_kernel().basis()[0]
        fixed=[Z[j] for j in range(n) if vector(GF(2),Q.column(j)).dot_product(action)!=0]
        ideal=polyring.ideal(relations+[Z[j-1]-1 for j in pair]+fixed)
        require(ideal.is_one(),'Index-two residual action is not free')
        residual_checks.append(list(pair))
    candidates=set()
    for support in profiles.values():
        for size in range(2,len(support)+1):
            for subset in combinations(support,size):
                if any(set(pair)<=set(subset) for pair in pairs):candidates.add(tuple(subset))
    require(len(candidates)==163,'Complete 163 scalar-fixed support candidates')
    monomials=[[{j+1 for j,v in enumerate(e) if v} for e in f.exponents()] for f in relations]
    rejected=[];necessary=[]
    for support in sorted(candidates):
        witness=next((i for i,terms in enumerate(monomials) if sum(term<=set(support) for term in terms)==1),None)
        if witness is None:necessary.append(support)
        else:rejected.append({'support':list(support),'single_nonzero_monomial_relation':witness+1})
    require(len(necessary)==35 and len(rejected)==128,'Exact support sieve')
    for idx,support in enumerate(necessary):
        print('114: starting fixed support '+str(idx+1)+'/35 '+str(support),flush=True)
        pair=next(pair for pair in sorted(pairs) if set(pair)<=set(support))
        zero_support=[j-1 for j in support];zero_pair=[j-1 for j in pair]
        stabilizer=gcd([abs(Q.matrix_from_columns(p).det()) for p in combinations(zero_support,2)])
        require(stabilizer==1,'Every surviving fixed support is free in the primitive class lattice')
        if {5,9}<=set(support):
            item={'status':'SMOOTH','method':'contained in the freshly proved smooth free slice (5,9)'}
        elif len(support)==2:
            point=[K(1) if j+1 in support else K(0) for j in range(n)]
            values,J=point_values_and_jacobian(relations,point)
            if any(values):item={'status':'EMPTY','method':'full equations at the unique gauged point'}
            else:
                rank=J.rank();require(rank==10,'Full ambient point Jacobian')
                item={'status':'SMOOTH','method':'exact point Jacobian','full_ambient_jacobian_rank':int(rank)}
        else:
            item=check_support(relations,Q,zero_support,zero_pair,10)
            if item['status']=='INCONCLUSIVE':item=finite_stratum(relations,zero_support,zero_pair,10)
        require(item['status'] in ['SMOOTH','EMPTY'],'Unresolved support')
        item.update(support=list(support),gauge=list(pair),primitive_stabilizer_index=int(stabilizer))
        fixed_records.append(item)
        (out/'fixed_progress.json').write_text(json.dumps(fixed_records,indent=2)+'\n')
        print('114: PASS fixed support '+str(idx+1)+' '+item['status'],flush=True)
    require(len(fixed_records)==35,'Complete fixed support verification')
    result={'status':'PASS','complete':True,'case':114,'characters':[list(map(int,c)) for c in characters],
            'simplicial_opens_per_character':list(map(len,covers)),'distinct_smooth_slices':len(GOOD),
            'fixed_profiles':[{'scalar_parameters':list(map(str,lam)),'allowed_support':list(support)} for lam,support in sorted(profiles.items())],
            'fixed_support_candidates':len(candidates),'single_monomial_exclusions':rejected,
            'fixed_supports_checked':len(fixed_records),'fixed_records':fixed_records,
            'residual_freeness_checks':residual_checks,'complete_cover':True,'admissibility_gcd_checks':2,'records':records,
            'inputs':{str(p.relative_to(SUPPLEMENT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [mp,ip,Path(__file__).resolve(),HERE/'strata.py',HERE.parent/'laurent_strata.py']},
            'seconds':round(time.monotonic()-start,3),'scope':'Both complete geometric endpoints conditional on the separately verified full Cox ring identification.'}
    (out/'certificate.json').write_text(json.dumps(result,indent=2)+'\n');print('CASE114_ALL_ENDPOINT_CHECKS_PASS',flush=True);return result
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output-dir',type=Path,required=True);args=p.parse_args();verify(args.output_dir)
