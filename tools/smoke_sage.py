#!/usr/bin/env python3
"""Fresh, bounded Sage smoke checks; not the complete reproducibility suite.

Run with Python or ``sage -python``. Required tools are discovered through the
same helper as reproduce.py; --sage/--gap/--singular/--cxx override discovery.
The manuscript is deliberately omitted. Output must be a new external directory.
No saved verification outputs are treated as freshly computed certificates.
"""
import argparse
import datetime as dt
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import time

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
REQUIRED = ("sage", "gap", "singular", "cxx")
CLAIMS = {"CE02", "CE03_table_selection", "CE05", "CE06", "CE10", "CE12"}
GACHET_MARKER = "PASS: two dual representations; age polynomial 1+t+2*t^2+2*t^3+t^4; b2=1, b4=2."


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--timeout", type=float, default=180,
                        help="Maximum seconds per calculation (default: 180)")
    for name in REQUIRED + ("magma",):
        parser.add_argument("--" + name)
    args = parser.parse_args()
    if sys.flags.optimize or os.environ.get("PYTHONOPTIMIZE"):
        parser.error("Assertions must remain enabled")
    out = args.output_dir.expanduser().resolve()
    if out == ROOT or ROOT in out.parents or out in ROOT.parents:
        parser.error("Output must be outside the repository and its ancestors")
    if out.exists() and (not out.is_dir() or any(out.iterdir())):
        parser.error("Output must be new or empty")
    if args.timeout <= 0:
        parser.error("Timeout must be positive")
    out.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    report = dict(status="RUNNING", complete=False,
                  created_utc=dt.datetime.now(dt.timezone.utc).isoformat(),
                  scope="Runtime preflight, supplementary exact claims, Gachet ages and legacy criterion coverage only.",
                  paper_binding="not_requested", steps=[],
                  input_sha256={"smoke_program": sha(__file__), "reproduce_program": sha(ROOT/"reproduce.py")})

    def save():
        report["seconds"] = round(time.monotonic() - started, 3)
        (out/"report.json").write_text(json.dumps(report, indent=2) + "\n")

    save()
    try:
        reproduce = load(ROOT/"reproduce.py", "sl4_smoke_reproduce")
        runtime = load(ROOT/"verification/runtime_probe.py", "sl4_smoke_runtime")
        validation = load(ROOT/"verification/validation.py", "sl4_smoke_validation")
        overrides = {name: getattr(args, name) for name in REQUIRED + ("magma",)}
        tools = reproduce.probe_runtimes(runtime, "all", overrides, output_dir=out/"runtimes")
        report["runtimes"] = tools
        bad = [name for name in REQUIRED if tools.get(name, {}).get("status") != "pass"]
        require(not bad, "Runtime preflight failed: " + ", ".join(bad))
        report["steps"].append(dict(name="preflight", status="PASS"))
        save()
        paths = {name: tools[name]["path"] for name in REQUIRED}
        env = os.environ.copy()
        bindir = out/"bin"
        bindir.mkdir()
        for name, key in (("sage", "sage"), ("gap", "gap"), ("Singular", "singular"),
                          ("singular", "singular"), ("g++", "cxx")):
            link = bindir/name
            if link.is_symlink():  # Singular/singular coincide on typical macOS disks.
                link.unlink()
            link.symlink_to(paths[key])
        env.update(PATH=str(bindir) + os.pathsep + env.get("PATH", ""),
                   SL4_TOOL_BIN=str(bindir), SL4_SINGULAR=paths["singular"],
                   PYTHONDONTWRITEBYTECODE="1", PYTHONUNBUFFERED="1", OMP_NUM_THREADS="1")
        cache = out/"cache"
        cache.mkdir()
        env.update(DOT_SAGE=str(cache), SL4_RUNTIME_CACHE=str(cache), XDG_CACHE_HOME=str(cache/"xdg"))
        logs = out/"commands"
        logs.mkdir()

        def run(name, command):
            print("START " + name, flush=True)
            result = runtime._run(command, cwd=out, env=env, timeout=args.timeout)
            logfile = logs/(name + ".log")
            logfile.write_text(result.pop("output"))
            step = dict(name=name, log=str(logfile.relative_to(out)),
                        log_sha256=sha(logfile), **result)
            # _run's execution status is distinct from mathematical validation.
            step["execution_status"] = step.pop("status")
            step["status"] = "RUNNING"
            report["steps"].append(step)
            save()
            require(step["returncode"] == 0 and step["execution_status"] == "completed",
                    name + " subprocess failed; see " + str(logfile))
            return step, logfile

        claims_source = ROOT/"verification/verify_paper_claims.py"
        step, _ = run("claims", [paths["sage"], "-python", str(claims_source),
                                "--repo", str(ROOT), "--output-dir", str(out/"claims")])
        proof = out/"claims/report.json"
        claims = json.loads(proof.read_text())
        require(claims.get("status") == "PASS" and claims.get("complete") is True,
                "Supplementary claims did not complete")
        require(set(claims.get("checks", {})) == CLAIMS and
                all(v.get("status") == "PASS" for v in claims["checks"].values()),
                "Required exact claims are missing or failed")
        require(claims.get("paper_binding") == {"status": "not_requested"} and
                claims.get("input_sha256") == {"program": sha(claims_source),
                    "catalogue": sha(ROOT/"manuscript106/catalogue/catalogue.json")},
                "Claim input binding differs from this run")
        step.update(status="PASS", proof_sha256=sha(proof))
        save()

        gachet_source = ROOT/"verification/gachet_cohomology.g"
        step, log = run("gachet", [paths["gap"], "-q", "--quitonbreak", str(gachet_source)])
        require(GACHET_MARKER in log.read_text().replace("\\\n", ""),
                "Gachet completion assertion missing")
        step.update(status="PASS", input_sha256=sha(gachet_source))
        save()

        step, _ = run("legacy-criteria", [sys.executable, str(ROOT/"legacy245/run_verification.py"),
                                         "--steps", "criteria", "--sage", paths["sage"],
                                         "--output-dir", str(out/"legacy-criteria")])
        checked = validation.validate_legacy(out/"legacy-criteria", ["criteria"])
        (out/"legacy-validation.json").write_text(json.dumps(checked, indent=2) + "\n")
        step.update(status="PASS", validated_certificate=checked)
        report.update(status="PASS", complete=True)
        save()
        print("PASS: four fresh smoke stages; the full verification suite was not run.", flush=True)
        print(str(out/"report.json"), flush=True)
        return 0
    except BaseException as error:
        report.update(status="INTERRUPTED" if isinstance(error, KeyboardInterrupt) else "FAILED",
                      error=str(error) or type(error).__name__)
        if report["steps"] and report["steps"][-1]["status"] == "RUNNING":
            report["steps"][-1]["status"] = report["status"]
        save()
        raise


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(130)
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(str(error), file=sys.stderr)
        raise SystemExit(1)
