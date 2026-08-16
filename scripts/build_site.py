#!/usr/bin/env python3
"""Build the validated Vaping26 static publication bundle."""
from __future__ import annotations

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
    return target


if __name__ == "__main__":
    destination = build_site()
    print(f"Built validated site at {destination}")
