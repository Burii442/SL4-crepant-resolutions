#!/usr/bin/env sage -python
"""Exact modular rank certificate for invariant-algebra generation.

Nonzero minors modulo a good prime prove lower bounds on characteristic-zero
ranks. Together with exact invariance and the actual-representation binding,
matching Molien dimensions through the Noether bound proves generation.
The other two hypotheses are deliberately not inferred by this program.
"""
from sage.all import *
from pathlib import Path
import argparse,json,hashlib,time
ap=argparse.ArgumentParser(description=__doc__)
ap.add_argument('--case',type=int,required=True)
ap.add_argument('--output-dir',type=Path,required=True)
ap.add_argument('--prime',type=int,default=1009)
ap.add_argument('--groebner-algorithm',choices=['std','slimgb'],default='slimgb')
ap.add_argument('--hilbert-field',choices=['modular','rational'],default='modular')
ap.add_argument('--generation-bound',choices=['auto','noether','parameters'],default='auto')
ap.add_argument('--hilbert-method',choices=['auto','full','artinian'],default='auto')
ap.add_argument('--kernel-hilbert',action='store_true',help='Also compute the weighted Hilbert series of the public ordinary relation ideal.')
aargs=ap.parse_args(); root=Path(__file__).resolve().parent.parent;out=aargs.output_dir;out.mkdir(parents=True,exist_ok=True)
start=time.time()
def say(event,**kw):print(json.dumps(dict(event=event,case=aargs.case,elapsed_seconds=float(time.time()-start),**kw)),flush=True)
a=json.loads((root/str(aargs.case)/'invariants.json').read_text())
c=next(x for x in json.loads((root/'catalogue.json').read_text()) if x['index']==aargs.case)
hashes={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [root/str(aargs.case)/'invariants.json',root/'catalogue.json',Path(__file__).resolve()]}
gens=[matrix(QQ,g) for g in c['actual_generators']]
from sage.libs.gap.libgap import libgap
H=libgap.Group(gens).DerivedSubgroup()
elements=[matrix(QQ,h.sage()) for h in H.Elements()];bound=len(elements)
T=PolynomialRing(QQ,'t');t=T.gen(); identity=identity_matrix(T,4)
molien=sum(1/(identity-t*matrix(T,h)).det() for h in elements)/bound
coeffs=(PowerSeriesRing(QQ,'t',default_prec=bound+1)(molien)).list();coeffs += [0]*(bound+1-len(coeffs))
say('CATALOGUE_COMMUTANT_MOLIEN',derived_order=bound,molien=str(molien))
p=aargs.prime;assert is_prime(p)
Fp=GF(p);minpoly=a['cyclotomic_minpoly']
if minpoly:
 L=PolynomialRing(QQ,'zeta');K=NumberField(L(minpoly),'zeta')
 modpoly=PolynomialRing(Fp,'zeta')(minpoly)
 roots=modpoly.roots(multiplicities=False);assert roots,'Prime does not split the coefficient field; choose another --prime.'
 z=roots[0]
 def residue(q):
  q=K(q); ans=Fp(0)
  for k,b in enumerate(q.list()):
   assert ZZ(b.denominator())%p,'Coefficient denominator vanishes modulo prime.'
   ans += Fp(b.numerator())/Fp(b.denominator())*z**k
  return ans
else:
 K=QQ;z=Fp(0)
 def residue(q):
  q=QQ(q); assert ZZ(q.denominator())%p
  return Fp(q.numerator())/Fp(q.denominator())
X=PolynomialRing(K,a['polynomial_coordinate_order']); XP=PolynomialRing(Fp,a['polynomial_coordinate_order'])
forms=[X(f) for f in a['generator_polynomials']]
Fpforms=[XP({e:residue(co) for e,co in f.dict().items()}) for f in forms]
degrees=list(map(int,a['polynomial_degrees']))
def parameter_coefficients(k,d):
 return [(1 if k==0 else j+1 if k==1 else j+3 if k==2 else j*j+2) if degrees[j]==d else 0 for j in range(len(forms))]
