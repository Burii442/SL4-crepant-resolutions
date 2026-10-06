# ASL4 236–237: bezpośrednie trzy rozdmuchania dają projektowe rozdzielenie krepantne

**Wynik: YES dla standardowej reprezentacji (C_2\times A_5\subset SL_4(\mathbb C)).** Rozdzielenie powstaje przez rozdmuchanie dodatkowego ośrodka inwolucji, następnie ścisłego ośrodka potrójnego pierwiastka, a na końcu ścisłego ośrodka dwóch podwójnych pierwiastków. Jest to bezpośrednia konstrukcja nad ilorazem (C_2\times A_5); nie jest ilorazem rozdzielenia z `PROOF234.md`.

Wszystkie lokalne modele, równania ideałów i minory są nad \(\mathbb Q\). Transfer z grup kanonicznych do rzeczywistych macierzy ASL4[236], ASL4[237] przez porównanie charakterów na wszystkich 120 elementach znajduje się w `transfer234_237.g`.

## 1. Pierwsza ekstrakcja i globalne ośrodki

Używamy pełnego równania i pierwszych ideałów (I_3,I_{22}) z §1 `PROOF234.md`. Dodatkowy element działa przez
\[
(p,q,r,h,w)\longmapsto(p,-q,r,-h,w).
\]
Niech (Q_0=q^2,H=qh,K=h^2). Pełne równania nowego ilorazu (X) to
\[
Q_0K=H^2,\qquad w^2=\overline D(p,r,Q_0,H,K).
\]
Drugi wielomian jest dokładnie podany w `a5_discriminant_input.json`. To pełny pierścień niezmienników: parzyste monomy w (q,h) generują (Q_0,H,K), z jedyną relacją (Q_0K=H^2), a (w) jest parzysty.

Rozdmuchujemy (I_-=(Q_0,H,K)). Ponieważ drugie równanie jest moniczne w (w), zmiana bazy jest płaska i rozdmuchanie jest rzeczywistą zmianą bazy minimalnego rozdzielenia (A_1). Dwie karty (X_0) mają postać
\[
\begin{array}{ll}
q\text{-karta}:&Q_0=s,H=st,K=st^2,\\
h\text{-karta}:&Q_0=st^2,H=st,K=s.
\end{array}
\]
W obu występuje jedna hipersurfacja (w^2=D_q(p,r,s,t)) albo (w^2=D_h(p,r,s,t)). Na (s=0) obie mają równanie
\[
w^2=16r^3(p^2-4r)^2.
\]
Nie ma wyjątkowego czynnika w drugim równaniu. Adjunkcja po krepantnym rozdzieleniu bazy (A_1) dowodzi krepantności pierwszego kroku.

Globalne ośrodki (S_3,S_{22}\subset X) są kontrakcjami pierwszych ideałów (I_3,I_{22}\subset\mathcal O(\mathbb A^4/A_5)). Kontrakcję oblicza się bez niejawnego założenia: trzy generatory (g_1,g_3,g_4) są parzyste, (g_2) nieparzysty; ideał kontrakcji generują zatem
\[
w,g_1,g_3,g_4,qg_2,hg_2
\]
po zapisaniu wszystkiego przez (Q_0,H,K). Moduł nieparzysty jest generowany nad pierścieniem parzystym przez (q,h), co dowodzi kompletności listy. Analogicznie dla (k_1,k_2,k_3,k_4). Kontrakcja ideału pierwszego pozostaje pierwsza.

**Definicja całej konstrukcji:**
\[
Y=\operatorname{Bl}_{\widetilde S_{22}}
  \operatorname{Bl}_{\widetilde S_3}X_0\longrightarrow X.
\]
Tyldy oznaczają kolejne ścisłe transformaty, nie schematyczne pełne obrazy odwrotne. Obliczamy je przez saturację względem współrzędnych wyjątkowych. Wszystkie ośrodki i morfizmy są globalne i projektowe.

## 2. Ścisły ośrodek potrójny w q-karcie i trzy karty jego rozdmuchania

