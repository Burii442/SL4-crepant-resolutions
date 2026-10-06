# Independent remaining finite calculations from Sections 30--31.
SetAssertionLevel(1);
ii:=E(4);; phi:=1+E(5)+E(5)^-1;;
aa:=[[phi+ii/phi,1],[-1,phi-ii/phi]]/2;;
bb:=DiagonalMat([ii,-ii]);;
ca:=aa^3*bb*aa;;cb:=[[0,ii],[ii,0]];;
kt:=Group(aa,bb);; at:=GroupHomomorphismByImages(kt,kt,[aa,bb],[ca,cb]);;
Assert(1,Size(kt)=120 and at<>fail and IsBijective(at));
Assert(1,ForAll(Elements(kt),g->Image(at,Image(at,g))=g));
Assert(1,TraceMat(aa)=phi and TraceMat(ca)=1-phi);
Assert(1,Order(aa)=10 and Order(ca)=10 and Order(-aa*bb*aa^3)=5);
bl:=function(a,b) local out,i,j; out:=NullMat(4,4); for i in [1..2] do for j in [1..2] do out[i][j]:=a[i][j];out[i+2][j+2]:=b[i][j];od;od;return out;end;;
sw:=[[0,0,1,0],[0,0,0,1],[1,0,0,0],[0,1,0,0]];;
gt:=Group(bl(aa,ca),bl(bb,cb),sw);;
rt:=Filtered(Elements(gt),g->RankMat(IdentityMat(4)-g)=2);;
Assert(1,Size(gt)=240 and Length(rt)=20 and Size(Group(rt))=240);
Assert(1,Sum(Elements(gt),g->TraceMat(g)*ComplexConjugate(TraceMat(g)))/Size(gt)=1);
Print("TYPE_V: |K|=120 involutive outer automorphism; traces=phi,1-phi; orders=10,10; older expression order=5; |G|=240; reflections=20 generate G; character norm=1.\n");
qi:=DiagonalMat([ii,-ii]);; qj:=[[0,1],[-1,0]];;
sign:=DiagonalMat([1,1,-1,-1]);;
gg:=Group(bl(qi,qi),bl(qj,qj),sign,sw);;
rr:=Filtered(Elements(gg),g->RankMat(IdentityMat(4)-g)=2);;
Assert(1,Size(gg)=32 and Length(rr)=10);
Assert(1,Collected(List(Elements(gg),TraceMat))=[[-4,1],[0,30],[4,1]]);
Assert(1,ForAll(rr,s->Size(Centralizer(gg,s))=16));
subs:=[TrivialSubgroup(gg)];;sets:=[Set(Elements(subs[1]))];;p:=1;;
while p<=Length(subs) do
 for r in rr do
  ss:=ClosureGroup(subs[p],r);ee:=Set(Elements(ss));
  if not ee in sets then Add(subs,ss);Add(sets,ee);fi;
 od;
 p:=p+1;
od;
contain:=Filtered(subs,s->-IdentityMat(4) in s);;
Assert(1,Collected(List(contain,Size))=[[4,5],[8,10],[16,10],[32,1]]);
Print("G32: 10 reflections; character [4,-4,0]; centralizers order16; all reflection-generated subgroups containing -I: ",Collected(List(contain,Size)),".\n");
Print("ALL_PART6_EXTRA_FINITE_CHECKS_PASSED\n");
QUIT;