generation_bound=bound;parameter_certificate=None
parameter_method=aargs.generation_bound=='parameters' or (aargs.generation_bound=='auto' and aargs.case in [173,177])
if parameter_method:
 hd=[2,6,8,12];hc=[parameter_coefficients(k,d) for k,d in enumerate(hd)]
 hp=[sum(c*f for c,f in zip(row,Fpforms)) for row in hc]
 for f,d in zip(hp,hd):assert f and all(sum(e)==d for e in f.exponents())
 say('PHYSICAL_PARAMETER_IDEAL_START',degrees=hd)
 hgb=XP.ideal(hp).groebner_basis()
 powers=[]
 for j in range(4):
  candidates=[int(f.lm().exponents()[0][j]) for f in hgb if all(not f.lm().exponents()[0][k] for k in range(4) if k!=j)]
  assert candidates,('Parameters do not have proved finite colength',j)
  powers.append(min(candidates))
 generation_bound=min(bound,sum(hd)-4)
 parameter_certificate=dict(degrees=hd,coefficients_in_public_generators=hc,prime=p,
  groebner_basis=[str(f) for f in hgb],leading_pure_powers=powers,
  finite_colength_over_characteristic_zero=True,generation_degree_bound=generation_bound,
  proof='Pure powers in the full modular leading ideal imply finite colength after lifting by ranks of homogeneous relation matrices. Four parameters form a regular sequence in the four-variable polynomial ring. Its parameter quotient vanishes above sum(degrees)-4, so graded Nakayama gives polynomial-module generators up to that degree. The parameter-linear degree-preserving Reynolds operator gives invariant-module generators of the same bound. Exact parameter invariance is supplied by the separate actual-group binding.')
 say('PHYSICAL_PARAMETERS_AND_REYNOLDS_BOUND_PROVED',leading_pure_powers=powers,generation_degree_bound=generation_bound)
B={0:[XP(1)]};rows=[]
report=dict(case=aargs.case,input_hashes=hashes,derived_order=bound,noether_bound=bound,prime=p,
 coefficient_root=int(z),generation_degree_bound=generation_bound,parameter_certificate=parameter_certificate,molien_numerator=[str(x) for x in molien.numerator().list()],molien_denominator=[str(x) for x in molien.denominator().list()],
 exact_invariance_verified_here=False,actual_representation_binding_verified_here=False,
 scope='Modular product rank lower bounds through the proved Noether or parameter/Reynolds generation bound; combine with independently checked exact invariance and actual representation binding.',degrees=rows,complete=False)
for d in range(1,generation_bound+1):
 target=int(coeffs[d]);
 products=[f*b for f,deg in zip(Fpforms,degrees) if deg<=d for b in B[d-deg]]
 if products:
  mons=sorted(set(e for f in products for e in f.dict())); columns={e:j for j,e in enumerate(mons)}
  M=matrix(Fp,len(products),len(mons),{(i,columns[e]):v for i,f in enumerate(products) for e,v in f.dict().items()},sparse=False)
  M.echelonize();rank=int(M.rank())
  B[d]=[XP({e:M[i,j] for j,e in enumerate(mons) if M[i,j]}) for i in range(rank)]
 else:rank=0;B[d]=[]
 row=dict(degree=d,product_count=len(products),rank_mod_prime=rank,molien_dimension=target,equals=rank==target);rows.append(row)
 (out/'generation_report.json').write_text(json.dumps(report,indent=2)+'\n')
 say('DEGREE_RANK',**row)
 assert rank==target,('Generation rank does not match Molien',d,rank,target)