`c2a5_direct_first.py` podstawia obie karty do sześciu generatorów kontrakcji i wykonuje pełną saturację przez (s). W q-karcie wynik upraszcza się dokładnie do
\[
(w,L,J_3),
\]
gdzie
\[
\begin{aligned}
s_0&=-5p^2t+\frac{32}{9}pr+\frac{100}{9}rt,\qquad L=s-s_0,\\
J_3&=9p^3t-p^2r-225p^2t^2+140prt-12r^2+500rt^2.
\end{aligned}
\]
W szczególności jest to równość ideałów, a nie wybór generatorów jedynie na gęstym otwartym zbiorze. Rozwinięcie dyskryminantu jest
\[
D_q(s_0+L)=a_0J_3^2+c_1J_3L+a_2L^2+108tL^3,
\]
\[
\begin{aligned}
a_0&=-\frac{140pt-144r-125t^2}{81},\\
c_1&=-\frac{2(26p^2t-18pr+725pt^2-825rt-625t^3)}9,\\
a_2&=16p^3t-795p^2t^2+522prt-3750pt^3-27r^2+5850rt^2+3125t^4.
\end{aligned}
\]
Dane i tożsamości są w `c2a5_q_first_model.json`, `c2a5_q_triple_charts.json`.

W karcie (L) piszemy (w=La,J_3=Lb). Otrzymujemy pełny czterowymiarowy model będący przecięciem zupełnym w sześciu zmiennych (p,r,t,L,a,b):
\[
J_3-Lb=0,\qquad a^2-a_0b^2-c_1b-a_2-108tL=0.\tag{L}
\]
W karcie (J_3), gdzie (w=J_3a,L=J_3b), równanie to
\[
a^2-a_0-c_1b-a_2b^2-108tJ_3b^3=0.\tag{J}
\]
Karta (w), (J_3=wb,L=wa), ma równania
\[
J_3-wb=0,\qquad1-a_0b^2-c_1ab-a_2a^2-108twa^3=0.\tag{w}
\]
Są to rzeczywiste karty Reesa. Po odwróceniu odpowiedniej współrzędnej wyjątkowej są grafami ilorazów. Na jej zerowaniu wymiar spada o jeden: w (L) równanie (J_3=0) jest niezerowe, a drugie jest moniczne w (a); podobnie w pozostałych kartach. Przecięcia zupełne nie mają zanurzonych składowych, więc nie występuje dodatkowa składowa wyjątkowa; podane ideały są nasycone.

Nad początkiem q-bazy (p=r=s=t=w=0): karta (w) jest pusta; karta (J) jest gładka, ponieważ pochodna równania po (r) wynosi (-16/9). W (L) mamy (L=a=0), dowolne (b). Dla (b\ne0) pierwsze równanie ma pochodną po (L) równą (-b), a drugie po (r) równą (-16b^2/9). Jedyny punkt wymagający ostatniego rozdmuchania to
\[
p=r=t=L=a=b=0.\tag{P_q}
\]

## 3. Pełny ostatni ośrodek i cztery karty nad trudnym punktem q

Saturacja kontrakcji (I_{22}) przez (Ls) w (L), policzona w `c2a5_q_L_dd.sing`, daje pierwszy ideał wymiaru 2. Po trzech eliminacjach o stałych niezerowych współczynnikach jest to
\[
(a,u,V,J),\qquad u=r-r_0(p,t,b),\quad V=L-L_0(p,t,b),
\]
\[
\boxed{J=\frac{b^2}{27}+\frac{25bt}{9}+pt+50t^2.}
\]
Wielomiany (r_0,L_0) oraz ich równoważne redukcje modulo (J) są w `c2a5_q_L_dd_reduced.json` i `c2a5_q_dd_normal_input.json`. To odwracalna wielomianowa zmiana współrzędnych: oba zastępowane wielomiany zależą wyłącznie od (p,t,b). Redukcja (r_0,L_0) modulo (J) nie zmienia ideału ośrodka. Sam ośrodek jest powierzchnią (A_1), więc jego gładkość nie jest założeniem.

