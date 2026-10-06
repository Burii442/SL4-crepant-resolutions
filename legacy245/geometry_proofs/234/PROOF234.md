# Dwa jawne rozdmuchania: projektowe rozstrzygnięcie YES dla ASL4 234–235

**Twierdzenie.** Iloraz standardowej czterowymiarowej reprezentacji (A_5) ma projektowe rozdzielenie krepantne. Jest nim
\[
Y=\operatorname{Bl}_{\widetilde S_{22}}
       \operatorname{Bl}_{S_3}(\mathbb A^4/A_5),
\]
gdzie (S_3) jest zredukowanym ośrodkiem potrójnego pierwiastka, a \(\widetilde S_{22}\) ścisłą transformatą zredukowanego ośrodka dwóch podwójnych pierwiastków. Wszystkie rozdmuchania są zwykłymi rozdmuchaniami ideałów podanych poniżej. Nie występuje niejawna zmiana modelu ani założenie o kompletności pierścienia Coxa.

**Zakres.** Argument dotyczy lokalnych afinicznych ilorazów nad \(\mathbb C\). Identyfikację z rzeczywistymi macierzami ASL4[234], ASL4[235] sprawdza `transfer234_237.g`: izomorfizm grup oraz zgodność śladów na wszystkich 60 elementach. Test przenosi reprezentację liniową, nie tylko abstrakcyjną grupę. Przypadki 236–237 rozstrzyga oddzielna bezpośrednia konstrukcja w `PROOF236.md`; §8 wyjaśnia konkretną przeszkodę dla naiwnego przeniesienia konstrukcji z niniejszego pliku.

## 1. Pełne równanie ilorazu i dwa ośrodki

Niech (t_1+\cdots+t_5=0), a
\[
 f(T)=\prod(T-t_i)=T^5+pT^3+qT^2+rT+h,\qquad
 w=\prod_{i<j}(t_i-t_j).
\]
Pierścień niezmienników (A_5) to
\[
\mathbb C[p,q,r,h,w]/(w^2-D),\quad D=\operatorname{disc}_T(f).
\]
To pełny pierścień: każdy niezmiennik (A_5) rozkłada się na część symetryczną i antysymetryczną względem jednej transpozycji; część antysymetryczna jest podzielna przez Vandermonde'a, a iloraz jest symetryczny. Jedyną relacją jest (w^2=D).

Dane i dokładne eliminacje w `a5_discriminant_input.py/.json` dają
\[
I_3=(w,g_1,g_2,g_3,g_4),\qquad I_{22}=(w,k_1,k_2,k_3,k_4),
\]
gdzie
\[
\begin{aligned}
g_1&=1875h^2+9p^3r-3p^2q^2+140pr^2-45q^2r,\\
g_2&=-45hp^2+100hr+32pqr-9q^3,\\
g_3&=75hq+9p^2r-3pq^2-20r^2,\\
g_4&=81p^4r-27p^3q^2-360p^2r^2+540pq^2r-135q^4+400r^3;
\end{aligned}
\]
\[
\begin{aligned}
k_1&=625h^2-32p^5+308p^3r-216p^2q^2-720pr^2+135q^2r,\\
k_2&=-40hp^2+200hr+4p^3q-36pqr+27q^3,\\
k_3&=50hq-4p^4+36p^2r-27pq^2-80r^2,\\
k_4&=-16p^6+224p^4r-88p^3q^2-1040p^2r^2+360pq^2r+135q^4+1600r^3.
\end{aligned}
\]
Są to ideały pierwsze: stanowią jądra parametryzacji odpowiednio
\[
(T-a)^3(T^2+3aT+b),\qquad (T^2-aT+b)^2(T+2a).
\]
Pełne bazy eliminacyjne, a nie tylko podstawienia potwierdzające zawieranie, znajdują się w danych wejściowych.

## 2. Wszystkie niezerowe straty

Stabilizatorem punktu jest podgrupa parzystych permutacji w iloczynie grup symetrycznych jego bloków równych współrzędnych. Poza zerem jedyne nietrywialne możliwości to:

