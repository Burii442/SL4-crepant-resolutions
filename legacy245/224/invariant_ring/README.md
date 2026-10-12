# Legacy case 224: invariant ring

These inputs support [manuscript case 90](../../../cases/090/README.md).

`ring_certificate.json` gives the ordered invariant polynomials in the original matrix coordinates, their weights, the minimal defining relations, and the exact Molien series. `coordinates.json` identifies the variables used in the article. The matrices are in `input_matrices.json`; `compute_invariants.sing` and the complete polynomial lists are supplied for inspection.

From the repository root, run all invariant-ring and abelian-fan checks in an isolated copy:

```sh
python3 legacy245/run_verification.py --steps geometry --output-dir ../sl4-results/invariant-rings-001
```

Use a new or empty output directory. The checks verify exact invariance, the complete elimination kernels and Molien/Hilbert equality. The geometric construction for this case is covered by [Sieve F](../../../docs/methods.md#sieve-f) in the manuscript.
