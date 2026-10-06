# Supported geometric proof calculations

These packages accompany Sections 7–8 of the article and run independently of the authors' former directory layout. They require SageMath (including SymPy, Singular and GAP). No archived log, stored PASS flag or reviewer directory is an input.

The runner records its Sage cache path and ownership in the report. It inherits a whitespace-free `DOT_SAGE` from the unified runner when available; otherwise it chooses an output-local cache or a fresh temporary path without whitespace. It never deletes an inherited cache or removes a temporary cache while its process group remains alive.

From the supplement directory:

```sh
sage -python geometry_proofs/run.py --case 132 --output-dir /tmp/geometry-132
sage -python geometry_proofs/run.py --case 234 --output-dir /tmp/geometry-234
sage -python geometry_proofs/run.py --case 236 --output-dir /tmp/geometry-236
```

Each output directory must be new or empty. The wrapper copies the required inputs there, creates the GAP matrix list from the current `catalogue.json`, and performs every stage afresh. Optional `--singular` and `--gap` arguments select executables. There is no fixed short timeout. The wrappers propagate failed assertions and incomplete chart calculations as failures.

| Representative | Covered indices | Fresh assertions |
|---|---|---|
| 132 | 132–137 | Full matrix-group equality with the even-sign/C3 model; all three A2 charts and their overlap equations; critical-curve translation; strict-transform equations and explicit smoothness identities for the final three charts. |
| 234 | 234–235 | Discriminant and both complete stratum kernels; five saturated Rees charts and exact central-fiber ideals; input binding and boundary minors; full eliminated hypersurface and saturated second center; three final smooth charts; local nonzero-stabilizer models and representation transfer. |
| 236 | 236–237 | Discriminant and complete stratum kernels; contracted centers; full q-Rees input and saturation; four final q-charts, all minor-cover identities and whole original fiber dimensions with t free; all h-boundary fibers; freshly constructed final h-center; exact local quadratic/cubic calculation at its remaining point; representation transfer. |

`run.json` is written before and after each stage and records status, input SHA-256 hashes, elapsed time, executable paths and per-stage logs. `work/` retains freshly generated equations and certificates. Mathematical implications such as projectivity and crepancy are explained in the article and the accompanying proof text; a computed identity is not a substitute for those arguments.

The files containing row/column choices and determinant witnesses are mathematical inputs. The validators differentiate the fresh full relation ideals, recompute the determinants, and check their covering identities. Similarly, the stored four generators of each stratum are checked against an independently eliminated full kernel. The final h-center is generated from the current stratum generators and current Rees equations; its saved source is not trusted in place of that calculation.
