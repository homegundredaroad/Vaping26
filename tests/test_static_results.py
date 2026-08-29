from __future__ import annotations

import importlib.util
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


class StaticResultsTests(unittest.TestCase):
    def _build(self) -> Path:
        sys.path.insert(0, str(SCRIPTS))
        try:
            spec = importlib.util.spec_from_file_location("build_site_static_results", SCRIPTS / "build_site.py")
            self.assertIsNotNone(spec)
            module = importlib.util.module_from_spec(spec)
            assert spec and spec.loader
            spec.loader.exec_module(module)
            return module.build_site()
        finally:
            sys.path.remove(str(SCRIPTS))

    def test_results_are_in_html_without_javascript(self) -> None:
        target = self._build()
        text = (target / "results.html").read_text(encoding="utf-8")
        self.assertIn('type="application/ld+json"', text)
        self.assertIn('"@type":"Dataset"', text)
        self.assertNotIn("Loading latest approved synthesis register", text)
        self.assertNotIn('id="r-literature">Data unavailable', text)
        self.assertNotIn('id="r-cards">Data unavailable', text)
        self.assertNotIn('id="r-trials">Data unavailable', text)
        self.assertNotIn('id="r-prev-year">Data unavailable', text)
        self.assertRegex(text, r'id="r-literature">[0-9,]+<')
        self.assertRegex(text, r'id="r-trials">[0-9,]+<')
        self.assertRegex(text, r'<tbody id="question-rows"><tr><td>[^<]+</td><td>[0-9,]+</td><td>[0-9,]+</td><td>[^<]+</td></tr>')

    def test_results_page_has_explicit_non_js_fallbacks_in_source(self) -> None:
        text = (ROOT / "site" / "results.html").read_text(encoding="utf-8")
        self.assertNotIn('id="r-literature">—', text)
        self.assertIn('id="r-literature">Data unavailable', text)
        self.assertIn("Who runs this and how to interpret it", text)
        self.assertIn("Provenance and limitations", text)


if __name__ == "__main__":
    unittest.main()
