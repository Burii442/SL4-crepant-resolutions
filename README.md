# Crepant resolutions of four-dimensional finite quotients

[![Portable exact checks](https://github.com/Burii442/SL4-crepant-resolutions/actions/workflows/portable.yml/badge.svg)](https://github.com/Burii442/SL4-crepant-resolutions/actions/workflows/portable.yml)
[![Sage environment checks](https://github.com/Burii442/SL4-crepant-resolutions/actions/workflows/sage.yml/badge.svg)](https://github.com/Burii442/SL4-crepant-resolutions/actions/workflows/sage.yml)

Verification programs for the manuscript by **Dominik Burek and Sławomir Cynk**:
**106 quotient representations, 61 YES and 45 NO**. The
[case index](cases/README.md) links every case to its integral matrices,
earlier catalogue numbers and applicable checks.

This repository contains verification code, required mathematical input data
and instructions. Results and logs are generated outside the checkout.
Manuscripts, conversations, working notes and saved execution reports are
excluded. Matrix entries, polynomial presentations, fans and exact algebraic
certificates are retained as inputs and checked afresh by the programs.

## Quick start

Use Python 3.9 or later on Linux, macOS, or Windows through WSL2.
While the repository is private, GitHub access is required to clone it.
The portable checks need only the Python standard library:

```sh
git clone https://github.com/Burii442/SL4-crepant-resolutions.git
cd SL4-crepant-resolutions
python3 reproduce.py --profile portable --run-dir ../sl4-results/portable-001
```

This reconstructs the 106 matrix groups, checks the 245-to-106 reduction,
the finite sieve cover and the CE-03/CE-07 group calculations. Read
`REPORT.txt` or `status.json` in the output directory. The overall status
must be `PASS`. The portable profile checks recorded geometric labels for
consistency; it does not establish every geometric YES/NO decision.

## Full reproduction

Install SageMath, GAP with CrystCat and SmallGrp, Singular and a C++17 compiler
using the [installation guide](docs/reproducibility.md#installation), or use
the supplied [Docker environment](docs/reproducibility.md#docker).
Magma and AI services are not required.

```sh
python3 reproduce.py --check-tools
python3 reproduce.py --plan
python3 reproduce.py --profile all --run-dir ../sl4-results/full-001
```

The full profile has **47 stages**. It incorporates all **77 legacy checks**
in 14 shared stages and 21 complete binding/Cox/endpoint bundles, together with
the current catalogue, cross-case counterexample, Gachet, abelian, E/F and DHZ
checks. The [coverage map](verification/coverage.json) identifies the stages
and labels five inherited compact/Kummer checks.

An optional `--paper /path/to/manuscript.tex` adds a 48th stage comparing the
106 printed matrix blocks. A manuscript file is not required for the other
calculations and is not distributed here.

Some Cox calculations take hours or longer. To check progress or resume:

```sh
python3 reproduce.py --status ../sl4-results/full-001
python3 reproduce.py --resume ../sl4-results/full-001
```

Use `--background` for an independent local process. New runs require a new
or empty output directory outside the repository. Resuming uses frozen
programs and inputs, verifies saved evidence hashes and retains completed
stages. An interrupted Cox bundle restarts as a whole. Keep Python assertions
enabled. See the [guide](docs/reproducibility.md) for stopping a run, runtime
overrides and interpreting failures.

## Individual cases

The original dispatcher remains available:

```sh
python3 verify.py --list
python3 verify.py --case 45 --plan
python3 verify.py --case 45 --output-dir ../sl4-results/case-045
```

It combines the legacy stages and extensions assigned to a manuscript case
and writes `verification.json`. It has no checkpoints and does not add every
current cross-case comparison. Use `reproduce.py` for the full current suite.

The earlier catalogue has **245 integral representations**. Files under
`legacy245/` retain those numbers because the exact polynomial presentations
depend on their inputs. Consult [the number map](cases/index.json) before
interchanging manuscript and legacy numbers.

## Contents and scope

| Directory | Contents |
|---|---|
| [cases/](cases/README.md) | Input and execution map for cases 001–106 |
| [manuscript106/](manuscript106/README.md) | Matrix catalogue, conjugating matrices and finite sieve-cover inputs |
| [legacy245/](legacy245/README.md) | Cox, binding, endpoint, toric, invariant-ring and geometric verification programs and inputs |
| [classification/](classification/README.md) | CrystCat enumeration and independent catalogue comparison |
| [extensions/](extensions/) | Abelian character, E/F geometry and four DHZ invariant-ring checks |
| [verification/](verification/) | Runtime checks, strict output validation, cross-case checks and the resumable execution plan |

For the four nonabelian counterexamples to the Dais–Henk–Ziegler conjecture
(cases 45, 65, 66 and 105), the programs check both the complete-intersection
presentations and the full Cox-ring generation and geometric endpoint
calculations. The proof that these quotients have no projective crepant
resolution combines these computations with the criteria in Sieve I of the
manuscript. More generally, the verification follows the arguments in the
paper: exact group and ring computations are combined with the stated
geometric theorems. The finite minimum-cover check concerns the fourteen
recorded families of applications.

GitHub Actions tests the portable profile, checkpoint reuse, runtime selection
and small fresh Sage/GAP calculations. Its badges do not assert completion of
the full 47-stage suite. Users with workflow permissions can run these checks
from the Actions tab. Full calculations run on the user's own computer or
server. CI does not upload calculation reports as artifacts.

Citation metadata is in [CITATION.cff](CITATION.cff). Third-party notices are
in [THIRD_PARTY.md](THIRD_PARTY.md). The authors have not yet selected a
project-wide public reuse license; the repository remains private.
