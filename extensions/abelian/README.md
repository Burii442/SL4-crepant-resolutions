# Actual abelian character lattices

This check reconstructs the abelian matrix groups from `legacy245/catalogue.json`,
decomposes their actual natural characters in GAP, and compares every fractional
character vector with `legacy245/abelian_characters.csv`, allowing one permutation
of the four coordinates. No saved success flag or character export is consumed.

```sh
python3 extensions/abelian/verify.py --output-dir /tmp/sl4-abelian-lattices
python3 extensions/abelian/verify.py --legacy-case 210 --output-dir /tmp/sl4-case210-lattice
```

The default checks all 68 abelian entries of the old catalogue. These represent
32 of the current complex conjugacy classes: 17 positive cases in Sieve C and
15 negative cases already excluded by Sieve A. The exact Sage fan check remains
`legacy245/run_verification.py --steps geometry`. Together the two computations
bind every certified fan to the actual quotient lattice and verify its coherent
unimodular full cover. The classical toric resolution theorem supplies the
geometric implication.

Requirements: Python 3 and GAP; select the latter with `--gap` if necessary.
The output directory must be fresh and outside the repository. GAP matrices,
actual character data, logs, input hashes and a scope-specific report are retained.
