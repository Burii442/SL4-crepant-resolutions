# The minimum cover of the recorded applications

From the repository root, run the portable checks with Python 3:

```sh
python3 reproduce.py --profile portable --run-dir ../sl4-results/sieves-001
```

This runs the sieve verifier together with the catalogue and CE-03/CE-07
checks in an isolated copy. No third-party Python packages are needed.
The output directory must be new or empty and outside the repository.
Read `REPORT.txt` there; a complete successful run has status `PASS`.
Keep Python assertions enabled.

The finite library contains fourteen named families. The ten retained
families use the manuscript labels A–J. The other four are independent
quotient factors, Davis's cyclic-fourfold tests, Fujiki–Oka resolutions, and
Roan's scalar-quotient obstruction. `families.json` gives their names,
historical labels, reference keys, and the ten cases covered by a unique family.

`original_applications.csv` preserves all 341 recorded decisive applications
to the earlier 245 matrix entries. `catalogue_projection.json` assigns each
old entry to one of the 106 manuscript classes. Projecting and merging
duplicate applications gives the 155 rows of `recorded_applications.csv`;
the last column retains the old entries responsible for each row.
Every outcome is checked against the corresponding class decision.

The historical abelian family C includes 17 positive and 15 negative
projected applications. The printed Sieve C records only the 17 positive
applications. All 15 negative abelian applications, and all 12 negative
cyclic-fourfold applications, are also covered by A. These exclusions do
not infer nonexistence from a failed construction or triangulation search.
`manuscript_assignments.json` preserves the actual A–J table assignments.
The verifier checks both the full historical library and the library with
C restricted to its printed positive applications; both have the same
unique smallest cover, A–J, of size ten.

The cases covered only by A–J respectively are 16, 13, 15, 14, 23, 28, 52,
31, 35, and 57. Each is covered by its named family and by no other family
in the fourteen-family library. Thus every cover must contain A–J; their
union covers all 106 classes. The verifier also enumerates all 16,384
subsets independently for each of the two libraries.

This is a minimum for a fixed, recorded incidence relation. The calculation
does not prove the geometric assertions underlying its rows, classify all
possible criteria, establish a lower bound for arbitrary combinations of
methods, or prove completeness of the group catalogue. The geometric
arguments belong to the manuscript and the corresponding computational
certificates. This folder needs no files outside itself to verify the
finite-cover calculation.

`provenance.json` contains the input hashes checked by the verifier, the
projection rule, and the scope of the finite-cover calculation.
