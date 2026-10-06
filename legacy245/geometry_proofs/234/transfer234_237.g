Read("ASL4.txt");;
Std4:=function(pi)
 local M,i,j;
 M:=NullMat(4,4);
 for i in [1..4] do for j in [1..4] do
 if i=j^pi then M[i][j]:=M[i][j]+1;fi;
 if i=5^pi then M[i][j]:=M[i][j]-1;fi;
 od;od;return M;
end;;
A5std:=Group(Std4((1,2,3)),Std4((1,2,3,4,5)));;
C2A5std:=Group(Concatenation(GeneratorsOfGroup(A5std),[-IdentityMat(4)]));;
for n in [234..237] do
 G:=Group(ASL4[n]);;
 if n<236 then H:=A5std;else H:=C2A5std;fi;
 iso:=IsomorphismGroups(G,H);;
 if iso=fail then Error("IsomorphismGroups failed");fi;
 good:=ForAll(Elements(G),g->TraceMat(g)=TraceMat(Image(iso,g)));;
 Print("CASE ",n," ORDER ",Size(G)," ALL_CHARACTER_VALUES_EQUAL ",good,"\n");
 if not good then Error("representation transfer failed");fi;
od;
Print("TRANSFER_234_237_PASS\n");QUIT;