report['complete']=True;report['status']='MODULAR_SPANS_MATCH_MOLIEN_THROUGH_PROVED_GENERATION_BOUND'
if aargs.kernel_hilbert:
 say('ORDINARY_RELATION_HILBERT_START')
 n=len(forms)
 artinian=aargs.hilbert_method=='artinian' or (aargs.hilbert_method=='auto' and aargs.case in [171,173,177])
 order=TermOrder('wdegrevlex',degrees) if artinian else TermOrder(matrix(ZZ,[degrees]+[[-int(j==k) for j in range(n)] for k in range(n-1)]))
 ordinary_field=QQ if all('zeta' not in f for f in a['base_relations']) else K
 U=PolynomialRing(ordinary_field,[f'u{j+1}' for j in range(n)],order=order)
 ordinary=[U(f) for f in a['base_relations']]
 for f in ordinary:
  assert len({sum(int(e[j])*degrees[j] for j in range(n)) for e in f.exponents()})<=1,'Ordinary relation is not weighted homogeneous'
 if aargs.hilbert_field=='modular':
  UP=PolynomialRing(Fp,list(U.variable_names()),order=order)
  integral=[]
  for f in ordinary:
   denominator=f.denominator() if ordinary_field==QQ else lcm([b.denominator() for c in f.coefficients() for b in K(c).list()])
   f=f*denominator
   content=gcd([ZZ(c) for c in f.coefficients()]) if ordinary_field==QQ else gcd([ZZ(b) for c in f.coefficients() for b in K(c).list()])
   if content:f=f/content
   integral.append(UP({e:(Fp(ZZ(c)) if ordinary_field==QQ else residue(c)) for e,c in f.dict().items()}))
  I=UP.ideal(integral)
 else:I=U.ideal(ordinary)
 parameter_degrees=[2,6,8,12] if artinian else []
 parameter_polynomials=[]
 if artinian:
  IR=I.ring()
  for k,d in enumerate(parameter_degrees):
   members=[j for j in range(n) if degrees[j]==d];assert members,('No parameter of the requested degree',d)
   parameter_polynomials.append(sum(c*IR.gen(j) for j,c in enumerate(parameter_coefficients(k,d))))
  I=I+IR.ideal(parameter_polynomials)
 say('HILBERT_GROEBNER_START',algorithm=aargs.groebner_algorithm,artinian_parameters=parameter_degrees)
 basis=I.groebner_basis(algorithm='libsingular:'+aargs.groebner_algorithm)
 say('HILBERT_GROEBNER_COMPLETE',generators=len(basis))
 leading=I.ring().ideal([f.lm() for f in basis])
 quotient_hs=leading.hilbert_series(grading=degrees)
 hs=quotient_hs/prod(1-t**d for d in parameter_degrees)
 report['ordinary_relation_hilbert']=dict(method='artinian_upper_bound' if artinian else 'full_quotient',parameter_degrees=parameter_degrees,parameter_polynomials=[str(f) for f in parameter_polynomials],parameter_quotient_hilbert=str(quotient_hs),coefficient_field=aargs.hilbert_field,prime=p if aargs.hilbert_field=='modular' else None,proof='Specialization bounds characteristic-zero quotient dimensions by modular quotient dimensions. For homogeneous h of degree d, H_R <= H_(R/h)/(1-t^d) coefficientwise, by the exact multiplication sequence. Iterating gives an upper bound from the parameter quotient without assuming regularity. Exact relation identities and invariant generation give the opposite Molien bound, so equality proves the full characteristic-zero kernel.',numerator=[str(x) for x in hs.numerator().list()],denominator=[str(x) for x in hs.denominator().list()],rational_function=str(hs),equals_molien=bool(hs==molien))
 assert hs==molien,('Public ordinary relation Hilbert differs from Molien',str(hs),str(molien))
 say('ORDINARY_RELATION_HILBERT_EQUALS_MOLIEN',rational_function=str(hs))
report['elapsed_seconds']=float(time.time()-start)
(out/'generation_report.json').write_text(json.dumps(report,indent=2)+'\n')
say('MODULAR_GENERATION_COMPLETE',noether_bound=bound,generation_degree_bound=generation_bound)