`c2a5_q_dd_charts.py` tworzy cztery pełne karty Reesa zwykłego rozdmuchania ((a,u,J,V)): dodaje równania ilorazów i nasyca przez współrzędną wyjątkową. Wszystkie mają wymiar 4 i są dziedzinami jako podpierścienie lokalizacji poprzedniej dziedziny.

Włókno nad (P_q), po wyzerowaniu (p,t,b,u,V,a) i nowej współrzędnej wyjątkowej, ma równania:

| Karta | Pozostałe równanie |
|---|---|
| (a), nr0 | (z_2z_3=0) |
| (u), nr1 | (z_2z_3=0) |
| (J), nr2 | (z_3=0) |
| (V), nr3 | (z_2=0) |

W plikach nazwy ilorazów to `y0`–`y3`; w tym paragrafie zapisano je (z_i), aby nie mylić z h-kartą poniżej. Każde włókno ma wymiar 2.

Gładkość całego pokrycia jest potwierdzona następującymi minorami rzędu 6 w dziesięciozmiennym osadzeniu. Dokładne wiersze i kolumny zapisano w `c2a5_q_dd_jacobian.json`, `c2a5_q_dd_jacobian_special.json`, `c2a5_q_dd_cover.json`.

1. Karta (V), na całym włóknie: stały minor (-229582512).
2. Karta (J), (z_3=0): minor (-34992(9z_1-16)). Na pozostałej prostej (z_1=16/9) drugi minor to (11664(3z_0^2-2048)). Przy jego zerach trzeci minor ma modulo (3z_0^2-2048) niezerową stałą resztę (450953216).
3. Pozostały brzeg poza kartami (J,V) w karcie (a) ma (z_2=z_3=0). Pierwszy minor upraszcza się tam do (5832(27z_1^2+1)^3). Drugi minor ma modulo (27z_1^2+1) stałą resztę (-663552).
4. W karcie (u) pozostały brzeg ma (z_2=z_3=0). Pierwszy minor jest niezerowy przy (z_0=0); przy (z_0\ne0) punkt należy do karty (a). To zamyka pokrycie.

Nie chodzi o test kilku punktów: reszty i warunki odwracalności pokazują, że wszystkie algebraiczne zera pierwszych minorów są pokryte przez kolejne.

### Rozszerzenie z włókna na całą q-kartę

q-baza ma działanie \(\mathbb G_m\) z dodatnimi wagami (p:2,r:4,s:6,t:2,w:10), ściągające całą bazę do jej początku. Oba ideały kolejnych ośrodków są jednorodne, więc działanie podnosi się do projektowego morfizmu końcowego. Zbiór punktów osobliwych końcowej przestrzeni jest zamknięty, a jego obraz w q-bazie jest zamknięty dzięki właściwości. Gdyby był niepusty, jako zbiór niezmienniczy zawierałby początek. Całe włókno nad początkiem jest gładkie z poprzednich kontroli, więc obraz jest pusty. Końcowa przestrzeń jest gładka nad całą q-kartą.

Ośrodek ostatniego rozdmuchania nie dotyka gładkich punktów poprzedniego modelu: jest domknięciem ścisłego obrazu gęstej części (S_{22}), gdzie pozostaje poprzeczna osobliwość (A_1), a zbiór osobliwy jest zamknięty. Dlatego gładkie punkty nad q-początkiem z §2 pozostają bez zmian.

## 4. Drugi koniec pierwszego włókna: h-karta

q-karta pomija w pierwszym wyjątkowym \(\mathbb P^1\) tylko punkt h-karty (p=r=s=t=w=0). Poza pierwotnym zerem wszystkie straty opisano w §6. Pozostała kontrola dotyczy wyłącznie tego punktu.

