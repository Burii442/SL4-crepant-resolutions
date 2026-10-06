# Export the lattice points of the junior simplex for every abelian group in
# ASL4/ASL6 format.  For an abelian diagonal action, these are the coordinate
# vertices together with the fractional character vectors of age one.

if not IsBound(SLDataFile) or not IsBound(SLVariableName)
   or not IsBound(SLDimension) or not IsBound(SLOutputFile) then
    Error("set SLDataFile, SLVariableName, SLDimension and SLOutputFile");
fi;

SizeScreen([10000, 24]);
Read(SLDataFile);
groupsData := ValueGlobal(SLVariableName);
dim := SLDimension;

RootFraction := function(value)
    local conductor, exponent;
    if value = 1 then
        return 0;
    fi;
    conductor := Order(value);
    for exponent in [0 .. conductor - 1] do
        if E(conductor) ^ exponent = value then
            return exponent / conductor;
        fi;
    od;
    Error("character value is not a root of unity: ", value);
end;

PointString := function(point)
    return JoinStringsWithSeparator(List(point, String), ",");
end;

PrintTo(SLOutputFile,
    "index,order,structure,group_elements,junior_points,points,",
    "fractional_points\n");

if not IsBound(SLSelectedIndices) then
    SLSelectedIndices := [1 .. Length(groupsData)];
fi;

for index in SLSelectedIndices do
    if index = 1 and Length(groupsData[index]) = 0 then
        matrices := [ ImmutableMatrix(Rationals, IdentityMat(dim)) ];
    else
        matrices := List(groupsData[index],
            matrix -> ImmutableMatrix(Rationals, matrix));
    fi;
    group := Group(matrices);

    if IsAbelian(group) then
        chi := NaturalCharacter(group);
        constituents := ConstituentsOfCharacter(chi);
        charactersWithMultiplicity := [];
        for constituent in constituents do
            multiplicity := ScalarProduct(chi, constituent);
            for unused in [1 .. multiplicity] do
                Add(charactersWithMultiplicity, constituent);
            od;
        od;

        juniorPoints := [];
        fractionalPoints := [];
        for classPosition in [1 .. NrConjugacyClasses(group)] do
            point := List(charactersWithMultiplicity,
                character -> RootFraction(character[classPosition]));
            AddSet(fractionalPoints, point);
            if Sum(point) = 1 then
                AddSet(juniorPoints, point);
            fi;
        od;

        vertices := List([1 .. dim], position ->
            List([1 .. dim], function(coordinate)
                if position = coordinate then
                    return 1;
                fi;
                return 0;
            end));
        points := Set(Concatenation(vertices, juniorPoints));

        AppendTo(SLOutputFile,
            String(index), ",",
            String(Size(group)), ",\"",
            ReplacedString(StructureDescription(group), "\"", "'"), "\",",
            String(Size(group)), ",",
            String(Length(juniorPoints)), ",\"",
            JoinStringsWithSeparator(List(points, PointString), ";"),
            "\",\"",
            JoinStringsWithSeparator(List(fractionalPoints, PointString), ";"),
            "\"\n");
    fi;
od;

QUIT_GAP(0);
