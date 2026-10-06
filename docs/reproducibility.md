# Reproducing the computations

The supported complete entry point is `reproduce.py`. It runs existing
mathematical programs in an isolated copy, validates their outputs and saves
checkpoints. Python assertions must remain enabled. The calculations make
no calls to AI services and do not require Magma or a network connection
after the software and repository have been obtained.

## Installation

Use Linux, macOS, or a Linux distribution under WSL2 on Windows. The resumable
runner uses POSIX process groups and file locking and does not support native
Windows Python. Python 3.9 or later is required.

For the portable profile, no third-party Python packages are needed:

```sh
python3 reproduce.py --profile portable --run-dir ../sl4-results/portable-001
```

For all calculations, install:

| Component | Purpose |
|---|---|
| SageMath 10.9 | Exact algebra, polynomial kernels, invariant rings and geometry |
| GAP with CrystCat and SmallGrp | Catalogue enumeration and finite-group identification |
| Singular | Gröbner bases, saturation and chart calculations |
| C++17 compiler, available as `g++` or `clang++` | Native exact checks |

The Sage environment must include its Singular interface, PyNormaliz, SymPy
and GAP packages. The preflight tests these components with actual small
calculations; an executable filename alone is not accepted.

Sage provides [official installation instructions](https://doc.sagemath.org/html/en/installation/index.html)
and [Conda instructions for Linux and macOS](https://doc.sagemath.org/html/en/installation/conda.html).
For an existing Conda installation, the upstream basic installation is:

```sh
conda create -n sl4 -c conda-forge sage=10.9
conda activate sl4
```

Check that CrystCat and SmallGrp are installed in the GAP used by the command
line and by Sage. Package-manager distributions may split them into separate
packages; see the [GAP package instructions](https://www.gap-system.org/Packages/packages.html).
For example, Debian/Ubuntu provides `gap-crystcat` and `gap-smallgrp`.
The Docker environment below supplies these packages explicitly.

After installation, from the repository root:

```sh
python3 reproduce.py --check-tools
```

Every required component must pass before starting a full run. Magma is an
optional diagnostic and may be absent. The local macOS framework launcher
also supports an existing SageMath app without modifying its installation.
To select programs explicitly:

```sh
python3 reproduce.py --check-tools --sage /path/to/sage --gap /path/to/gap --singular /path/to/Singular --cxx /path/to/g++
```

Use the same overrides when creating the run. They are recorded with it.

## Docker

The [Dockerfile](../Dockerfile) builds on the official
[`sagemath/sagemath:10.9` image](https://hub.docker.com/r/sagemath/sagemath/tags).
It includes the command-line dependencies and runs the environment preflight.
The reference image is Linux/amd64; Apple Silicon uses emulation with these
commands and may be substantially slower than native Sage.

```sh
docker build --platform linux/amd64 -t sl4-verification .
mkdir -p ../sl4-results
docker run --rm --platform linux/amd64 -v "$(cd ../sl4-results && pwd):/results" sl4-verification --check-tools
docker run --rm --platform linux/amd64 -v "$(cd ../sl4-results && pwd):/results" sl4-verification --profile all --run-dir /results/full-001
```

The mounted directory must be writable by the container user. Docker Desktop
handles this on macOS; on Linux, set ownership or access for the image's `sage`
user on this results directory. Do not make the repository writable to solve
an output-directory permission error. On Windows, run these shell commands
inside WSL2. If the foreground container is interrupted, start a new container
with the same image and volume and pass `--resume /results/full-001`.
Use Docker's detached mode (`docker run -d`) for background container runs;
do not use the Python runner's `--background` inside a disposable container.

The Sage base version is fixed. System package updates are not a bit-for-bit
environment lock; each run records the actual runtime versions. GitHub Actions
builds this image and exercises a small subset, not all long Cox calculations.

## Full runs and checkpoints

```sh
python3 reproduce.py --plan
python3 reproduce.py --profile all --run-dir ../sl4-results/full-001 --background
python3 reproduce.py --status ../sl4-results/full-001
```

Keep the computer awake. The macOS background launcher uses `caffeinate` to
prevent idle sleep; closing a laptop lid, rebooting or manually suspending it
can interrupt a run. Other systems should use their usual power settings.
The foreground form is the same command without `--background`.

The output contains:

- `REPORT.txt`: current state and completed stages;
- `status.json`: machine-readable state, timings and runtime checks;
- `inputs/`: the frozen programs, data and optional external manuscript;
- `steps/`: fresh certificates and logs, separated by stage and attempt;
- `input_manifest.json`: input hashes used to validate a resumed run.

Stop or resume a particular run with:

```sh
python3 reproduce.py --stop ../sl4-results/full-001
python3 reproduce.py --resume ../sl4-results/full-001 --background
```

Only completed stages whose saved evidence still matches are reused.
Interrupted stages restart in a new attempt directory. Binding, Cox generation,
Hilbert–Molien comparison and the geometric endpoint remain in the same bundle.
Changes to the checkout do not change a previously started run. To verify new
code or data, create a new output directory.

The runner requires at least 4 GiB free space before a full run. This is a
minimum guard, not a bound on total output or memory use. Large Gröbner-basis
calculations may take hours or longer and use substantial memory. Stages run
sequentially. A quiet log does not, by itself, indicate a stopped process.

## Scope and interpreting results

The default full profile comprises 47 stages. It includes all 77 earlier
checks and the current cross-case CE checks, the Gachet age calculation,
fresh CrystCat enumeration and the abelian, E/F and DHZ extensions. Five
labelled inherited stages concern additional compact/Kummer calculations.
The [coverage map](../verification/coverage.json) gives the correspondence.

To compare the matrices with an externally supplied manuscript, add
`--paper /path/to/manuscript.tex` when creating the run. This adds a 48th stage.
No PDF or LaTeX source is needed to reproduce the distributed computations.

`PASS` for the whole run requires all selected stages to pass. `FAILED` means
an execution error or a failed check: inspect the named stage's log. It is
not itself a geometric nonexistence result. Independent stages continue so
that one failure does not discard unrelated results. An absent prerequisite
blocks the dependent stage. The mathematical theorems cited in the paper
remain part of the proof; numeric output does not replace them.

The original `verify.py --case N` interface is retained for a single manuscript
case, and `verify.py --profile core` retains the earlier short suite. These
interfaces do not provide checkpointing or all current cross-case checks.
