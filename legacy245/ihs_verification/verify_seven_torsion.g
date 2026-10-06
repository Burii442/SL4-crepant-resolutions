# New independent transcription of Part VI matrices and finite subgroup checks.
# Does not read historic reports or author-generated subgroup data.
SetAssertionLevel(1);
one4:=IdentityMat(4);;
aa:=(-E(24)+E(24)^11+E(24)^17-E(24)^19)/6;;
bb:=(-E(12)^7+E(12)^11)/6;; cc:=(E(8)-E(8)^3)/2;;
oo1:=DiagonalMat([1,E(3),1,E(3)^2]);;
oo2:=[[1/2,aa,bb,cc],[2*aa,0,0,2*bb],[-bb,-cc,1/2,aa],[0,-2*bb,2*aa,0]];;
oo3:=[[-1/2,0,3*bb,0],[0,1,0,0],[-3*bb,0,-1/2,0],[0,0,0,1]];;
oo4:=[[2*bb,0,0,-2*aa],[0,-2*bb,2*aa,0],[0,2*aa,2*bb,0],[-2*aa,0,0,-2*bb]];;
ii:=E(4);;
pp1:=[[1,0,0,0],[0,0,0,-1],[0,0,1,0],[0,1,0,0]];;
pp2:=[[1+ii,-1-ii,0,0],[1+ii,1+ii,0,0],[0,0,1-ii,-1+ii],[0,0,1-ii,1-ii]]/2;;
pp3:=[[1,0,0,0],[0,0,0,-ii],[0,0,1,0],[0,-ii,0,0]];;
pp4:=[[0,E(8)^3,0,0],[-E(8),0,0,0],[0,0,0,-E(8)],[0,0,E(8)^3,0]];;
Assert(1,TraceMat(oo1*oo4)^2=3);
Assert(1,TraceMat(pp2*pp4)^2=2);
Print("Irrational trace witnesses: O3=",TraceMat(oo1*oo4),"; P3=",TraceMat(pp2*pp4),"\n");
qqi:=DiagonalMat([ii,-ii]);; qqj:=[[0,1],[-1,0]];; qqk:=qqi*qqj;;
qqt:=(-IdentityMat(2)+qqi+qqj+qqk)/2;;
omega:=(IdentityMat(2)+qqi)/(E(8)+E(8)^-1);;
vee:=function(h) local r, j, k, hd; r:=NullMat(4,4); hd:=TransposedMat(h)^-1; for j in [1..2] do for k in [1..2] do r[j][k]:=h[j][k]; r[j+2][k+2]:=hd[j][k]; od; od; return r; end;;
ss:=[[0,0,0,1],[0,0,-1,0],[0,-1,0,0],[1,0,0,0]];;
allgens:=[[oo1,oo2],[oo1,oo2,oo3],[pp1,pp2],[pp1,pp2,pp3],Concatenation(List([qqi,qqj,qqt,E(6)*IdentityMat(2)],vee),[ss]),Concatenation(List([qqi,qqj,qqt,ii*IdentityMat(2),E(8)*omega],vee),[ss]),Concatenation(List([qqi,qqj,qqt,ii*omega],vee),[ss])];;
names:=["O1","O2","P1","P2","E_mu6T","E_OT4","E_OT2"];;
expectedorders:=[120,720,320,1920,144,192,96];;
expectedeligible:=[[[1,1],[3,10]],[[1,1],[3,20],[9,10]],[[1,1],[2,10],[4,10]],[[1,1],[2,10],[4,30],[8,10]],[[1,1],[2,6],[3,8],[6,2],[9,4],[18,8]],[[1,1],[2,10],[4,6]],[[1,1],[2,14],[6,8]]];;
for gi in [1..7] do
  matgroup:=Group(allgens[gi]);; Assert(1,Size(matgroup)=expectedorders[gi]);
  elts:=Elements(matgroup);; refl:=Filtered(elts,g->RankMat(one4-g)=2);;
  iso:=IsomorphismPermGroup(matgroup);; pg:=Image(iso);; zz:=Image(iso,-one4);;
  perms:=List(refl,g->Image(iso,g));;
  eligible:=[TrivialSubgroup(pg)];; sets:=[Set(Elements(eligible[1]))];; pos:=1;;
  while pos<=Length(eligible) do
    for rr in perms do
      if not rr in eligible[pos] then
        nh:=ClosureGroup(eligible[pos],rr);;
        if not zz in nh then
          ne:=Set(Elements(nh));;
          if not ne in sets then Add(sets,ne); Add(eligible,nh); fi;
        fi;
      fi;
    od;
    pos:=pos+1;
  od;
  hist:=Collected(List(eligible,Size));;
  Print(names[gi],": |G|=",Size(matgroup)," refl=",Length(refl)," eligible=",Length(eligible)," histogram=",hist,"\n");
  Assert(1,hist=expectedeligible[gi]);
  if gi in [1,2,3,4,6] then
    if gi in [1,2,3] then prime:=5;detexpected:=5;else prime:=3;detexpected:=9;fi;
    witnesses:=Filtered(elts,g->Order(g)=prime and RankMat(one4-g)=4 and DeterminantMat(one4-g)=detexpected);;
    Assert(1,Length(witnesses)>0);
    Assert(1,ForAll(eligible,h->Size(h) mod prime<>0));
    Print("det witness p=",prime," det=",detexpected," number=",Length(witnesses),"\n");
  elif gi=5 then
    cls:=Filtered(ConjugacyClasses(matgroup),c->Order(Representative(c))=3 and RankMat(one4-Representative(c))=4);;
    candidates:=List(cls,c->Representative(c));;
    cosets:=List(eligible,h->RightCosets(pg,h));;
    marks:=List(candidates,g->List(cosets,cs->Number(cs,c->c*Image(iso,g)=c)));;
    goodpairs:=[];
    expectedpairhist:=[[[1,0,0],1],[[2,0,0],6],[[3,0,0],8],[[6,0,24],2],[[9,4,16],4],[[18,2,8],8]];;
    for u in [1..Length(candidates)] do for v in [1..Length(candidates)] do
      ph:=Collected(List([1..Length(eligible)],j->[Size(eligible[j]),marks[u][j],marks[v][j]]));;
      if ph=expectedpairhist then Add(goodpairs,[u,v]); fi;
    od;od;
    Assert(1,Length(goodpairs)>0);
    Assert(1,ForAll(candidates,g->DeterminantMat(one4-g)=9));
    Print("mark pair histogram=",expectedpairhist," pairs=",goodpairs," contradiction 80-4*80=-240\n");
  elif gi=7 then
    markhist:=Collected(List(eligible,h->[Size(h),Number(RightCosets(pg,h),c->c*Image(iso,ss)=c)]));;
    Assert(1,markhist=[[[1,0],1],[[2,0],12],[[2,24],2],[[6,0],8]]);
    Print("s marks=",markhist,"; 80 mod 24=",80 mod 24,"\n");
  fi;
od;
Print("ALL_PART6_SEVEN_TORSION_EXCLUSIONS_PASSED\n");
QUIT;
