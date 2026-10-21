# -*- coding: utf-8 -*-
"""
Test Suite: Stage 1 Semantic Restructuring & Stage 2 Fact-Citation Auditor
"""

import unittest
from nonai.core.semantic_restructure import restructure_semantics_and_burstiness
from nonai.core.fact_citation_auditor import audit_fact_citations


class TestStage1AndStage2(unittest.TestCase):
    def test_stage1_cliche_and_burstiness(self):
        text = (
            "值得注意的是，人工智慧在當今數位化時代扮演著舉足輕重的角色，深入探討其發展乃是至關重要。"
            "首先，它不僅僅是工具，更是革命性力量。其次，它顯著提升了生產力。最後，它也是一把雙刃劍。"
            "In conclusion, we must delve into the rich tapestry of deep learning, which plays a pivotal role in modern science."
        )
        res = restructure_semantics_and_burstiness(text, target_cv=0.65)
        
        # Verify cliches replaced
        self.assertNotIn("值得注意的是", res.cleaned_text)
        self.assertNotIn("delve into", res.cleaned_text)
        self.assertNotIn("rich tapestry", res.cleaned_text)
        self.assertGreater(res.metrics.cliches_purged_count, 0)
        self.assertGreaterEqual(res.metrics.rules_of_three_disrupted, 1)
        self.assertGreaterEqual(res.metrics.reshaped_sentence_count, res.metrics.original_sentence_count)

    def test_stage2_unanchored_claims_and_citations(self):
        sample_doc = (
            "本研究探討觀光體驗之流動性。\n"
            "過去十年中，遊客參與度顯著提升了 28.5%，帶來了深遠影響。\n"  # Unanchored claim 1 (percentage)
            "然而另一項調查發現，滿意度大幅下滑，缺乏後續追蹤。\n"  # Unanchored claim 2 (comparative)
            "根據最新的統計數據顯示，整體營收成長了 3.2 倍 [1]。\n"  # Anchored claim [1]
            "此外，研究表明跨國旅遊回流率達 45% (Wang et al., 2023)。\n"  # Anchored claim (Wang et al., 2023)
            "\nReferences:\n"
            "[1] Smith, J. (2022). Flow in Tourism. Journal of Travel Research, 10.1177/00472875211000000.\n"
            "[2] Fake Author (2024). Hallucinated Article Without Journal.\n"  # Suspicious reference
        )
        audit = audit_fact_citations(sample_doc)
        
        self.assertGreaterEqual(audit.total_claims_detected, 3)
        self.assertGreaterEqual(audit.unanchored_claims_count, 2)
        self.assertEqual(audit.anchored_claims_count, 2)
        self.assertGreaterEqual(audit.total_references_detected, 2)
        self.assertGreaterEqual(audit.suspicious_references_count, 1)
        self.assertTrue(0 <= audit.fact_integrity_score <= 100)


if __name__ == "__main__":
    unittest.main()