| Partycja | Stabilizator | Nietrywialny model poprzeczny |
|---|---|---|
| (3+1+1) | (C_3) | (A_2) |
| (2+2+1) | (C_2) | (A_1) |
| (3+2) | (S_3) | standardowa (2)-reprezentacja plus znak |
| (4+1) | (A_4) | standardowa (3)-reprezentacja |

Do modeli trójwymiarowych dochodzi jeden gładki parametr. Pozostałe partycje mają trywialny stabilizator. Partycja (5), czyli cały stabilizator (A_5), występuje wyłącznie w zerze. Analityczny lokalny model ilorazu skończonej grupy jest ilorazem przez stabilizator; tutaj pochodzi to bezpośrednio z rozłącznych małych otoczeń punktów skończonej orbity.

### Strata (3+2)

Po nieszkodliwym przeskalowaniu współrzędnych równanie to
\[
w^2=s(q^2+p^3).
\]
Ośrodek potrójny to ((p,q,w)). Jego trzy karty:

- (p): (q=pv,w=pz), zatem (z^2=s(v^2+p));
- (q): (p=qv,w=qz), zatem (z^2=s(1+qv^3));
- (w): (p=wv,q=wz), zatem (1=s(z^2+wv^3)).

Pierwsza karta ma dokładnie osobliwą krzywą (s=z=v^2+p=0). Jest to ścisły ośrodek (S_{22}); po zmianie (c=v^2+p) mamy (z^2=sc). Osobliwości drugiej karty mają (v\ne0), więc należą do pierwszej. Trzecia jest gładka. Rozdmuchanie ((s,z,c)) rozwiązuje (A_1). Pierwszy krok ma w gładkiej przestrzeni otaczającej kowymiar ośrodka 3 i krotność równania 2, więc rozbieżność (3-1-2=0). Drugi krok również jest krepantny.

### Strata (4+1)

Dla (A_4=V_4\rtimes C_3), najpierw biorąc niezmienniki parzystych zmian znaków i następnie współrzędne Fouriera cyklicznej permutacji, otrzymujemy
\[
 UV=W^3,\qquad e^2=a^3+U+V-3aW.
\]
Ośrodek potrójny to ((U,V,W)): jego obraz jest zredukowaną krzywą (e^2=a^3). Drugie równanie jest moniczne w (e), więc pierścień jest płaski nad bazą (UV=W^3). Rozdmuchanie ośrodka jest zatem zmianą bazy minimalnego rozdzielenia (A_2), o kartach
\[
(U,V,W)=(x^3y^2,y,xy),\ (x^2y,xy^2,xy),\ (x,x^2y^3,xy).
\]
W lewej karcie przy (x=0) pochodna prawej strony równania względem (y) jest 1, a poza tym brzegiem jesteśmy w karcie środkowej. Prawa karta jest symetryczna. W środkowej jedyny zbiór osobliwy to (e=0,x=y=a). Po (X=x-a,Y=y-a) równanie brzmi
\[
 e^2=a(X^2+XY+Y^2)+XY(X+Y).
\]
To ścisły ośrodek (S_{22}), o ideale ((e,X,Y)). Karta (X) drugiego rozdmuchania ma równanie
\[
 t^2=a(1+v+v^2)+Xv(1+v).
\]
Pochodne względem (a,X) nie zerują się równocześnie, bo ((1+v+v^2)-v(1+v)=1). Karta (Y) jest symetryczna. Karta (e) ma równanie
\[
1=a(u^2+uv+v^2)+euv(u+v).
\]
Wspólne zero (u^2+uv+v^2) i (uv(u+v)) to ((0,0)), które nie spełnia równania. Wszystkie karty są gładkie. Pierwszy krok jest krepantny przez adjunkcję po krepantnym rozdzieleniu bazy (A_2): równanie moniczne nie ma wyjątkowego czynnika. Drugi ma ponownie rozbieżność (3-1-2=0).

To dowodzi normalności pierwszego rozdmuchania i gładkości oraz krepantności całej sekwencji poza włóknem nad zerem.

## 3. Pięć pełnych kart pierwszego rozdmuchania

