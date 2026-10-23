# -*- coding: utf-8 -*-
"""
Test Suite: Multilingual i18n Integrity & Zero-Defect Symmetry
Validates all 7 supported languages (zh-TW, en, zh-CN, ja, ko, th, ru).
"""

import json
import re
import html.parser
from pathlib import Path
import unittest


def load_i18n():
    js_path = Path("public/i18n.js")
    assert js_path.exists(), "public/i18n.js must exist"
    content = js_path.read_text(encoding="utf-8")
    m = re.search(r"const I18N_TRANSLATIONS = (\{.*?\});", content, re.DOTALL)
    assert m, "I18N_TRANSLATIONS not found in i18n.js"
    return json.loads(m.group(1))


class TestI18nIntegrity(unittest.TestCase):
    def test_supported_languages(self):
        data = load_i18n()
        expected_langs = ["zh-TW", "en", "zh-CN", "ja", "ko", "th", "ru"]
        self.assertEqual(set(data.keys()), set(expected_langs))

    def test_key_symmetry_across_all_languages(self):
        data = load_i18n()
        langs = ["zh-TW", "en", "zh-CN", "ja", "ko", "th", "ru"]
        base_keys = set(data["zh-TW"].keys())

        for l in langs:
            curr_keys = set(data[l].keys())
            missing = base_keys - curr_keys
            extra = curr_keys - base_keys
            self.assertFalse(missing, f"Language {l} missing keys: {missing}")
            self.assertFalse(extra, f"Language {l} has extra keys: {extra}")

    def test_modal_symmetry_across_all_languages(self):
        data = load_i18n()
        langs = ["zh-TW", "en", "zh-CN", "ja", "ko", "th", "ru"]
        expected_modal_keys = {
            "rsid", "runs_split", "claude_purged", "pkg_synthesized",
            "semantic", "ghost_styles", "unicode", "human_time",
            "app_spoofed", "pdf_producer", "markdown",
            "stage1_restructure", "stage2_fact_citation",
            "stage3_workflow", "stage4_workflow"
        }

        base_modals = data["zh-TW"]["modal_details"]
        self.assertEqual(set(base_modals.keys()), expected_modal_keys)

        for l in langs:
            curr_modals = data[l]["modal_details"]
            self.assertEqual(set(curr_modals.keys()), expected_modal_keys, f"Language {l} modal key mismatch")
            for mk in expected_modal_keys:
                base_subkeys = set(base_modals[mk].keys())
                curr_subkeys = set(curr_modals[mk].keys())
                self.assertEqual(curr_subkeys, base_subkeys, f"Language {l} modal subkey mismatch in {mk}: {curr_subkeys ^ base_subkeys}")

    def test_html_data_i18n_attributes_exist(self):
        data = load_i18n()
        langs = ["zh-TW", "en", "zh-CN", "ja", "ko", "th", "ru"]

        class AttrExtractor(html.parser.HTMLParser):
            def __init__(self):
                super().__init__()
                self.i18n_keys = set()
                self.placeholder_keys = set()
                self.title_keys = set()

            def handle_starttag(self, tag, attrs):
                for k, v in attrs:
                    if k == "data-i18n":
                        self.i18n_keys.add(v)
                    elif k == "data-i18n-placeholder":
                        self.placeholder_keys.add(v)
                    elif k == "data-i18n-title":
                        self.title_keys.add(v)

        for html_file in ["public/index.html", "nonai/web/index.html"]:
            extractor = AttrExtractor()
            content = Path(html_file).read_text(encoding="utf-8")
            extractor.feed(content)

            for l in langs:
                lang_dict = data[l]
                for key in extractor.i18n_keys:
                    self.assertIn(key, lang_dict, f"File {html_file}: Key '{key}' referenced in data-i18n missing in {l}")
                for key in extractor.placeholder_keys:
                    self.assertIn(key, lang_dict, f"File {html_file}: Key '{key}' referenced in data-i18n-placeholder missing in {l}")
                for key in extractor.title_keys:
                    self.assertIn(key, lang_dict, f"File {html_file}: Key '{key}' referenced in data-i18n-title missing in {l}")

    def test_timing_keys_match_html(self):
        data = load_i18n()
        html_content = Path("public/index.html").read_text(encoding="utf-8")
        timing_keys = set(re.findall(r'data-timing="([a-zA-Z0-9_]+)"', html_content))
        self.assertEqual(timing_keys, {"author", "rsid", "pdf", "perturb"})

        for l in data:
            for tk in timing_keys:
                self.assertIn(f"timing_{tk}_title", data[l], f"Missing timing_{tk}_title in {l}")
                self.assertIn(f"timing_{tk}_desc", data[l], f"Missing timing_{tk}_desc in {l}")

    def test_prohibited_phrases(self):
        prohibited = ["零基礎", "手把手"]
        for path in [
            "public/i18n.js", "nonai/web/i18n.js",
            "public/index.html", "nonai/web/index.html",
            "public/app.js", "nonai/web/app.js"
        ]:
            content = Path(path).read_text(encoding="utf-8")
            for p in prohibited:
                self.assertNotIn(p, content, f"Prohibited phrase '{p}' found in {path}")


if __name__ == "__main__":
    unittest.main()
