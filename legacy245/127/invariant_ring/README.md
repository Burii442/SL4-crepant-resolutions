# Case 127: invariant ring

`ring_certificate.json` gives the ordered invariant polynomials in the original matrix coordinates, their weights, the minimal defining relations, and the exact Molien series. `coordinates.json` identifies the variables used in the article. The matrices are in `input_matrices.json`; `compute_invariants.sing` and the complete polynomial lists are supplied for inspection.

Run the supplement's `verify_geometry.py` with SageMath to verify invariance, the complete elimination kernel and Molien/Hilbert equality from these inputs. The crepant blow-up and smoothness argument is in Part IV of the article.