Oznaczmy (f_0=w,f_i=g_i) dla (1\le i\le4). W karcie (f_j) wprowadzamy (v=f_j) i (y_i=f_i/f_j), (i\ne j). Używamy pierścienia dziewięciu zmiennych (p,q,r,h,(y_i)_{i\ne j},v); (w=v) dla (j=0), a (w=vy_0) w pozostałych kartach.

**Definiujący ideał karty jest saturacją** pięciu równań grafu przez (v). Ponieważ pierścień ilorazu jest dziedziną, jest to dokładnie podpierścień (mathcal O(X)[I_3/f_j]\subset\mathcal O(X)[1/f_j]), czyli karta Reesa rzeczywistego rozdmuchania. Pliki `a5_triple_chart0.sing`–`a5_triple_chart4.sing` obliczają pełne saturacje nad \(\mathbb Q\). Uwaga techniczna: używany `elim.lib` zwraca z `sat` ideał; zapis `list L=sat(...); L[1]` jest jawnym rzutowaniem tego ideału do jednoelementowej listy. Nie wolno tutaj zastąpić go bezpośrednio `sat(...)[1]`, co wybierałoby tylko pierwszy generator.

Wszystkie karty mają wymiar 4. Po podstawieniu (p=q=r=h=v=0), ideal włókna daje:

| Karta | Równania włókna w czterech zmiennych ilorazowych |
|---|---|
| (w) | (y_4=0,\ y_1^2=1125) |
| (g_1) | (y_4=0,\ 1125y_0^2=1) |
| (g_2) | (y_4=0,\ 1125y_0^2=y_1^2) |
| (g_3) | (y_4=0,\ 1125y_0^2=y_1^2) |
| (g_4) | (1=0), karta nie przecina włókna |

Włókno to dwie płaszczyzny projektowe przecinające się w prostej. W szczególności ma wymiar 2 i nie zawiera wyjątkowego dzielnika całej czterowymiarowej przestrzeni.

## 4. Cały brzeg poza kartą (g_3) jest gładki

W kartach (w,g_1,g_2) brzeg poza (g_3\ne0) zadany jest przez (y_3=0). Na jego przecięciu z włóknem centralnym wystarczają następujące minory Jacobiego pełnych, nasyconych ideałów kart:

| Karta | Wiersze wyliczonej bazy (od 1) | Kolumny | Wyznacznik po ograniczeniu |
|---|---|---|---|
| (w) | 1,2,3,6,7 | (q,r,y_1,y_4,v) | (360y_1^4) |
| (g_1) | 2,3,4,5,7 | (q,r,y_0,y_4,v) | (405000y_0) |
| (g_2) | 1,2,3,6,8 | (p,q,r,h,v) | (15187500) |

Ograniczenie znaczy (p=q=r=h=v=y_3=y_4=0); pozostałe współrzędne nie są specjalizowane. Pierwsze dwa wyznaczniki są wszędzie niezerowe na włóknie z §3. Trzeci jest stały niezerowy. Ranga wynosi zatem 5 w dziewięciozmiennym osadzeniu czterowymiarowej dziedziny. Każdy taki punkt jest gładki.

Wszystkie możliwe osobliwości pierwszego rozdmuchania nad zerem leżą więc w karcie (g_3). To kontrola całego pokrycia, a nie test skończonego zbioru wybranych punktów.

## 5. Karta (g_3) jest prostą hipersurfacją; ścisły ośrodek jest jawny

Po czterech eliminacjach o stałych niezerowych współczynnikach karta (g_3) ma współrzędne (p,q,Z=y_0,z_1=y_1,t=y_2). Wszystkie 33 relacje jej niezależnie nasyconej bazy `dp` redukują się do jednej hipersurfacji; pełne odwrotne podstawienia są w `certificate234_geometry.json`. Wprowadźmy odwracalną wielomianową zmianę współrzędnych
\[
\begin{aligned}
A&=-22p+2z_1-15t^2,\\
B&=-4p+4z_1-5t^2,\\
Q&=q-\frac{t(52p-8z_1+15t^2)}{72}.
\end{aligned}
\]
Jej odwrotność w pierwszych dwóch zmiennych to
\[
p=-\frac A{20}+\frac B{40}-\frac58t^2,\qquad
z_1=-\frac A{20}+\frac{11B}{40}+\frac58t^2.
\]
Równanie karty przyjmuje postać
\[
\boxed{25920Q^2=B(8100Z^2-A^2)-7200AZ^2.}\tag{*}
\]
Parametr (t) jest wolny. Zredukowany zbiór osobliwy (*) to dokładnie ((A,Z,Q)=0): pochodna względem (Q) daje (Q=0), względem (B) daje (A^2=8100Z^2), a pozostałe pochodne wykluczają (Z\ne0). Ma on wymiar 2 w wymiarze 4. Hipersurfacja jest dziedziną (jest kartą Reesa) i spełnia (S_2); jest regularna w kowymiarze 1, zatem normalna.

