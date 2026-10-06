# Optional Linux environment. The release tag may be replaced by an immutable
# digest with --build-arg SAGE_IMAGE=sagemath/sagemath@sha256:... .
ARG SAGE_IMAGE=sagemath/sagemath:10.9
FROM ${SAGE_IMAGE}

USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        python3 g++ gap gap-crystcat gap-cryst gap-polycyclic gap-alnuth \
        gap-autpgrp gap-gapdoc gap-smallgrp pari-gp singular \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /opt/sl4 /results \
    && chown sage:sage /opt/sl4 /results \
    && ln -s /results /opt/SL4-results

# Expose the required architecture-independent packages, including the complete
# Ubuntu noble CrystCat -> Cryst -> Alnuth/Polycyclic -> AutPGrp dependency chain.
# Do not add Ubuntu's GAP core library or compiled package modules to its roots.
RUN python3 -c 'from pathlib import Path; import re; \
    names={"crystcat", "cryst", "polycyclic", "alnuth", "autpgrp", "gapdoc", "smallgrp"}; \
    packages=[p for p in Path("/usr/share/gap/pkg").iterdir() if p.name.lower() in names]; \
    assert {p.name.lower() for p in packages} == names; \
    targets=[Path("/home/sage/sage/local")/part/"gap/pkg" for part in ("lib", "share")]; \
    [t.mkdir(parents=True, exist_ok=True) for t in targets]; \
    [(t/p.name).symlink_to(p, target_is_directory=True) for t in targets for p in packages if not any(re.fullmatch(re.escape(p.name)+r"([_-]?[0-9].*)?", q.name, re.I) for q in t.iterdir())]'

# Use Sage's GAP executable together with Sage's matching core library.
ENV PATH="/home/sage/sage/local/bin:/usr/local/bin:/usr/bin:/bin" \
    GAP_ROOT_PATHS="/home/sage/sage/local/lib/gap;/home/sage/sage/local/share/gap" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    OMP_NUM_THREADS=1

COPY --chown=sage:sage . /opt/sl4
USER sage
WORKDIR /results

# The official Sage image omits this optional backend. Use the published wheel
# for Sage's Python, including bundled Normaliz libraries; do not compile it.
RUN /usr/bin/sage -python -m pip install --no-cache-dir --only-binary=:all: --no-deps PyNormaliz==2.24

# Report the particular missing package before the mathematical preflight.
RUN printf '%s\n' \
    'Print("GAP_VERSION=", GAPInfo.Version, "\nROOTS=", GAPInfo.RootPaths, "\n");;' \
    'for name in ["gapdoc", "autpgrp", "polycyclic", "alnuth", "cryst", "crystcat", "smallgrp"] do loaded := LoadPackage(name); Print("PACKAGE ", name, " = ", loaded, "\n"); if loaded <> true then QUIT_GAP(1); fi; od;' \
    'QUIT_GAP(0);' | /home/sage/sage/local/bin/gap -q --quitonbreak

# Fail the image build if an actual required runtime/package check fails.
# Magma is optional and is neither installed nor required by this image.
RUN /usr/bin/sage -python /opt/sl4/reproduce.py --check-tools

# Replace the upstream interactive/notebook wrapper; Sage sets its own runtime
# environment and preserves argument boundaries for this batch command.
ENTRYPOINT ["/usr/bin/sage", "-python", "/opt/sl4/reproduce.py"]
CMD ["--run-dir", "/results/run"]