Na otoczeniu (U=8pt+25\ne0) ścisły ośrodek potrójny h-karty jest generowany przez
\[
w,\quad f_1=9st^3-32prt+45p^2-100r,\quad
f_2=9rst^2-32pr^2+15pst-375s.
\]
Równość z pełnym nasyconym ideałem sprawdza eliminacja
\[
r=\frac{9(5p^2+st^3)}{4(8pt+25)}.
\]
Po niej wszystkie pozostałe generatory są wielokrotnościami jednego wielomianu
\[
216p^5-8p^3st^3+825p^2st^2+7500pst-27s^2t^5+12500s,
\]
a (f_2) jest jego niezerową stałą razy jednostką. Jest to pełny opis na (U\ne0), obejmującym badany punkt.

`c2a5_h_triple_charts.py` liczy trzy karty Reesa, nasycając przez (vU). Ich włókna nad tym punktem mają wymiar 1:

| Karta | Równanie włókna | Minor rzędu4 |
|---|---|---|
| (w) | (y_2^2=45) | (9375000y_2\ne0) |
| (f_1) | (45y_0^2=y_2^2) | tylko przecięcie linii wymaga dalszego kroku |
| (f_2) | (45y_0^2=1) | (421875000y_0\ne0) |

Każdy punkt środkowej karty poza (y_0=y_2=0) jest w jednej ze skrajnych kart. Zostaje zatem jeden punkt (P_h) z wszystkimi ośmioma współrzędnymi równymi zero.

## 5. Ostatni h-punkt: skończony certyfikat z wyrazów kwadratowych i sześciennych

W środkowej karcie używamy ośmiu współrzędnych (p,r,s,t,w,y_0,y_2,v). Pełny ideał karty ma 33 generatory z dokładnej saturacji `c2a5_h_triple_chart1.sing`. Pierwsze trzy to
\[
\begin{aligned}
wy&=y_0v-w,\\
rv&=9st^3-32prt+45p^2-100r-v,\\
sv&=9rst^2-32pr^2+15pst-y_2v-375s.
\end{aligned}
\]
Ich pochodne po (w,v,s) mają niezerowy wyznacznik w (P_h). Definiują więc gładki pięciowymiarowy germ (W), w którym poprzedni model (X_1) jest całkowitym germem kowymiaru1.

Ścisły ośrodek (S_{22}) jest pierwszym ideałem wymiaru2; pełna saturacja przez (vsU), dająca 31 generatorów, jest w `c2a5_h_R_dd.sing`. Wybieramy z niego
\[
\begin{aligned}
A&=y_0,\\
B&=12pt^2y_2-12prt-20p^2-25ty_2+100r,\\
C&=4r^2t-16st^2+12pty_2-4pr-25y_2.
\end{aligned}
\]
Pierwsze trzy równania (W) wraz z (A,B,C) mają rangę Jacobiego6 w (\mathbb A^8); dołączenie (p,t) daje odwracalną macierz8×8. Zatem definiują gładki germ powierzchni i ((A,B,C,p,t)) są współrzędnymi na (W). Te sześć równań należy do pierwszego ideału ośrodka wysokości6. Ich lokalny iloraz jest regularną dziedziną wymiaru2, więc zawierający je ideał pierwszy tej samej wysokości jest im równy. **Ośrodek na (X_1) jest lokalnie dokładnie ((A,B,C)).**

Siódmy generator pełnej karty,
\[
\begin{aligned}
F={}&144rt^2y_2^2-288r^2ty_2-180st^2y_2-140pty_2^2+144r^3\\
 &+180rst+140pry_2+300ps-5625y_0^2+125y_2^2,
\end{aligned}
\]
zeruje się na (X_1\subset W). Mamy (F\in(A,B,C)^2). Uzasadnienie nie wymaga normalności (X_1): regularny lokalny pierścień (W) jest UFD, a ideał całkowitego germu (X_1) wysokości1 jest główny. Każde równanie (F) tego germu ma zerową różniczkę na jego zbiorze osobliwym. Ścisły ośrodek leży w tym zbiorze przez argument domknięcia z §3. Ponieważ ośrodek w (W) jest gładki, znikanie funkcji i jej pierwszego wyrazu normalnego oznacza właśnie przynależność do kwadratu ideału.

