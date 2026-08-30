from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
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
TEXT_SUFFIXES = {".md", ".txt", ".json", ".csv", ".yml", ".yaml", ".html", ".css", ".js", ".py", ".xml"}
REQUIRED_ROOT_FILES = [
    "README.md", "METHODOLOGY.md", "LIMITATIONS.md", "DATA-LICENSING.md",
    "AUDITABILITY.md", "EXTERNAL_REVIEW.md"
]
REQUIRED_SITE_FILES = [
    "index.html", "results.html", "health.html", "cessation.html", "young-people.html", "prevalence.html",
    "exposure.html", "products.html", "retail-enforcement.html", "regulation.html", "evidence.html",
    "sources.html", "methodology.html", "limitations.html", "downloads.html",
    "environment.html", "ai-governance.html", "citation.html",
    "assets/site.css", "assets/site.js", "assets/youth.js", "robots.txt", "sitemap.xml",
]

MANIFESTED_DATA_ROOTS = ("data/public", "evidence", "environment", "regulation", "provenance")
MANIFEST_STATIC_EXCEPTIONS = {"data/public/README.md", "evidence/README.md", "provenance/README.md"}
REVIEWED_STATES = {"reviewed", "verified", "validated", "human_reviewed"}
SYNTHESIS_READY_STATES = {
    "synthesis_ready", "ready_for_synthesis", "validated_for_synthesis",
    "quantitative_synthesis_ready"
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def validate_manifest(errors: list[str], root: Path = ROOT) -> None:
    manifest_path = root / "provenance" / "publication_manifest.json"
    generated_files: set[str] = set()
    for rel_root in MANIFESTED_DATA_ROOTS:
        source = root / rel_root
        if not source.exists():
            continue
        for path in source.rglob("*"):
            if not path.is_file():
                continue
            rel = path.relative_to(root).as_posix()
            if rel == "provenance/publication_manifest.json" or rel in MANIFEST_STATIC_EXCEPTIONS:
                continue
            generated_files.add(rel)

    if not manifest_path.exists():
        if generated_files:
            errors.append("publication manifest missing while generated public data are present")
        return

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"invalid publication manifest: {exc}")
        return
    files = manifest.get("files")
    if not isinstance(files, list):
        errors.append("publication manifest has no files list")
        return

    manifested_paths: set[str] = set()
    for item in files:
        if not isinstance(item, dict) or not isinstance(item.get("path"), str):
            errors.append("publication manifest contains an invalid file entry")
            continue
        rel = Path(item["path"])
        if rel.is_absolute() or ".." in rel.parts:
            errors.append(f"unsafe manifest path: {item.get('path')}")
            continue
        rel_text = rel.as_posix()
        if rel_text in manifested_paths:
            errors.append(f"duplicate manifest path: {rel_text}")
            continue
        manifested_paths.add(rel_text)
        path = root / rel
        if not path.exists() or not path.is_file():
            errors.append(f"manifest file missing: {rel}")
            continue
        if item.get("sha256") != sha256(path):
            errors.append(f"manifest hash mismatch: {rel}")
        if item.get("bytes") != path.stat().st_size:
            errors.append(f"manifest byte-size mismatch: {rel}")

    unmanifested = sorted(generated_files - manifested_paths)
    for rel in unmanifested:
        errors.append(f"generated public data not covered by publication manifest: {rel}")

    unexpected = sorted(
        rel for rel in manifested_paths
        if rel not in generated_files and rel not in MANIFEST_STATIC_EXCEPTIONS
    )
    for rel in unexpected:
        errors.append(f"manifest references file outside generated public data contract: {rel}")


def validate_evidence_cards(errors: list[str], root: Path = ROOT, *, current_year: int | None = None) -> None:
    path = root / "evidence" / "evidence_cards.json"
    if not path.exists():
        return
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"invalid evidence cards: {exc}")
        return

    records = payload.get("records")
    if not isinstance(records, list):
        errors.append("evidence cards have no records list")
        return

    if payload.get("card_count") != len(records):
        errors.append(
            f"evidence card_count mismatch: declared={payload.get('card_count')!r} actual={len(records)}"
        )

    design_counts = Counter()
    integrity_counts = Counter()
    year_now = current_year if current_year is not None else datetime.now(timezone.utc).year

    for index, record in enumerate(records):
        if not isinstance(record, dict):
            errors.append(f"evidence record {index} is not an object")
            continue

        design = str(record.get("study_design") or "unknown")
        integrity = str(record.get("integrity_status") or "unknown")
        design_counts[design] += 1
        integrity_counts[integrity] += 1

        evidence_id = record.get("evidence_id")
        if not isinstance(evidence_id, str) or not evidence_id.strip():
            errors.append(f"evidence record {index} has no stable evidence_id")

        year = record.get("year")
        if year not in (None, ""):
            year_text = str(year).strip()
            if not re.fullmatch(r"\d{4}", year_text):
                errors.append(f"{evidence_id or index}: invalid publication year {year!r}")
            else:
                year_value = int(year_text)
                if year_value > year_now + 1:
                    errors.append(
                        f"{evidence_id or index}: implausible future publication year {year_value}"
                    )
                elif year_value == year_now + 1:
                    has_identifier = any(record.get(key) for key in ("pmid", "pmcid", "doi"))
                    if not has_identifier:
                        errors.append(
                            f"{evidence_id or index}: next-year publication needs a stable "
                            "bibliographic identifier for date verification"
                        )

        readiness = str(record.get("synthesis_readiness") or "").strip().lower()
        review_state = str(record.get("human_review_status") or "").strip().lower()
        if readiness in SYNTHESIS_READY_STATES and review_state not in REVIEWED_STATES:
            errors.append(
                f"{evidence_id or index}: synthesis-ready state requires completed human review"
            )

    declared_design = payload.get("study_design_counts")
    if isinstance(declared_design, dict) and dict(design_counts) != declared_design:
        errors.append("study_design_counts do not reconcile with evidence records")

    declared_integrity = payload.get("integrity_status_counts")
    if isinstance(declared_integrity, dict) and dict(integrity_counts) != declared_integrity:
        errors.append("integrity_status_counts do not reconcile with evidence records")


def validate_repository(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    for path in root.rglob("*"):
        if not path.is_file() or ".git" in path.parts or "build" in path.parts:
            continue
        rel = path.relative_to(root)
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

    for name in REQUIRED_ROOT_FILES:
        if not (root / name).exists():
            errors.append(f"missing required file: {name}")

    for name in REQUIRED_SITE_FILES:
        if not (root / "site" / name).exists():
            errors.append(f"missing required site file: site/{name}")

    validate_manifest(errors, root)
    validate_evidence_cards(errors, root)
    return errors


def main() -> int:
    errors = validate_repository()
    if errors:
        print("PUBLIC VALIDATION FAILED")
        for err in errors:
            print(f" - {err}")
        return 1
    print("PUBLIC VALIDATION PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
