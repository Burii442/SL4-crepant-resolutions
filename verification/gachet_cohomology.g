# Gachet, JEP 11 (2024), Remark 8.15: three copies of a faithful
# degree-two representation of SL(2,3) with a junior order-three class.
# EigenvaluesChar lists multiplicities for exponents 1,...,order;
# its last entry corresponds to exponent zero.
group := SL(2,3);;
table := CharacterTable(group);;
orders := OrdersClassRepresentatives(table);;
sizes := SizesConjugacyClasses(table);;
characters := Filtered(Irr(table), chi -> chi[1] = 2);;
matches := 0;;
order := 1;;
multiplicities := [];;
for chi in characters do
    if Filtered([1..Length(orders)], i -> chi[i] = 2) <> [1] then
        Error("The degree-two representation is not faithful");
    fi;
    ages := [];
    for i in [1..Length(orders)] do
        order := orders[i];
        multiplicities := EigenvaluesChar(chi,i);
        Add(ages, 3 * Sum([1..order], j ->
            (j mod order) * multiplicities[j]) / order);
    od;
    if Number(ages, a -> a = 1) = 1 then
        matches := matches + 1;
        if SortedList(ages) <> [0,1,2,2,3,3,4] then
            Error("Unexpected age distribution");
        fi;
        if not ForAll(ages, IsInt) then
            Error("The six-dimensional representation is not special linear");
        fi;
        Print("faithful_character=", chi, "\n");
        Print("class_orders=", orders, "\nclass_sizes=", sizes,
              "\nclass_ages=", ages, "\n");
    fi;
od;
if Size(group) <> 24 or matches <> 2 then
    Error("Expected the two dual faithful representations of order 24");
fi;
Print("PASS: two dual representations; age polynomial 1+t+2*t^2+2*t^3+t^4; b2=1, b4=2.\n");
QUIT;
