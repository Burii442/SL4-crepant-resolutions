# Matrix catalogue and conjugacy certificates

Run with Python 3 (standard library only), from this directory:

```sh
python3 verify_catalogue.py
python3 verify_reduction.py
```

`catalogue.json` gives the 106 representatives used in Appendix A, with the
ordered integral generators, group orders, spectral distributions and outcome
labels. The first verifier reconstructs each finite group with exact matrix
arithmetic, checks determinant one and the stored order, and verifies 106
pairwise distinct characteristic-polynomial distributions. Distinct such
distributions imply nonconjugacy over C.

`catalogue_245.json` is the input list used before reduction.
`conjugacy_certificates.json` gives all 139 rational conjugating matrices.
The second verifier reconstructs all 245 groups and checks equality of the
complete conjugated matrix sets. It also checks that the selected generators
and their order agree exactly with the delivered 106-case catalogue.
Rescaling each rational conjugating matrix by a fourth root of the inverse
of its determinant gives a matrix in SL4(C) with the same conjugation action.

The resulting reports are `verification_106.json` and
`verification_reduction.json`; `catalogue_reduced.json` is a reconstructed
copy with the old-to-new index mapping. Neither script uses a stored PASS
report as evidence.

## Scope

These checks prove pairwise nonconjugacy of the 106 representatives and
correct reduction of the supplied 245-entry list. They do not prove that the
input list exhausts all finite subgroups of SL4(Z). The independent CrystCat comparison in `../../classification/` supplies
the separate link with the exhaustive classical catalogue. The earlier
empty Section 4 has been removed from the manuscript. The checks count the stored YES/NO
labels but do not independently prove those geometric decisions.

## Source files

The two catalogues and the conjugacy certificates are byte-for-byte copies of
the corresponding project data. The verifiers are portable adaptations of
`sprawdz_katalog.py` and `sprawdz_redukcje.py`, with local paths, explicit scope,
and an added comparison with the delivered 106-entry catalogue. The root
manifest records hashes for all delivered files.
