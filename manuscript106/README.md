# Manuscript catalogue and sieve inputs

Case numbers refer to the 106 representatives in the manuscript.

| Directory | Inputs and checks |
|---|---|
| [catalogue/](catalogue/README.md) | Ordered integral matrices and all 139 rational conjugating matrices for the 245-to-106 reduction |
| [sieves/](sieves/README.md) | Fourteen criterion families, recorded applications and exhaustive enumeration of the finite minimum-cover problem |

From the repository root, use:

```sh
python3 reproduce.py --profile portable --run-dir ../sl4-results/portable-001
```

The runner works in a copy and writes fresh reports outside the repository.
The independent CrystCat comparison is in [classification/](../classification/README.md).
The complete Cox computations are in [legacy245/](../legacy245/README.md);
the four complete-intersection presentations are checked by
[extensions/dhz/](../extensions/dhz/README.md).

Matrix and finite-incidence checks do not independently prove every geometric
YES/NO decision. The [case index](../cases/README.md) states the separate scopes.