W punkcie (P_h) forma kwadratowa normalna jest
\[
F_2=-5625A^2+\frac15C^2.
\]
W rozdmuchaniu (W) w ((A,B,C)) daje to dwie proste w wyjątkowej \(\mathbb P^2\). Poza ich przecięciem gradient formy jest niezerowy, więc ścisła transformata (F=0) jest gładka. Jedyne przecięcie to punkt karty (B) z (A/B=C/B=0).

Tam wystarcza jeden wyraz sześcienny, również policzony **dokładnie**, bez obcięcia nieznanej funkcji: na krzywej (p=t=A=C=0) równania (W) dają
\[
y_2=s=w=0,\quad v=-100r,\quad B=100r,\quad F=144r^3.
\]
Zatem w karcie (B), po podzieleniu (F) przez (B^2), pochodna po (B) wynosi (144/100^3\ne0). Ścisła transformata (F=0) jest gładka również w ostatnim punkcie.

**Dlaczego wystarcza to dla rzeczywistego rozdmuchania (X_1)?** Surjekcja algebr Reesa daje zamknięte zanurzenie \(\operatorname{Bl}_{(A,B,C)}X_1\) w \(\operatorname{Bl}_{(A,B,C)}W\). Ponieważ karta rzeczywistego rozdmuchania jest podpierścieniem lokalizacji dziedziny, jest całkowita; równanie podzielone przez współrzędną wyjątkową do potęgi2 nadal zeruje się na niej. Leży więc w ścisłej transformacie (F). Ta ostatnia jest gładkim czterowymiarowym germem w każdym punkcie badanego włókna. Zamknięty całkowity czterowymiarowy germ w gładkim czterowymiarowym germie ma zerowy lokalny ideał. Oba germy są równe, a rzeczywiste rozdmuchanie jest gładkie.

Ten skończony argument sprawdza `verify236_h_jet.py`; wynik to `certificate236_h_jet.json`. Kosztowne próby `c2a5_h_R_dd_chart*.sing` nie są przesłankami dowodu i nie są potrzebne do odtworzenia certyfikatu.

## 6. Krepantność poza zerem: pełny katalog stabilizatorów

Gdy multizbiór pierwiastków nie jest zachowany przez zmianę znaku, stabilizator jest podgrupą (A_5). Pierwszy krok jest lokalnie identycznością, a pozostałe dwa rozdmuchania są dokładnie tymi z §2 `PROOF234.md`; obejmuje to również (A_4) dla (4+1) i (S_3) dla (3+2).

Multizbiór zachowany przez zmianę znaku ma postać (0,\pm a,\pm b). Poza zerem pojawiają się tylko trzy dodatkowe możliwości:

1. (a,b\ne0,a\ne\pm b): stabilizator (C_2), poprzeczne (A_1). Rozwiązuje je już pierwsza ekstrakcja.
2. Trzy zera i para (\pm a\ne0): stabilizator (S_3), lokalne równanie (w^2=s(q^2+p^3)) plus wolny parametr. Pierwszy ośrodek to ((s,w,q^2+p^3)). Rozdzielenie bazy (w^2=sc), (c=q^2+p^3), ma jedną gładką kartę oraz kartę (q^2+p^3=sz^2). Ścisły ośrodek potrójny to ((p,q,z)). Jego karty mają równania (v^2+p=su^2), (1+qv^3=su^2), (u^2+zv^3=s); wszystkie są gładkie. Pierwszy krok jest krepantny przez adjunkcję po bazowym (A_1), drugi ma rozbieżność (3-1-2=0).
3. (0,a,a,-a,-a), (a\ne0): stabilizator (V_4), model (e^2=xyz) plus wolny parametr. Ośrodek pierwszego kroku to ((z,e,xy)). Jego rozdzielenie ma jedną gładką kartę oraz (xy=zt^2). Ośrodek dwóch podwójnych pierwiastków to ((x,y,t)). Karty (v=zu^2) i (uv=z) są gładkie; obydwa kroki są krepantne przez tę samą adjunkcję.

