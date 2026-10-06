#!/usr/bin/env python3
"""Read-only runtime discovery and small exact-mathematics preflight checks.

discover(sage=None, gap=None, magma=None, singular=None, cxx=None) returns records
with executable ``path`` and ``found``; no program is run during discovery.
probe(discovered=None, output_dir=None, timeout=30) returns fresh records with
``tested``, ``status`` (pass/failed/timed_out/missing), ``version`` and ``checks``.
All scratch/cache files are under output_dir or a private temporary directory.
Neither licenses nor global installation/configuration files are changed.
"""
import argparse
import copy
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import tempfile
import time


def _executable(value):
    if not value:
        return None
    expanded = os.path.expanduser(str(value))
    candidate = shutil.which(expanded)
    return os.path.abspath(candidate) if candidate else None


def discover(sage=None, gap=None, magma=None, singular=None, cxx=None):
    """Honor explicit executable overrides, including invalid ones (no fallback)."""
    launcher = Path(__file__).parent / "launchers/sage"
    bundle_candidates = list(Path("/Applications").glob(
        "SageMath-*.app/Contents/Frameworks/Sage.framework/Versions/Current/venv/bin/python3"))
    bundle_candidates += list((Path.home() / "Applications").glob(
        "SageMath-*.app/Contents/Frameworks/Sage.framework/Versions/Current/venv/bin/python3"))
    supplied = dict(sage=sage, gap=gap, magma=magma, singular=singular, cxx=cxx)
    defaults = {
        "sage": ([str(launcher)] if bundle_candidates or os.environ.get("SL4_SAGE_BUNDLE") else []) + ["sage"],
        "gap": ["gap", "/opt/homebrew/bin/gap"],
        "magma": ["magma", str(Path.home() / ".local/bin/magma")],
        "singular": ["Singular", "singular", "/opt/homebrew/bin/Singular"],
        "cxx": ["g++", "clang++", "/usr/bin/clang++"],
    }
    result = {}
    for name, override in supplied.items():
        options = [override] if override is not None else defaults[name]
        path = next((found for found in map(_executable, options) if found), None)
        result[name] = dict(path=path, found=bool(path), tested=False,
                            status="found" if path else "missing", version=None, checks={})
        result[name]["source"] = "override" if override is not None else (
            "macos_bundle_launcher" if path == str(launcher.absolute()) else "PATH_or_known_location")
        if override is not None:
            result[name]["requested"] = str(override)
    return result


def _signal_owned_group(process, signum):
    try:
        os.killpg(process.pid, signum)
    except ProcessLookupError:
        pass  # The process/group may have exited between communicate and killpg.


def _stop_owned_group(process):
    """Terminate our private session, escalate, and reap before propagating Ctrl-C."""
    interrupted = False
    try:
        _signal_owned_group(process, signal.SIGTERM)
        process.communicate(timeout=2)
    except subprocess.TimeoutExpired:
        pass
    except KeyboardInterrupt:
        interrupted = True
    finally:
        # Also stop descendants when the leader exited and closed its pipes.
        _signal_owned_group(process, signal.SIGKILL)
        while True:
            try:
                output = process.communicate()
                break
            except KeyboardInterrupt:
                interrupted = True
                _signal_owned_group(process, signal.SIGKILL)
    if interrupted:
        raise KeyboardInterrupt
    return output


def _run(command, *, cwd, env, timeout, input_text=None):
    started = time.monotonic()
    try:
        process = subprocess.Popen(command, cwd=cwd, env=env, stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                   text=True, start_new_session=True)
        try:
            output, _ = process.communicate(input_text, timeout=timeout)
            status = "completed"
        except subprocess.TimeoutExpired:
            output, _ = _stop_owned_group(process)
            status = "timed_out"
        except KeyboardInterrupt:
            _stop_owned_group(process)
            raise
        output = re.sub(r"(?i)\b(?:[0-9a-f]{2}:){5}[0-9a-f]{2}\b", "[MAC address redacted]", output)
        return dict(command=list(map(str, command)), returncode=process.returncode,
                    status=status, output=output[-20000:], seconds=round(time.monotonic() - started, 3))
    except OSError as error:
        return dict(command=list(map(str, command)), returncode=None, status="failed",
                    output=str(error), seconds=round(time.monotonic() - started, 3))


SAGE_CODE = '''from sage.all import *
from sage.version import version
from sage.libs.gap.libgap import libgap
assert QQ(1)/3 + QQ(1)/6 == QQ(1)/2
assert matrix(QQ, [[1,2],[2,4]]).rank() == 1
print("SL4_EXACT_PASS", flush=True)
R=PolynomialRing(QQ, 'x,y'); x,y=R.gens()
assert R.ideal([x*x-y,y*y-1]).reduce(x**4-1) == 0
print("SL4_SINGULAR_PASS", flush=True)
assert Polyhedron(vertices=[[0,0],[1,0],[0,1]], backend='normaliz').volume() == QQ(1)/2
print("SL4_NORMALIZ_PASS", flush=True)
assert bool(libgap.LoadPackage('crystcat'))
assert bool(libgap.LoadPackage('smallgrp'))
assert str(libgap.eval('1/3+1/6')) == '1/2'
print("SL4_GAP_PACKAGES_PASS", flush=True)
print("SL4_GAP_VERSION=" + str(libgap.eval('GAPInfo.Version')), flush=True)
print("SL4_VERSION=" + version, flush=True)
'''
GAP_CODE = '''if LoadPackage("crystcat") <> true then QUIT_GAP(1); fi;
if LoadPackage("smallgrp") <> true then QUIT_GAP(1); fi;
if RankMat([[1,2],[2,4]]) <> 1 or 1/3+1/6 <> 1/2 then QUIT_GAP(1); fi;
Print("SL4_VERSION=",GAPInfo.Version,"\\n");;
Print("SL4_EXACT_PASS\\nSL4_CRYSTCAT_PASS\\nSL4_SMALLGRP_PASS\\n");;
QUIT_GAP(0);
'''
SINGULAR_CODE = '''ring r=0,(x,y),dp;
ideal I=x^2-y,y^2-1;
ideal J=std(I);
if (reduce(x^4-1,J)==0) { print("SL4_EXACT_PASS"); }
quit;
'''
MAGMA_CODE = '''assert 1/3 + 1/6 eq 1/2;
assert Rank(Matrix(Rationals(),2,2,[1,2,2,4])) eq 1;
printf "SL4_VERSION=%o\\n", GetVersion();
print "SL4_EXACT_PASS";
quit;
'''


