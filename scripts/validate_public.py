from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FORBIDDEN_DIRECTORY_NAMES = {
    "raw", "working", "protected", "investigation", "private", "credentials", "secrets"
}
SECRET_PATTERNS = [
    re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----"),
    re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"gh[pousr]_[A-Za-z0-9_]{20,}"),
    re.compile(r"AIza[0-9A-Za-z_-]{30,}"),
    re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    re.compile(r"(?i)(?:api[_ -]?key|access[_ -]?token|password|client[_ -]?secret)\s*[:=]\s*['\"][^'\"]{12,}['\"]"),
]
TEXT_SUFFIXES = {".md", ".txt", ".json", ".csv", ".yml", ".yaml", ".html", ".css", ".js", ".py"}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def validate_manifest(errors: list[str]) -> None:
    manifest_path = ROOT / "provenance" / "publication_manifest.json"
    if not manifest_path.exists():
        return  # bootstrap repositories may exist before the first publication
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"invalid publication manifest: {exc}")
        return
    files = manifest.get("files")
    if not isinstance(files, list):
        errors.append("publication manifest has no files list")
        return
    for item in files:
        if not isinstance(item, dict) or not isinstance(item.get("path"), str):
            errors.append("publication manifest contains an invalid file entry")
            continue
        rel = Path(item["path"])
        if rel.is_absolute() or ".." in rel.parts:
            errors.append(f"unsafe manifest path: {item.get('path')}")
            continue
        path = ROOT / rel
        if not path.exists() or not path.is_file():
            errors.append(f"manifest file missing: {rel}")
            continue
        if item.get("sha256") != sha256(path):
            errors.append(f"manifest hash mismatch: {rel}")
        if item.get("bytes") != path.stat().st_size:
            errors.append(f"manifest byte-size mismatch: {rel}")


def main() -> int:
    errors: list[str] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        rel = path.relative_to(ROOT)
        directory_parts = {part.lower() for part in rel.parts[:-1]}
        if directory_parts & FORBIDDEN_DIRECTORY_NAMES:
            errors.append(f"forbidden public path: {rel}")
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                errors.append(f"possible secret in {rel}")
                break

    required = ["README.md", "METHODOLOGY.md", "LIMITATIONS.md", "DATA-LICENSING.md", "AUDITABILITY.md"]
    for name in required:
        if not (ROOT / name).exists():
            errors.append(f"missing required file: {name}")

    validate_manifest(errors)

    if errors:
        print("PUBLIC VALIDATION FAILED")
        for err in errors:
            print(f" - {err}")
        return 1
    print("PUBLIC VALIDATION PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
