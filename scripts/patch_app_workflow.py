# -*- coding: utf-8 -*-
"""
Helper script to update nonai/web/app.js with execution logs and workflow card click logic.
"""

from pathlib import Path

app_js_path = Path("nonai/web/app.js")
code = app_js_path.read_text(encoding="utf-8")

# 1. Add Workflow cards status update into renderFileResult
old_render_wf = """    // Attach click inspection handlers
    document.querySelectorAll(".stat-box.clickable").forEach(box => {"""

new_render_wf = """    // Update Workflow Best Practice Cards with real-time execution status
    const s1Badge = document.getElementById("wfStep1Badge");
    const s2Badge = document.getElementById("wfStep2Badge");
    const s3Badge = document.getElementById("wfStep3Badge");
    const s1Hint = document.getElementById("wfStep1Hint");
    const s2Hint = document.getElementById("wfStep2Hint");
    const s3Hint = document.getElementById("wfStep3Hint");

    if (s1Badge) {
      s1Badge.classList.add("executed");
      s1Badge.innerHTML = t.wf_step1_badge_executed || "階段 1 ⚡ ✅ 本檔案已自動重構";
    }
    if (s2Badge) {
      s2Badge.classList.add("executed");
      s2Badge.innerHTML = t.wf_step2_badge_executed || "階段 2 ⚡ ✅ 本檔案已自動審計";
    }
    if (s3Badge) {
      s3Badge.classList.add("executed");
      s3Badge.innerHTML = t.wf_step3_badge_executed || "階段 3 ⚡ ✅ 本檔案已自動注入";
    }

    if (s1Hint) {
      const boost = s.burstiness_boost ? `+${s.burstiness_boost}%` : `${s.semantic_replacements || 0} 處`;
      s1Hint.innerHTML = `📋 點擊查看本檔案重構歷程 (${boost})`;
    }
    if (s2Hint) {
      const score = s.fact_integrity_score ? `${s.fact_integrity_score} 分` : (s.unanchored_claims_count > 0 ? `${s.unanchored_claims_count} 處未錨定` : '100% 錨定');
      s2Hint.innerHTML = `📋 點擊查看本檔案審計報告 (${score})`;
    }
    if (s3Hint) {
      const rsid = s.rsid_injected || 25;
      const mins = s.human_editing_minutes || 170;
      s3Hint.innerHTML = `📋 點擊查看本檔案注入記錄 (${rsid} 會話 / ${mins} 分鐘)`;
    }

    // Attach click inspection handlers
    document.querySelectorAll(".stat-box.clickable").forEach(box => {"""

assert old_render_wf in code, "old_render_wf not found in app.js"
code = code.replace(old_render_wf, new_render_wf, 1)

# 2. Add Workflow Cards Click Listeners in DOMContentLoaded
old_timing_listener = """  if (btnCloseTiming) {
    btnCloseTiming.addEventListener("click", () => {
      timingPopoverCard.classList.add("hidden");
      activeTimingKey = null;
    });
  }"""

new_timing_listener = """  if (btnCloseTiming) {
    btnCloseTiming.addEventListener("click", () => {
      timingPopoverCard.classList.add("hidden");
      activeTimingKey = null;
    });
  }

  // 4.1 Workflow Step Cards Click Controller
  document.querySelectorAll(".workflow-step-item.clickable-wf-step").forEach(step => {
    const handleStepAction = () => {
      const stepNum = step.getAttribute("data-wf-step");
      const currentData = lastFileResult || {};
      if (stepNum === "1") {
        openExecutionDetailsModal("stage1_restructure", currentData);
      } else if (stepNum === "2") {
        openExecutionDetailsModal("stage2_fact_citation", currentData);
      } else if (stepNum === "3") {
        openExecutionDetailsModal("stage3_workflow", currentData);
      } else if (stepNum === "4") {
        openExecutionDetailsModal("stage4_workflow", currentData);
      }
    };

    step.addEventListener("click", handleStepAction);
    step.addEventListener("keydown", (e) => {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        handleStepAction();
      }
    });
  });"""

assert old_timing_listener in code, "old_timing_listener not found in app.js"
code = code.replace(old_timing_listener, new_timing_listener, 1)

app_js_path.write_text(code, encoding="utf-8")
print("[OK] Step 1 & 2 applied to nonai/web/app.js")
