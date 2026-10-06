# Run with GAP + CrystCat from this script's directory.
# Input is the official CrystCat catalogue, never the manuscript's groups.
if LoadPackage("crystcat") <> true then Error("CrystCat is required"); fi;
out := OutputTextFile("all_qclasses.json", false);;
SetPrintFormattingStatus(out, false);;
PrintTo(out, "{\"gap_version\":\"", GAPInfo.Version,
  "\",\"crystcat_version\":\"", PackageInfo("crystcat")[1].Version,
  "\",\"classes\":[\n");;
allq := 0;; allz := 0;; slq := 0;; slz := 0;;
for sys in [1..NrCrystalSystems(4)] do
 for qc in [1..NrQClassesCrystalSystem(4,sys)] do
  allq := allq+1;
  nz := NrZClassesQClass(4,sys,qc);
  allz := allz+nz;
  gg := MatGroupZClass(4,sys,qc,1);
  gens := GeneratorsOfGroup(gg);
  dets := List(gens,DeterminantMat);
  sl := ForAll(dets,d->d=1);
  if sl then slq:=slq+1; slz:=slz+nz; fi;
  if allq>1 then PrintTo(out,",\n"); fi;
  PrintTo(out,"{\"global_qclass\":",allq,",\"system\":",sys,
   ",\"qclass\":",qc,",\"zclasses\":",nz,",\"order\":",Size(gg),
   ",\"determinant_one\":",sl,",\"generator_determinants\":",dets,
   ",\"generators\":",gens,"}");
 od;
od;
PrintTo(out,"\n],\"counts\":{\"all_qclasses\":",allq,
 ",\"all_zclasses\":",allz,",\"det_one_qclasses\":",slq,
 ",\"det_one_zclasses\":",slz,"}}\n");;
CloseStream(out);;
Print("ALL_Q=",allq," ALL_Z=",allz," SL4_Q=",slq," SL4_Z=",slz,"\n");
QUIT;
