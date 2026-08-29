#!/usr/bin/env python3
"""Build the validated Vaping26 static publication bundle."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

from validate_public import ROOT, validate_repository

PUBLIC_DATA_ROOTS = (
    Path("data/public"),
    Path("evidence"),
    Path("environment"),
    Path("regulation"),
    Path("provenance"),
)

# These files are consumed directly by the public JavaScript. A build is not
# publishable unless they are present in the final deployable tree and contain
# parseable JSON. This prevents a successful Pages deploy from silently serving
# a methodology-only shell while the generated evidence remains outside the
# publication bundle.
REQUIRED_PUBLIC_JSON = (
    Path("data/public/research_status.json"),
    Path("evidence/evidence_cards.json"),
    Path("evidence/health_evidence_summary.json"),
    Path("evidence/ons_prevalence.json"),
    Path("evidence/synthesis_register.json"),
    Path("evidence/youth_prevalence.json"),
    Path("provenance/source_register.json"),
    Path("provenance/source_coverage.json"),
    Path("provenance/publication_manifest.json"),
)


def validate_built_bundle(target: Path) -> None:
    errors: list[str] = []

    if not (target / "index.html").is_file():
        errors.append("missing index.html")
    if not (target / "assets" / "site.js").is_file():
        errors.append("missing assets/site.js")

    for rel in REQUIRED_PUBLIC_JSON:
        path = target / rel
        if not path.is_file():
            errors.append(f"missing public JSON: {rel.as_posix()}")
            continue
        if path.stat().st_size == 0:
            errors.append(f"empty public JSON: {rel.as_posix()}")
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"invalid public JSON {rel.as_posix()}: {exc}")
            continue
        if not isinstance(payload, dict):
            errors.append(f"public JSON must contain an object: {rel.as_posix()}")

    if errors:
        raise RuntimeError("Built public bundle contract failed:\n - " + "\n - ".join(errors))


def build_site() -> Path:
    errors = validate_repository()
    if errors:
        raise RuntimeError("Public repository validation failed:\n - " + "\n - ".join(errors))

    target = ROOT / "build" / "site"
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(ROOT / "site", target)

    for rel in PUBLIC_DATA_ROOTS:
        source = ROOT / rel
        if source.exists():
            destination = target / rel
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(source, destination, dirs_exist_ok=True)

    (target / ".nojekyll").write_text("", encoding="utf-8")
    validate_built_bundle(target)
    return target


if __name__ == "__main__":
    destination = build_site()
    print(f"Built validated site at {destination}")
