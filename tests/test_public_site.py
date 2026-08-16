from __future__ import annotations

import importlib.util
import re
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"

CORE_NAV = {
    "index.html", "health.html", "cessation.html", "young-people.html", "prevalence.html",
    "exposure.html", "products.html", "retail-enforcement.html", "regulation.html", "evidence.html",
}
REQUIRED = CORE_NAV | {
    "sources.html", "methodology.html", "limitations.html", "downloads.html", "environment.html",
    "robots.txt", "sitemap.xml", "assets/site.css", "assets/site.js",
}


class PublicSiteTests(unittest.TestCase):
    def test_required_pages_exist(self) -> None:
        missing = sorted(str(path) for path in REQUIRED if not (SITE / path).is_file())
        self.assertEqual(missing, [])

    def test_internal_html_links_resolve(self) -> None:
        href_pattern = re.compile(r'href=["\']([^"\']+)["\']', re.I)
        errors: list[str] = []
        for page in SITE.glob("*.html"):
            text = page.read_text(encoding="utf-8")
            for href in href_pattern.findall(text):
                if href.startswith(("http://", "https://", "mailto:", "#")):
                    continue
                path = href.split("#", 1)[0].split("?", 1)[0]
                if not path:
                    continue
                if path.startswith(("data/", "evidence/", "environment/", "regulation/", "provenance/")):
                    target = (ROOT / path).resolve()
                else:
                    target = (page.parent / path).resolve()
                if not target.exists():
                    errors.append(f"{page.name}: {href}")
        self.assertEqual(errors, [])

    def test_primary_navigation_is_vaping_led_and_consistent(self) -> None:
        nav_pattern = re.compile(r'<nav class="nav-links"[^>]*>(.*?)</nav>', re.I | re.S)
        href_pattern = re.compile(r'href=["\']([^"\']+)["\']', re.I)
        for page in SITE.glob("*.html"):
            text = page.read_text(encoding="utf-8")
            match = nav_pattern.search(text)
            self.assertIsNotNone(match, page.name)
            hrefs = set(href_pattern.findall(match.group(1)))
            self.assertEqual(CORE_NAV - hrefs, set(), f"{page.name} missing core nav links")
            self.assertNotIn("environment.html", hrefs, f"{page.name} promotes legacy environment page")

    def test_pages_have_basic_accessibility_metadata_and_one_h1(self) -> None:
        for page in SITE.glob("*.html"):
            text = page.read_text(encoding="utf-8")
            low = text.lower()
            self.assertIn('<html lang="en-gb">', low, page.name)
            self.assertIn('<meta name="viewport"', low, page.name)
            self.assertIn('<meta name="description"', low, page.name)
            self.assertIn('<main', low, page.name)
            self.assertIn('href="#main"', low, page.name)
            self.assertEqual(len(re.findall(r'<h1(?:\s[^>]*)?>', text, re.I)), 1, page.name)

    def test_site_copy_does_not_claim_satellite_is_direct_vaping_evidence(self) -> None:
        combined = "\n".join(p.read_text(encoding="utf-8").lower() for p in SITE.glob("*.html"))
        self.assertIn("satellite", combined)
        self.assertIn("cannot detect an individual vaping event", combined)
        self.assertNotIn("satellite vaping detector", combined)

    def test_build_contains_only_approved_public_data_roots(self) -> None:
        scripts = ROOT / "scripts"
        sys.path.insert(0, str(scripts))
        try:
            spec = importlib.util.spec_from_file_location("build_site", scripts / "build_site.py")
            self.assertIsNotNone(spec)
            module = importlib.util.module_from_spec(spec)
            assert spec and spec.loader
            spec.loader.exec_module(module)
            target = module.build_site()
        finally:
            sys.path.remove(str(scripts))

        self.assertTrue((target / "index.html").is_file())
        self.assertTrue((target / ".nojekyll").is_file())
        self.assertTrue((target / "health.html").is_file())
        self.assertTrue((target / "young-people.html").is_file())
        self.assertFalse((target / "scripts").exists())
        self.assertFalse((target / ".github").exists())
        for forbidden in ("raw", "working", "investigation", "private", "secrets"):
            self.assertFalse(any(forbidden in p.parts for p in target.rglob("*")), forbidden)

    def test_manifest_rejects_unmanifested_generated_data(self) -> None:
        scripts = ROOT / "scripts"
        sys.path.insert(0, str(scripts))
        try:
            spec = importlib.util.spec_from_file_location("validate_public", scripts / "validate_public.py")
            self.assertIsNotNone(spec)
            module = importlib.util.module_from_spec(spec)
            assert spec and spec.loader
            spec.loader.exec_module(module)
        finally:
            sys.path.remove(str(scripts))

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "provenance").mkdir(parents=True)
            (root / "evidence").mkdir(parents=True)
            (root / "provenance" / "publication_manifest.json").write_text(
                '{"schema_version":3,"files":[]}\n', encoding="utf-8"
            )
            (root / "evidence" / "rogue.json").write_text('{"unexpected":true}\n', encoding="utf-8")
            errors: list[str] = []
            module.validate_manifest(errors, root)
            self.assertTrue(any("not covered by publication manifest" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