**Identyfikacja ośrodka jest obliczeniem ideału, nie tylko porównaniem zbiorów osobliwych.** Podstawiamy cztery wyeliminowane współrzędne do (I_{22}) i liczymy
\[
(I_{22}\mathcal O(X_1)):v^\infty.
\]
Dwustronna redukcja baz Gröbnera w `a5_g3_center_certificate.sing` daje dokładnie ideał ((A,Z,Q)). Wykluczenie (v=0) usuwa pierwotny ośrodek rozdmuchania i bierze domknięcie jego dopełnienia, czyli właśnie ścisłą transformatę (S_{22}).

## 6. Drugie rozdmuchanie: wszystkie trzy karty są gładkie

Rozdmuchujemy w (*) ideał ((A,Z,Q)). Pomijamy wolny parametr (t).

| Karta | Podstawienie | Równanie ścisłej transformaty |
|---|---|---|
| (A) | (Z=Au,Q=AV) | (25920V^2-B(8100u^2-1)+7200Au^2=0) |
| (Z) | (A=Za,Q=ZV) | (25920V^2-B(8100-a^2)+7200Za=0) |
| (Q) | (A=Qa,Z=Qb) | (25920-B(8100b^2-a^2)+7200Qab^2=0) |

W pierwszej karcie pochodna po (A) wymusza (u=0), ale wtedy pochodna po (B) wynosi 1. W drugiej pochodna po (Z) wymusza (a=0), ale wtedy pochodna po (B) wynosi (-8100). W trzeciej jednoczesne zerowanie pochodnych po (Q,B) wymusza (ab^2=0) oraz (8100b^2=a^2), stąd (a=b=0), co przeczy równaniu o stałej 25920. Wszystkie trzy karty są gładkie, również nad (A=Z=Q=B=0).

Są to pełne karty rzeczywistego rozdmuchania: po podstawieniu równanie zawiera dokładnie kwadrat współrzędnej wyjątkowej; podane ilorazy nie mają składowej zawartej w jej zerowaniu. Ośrodek w otaczającej przestrzeni \(\mathbb A^5\) jest gładki, kowymiaru 3, a równanie ma wzdłuż całego ośrodka krotność 2 (współczynnik (Q^2) nie znika). Adjunkcja daje rozbieżność (3-1-2=0).

## 7. Domknięcie argumentu globalnego

Pierwsze rozdmuchanie jest normalne: poza zerem z §2; nad zerem z normalnej hipersurfacji §5 i gładkich punktów §4. Jest krepantne poza włóknem centralnym. Rozbieżności są współczynnikami dzielników. Włókno nad zerem ma wymiar 2, więc nie może zawierać nowego dzielnika wyjątkowego czterowymiarowego modelu. Stąd pierwszy morfizm jest krepantny również globalnie.

Ścisła transformata (S_{22}) jest domknięciem części zawartej w zbiorze osobliwym pierwszego modelu. Ponieważ zbiór osobliwy jest zamknięty, ten ośrodek nie spotyka gładkich punktów brzegu opisanych w §4. Drugie rozdmuchanie jest tam identycznością. Pozostałe punkty pokrywają §2 i trzy gładkie karty §6. Drugie rozdmuchanie jest więc wszędzie gładkie i krepantne. Oba morfizmy są projektowe i biracjonalne z definicji rozdmuchania niezerowego ideału dziedziny. Ich złożenie jest żądanym projektowym rozdzieleniem krepantnym.