def probe(discovered=None, output_dir=None, timeout=30):
    """Execute short checks. Retain logs/cache only when output_dir is provided."""
    records = copy.deepcopy(discovered if discovered is not None else discover())
    temporary = tempfile.TemporaryDirectory(prefix="sl4-runtime-probe-") if output_dir is None else None
    root = Path(temporary.name if temporary else output_dir).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    try:
        for name, record in records.items():
            if not record["found"]:
                continue
            work = root / name
            work.mkdir(parents=True, exist_ok=True)
            env = os.environ.copy()
            for variable, dirname in (("DOT_SAGE", "dot_sage"), ("XDG_CACHE_HOME", "xdg"),
                                      ("MPLCONFIGDIR", "matplotlib"), ("TMPDIR", "tmp")):
                location = work / dirname
                location.mkdir(exist_ok=True)
                env[variable] = str(location)
            env.update(SL4_RUNTIME_CACHE=str(work / "sage_cache"), PYTHONNOUSERSITE="1",
                       PYTHONDONTWRITEBYTECODE="1", SAGE_STARTUP_FILE=os.devnull)
            path = record["path"]
            record["tested"] = True
            commands = []
            expected = ["SL4_EXACT_PASS"]
            if name == "sage":
                script = work / "probe.py"
                script.write_text(SAGE_CODE)
                commands.append(_run([path, "-python", str(script)], cwd=work, env=env, timeout=timeout))
                expected += ["SL4_SINGULAR_PASS", "SL4_NORMALIZ_PASS", "SL4_GAP_PACKAGES_PASS"]
            elif name == "gap":
                commands.append(_run([path, "-q", "-b"], cwd=work, env=env, timeout=timeout, input_text=GAP_CODE))
                expected += ["SL4_CRYSTCAT_PASS", "SL4_SMALLGRP_PASS"]
            elif name == "singular":
                commands.append(_run([path, "--version"], cwd=work, env=env, timeout=timeout))
                commands.append(_run([path, "-q"], cwd=work, env=env, timeout=timeout, input_text=SINGULAR_CODE))
            elif name == "magma":
                # Respect the user's installed launcher, including its license handling.
                commands.append(_run([path], cwd=work, env=env, timeout=timeout, input_text=MAGMA_CODE))
            elif name == "cxx":
                commands.append(_run([path, "--version"], cwd=work, env=env, timeout=timeout))
                source = work / "probe.cpp"
                binary = work / "probe"
                source.write_text('#include <iostream>\n#include <numeric>\nint main(){if(std::gcd(84,30)!=6)return 1;std::cout<<"SL4_EXACT_PASS\\n";}\n')
                built = _run([path, "-std=c++17", str(source), "-o", str(binary)], cwd=work, env=env, timeout=timeout)
                commands.append(built)
                if built["returncode"] == 0:
                    commands.append(_run([str(binary)], cwd=work, env=env, timeout=timeout))
            else:
                record.update(tested=False, status="unsupported")
                continue
            combined = "\n".join(run["output"] for run in commands)
            checks = {marker.removeprefix("SL4_").removesuffix("_PASS").lower(): marker in combined
                      for marker in expected}
            success = all(checks.values()) and all(run["returncode"] == 0 and run["status"] == "completed" for run in commands)
            # GAP may enter a break loop while still returning shell exit 0.
            if name in ("gap", "sage") and re.search(r"(^|\n)(Error,|Error:|Traceback \()", combined):
                success = False
            record.update(checks=checks, commands=commands, seconds=round(sum(run["seconds"] for run in commands), 3),
                          status="pass" if success else ("timed_out" if any(run["status"] == "timed_out" for run in commands) else "failed"))
            match = re.search(r"SL4_VERSION=([^\n]+)", combined)
            if match:
                record["version"] = match.group(1).strip()
            elif name in ("singular", "cxx") and commands[0]["returncode"] == 0:
                record["version"] = commands[0]["output"].splitlines()[0]
            if name == "magma" and "not authorised" in combined:
                record["failure_reason"] = "Installed Magma launcher reports that this machine is not authorised."
            if not temporary:
                (work / "probe.log").write_text(combined)
        if not temporary:
            (root / "runtime_probe.json").write_text(json.dumps(records, indent=2) + "\n")
        return records
    finally:
        if temporary:
            temporary.cleanup()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("sage", "gap", "magma", "singular", "cxx"):
        parser.add_argument("--" + name)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--timeout", type=float, default=30)
    parser.add_argument("--discover-only", action="store_true")
    args = parser.parse_args()
    records = discover(**{name: getattr(args, name) for name in ("sage", "gap", "magma", "singular", "cxx")})
    if not args.discover_only:
        records = probe(records, args.output_dir, args.timeout)
    print(json.dumps(records, indent=2))
    return 0 if args.discover_only or all(record["status"] == "pass" for record in records.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