W modelach złożonych (w^2=sc(p,q)) pierwsze rozdmuchanie można oglądać w gładkiej przestrzeni z niezależnym (c) i dodatkowym równaniem (c-c(p,q)=0). To drugie równanie nie ma wyjątkowego czynnika, co uzasadnia zastosowanie adjunkcji także w punkcie, gdzie (dc(p,q)=0).

Lista jest wyczerpująca, ponieważ nieparzysta liczba pięciu pierwiastków wymaga zera, a pozostałe krotności występują parami. W rezultacie końcowy morfizm jest krepantny poza pierwotnym zerem.

## 7. Włókno centralne i globalny wniosek

W q-karcie cztery pliki `c2a5_q_dd_original_fiber0.sing`–`3.sing` sprawdzają **całe włókno nad pierwotnym zerem**, pozostawiając parametr (t) swobodny. Podstawiają (p=0,r=u+r_0=0,L=V+L_0=0) do pełnych nasyconych kart. Każda ma wymiar włókna2.

Te cztery karty wystarczają tam, gdzie ostatni ośrodek może spotykać centralne włókno karty (L). Brzeg poza (L) w karcie (J) ma (b=0). Przy (t\ne0) równanie włókna daje (a^2=125t^2/81\ne0), więc pochodna po (a) nie znika; przy (t=0) pochodna po (r) wynosi (-16/9). Brzeg jest gładki i ostatni ośrodek go nie dotyka. Karta (w) na tym brzegu jest pokryta przez (J). Przed ostatnim krokiem jej centralne włókno miało wymiar2, a więc zachowuje ten wymiar.

Na końcu h-włókna pierwsze dwa kroki dają dwie krzywe; ostatni krok zastępuje wyłącznie ich jeden punkt podzbiorem opisanej w §5 stożkowej krzywej w \(\mathbb P^2\). Wymiar tej części nie przekracza1. Całe końcowe włókno nad zerem ma zatem wymiar najwyżej2.

Końcowe (Y) jest gładkie z §§3–6, a morfizm (Y\to X) projektowy i biracjonalny jako złożenie rozdmuchań niezerowych ideałów dziedzin. Jest krepantny poza zerem. Każda rozbieżność jest współczynnikiem dzielnika na (Y); czterowymiarowy (Y) nie ma dzielnika zawartego we włóknie wymiaru2. Nie może więc pojawić się nowa rozbieżność nad zerem. Morfizm jest globalnie krepantny.

Nie potrzeba w tym ostatnim argumencie normalności wszystkich modeli pośrednich: wykorzystujemy gładkość modelu końcowego, rzeczywiste algebry Reesa i wymiar jego całego włókna centralnego.

## 8. Uruchomienie i zakres weryfikacji

W publicznym suplemencie pełną świeżą kontrolę uruchamia
`sage -python geometry_proofs/run.py --case 236 --output-dir /tmp/geometry-236`.
Katalog wynikowy musi być nowy lub pusty. `run.json` zapisuje rzeczywiste
wyniki etapów, logi i hashe wejść; skrypty kart i ich wyniki powstają w `work/`.

Jest to własny dowód konstrukcyjny, z odtwarzalną algebrą wielomianową; cytowane twierdzenia o istnieniu rozdzielenia w niższych wymiarach go nie zastępują. Pełne przedstawienie przez dyskryminant i ostrzeżenie o zakresie (n<4) pracy [Paranjape–Ramakrishnan](https://arxiv.org/abs/math/0411310) omówiono w `PROOF234.md`. Rozbieżności obliczono bezpośrednio przez adjunkcję; wniosek nie opiera się na samym teście juniorów ani na niepełnej homogenizacji Coxa.

Główne pliki kontrolne: `c2a5_direct_first.py`, `c2a5_q_triple_charts.py`, `c2a5_q_dd_charts.py`, trzy skrypty kontroli Jacobiego q, cztery skrypty całego włókna pierwotnego, `c2a5_h_triple_charts.py`, `c2a5_h_R_dd.sing`, `verify236_h_jet.py`.
