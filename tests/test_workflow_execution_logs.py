# -*- coding: utf-8 -*-
"""
Test Suite: Workflow Pipeline Inspection & Real-time Execution Logs
Verifies interactive cards, execution log banners, and workflow integrity.
"""

import unittest
from pathlib import Path
import re


class TestWorkflowExecutionLogs(unittest.TestCase):
    def test_workflow_cards_in_html(self):
        for html_path in [Path("nonai/web/index.html"), Path("public/index.html")]:
            self.assertTrue(html_path.exists())
            content = html_path.read_text(encoding="utf-8")
            for step in ["1", "2", "3", "4"]:
                self.assertIn(f'data-wf-step="{step}"', content)
                self.assertIn(f'id="wfStep{step}Hint"', content)

    def test_execution_log_banner_in_app_js(self):
        for js_path in [Path("nonai/web/app.js"), Path("public/app.js")]:
            self.assertTrue(js_path.exists())
            content = js_path.read_text(encoding="utf-8")
            self.assertIn("buildExecutionLogBannerHtml", content)
            self.assertIn("execution-log-banner", content)
            self.assertIn("stage3_workflow", content)
            self.assertIn("stage4_workflow", content)
            self.assertIn("clickable-wf-step", content)

    def test_workflow_css_styles(self):
        for css_path in [Path("nonai/web/style.css"), Path("public/style.css")]:
            self.assertTrue(css_path.exists())
            content = css_path.read_text(encoding="utf-8")
            self.assertIn(".clickable-wf-step", content)
            self.assertIn(".execution-log-banner", content)
            self.assertIn(".wf-step-footer", content)
            self.assertIn(".wf-inspect-hint", content)


if __name__ == "__main__":
    unittest.main()