## 8. Co konkretnie ustalono dla 236–237 i czego to nie rozstrzyga

Dodatkowy centralny element działa na pierwotnym równaniu przez
\[
(p,q,r,h,w)\mapsto(p,-q,r,-h,w).
\]
Oba ideały ośrodków są niezmiennicze. Powyższe rozdzielenie (Y) jest zatem ekwiwariantne. W karcie (g_3) działanie to
\[
(A,B,Z,Q,t)\mapsto(A,B,Z,-Q,-t).
\]
Po drugim rozdmuchaniu karty (A,Z) mają tylko dwa przeciwne znaki na współrzędnych stycznych; karta (Q) nie ma punktów stałych. Nie daje to jednak globalnego rozdzielenia dla (C_2\times A_5).

W karcie (g_2) pierwszego rozdmuchania punkt
\[
p=q=r=h=y_0=y_1=y_3=y_4=v=0
\]
jest gładki (§4), nie należy do drugiego ośrodka, a inwolucja go ustala. Spośród dziewięciu współrzędnych tylko (p,r) są parzyste. Jacobian ma rangę 5: rangę 2 na dwóch parzystych kolumnach i rangę 3 na siedmiu nieparzystych. Czterowymiarowa przestrzeń styczna ma więc wyłącznie wagę (-1). Lokalny iloraz (Y/C_2) zawiera izolowaną osobliwość \(\frac12(1,1,1,1)\).

To ścisła przeszkoda dla rozdzielania *tego wybranego modelu ilorazowego*: grupa (C_2\subset SL_4) nie ma elementów junior (jedyny nietrywialny ma wiek 2), więc taki lokalny iloraz nie ma rozdzielenia krepantnego. Zob. twierdzenie o konieczności generowania przez juniorów u [Yamagishiego, arXiv:1602.01572](https://arxiv.org/abs/1602.01572). Nie jest to dowód globalnego NO dla \(\mathbb A^4/(C_2\times A_5)\): inny model krepantny nad pierwotnym ilorazem nie musi dominować (Y/C_2).

Bezpośrednia pierwsza ekstrakcja na \(C_2\times A_5\) pozostaje jawna: (Q_0=q^2,H=qh,K=h^2), rozdmuchanie (Q_0K=H^2) w ((Q_0,H,K)), dwie karty z `a5_discriminant_input.json`. Po tej ekstrakcji i następnie odpowiednich dwóch ośrodkach wszystkie niezerowe stabilizatory mają elementarne rozdzielenia; kontrolę włókna nad zerem domyka osobny dowód `PROOF236.md`. Nie utożsamiamy niepowodzenia ekwiwariantnego ilorazu z nieistnieniem innego rozdzielenia.

## 9. Reprodukcja, źródła i zakres cytowań

Uruchom w głównym folderze publicznego suplementu, wskazując nowy lub pusty katalog wynikowy:

```
sage -python geometry_proofs/run.py --case 234 --output-dir /tmp/geometry-234
```

Walidator ponownie liczy pięć nasyconych kart, wszystkie trzy minory brzegu, redukcję **pełnej** karty (g_3), dwustronną równość ideału ścisłego ośrodka, ideały Jacobiego trzech końcowych kart, transfer reprezentacji oraz rangę stycznej inwolucji. Program nadrzędny zapisuje `run.json`, hashe wejść i logi etapów w katalogu wynikowym; świeże równania i certyfikaty pozostają w jego podkatalogu `work/`.

Część geometryczna jest własnym dowodem zapisanym wyżej; zewnętrzne źródła nie zastępują weryfikacji kart. Praca [Paranjape–Ramakrishnan, *Quotients of E^n by A_{n+1} and Calabi–Yau manifolds*](https://arxiv.org/abs/math/0411310) daje pokrewne przedstawienie przez podwójne nakrycie, ale jej twierdzenie o rozdzieleniu dotyczy (n<4), więc nie jest podstawą rozstrzygnięcia 234. Źródło [Yamagishi](https://arxiv.org/abs/1602.01572) jest użyte wyłącznie do lokalnej przeszkody z §8.
