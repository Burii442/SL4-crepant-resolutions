# Matrix catalogue and conjugacy certificates

From the repository root, run with Python 3 and its standard library:

```sh
python3 reproduce.py --profile portable --run-dir ../sl4-results/catalogue-001
```

The runner executes the catalogue and reduction verifiers in an isolated
copy, together with the sieve and CE-03/CE-07 checks. Choose a new or empty
output directory outside the repository and read its `REPORT.txt`.

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

Within the isolated run, the verifiers produce `verification_106.json` and
`verification_reduction.json` and reconstruct `catalogue_reduced.json` with
the old-to-new index mapping. The distributed inputs remain unchanged.
Neither verifier uses a stored PASS report as evidence.

## Scope

These checks prove pairwise nonconjugacy of the 106 representatives and
correct reduction of the supplied 245-entry list. They do not prove that the
input list exhausts all finite subgroups of SL4(Z). The independent
[CrystCat comparison](../../classification/README.md) supplies the link with
the exhaustive classical catalogue. The geometric YES/NO decisions are
proved by the manuscript’s sieves and their corresponding checks.

## Source files

The catalogues and rational conjugating matrices are the exact inputs for
the 245-to-106 reduction. Each verification report records its input and
program hashes. The runner also writes `input_manifest.json` in the output
directory, identifying the complete frozen input copy.
