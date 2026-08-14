from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FORBIDDEN_PATH_PARTS = {
    "raw", "protected", "investigation", "private", "credentials", "secrets"
}
SECRET_PATTERNS = [
    re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----"),
    re.compile(r"(?i)(?:api[_ -]?key|access[_ -]?token|password)\s*[:=]\s*['\"][^'\"]{12,}['\"]"),
    re.compile(r"gh[pousr]_[A-Za-z0-9_]{20,}"),
    re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
]
TEXT_SUFFIXES = {".md", ".txt", ".json", ".csv", ".yml", ".yaml", ".html", ".css", ".js", ".py"}


def main() -> int:
    errors: list[str] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        rel = path.relative_to(ROOT)
        lower_parts = {part.lower() for part in rel.parts}
        if lower_parts & FORBIDDEN_PATH_PARTS and not str(rel).startswith("data/public"):
            # Documentation may contain these words in file content, but not as private directories.
            if any(part.lower() in {"raw", "protected", "investigation", "private"} for part in rel.parts[:-1]):
                errors.append(f"forbidden public path: {rel}")
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                errors.append(f"possible secret in {rel}: {pattern.pattern}")

    required = ["README.md", "METHODOLOGY.md", "LIMITATIONS.md", "DATA-LICENSING.md"]
    for name in required:
        if not (ROOT / name).exists():
            errors.append(f"missing required file: {name}")

    if errors:
        print("PUBLIC VALIDATION FAILED")
        for err in errors:
            print(f" - {err}")
        return 1
    print("PUBLIC VALIDATION PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
