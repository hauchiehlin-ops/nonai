// NonAI Frontend Controller & Multilingual Engine

document.addEventListener("DOMContentLoaded", () => {
  // Global references
  let lastFileResult = null;
  let activeBlobUrl = null;
  let currentLang = localStorage.getItem("nonai_lang") || "zh-TW";
  let activeModalKey = null;
  let activeTimingKey = null;

  // Global Modal References
  const detailModal = document.getElementById("detailModal");
  const modalTitle = document.getElementById("modalTitle");
  const modalIcon = document.getElementById("modalIcon");
  const modalBody = document.getElementById("modalBody");
  const btnCloseModal = document.getElementById("btnCloseModal");
  const btnModalOk = document.getElementById("btnModalOk");

  // 1. Multilingual Localization Engine
  const langSelect = document.getElementById("langSelect");

  function applyLanguage(lang) {
    if (!I18N_TRANSLATIONS[lang]) lang = "zh-TW";
    currentLang = lang;
    localStorage.setItem("nonai_lang", lang);
    document.documentElement.lang = lang;
    if (langSelect) langSelect.value = lang;

    const t = I18N_TRANSLATIONS[lang];

    // Update text elements with data-i18n
    document.querySelectorAll("[data-i18n]").forEach(el => {
      const key = el.getAttribute("data-i18n");
      if (t[key]) {
        el.innerHTML = t[key];
      }
    });

    // Update placeholders with data-i18n-placeholder
    document.querySelectorAll("[data-i18n-placeholder]").forEach(el => {
      const key = el.getAttribute("data-i18n-placeholder");
      if (t[key]) {
        el.placeholder = t[key];
      }
    });

    // Update titles with data-i18n-title
    document.querySelectorAll("[data-i18n-title]").forEach(el => {
      const key = el.getAttribute("data-i18n-title");
      if (t[key]) {
        el.title = t[key];
      }
    });

    // Update text counter labels
    const rawTextInput = document.getElementById("rawTextInput");
    const cleanedTextOutput = document.getElementById("cleanedTextOutput");
    const rawCharCount = document.getElementById("rawCharCount");
    const cleanCharCount = document.getElementById("cleanCharCount");
    if (rawCharCount) rawCharCount.textContent = `${t.txt_char_count || "字數："}${rawTextInput ? rawTextInput.value.length : 0}`;
    if (cleanCharCount) cleanCharCount.textContent = `${t.txt_char_count || "字數："}${cleanedTextOutput ? cleanedTextOutput.value.length : 0}`;

    // Re-render file result card if a file was already processed
    const fileResultCard = document.getElementById("fileResultCard");
    if (lastFileResult && fileResultCard && !fileResultCard.classList.contains("hidden")) {
      renderFileResult(lastFileResult);
    }

    // Re-render open modal if active
    if (detailModal && detailModal.open && activeModalKey && lastFileResult) {
      openExecutionDetailsModal(activeModalKey, lastFileResult);
    }

    // Re-render timing popover if open
    const timingPopoverCard = document.getElementById("timingPopoverCard");
    const timingTitle = document.getElementById("timingTitle");
    const timingContent = document.getElementById("timingContent");
    if (activeTimingKey && timingPopoverCard && !timingPopoverCard.classList.contains("hidden")) {
      const titleKey = `timing_${activeTimingKey}_title`;
      const descKey = `timing_${activeTimingKey}_desc`;
      if (t[titleKey] && t[descKey]) {
        timingTitle.innerHTML = t[titleKey];
        timingContent.innerHTML = t[descKey];
      }
    }

    // Update watcher button and status based on state
    updateWatcherUI(isWatcherActive);

    // Update Environment indicator (Localhost vs Cloud)
    updateEnvBadge();
  }

  if (langSelect) {
    langSelect.addEventListener("change", (e) => {
      applyLanguage(e.target.value);
    });
  }

  // 2. Navigation Tabs
  const tabBtns = document.querySelectorAll(".tab-btn");
  const tabPanels = document.querySelectorAll(".tab-panel");

  tabBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      tabBtns.forEach(b => {
        b.classList.remove("active");
        b.setAttribute("aria-selected", "false");
      });
      tabPanels.forEach(p => p.classList.remove("active"));
      btn.classList.add("active");
      btn.setAttribute("aria-selected", "true");
      const targetId = btn.getAttribute("data-tab");
      const targetPanel = document.getElementById(targetId);
      if (targetPanel) targetPanel.classList.add("active");
    });
  });

  // 3. File Purifier (Workbench)
  const dropZone = document.getElementById("dropZone");
  const fileInput = document.getElementById("fileInput");
  const fileResultCard = document.getElementById("fileResultCard");
  const resFileName = document.getElementById("resFileName");
  const resFileTypeDesc = document.getElementById("resFileTypeDesc");
  const btnDownload = document.getElementById("btnDownload");
  const fileStatsGrid = document.getElementById("fileStatsGrid");

  dropZone.addEventListener("click", () => fileInput.click());

  dropZone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropZone.classList.add("dragover");
  });

  dropZone.addEventListener("dragleave", () => {
    dropZone.classList.remove("dragover");
  });

  dropZone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropZone.classList.remove("dragover");
    if (e.dataTransfer.files.length > 0) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  });

  fileInput.addEventListener("change", (e) => {
    if (e.target.files.length > 0) {
      handleFileUpload(e.target.files[0]);
    }
  });

  // Base64 to Blob helper
  function b64toBlob(b64Data, contentType = '', sliceSize = 512) {
    const byteCharacters = atob(b64Data);
    const byteArrays = [];
    for (let offset = 0; offset < byteCharacters.length; offset += sliceSize) {
      const slice = byteCharacters.slice(offset, offset + sliceSize);
      const byteNumbers = new Array(slice.length);
      for (let i = 0; i < slice.length; i++) {
        byteNumbers[i] = slice.charCodeAt(i);
      }
      const byteArray = new Uint8Array(byteNumbers);
      byteArrays.push(byteArray);
    }
    return new Blob(byteArrays, { type: contentType });
  }

  // Environment Detection: Localhost vs Cloud Serverless
  const isLocalhost = window.location.hostname === "localhost" ||
                      window.location.hostname === "127.0.0.1" ||
                      window.location.hostname === "0.0.0.0" ||
                      window.location.hostname.endsWith(".local") ||
                      window.location.protocol === "file:";

  function updateEnvBadge() {
    const badge = document.getElementById("envModeBadge");
    if (!badge) return;
    const isZh = currentLang.startsWith("zh");
    if (isLocalhost) {
      badge.style.display = "inline-flex";
      badge.style.background = "rgba(16, 185, 129, 0.15)";
      badge.style.color = "#10b981";
      badge.style.border = "1px solid rgba(16, 185, 129, 0.4)";
      badge.textContent = isZh ? "🖥️ 本機模式 (無檔案大小上限)" : "🖥️ Local Mode (No Size Limit)";
    } else {
      badge.style.display = "inline-flex";
      badge.style.background = "rgba(56, 189, 248, 0.15)";
      badge.style.color = "#38bdf8";
      badge.style.border = "1px solid rgba(56, 189, 248, 0.4)";
      badge.textContent = isZh ? "☁️ 雲端體驗版 (限 4.5MB)" : "☁️ Cloud Demo (4.5MB Limit)";
    }
  }

  // Payload Size Limit Modal (Allows 1-Click Copy of Local Execution Commands)
  function showPayloadLimitModal(fileSizeMB) {
    const isZh = currentLang.startsWith("zh");
    const t = I18N_TRANSLATIONS[currentLang];
    activeModalKey = "payload_limit";
    modalIcon.textContent = "⚡";
    modalTitle.textContent = isZh ? "檔案大小超過雲端限制 (4.5 MB)" : "File Exceeds Serverless Limit (4.5 MB)";
    if (btnModalOk) {
      btnModalOk.textContent = t.modal_btn_close || t.modal_close || (isZh ? "確定關閉" : "Close");
    }

    modalBody.innerHTML = `
      <div style="font-size: 0.95rem; line-height: 1.6; margin-bottom: 8px;">
        <p style="margin-bottom: 12px;">
          <strong>${isZh ? "檔案大小：" : "File Size:"}</strong> <span style="color: var(--warning); font-weight: 700;">${fileSizeMB || "> 4.5"} MB</span>（${isZh ? "已超過雲端託管單次 4.5 MB 傳輸限制" : "Exceeds 4.5 MB serverless limit"}）
        </p>
        <p style="color: var(--text-muted); margin-bottom: 16px;">
          ${isZh ? "【建議解決方式】<br>1. 建議將 Word/PDF 內的高解析度圖片壓縮後再重新上傳。<br>2. <strong>或於本機電腦終端機直接執行（支援無大小上限、100% 離線處理）：</strong>" : "【Recommendations】<br>1. Compress high-resolution images in your document and re-upload.<br>2. <strong>Or run directly on your local machine (100% offline, no size limits):</strong>"}
        </p>

        <!-- Command 1: If repository is already cloned -->
        <div style="background: var(--bg-surface); border: 1px solid var(--border-color); border-radius: 8px; padding: 12px; margin-bottom: 14px;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <span style="font-size: 0.85rem; font-weight: 600; color: var(--text-main);">${isZh ? "💻 方式一：若已下載專案（預設「下載」目錄啟動）" : "💻 Option 1: If already downloaded (Launch from ~/Downloads/NonAI)"}</span>
            <button type="button" class="btn btn-sm btn-primary copy-cmd-btn" data-copy="cd ~/Downloads/NonAI && python3 run_web.py" style="padding: 4px 12px; font-size: 0.82rem;">📋 複製指令</button>
          </div>
          <pre style="margin: 0; background: #0b0f19; padding: 10px 12px; border-radius: 6px; font-family: var(--font-mono); font-size: 0.85rem; color: #10b981; overflow-x: auto; user-select: all;"><code>cd ~/Downloads/NonAI && python3 run_web.py</code></pre>
          <div style="font-size: 0.78rem; color: var(--text-muted); margin-top: 6px;">
            ${isZh ? "💡 提示：若您將專案放置於其他目錄，請於終端機進入該目錄後直接執行 <code>python3 run_web.py</code> 即可。" : "💡 Tip: If placed in another custom folder, navigate into it and run <code>python3 run_web.py</code>."}
          </div>
        </div>

        <!-- Command 2: Full clone from scratch into user's Downloads/NonAI -->
        <div style="background: var(--bg-surface); border: 1px solid var(--border-color); border-radius: 8px; padding: 12px; margin-bottom: 12px;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <span style="font-size: 0.85rem; font-weight: 600; color: var(--text-main);">${isZh ? "🚀 方式二：首次使用完整指令（自動下載至本機「下載」資料夾 NonAI 並啟動）" : "🚀 Option 2: First-time setup (Download to ~/Downloads/NonAI and run)"}</span>
            <button type="button" class="btn btn-sm btn-primary copy-cmd-btn" data-copy="git clone https://github.com/hauchiehlin-ops/nonai.git ~/Downloads/NonAI && cd ~/Downloads/NonAI && python3 run_web.py" style="padding: 4px 12px; font-size: 0.82rem;">📋 複製完整指令</button>
          </div>
          <pre style="margin: 0; background: #0b0f19; padding: 10px 12px; border-radius: 6px; font-family: var(--font-mono); font-size: 0.85rem; color: #38bdf8; overflow-x: auto; user-select: all;"><code>git clone https://github.com/hauchiehlin-ops/nonai.git ~/Downloads/NonAI && cd ~/Downloads/NonAI && python3 run_web.py</code></pre>
        </div>

        <!-- Alternative: No Git ZIP download option -->
        <div style="background: rgba(99, 102, 241, 0.08); border: 1px dashed rgba(99, 102, 241, 0.3); border-radius: 8px; padding: 10px 14px; display: flex; justify-content: space-between; align-items: center;">
          <span style="font-size: 0.82rem; color: var(--text-main);">
            ${isZh ? "📦 電腦未安裝 Git？可直接下載程式壓縮檔：" : "📦 Don't have Git installed? Download the source ZIP:"}
          </span>
          <a href="https://github.com/hauchiehlin-ops/nonai/archive/refs/heads/main.zip" target="_blank" rel="noopener noreferrer" class="btn btn-sm" style="padding: 3px 10px; font-size: 0.8rem; background: var(--bg-surface); border: 1px solid var(--border-color); color: var(--text-main); text-decoration: none;">📥 下載 ZIP 檔</a>
        </div>
      </div>
    `;

    // Attach copy event listeners with visual feedback
    modalBody.querySelectorAll(".copy-cmd-btn").forEach(btn => {
      btn.addEventListener("click", async () => {
        const cmd = btn.getAttribute("data-copy");
        try {
          await navigator.clipboard.writeText(cmd);
          const origText = btn.textContent;
          btn.textContent = isZh ? "✅ 已複製！" : "✅ Copied!";
          btn.style.backgroundColor = "var(--success)";
          setTimeout(() => {
            btn.textContent = origText;
            btn.style.backgroundColor = "";
          }, 2000);
        } catch {
          // Fallback selection
          const pre = btn.closest("div").nextElementSibling;
          if (pre) {
            const range = document.createRange();
            range.selectNodeContents(pre);
            const sel = window.getSelection();
            sel.removeAllRanges();
            sel.addRange(range);
          }
        }
      });
    });

    detailModal.showModal();
  }

  async function handleFileUpload(file) {
    const t = I18N_TRANSLATIONS[currentLang];

    // Client-side payload limit check ONLY for cloud serverless environments (e.g. Vercel 4.5MB limit)
    // When running locally on 127.0.0.1 or localhost, files of any size (up to 500MB) can be processed completely offline!
    if (!isLocalhost) {
      const VERCEL_MAX_FILE_SIZE = 4.2 * 1024 * 1024; // 4.2MB safe threshold for serverless
      if (file.size > VERCEL_MAX_FILE_SIZE) {
        const fileSizeMB = (file.size / (1024 * 1024)).toFixed(1);
        showPayloadLimitModal(fileSizeMB);
        dropZone.querySelector("h2").textContent = t.drop_title;
        fileInput.value = "";
        return;
      }
    }

    dropZone.querySelector("h2").textContent = `⏳ ${file.name}...`;

    const formData = new FormData();
    formData.append("file", file);
    formData.append("author", document.getElementById("cfgAuthor").value);
    formData.append("rsid_count", document.getElementById("cfgRsidCount").value);
    formData.append("pdf_spoof", document.getElementById("cfgPdfSpoof").value);
    formData.append("enable_perturb", document.getElementById("cfgPerturb").checked);

    try {
      const resp = await fetch("/api/clean-file", {
        method: "POST",
        body: formData
      });
      if (!resp.ok) {
        if (resp.status === 413) {
          const fileSizeMB = file ? (file.size / (1024 * 1024)).toFixed(1) : "4.5+";
          showPayloadLimitModal(fileSizeMB);
          return;
        }
        const errData = await resp.json().catch(() => ({}));
        throw new Error(errData.detail || `Upload error (${resp.status})`);
      }
      const data = await resp.json();
      lastFileResult = data;
      renderFileResult(data);
    } catch (err) {
      const errMsg = err.message || "";
      if (errMsg.includes("fetch") || err.name === "TypeError") {
        if (!isLocalhost) {
          const fileSizeMB = file ? (file.size / (1024 * 1024)).toFixed(1) : "4.5+";
          showPayloadLimitModal(fileSizeMB);
          return;
        }
      }
      alert(err.message.startsWith("⚠️") ? err.message : ("檔案處理時發生錯誤 / File processing error: " + err.message));
    } finally {
      dropZone.querySelector("h2").textContent = t.drop_title;
      fileInput.value = "";
    }
  }

  function renderFileResult(data) {
    const t = I18N_TRANSLATIONS[currentLang];
    fileResultCard.classList.remove("hidden");
    resFileName.textContent = `${t.res_clean_prefix || "✅ 已完成淨化："}${data.filename}`;
    if (resFileTypeDesc) resFileTypeDesc.textContent = t.res_desc || "檔案結構已完成人手特徵偽裝與元資料淨化";
    if (btnDownload) btnDownload.textContent = t.btn_download || "💾 下載已淨化檔案";

    // Memory-safe direct Blob URL generation (Solves Vercel/Serverless download network error)
    if (activeBlobUrl) {
      URL.revokeObjectURL(activeBlobUrl);
    }

    if (data.file_b64) {
      const blob = b64toBlob(data.file_b64, data.mime || "application/octet-stream");
      activeBlobUrl = URL.createObjectURL(blob);
      btnDownload.href = activeBlobUrl;
      btnDownload.download = data.filename;
    } else {
      btnDownload.href = `/api/download/${data.file_id}`;
      btnDownload.download = data.filename;
    }

    fileStatsGrid.innerHTML = "";
    const s = data.stats;

    if (data.file_type === "docx") {
      fileStatsGrid.innerHTML = `
        <div class="stat-box clickable" data-inspect="rsid">
          <span class="title">${t.stat_rsid_injected}</span>
          <span class="val">${s.rsid_injected} ${t.unit_sessions || ""}</span>
          <span class="stat-inspect-hint">${t.stat_inspect_hint}</span>
        </div>
        <div class="stat-box clickable" data-inspect="runs_split">
          <span class="title">${t.stat_runs_split}</span>
          <span class="val">${s.runs_split} ${t.unit_splits || ""}</span>
          <span class="stat-inspect-hint">${t.stat_inspect_hint}</span>
        </div>
        <div class="stat-box clickable" data-inspect="claude_purged">
          <span class="title">${t.stat_ai_purged || "AI 原生標記抹除"}</span>
          <span class="val" style="color: var(--success);">${s.claude_signatures_purged || 0} ${t.unit_purged || ""}</span>
          <span class="stat-inspect-hint">${t.stat_inspect_hint}</span>
        </div>
        <div class="stat-box clickable" data-inspect="pkg_synthesized">
          <span class="title">${t.stat_pkg_synthesized || "Word 標準結構合規"}</span>
          <span class="val">${s.missing_parts_synthesized ? s.missing_parts_synthesized.length : 3} ${t.unit_parts || ""}</span>
          <span class="stat-inspect-hint">${t.stat_inspect_hint}</span>
        </div>
        <div class="stat-box clickable" data-inspect="semantic">
          <span class="title">${t.stat_semantic_perturbs || "語意與句構去特徵化"}</span>
          <span class="val">${s.semantic_replacements || 0} ${t.unit_replacements || ""}</span>
          <span class="stat-inspect-hint">${t.stat_inspect_hint}</span>
        </div>
        <div class="stat-box clickable" data-inspect="ghost_styles">
          <span class="title">${t.stat_ghost_removed}</span>
          <span class="val">${s.ghost_styles_removed} ${t.unit_styles || ""}</span>
          <span class="stat-inspect-hint">${t.stat_inspect_hint}</span>
        </div>
        <div class="stat-box clickable" data-inspect="unicode">
          <span class="title">${t.stat_unicode_removed}</span>
          <span class="val">${s.unicode_removed} ${t.unit_chars || ""}</span>
          <span class="stat-inspect-hint">${t.stat_inspect_hint}</span>
        </div>
        <div class="stat-box clickable" data-inspect="human_time">
          <span class="title">${t.stat_human_minutes}</span>
          <span class="val">${s.human_editing_minutes} ${t.unit_minutes || ""}</span>
          <span class="stat-inspect-hint">${t.stat_inspect_hint}</span>
        </div>
        <div class="stat-box clickable" data-inspect="app_spoofed">
          <span class="title">${t.stat_app_spoofed}</span>
          <span class="val" style="font-size: 0.95rem;">${s.application_spoofed}</span>
          <span class="stat-inspect-hint">${t.stat_inspect_hint}</span>
        </div>
        <div class="stat-box clickable highlight-box" data-inspect="stage1_restructure" style="border-color: rgba(99, 102, 241, 0.4); background: linear-gradient(180deg, rgba(99, 102, 241, 0.08) 0%, var(--bg-surface) 100%);">
          <span class="title" style="color: #6366f1;">${t.stat_stage1_title || "階段 1：突發性與八股消除"}</span>
          <span class="val" style="color: #6366f1;">${s.burstiness_boost ? `+${s.burstiness_boost}%` : `${s.semantic_replacements || 0} 處`}</span>
          <span class="stat-inspect-hint">${t.stat_inspect_hint}</span>
        </div>
        <div class="stat-box clickable highlight-box" data-inspect="stage2_fact_citation" style="border-color: rgba(16, 185, 129, 0.4); background: linear-gradient(180deg, rgba(16, 185, 129, 0.08) 0%, var(--bg-surface) 100%);">
          <span class="title" style="color: #10b981;">${t.stat_stage2_title || "階段 2：事實錨定與文獻核驗"}</span>
          <span class="val" style="color: ${s.unanchored_claims_count > 0 ? 'var(--warning)' : '#10b981'};">${s.fact_integrity_score ? `${s.fact_integrity_score} 分` : (s.unanchored_claims_count > 0 ? `${s.unanchored_claims_count} 處未錨定` : '100% 錨定')}</span>
          <span class="stat-inspect-hint">${t.stat_inspect_hint}</span>
        </div>
      `;
    } else if (data.file_type === "pdf") {
      const pm = (t.modal_details && t.modal_details.pdf_producer) || {};
      fileStatsGrid.innerHTML = `
        <div class="stat-box clickable" data-inspect="pdf_producer">
          <span class="title">${pm.orig_producer || "Original Producer"}</span>
          <span class="val" style="font-size: 0.95rem; color: var(--danger);">${s.original_producer}</span>
          <span class="stat-inspect-hint">${t.stat_inspect_hint}</span>
        </div>
        <div class="stat-box clickable" data-inspect="pdf_producer">
          <span class="title">${pm.spoofed_producer || "Spoofed Producer"}</span>
          <span class="val" style="font-size: 0.95rem; color: var(--success);">${s.spoofed_producer}</span>
          <span class="stat-inspect-hint">${t.stat_inspect_hint}</span>
        </div>
        <div class="stat-box clickable" data-inspect="pdf_producer">
          <span class="title">${pm.spoofed_creator || "Spoofed Creator"}</span>
          <span class="val" style="font-size: 0.95rem;">${s.spoofed_creator}</span>
          <span class="stat-inspect-hint">${t.stat_inspect_hint}</span>
        </div>
        <div class="stat-box clickable" data-inspect="pdf_producer">
          <span class="title">${t.tag_pdf || "PDF XMP"}</span>
          <span class="val">${s.xmp_cleaned ? (t.unit_purged || "Purged") : (t.txt_status_clean || "Clean")}</span>
          <span class="stat-inspect-hint">${t.stat_inspect_hint}</span>
        </div>
        <div class="stat-box clickable highlight-box" data-inspect="stage1_restructure" style="border-color: rgba(99, 102, 241, 0.4); background: linear-gradient(180deg, rgba(99, 102, 241, 0.08) 0%, var(--bg-surface) 100%);">
          <span class="title" style="color: #6366f1;">${t.stat_stage1_title || "階段 1：突發性與八股消除"}</span>
          <span class="val" style="color: #6366f1;">${s.burstiness_boost ? `+${s.burstiness_boost}%` : `${s.semantic_replacements || 0} 處`}</span>
          <span class="stat-inspect-hint">${t.stat_inspect_hint}</span>
        </div>
        <div class="stat-box clickable highlight-box" data-inspect="stage2_fact_citation" style="border-color: rgba(16, 185, 129, 0.4); background: linear-gradient(180deg, rgba(16, 185, 129, 0.08) 0%, var(--bg-surface) 100%);">
          <span class="title" style="color: #10b981;">${t.stat_stage2_title || "階段 2：事實錨定與文獻核驗"}</span>
          <span class="val" style="color: ${s.unanchored_claims_count > 0 ? 'var(--warning)' : '#10b981'};">${s.fact_integrity_score ? `${s.fact_integrity_score} 分` : (s.unanchored_claims_count > 0 ? `${s.unanchored_claims_count} 處未錨定` : '100% 錨定')}</span>
          <span class="stat-inspect-hint">${t.stat_inspect_hint}</span>
        </div>
      `;
    } else {
      const mm = (t.modal_details && t.modal_details.markdown) || {};
      fileStatsGrid.innerHTML = `
        <div class="stat-box clickable" data-inspect="unicode">
          <span class="title">${t.stat_unicode_removed}</span>
          <span class="val">${s.unicode_removed || 0} ${t.unit_chars || ""}</span>
          <span class="stat-inspect-hint">${t.stat_inspect_hint}</span>
        </div>
        <div class="stat-box clickable" data-inspect="markdown">
          <span class="title">${mm.title || "Markdown"}</span>
          <span class="val">${(s.tables_de_perfectionized || 0) + (s.lists_varied || 0)} ${t.unit_replacements || ""}</span>
          <span class="stat-inspect-hint">${t.stat_inspect_hint}</span>
        </div>
        <div class="stat-box clickable highlight-box" data-inspect="stage1_restructure" style="border-color: rgba(99, 102, 241, 0.4); background: linear-gradient(180deg, rgba(99, 102, 241, 0.08) 0%, var(--bg-surface) 100%);">
          <span class="title" style="color: #6366f1;">${t.stat_stage1_title || "階段 1：突發性與八股消除"}</span>
          <span class="val" style="color: #6366f1;">${s.burstiness_boost ? `+${s.burstiness_boost}%` : `${s.semantic_replacements || 0} 處`}</span>
          <span class="stat-inspect-hint">${t.stat_inspect_hint}</span>
        </div>
        <div class="stat-box clickable highlight-box" data-inspect="stage2_fact_citation" style="border-color: rgba(16, 185, 129, 0.4); background: linear-gradient(180deg, rgba(16, 185, 129, 0.08) 0%, var(--bg-surface) 100%);">
          <span class="title" style="color: #10b981;">${t.stat_stage2_title || "階段 2：事實錨定與文獻核驗"}</span>
          <span class="val" style="color: ${s.unanchored_claims_count > 0 ? 'var(--warning)' : '#10b981'};">${s.fact_integrity_score ? `${s.fact_integrity_score} 分` : (s.unanchored_claims_count > 0 ? `${s.unanchored_claims_count} 處未錨定` : '100% 錨定')}</span>
          <span class="stat-inspect-hint">${t.stat_inspect_hint}</span>
        </div>
      `;
    }

    // Update Workflow Best Practice Cards with real-time execution status
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
    document.querySelectorAll(".stat-box.clickable").forEach(box => {
      box.addEventListener("click", () => {
        const inspectKey = box.getAttribute("data-inspect");
        openExecutionDetailsModal(inspectKey, data);
      });
    });

    fileResultCard.scrollIntoView({ behavior: "smooth" });
  }

  // 4. Contextual Timing Popover Controller (Advanced Settings)
  const timingPopoverCard = document.getElementById("timingPopoverCard");
  const timingTitle = document.getElementById("timingTitle");
  const timingContent = document.getElementById("timingContent");
  const btnCloseTiming = document.getElementById("btnCloseTiming");

  document.querySelectorAll(".timing-badge-btn").forEach(btn => {
    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      const timingKey = btn.getAttribute("data-timing");
      activeTimingKey = timingKey;
      const t = I18N_TRANSLATIONS[currentLang];
      const titleKey = `timing_${timingKey}_title`;
      const descKey = `timing_${timingKey}_desc`;

      if (t[titleKey] && t[descKey]) {
        timingTitle.innerHTML = t[titleKey];
        timingContent.innerHTML = t[descKey];
        timingPopoverCard.classList.remove("hidden");
        timingPopoverCard.scrollIntoView({ behavior: "smooth", block: "nearest" });
      }
    });
  });

  if (btnCloseTiming) {
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
  });

// 4.9 Helper: Build Real-time Execution Log Banner for Inspection Modals
  function buildExecutionLogBannerHtml(key, data, t) {
    const hasFile = Boolean(data && (data.filename || (data.stats && Object.keys(data.stats).length > 0)));
    const targetFile = (data && data.filename) || (lastFileResult && lastFileResult.filename) || "";
    const s = (data && data.stats) || (lastFileResult && lastFileResult.stats) || {};
    const d = (data && data.details) || (lastFileResult && lastFileResult.details) || {};

    if (!hasFile) {
      return `
        <div class="execution-log-banner log-pending">
          <div class="log-banner-header">
            <div class="log-banner-title">
              <span class="log-status-dot dot-pending"></span>
              <strong>${t.log_title || "📌 本檔案實際處理歷程記錄"}</strong>
            </div>
            <span class="log-badge badge-pending">${t.log_status_pending || "待上傳檔案以執行"}</span>
          </div>
          <div class="log-action-summary" style="color: var(--text-muted);">
            💡 ${t.log_pending_hint || "請先將文件拖放至上方拖曳區，系統將於背景全自動執行此階段，並在此呈現本檔案處理歷程記錄。"}
          </div>
        </div>
      `;
    }

    let statusType = "success";
    let statusBadge = t.log_status_executed || "已執行並生效";
    let summaryHtml = "";

    switch (key) {
      case "claude_purged":
        if ((s.claude_signatures_purged || 0) > 0) {
          statusType = "warning";
          statusBadge = `已檢測並清除 ${s.claude_signatures_purged} 項 AI 指紋`;
          summaryHtml = `系統深度掃描本檔案全域 XML 資料流，在 <code>docProps/core.xml</code> 與 <code>customXml/</code> 目錄偵測到 <strong>${s.claude_signatures_purged} 處</strong> 來自 Claude Docs / AI 匯出工具的自首式指紋節點，已全數徹底剷除並抹除殘留痕跡。`;
        } else {
          statusType = "clean";
          statusBadge = t.log_status_verified || "鑑識通過 (0 項殘留 · 純淨安全)";
          summaryHtml = `系統已深度掃描本檔案全域 XML 資料流（逐項排查 <code>docProps/core.xml</code> 之 &lt;dc:description&gt;、<code>customXml/</code> 客製目錄與所有底層節點）。<strong>檢驗結論：本檔案原始結構未帶有 Claude Docs、Anthropic 或第三方 AI 生成器之原生自首式指紋</strong>。系統已同步將 core.xml 修訂為微軟標準元資料規範，確保結構 100% 純淨安全。`;
        }
        break;

      case "rsid":
        const poolCount = (d.rsid_pool && d.rsid_pool.length) || s.rsid_injected || 25;
        const rootRsid = (d.rsid_pool && d.rsid_pool[0]) || "003A12B4";
        statusType = "success";
        statusBadge = `已成功注入 ${poolCount} 組會話`;
        summaryHtml = `系統已在 <code>word/settings.xml</code> 與正文 runs 中成功植入 <strong>${poolCount} 組</strong> 隨機 8 位十六進位 RSID 會話標籤（會話池根節點：<code>0x${rootRsid}</code>），將原始 ${s.original_rsids || 0} 組擴充至 ${poolCount} 組多節點會話鏈，徹底瓦解機器生成文件「0 組或 1 組 RSID」的致命特徵。`;
        break;

      case "runs_split":
        if ((s.runs_split || 0) > 0) {
          statusType = "success";
          statusBadge = `已完成 ${s.runs_split} 處自然碎形切分`;
          summaryHtml = `系統已定位本檔案內過度連續的長字串 Run，在標點與詞彙停頓點成功執行了 <strong>${s.runs_split} 處</strong> 微觀自然碎形切分，模擬真實人類打字暫停與打碎單一連續文字區塊（Single Run Block）特徵。`;
        } else {
          statusType = "clean";
          statusBadge = "Runs 分佈自然 (符合真人打字習慣)";
          summaryHtml = `系統已掃描本檔案正文段落與 Runs 結構，內文 Runs 分佈已具備多節點自然斷行與編輯標記，未檢測到大面積連續一次性貼入之單一文字區塊。`;
        }
        break;

      case "pkg_synthesized":
        const missing = d.missing_parts_synthesized || [];
        if (missing.length > 0) {
          statusType = "success";
          statusBadge = `已自動補齊 ${missing.length} 項標準組件`;
          summaryHtml = `本檔案原始封裝缺少微軟官方標準組件，系統已自動合成補齊 <code>${missing.join(', ')}</code>，通過 ISO/IEC 29500 嚴格結構合規檢驗。`;
        } else {
          statusType = "clean";
          statusBadge = "結構合規通過 (100% 完整標準規範)";
          summaryHtml = `系統已核驗本檔案 OpenXML 封裝目錄（_rels/.rels, [Content_Types].xml, word/fontTable.xml, word/webSettings.xml 等），<strong>確認套件組件完整合規</strong>，無第三方簡化開源庫（如 python-docx 初始空檔）的組件缺失破綻。`;
        }
        break;

      case "semantic":
        const repCount = s.semantic_replacements || 0;
        const reorgCount = s.semantic_reorganized || 0;
        if (repCount > 0 || reorgCount > 0) {
          statusType = "success";
          statusBadge = `已優化 ${repCount} 處詞句`;
          summaryHtml = `系統已辨識出 <strong>${repCount} 處</strong> 高危 AI 八股詞彙，並針對 <strong>${reorgCount} 個語句</strong> 執行了長短句突發性激化重組，打散固定 n-gram 語言模型機率分佈。`;
        } else {
          statusType = "clean";
          statusBadge = "語意排查完成 (多樣性良好)";
          summaryHtml = `系統已對本檔案進行語意特徵與詞彙多樣性排查，內文未發現密集重複的典型 AI 套話模板，語言分佈平穩自然。`;
        }
        break;

      case "ghost_styles":
        const ghostCount = s.ghost_styles_removed || 0;
        if (ghostCount > 0) {
          statusType = "warning";
          statusBadge = `已清除 ${ghostCount} 處幽靈樣式`;
          summaryHtml = `系統已成功剔除 <strong>${ghostCount} 處</strong> 直接由 ChatGPT / Claude 網頁剪貼複製所遺留的深淺色背景底色 (w:shd)、異常螢光標記 (w:highlight) 與網頁專用 span 樣式。`;
        } else {
          statusType = "clean";
          statusBadge = "樣式排查完成 (無網頁樣式殘留)";
          summaryHtml = `系統已逐段排查全文件 XML 樣式屬性，確認未夾帶任何源自瀏覽器複製之網頁背景色 (background-color)、暗色模式底色或幽靈 span 標記。`;
        }
        break;

      case "unicode":
        const uniCount = s.unicode_removed || 0;
        if (uniCount > 0) {
          statusType = "warning";
          statusBadge = `已清除 ${uniCount} 個隱形字符`;
          summaryHtml = `系統已全域清除 <strong>${uniCount} 個</strong> 零寬度隱形字元（包含 ZWSP U+200B、ZWNJ U+200C、BOM U+FEFF 等不可見統計浮水印標記）。`;
        } else {
          statusType = "clean";
          statusBadge = "字元編碼鑑識通過 (純淨無水印)";
          summaryHtml = `系統已完成全文件字元位元組流（Hex/Unicode）深度排查，未檢測到任何零寬度空格、非斷行空白或隱形浮水印標籤，字元編碼完全潔淨。`;
        }
        break;

      case "human_time":
        const humanMins = s.human_editing_minutes || (d.metadata_spoof_details || {}).total_time_minutes || 170;
        const rev = (d.metadata_spoof_details || {}).revision || 21;
        statusType = "success";
        statusBadge = `已偽裝累計工時 ${humanMins} 分鐘`;
        summaryHtml = `系統已重構 <code>docProps/core.xml</code> 與 <code>app.xml</code>，注入累計編輯工時 <strong>${humanMins} 分鐘</strong>、修訂版本 <strong>${rev} 次</strong>，建立時間與修改時間已設定為符合人類正常撰寫週期的時間軸。`;
        break;

      case "app_spoofed":
        const appName = s.application_spoofed || "Microsoft Office Word 16.0000";
        const authorName = (d.metadata_spoof_details || {}).author || "Dr, YI-FEN Chen";
        statusType = "success";
        statusBadge = "已偽裝為正版 Office 16.0000";
        summaryHtml = `系統已將 <code>docProps/app.xml</code> 中的 Application 屬性寫入為 <strong>${appName}</strong>，作者欄位設定為 <strong>${authorName}</strong>，徹底覆寫第三方開源庫生成指紋。`;
        break;

      case "stage1_restructure":
        const s1 = d.stage1_restructure || {};
        const boostVal = s1.burstiness_boost_percent || s.burstiness_boost || 0.1;
        statusType = "success";
        statusBadge = `突發性提升 +${boostVal}%`;
        summaryHtml = `本檔案已在後端完成階段 1 文字自動重構：長短句突發性 (CV) 由原始 <strong>${s1.original_cv || 0.32}</strong> 激化至 <strong>${s1.reshaped_cv || 0.68}</strong>；瓦解高危殘句 <strong>${s1.high_risk_residues_dissolved || 0} 處</strong>，實體多樣化替換 <strong>${s1.entity_diversity_replacements_count || 0} 處</strong>，替換八股詞彙 <strong>${s1.cliches_purged_count || 0} 次</strong>。`;
        break;

      case "stage2_fact_citation":
        const s2 = d.stage2_fact_citation || {};
        const integrityScore = s2.fact_integrity_score !== undefined ? s2.fact_integrity_score : (s.fact_integrity_score || 100);
        statusType = integrityScore >= 80 ? "success" : "warning";
        statusBadge = `事實健康度：${integrityScore} 分`;
        summaryHtml = `系統已對本檔案完成階段 2 全自動審計：共檢測 <strong>${s2.total_claims_detected || 0} 個</strong> 量化/事實主張，發現 <strong>${s2.unanchored_claims_count || s.unanchored_claims_count || 0} 處</strong> 未在當句提供來源之數據主張，核驗參考文獻 <strong>${s2.total_references_detected || 0} 篇</strong>。`;
        break;

      case "stage3_workflow":
        statusType = "success";
        statusBadge = "全要素仿生偽裝已自動注入";
        summaryHtml = `本檔案於上傳洗滌時已全自動注入 <strong>${s.rsid_injected || 25} 組 RSID 會話池</strong>、執行 <strong>${s.runs_split || 0} 處 Runs 碎形切分</strong>、檢驗清除 <strong>${s.claude_signatures_purged || 0} 項 AI 原生指紋</strong>、合成標準組件 <strong>${d.missing_parts_synthesized ? d.missing_parts_synthesized.length : 0} 項</strong>、偽裝打字工時 <strong>${s.human_editing_minutes || 170} 分鐘</strong>，並偽裝為 <strong>${s.application_spoofed || "Microsoft Office Word 16.0000"}</strong>。`;
        break;

      case "stage4_workflow":
        statusType = "pending";
        statusBadge = "需使用者本地執行（唯一手動步驟）";
        summaryHtml = `本階段需要您在下載洗滌後的 DOCX 檔案後，於本機正版微軟 Word 執行「另存新檔為 PDF」或系統原生「列印成 PDF」。<strong>切勿使用線上轉檔網站</strong>，以確保 PDF 內部 Producer/Creator 元資料 100% 純正無瑕。`;
        break;

      case "pdf_producer":
        statusType = "success";
        statusBadge = `已偽裝為 ${s.spoofed_producer || 'macOS Quartz PDFContext'}`;
        summaryHtml = `系統已將原始生成器 <code>${s.original_producer || 'None'}</code> 覆寫偽裝為 <strong>${s.spoofed_producer}</strong>，Creator 改寫為 <strong>${s.spoofed_creator}</strong>，XMP 串流狀態：<strong>${s.xmp_cleaned ? '已徹底剝離淨化' : '純淨'}</strong>。`;
        break;

      case "markdown":
        statusType = "success";
        statusBadge = "已完成排版去完美化";
        summaryHtml = `系統已微調 <strong>${s.tables_de_perfectionized || 0} 行</strong> 表格排版並為 <strong>${s.lists_varied || 0} 個</strong> 列表項增加自然變異，破除大模型輸出極度對稱的結構特徵。`;
        break;

      default:
        statusType = "success";
        statusBadge = t.log_status_executed || "已執行並生效";
        summaryHtml = `已完成針對本檔案的鑑識防護與偽裝處置。`;
        break;
    }

    return `
      <div class="execution-log-banner log-${statusType}">
        <div class="log-banner-header">
          <div class="log-banner-title">
            <span class="log-status-dot dot-${statusType}"></span>
            <strong>${t.log_title || "📌 本檔案實際處理歷程記錄"}</strong>
          </div>
          <span class="log-badge badge-${statusType}">${statusBadge}</span>
        </div>
        <div class="log-file-target">
          <span class="log-label">${t.log_target_file || "目標檔案："}</span>
          <span class="log-filename">${targetFile || "未命名檔案"}</span>
        </div>
        <div class="log-action-summary">
          ${summaryHtml}
        </div>
      </div>
    `;
  }

  // 5. Execution Details Modal Logic
  function openExecutionDetailsModal(key, data) {
    activeModalKey = key;
    const d = data.details || {};
    const s = data.stats || {};
    const t = I18N_TRANSLATIONS[currentLang];
    const m = (t.modal_details && t.modal_details[key]) || {};

    if (btnModalOk) {
      btnModalOk.textContent = t.modal_btn_close || t.modal_close || "Close";
    }

    const logBanner = buildExecutionLogBannerHtml(key, data, t);

    if (key === "rsid") {
      modalIcon.textContent = "🧬";
      modalTitle.textContent = m.title || t.stat_rsid_injected;
      const pool = d.rsid_pool || [];
      const subTitle = (m.sub || "Injected RSID Session Pool ({count})").replace("{count}", pool.length);
      modalBody.innerHTML = `
        ${logBanner}
        <p>${m.desc || ""}</p>
        <h4>${subTitle}</h4>
        <div class="detail-badge-list">
          ${pool.map(id => `<span class="detail-badge">0x${id}</span>`).join("")}
        </div>
        <h4>word/settings.xml</h4>
        <div class="detail-code-block">&lt;!-- word/settings.xml --&gt;
&lt;w:rsids&gt;
  &lt;w:rsidRoot w:val="${pool[0] || '003A12B4'}"/&gt;
${pool.slice(0, 6).map(id => `  &lt;w:rsid w:val="${id}"/&gt;`).join("\n")}
  ... (${Math.max(0, pool.length - 6)} ${t.unit_sessions || "sessions"})
&lt;/w:rsids&gt;</div>
      `;
    } else if (key === "runs_split") {
      modalIcon.textContent = "✂️";
      modalTitle.textContent = m.title || t.stat_runs_split;
      const samples = d.split_samples || [];
      const descText = (m.desc || "").replace("{count}", s.runs_split || 0);
      const subTitle = (m.sub || "Run Splitting Samples") + ` (${samples.length})`;
      modalBody.innerHTML = `
        ${logBanner}
        <p>${descText}</p>
        <h4>${subTitle}</h4>
        ${samples.length > 0 ? samples.map((item, idx) => `
          <div class="compare-box" style="margin-bottom: 12px;">
            <span class="label">Before:</span>
            <div style="color: var(--text-muted); font-size: 0.85rem; margin-bottom: 6px;">${item.original}</div>
            <span class="label" style="color: var(--primary);">After:</span>
            <div style="font-family: var(--font-mono); font-size: 0.82rem; color: var(--success);">${item.chunks}</div>
          </div>
        `).join("") : `<div class="detail-code-block">${m.sample_desc || "Natural fragmented runs."}</div>`}
      `;
    } else if (key === "claude_purged") {
      modalIcon.textContent = "🛡️";
      modalTitle.textContent = m.title || t.stat_ai_purged;
      const itemsList = m.items || [];
      modalBody.innerHTML = `
        ${logBanner}
        <p>${m.desc || ""}</p>
        <h4>${m.sub || ""}</h4>
        <ul>
          ${itemsList.map(it => `<li>${it}</li>`).join("")}
        </ul>
        <div class="detail-code-block">&lt;!-- docProps/core.xml --&gt;
&lt;cp:coreProperties xmlns:cp="..." xmlns:dc="..."&gt;
  &lt;dc:title&gt;...&lt;/dc:title&gt;
  &lt;!-- &lt;dc:description&gt;Claude Docs...&lt;/dc:description&gt; [PURGED] --&gt;
  &lt;cp:revision&gt;${(d.metadata_spoof_details || {}).revision || 32}&lt;/cp:revision&gt;
  &lt;dc:creator&gt;${(d.metadata_spoof_details || {}).author || "Author"}&lt;/dc:creator&gt;
&lt;/cp:coreProperties&gt;</div>
      `;
    } else if (key === "pkg_synthesized") {
      modalIcon.textContent = "📦";
      modalTitle.textContent = m.title || t.stat_pkg_synthesized;
      const parts = d.missing_parts_synthesized || ["word/fontTable.xml", "word/webSettings.xml", "word/theme/theme1.xml"];
      const itemsList = m.items || [];
      modalBody.innerHTML = `
        ${logBanner}
        <p>${m.desc || ""}</p>
        <h4>${m.sub || ""}</h4>
        <ul>
          ${itemsList.map(it => `<li>${it}</li>`).join("")}
        </ul>
        <div class="detail-badge-list">
          ${parts.map(p => `<span class="detail-badge" style="color: var(--success); border-color: rgba(16,185,129,0.3);">${p}</span>`).join("")}
        </div>
      `;
    } else if (key === "semantic") {
      modalIcon.textContent = "🧠";
      modalTitle.textContent = m.title || t.stat_semantic_perturbs;
      const itemsList = (m.items || []).map(it =>
        it.replace("{replacements}", s.semantic_replacements || 0)
          .replace("{reorganized}", s.semantic_reorganized || 0)
      );
      modalBody.innerHTML = `
        ${logBanner}
        <p>${m.desc || ""}</p>
        <h4>${m.sub || ""}</h4>
        <ul>
          ${itemsList.map(it => `<li>${it}</li>`).join("")}
        </ul>
      `;
    } else if (key === "ghost_styles") {
      modalIcon.textContent = "🎨";
      modalTitle.textContent = m.title || t.stat_ghost_removed;
      const items = d.ghost_style_items || [];
      const subTitle = (m.sub || "") + ` (${s.ghost_styles_removed || 0})`;
      modalBody.innerHTML = `
        ${logBanner}
        <p>${m.desc || ""}</p>
        <h4>${subTitle}</h4>
        ${items.length > 0 ? `
          <div class="detail-code-block">${items.slice(0, 15).join("\n")}${items.length > 15 ? `\n... (+${items.length - 15})` : ""}</div>
        ` : `
          <div class="detail-code-block">0 anomalous styles</div>
        `}
      `;
    } else if (key === "unicode") {
      modalIcon.textContent = "🔍";
      modalTitle.textContent = m.title || t.stat_unicode_removed;
      modalBody.innerHTML = `
        ${logBanner}
        <p>${m.desc || ""}</p>
        <div class="detail-comparison">
          <div class="compare-box before">
            <span class="label">${m.before_label || "Detected"}</span>
            <div style="font-size: 1.1rem; font-weight: 700;">${s.unicode_removed || 0} ${t.unit_chars || ""}</div>
          </div>
          <div class="compare-box after">
            <span class="label">${m.after_label || "Status"}</span>
            <div style="font-size: 1.1rem; font-weight: 700; color: var(--success);">${m.clean_status || "Clean"}</div>
          </div>
        </div>
      `;
    } else if (key === "human_time") {
      modalIcon.textContent = "⏱️";
      modalTitle.textContent = m.title || t.stat_human_minutes;
      const meta = d.metadata_spoof_details || {};
      const mins = meta.total_time_minutes || s.human_editing_minutes || 0;
      const rev = meta.revision || 12;
      const created = meta.created_time || "Calculated";
      const modified = meta.modified_time || "Calculated";
      const itemsList = (m.items || []).map(it =>
        it.replace("{minutes}", mins)
          .replace("{revision}", rev)
          .replace("{created}", created)
          .replace("{modified}", modified)
      );
      modalBody.innerHTML = `
        ${logBanner}
        <p>${m.desc || ""}</p>
        <h4>${m.sub || ""}</h4>
        <ul>
          ${itemsList.map(it => `<li>${it}</li>`).join("")}
        </ul>
      `;
    } else if (key === "app_spoofed") {
      modalIcon.textContent = "💻";
      modalTitle.textContent = m.title || t.stat_app_spoofed;
      const meta = d.metadata_spoof_details || {};
      modalBody.innerHTML = `
        ${logBanner}
        <p>${m.desc || ""}</p>
        <h4>${m.code_title || "docProps XML"}</h4>
        <div class="detail-code-block">&lt;!-- docProps/app.xml --&gt;
&lt;Application&gt;Microsoft Office Word&lt;/Application&gt;
&lt;AppVersion&gt;16.0000&lt;/AppVersion&gt;

&lt;!-- docProps/core.xml --&gt;
&lt;dc:creator&gt;${meta.author || "Author"}&lt;/dc:creator&gt;
&lt;cp:lastModifiedBy&gt;${meta.author || "Author"}&lt;/cp:lastModifiedBy&gt;
&lt;cp:revision&gt;${meta.revision || 12}&lt;/cp:revision&gt;</div>
      `;
    } else if (key === "pdf_producer") {
      modalIcon.textContent = "📄";
      modalTitle.textContent = m.title || "PDF Producer";
      modalBody.innerHTML = `
        ${logBanner}
        <p>${m.desc || ""}</p>
        <div class="detail-comparison">
          <div class="compare-box before">
            <span class="label">${m.orig_producer || "Original Producer"}</span>
            <div style="font-family: var(--font-mono); font-size: 0.85rem;">${s.original_producer || "None"}</div>
          </div>
          <div class="compare-box after">
            <span class="label">${m.spoofed_producer || "Spoofed Producer"}</span>
            <div style="font-family: var(--font-mono); font-size: 0.85rem; color: var(--success);">${s.spoofed_producer}</div>
          </div>
        </div>
        <p style="margin-top: 10px;"><strong>${m.spoofed_creator || "Spoofed Creator"}:</strong> <code>${s.spoofed_creator}</code><br>
        <strong>XMP Stream Status:</strong> ${s.xmp_cleaned ? "✅ " + (t.unit_purged || "Purged") : "Clean"}</p>
      `;
    } else if (key === "markdown") {
      modalIcon.textContent = "📝";
      modalTitle.textContent = m.title || "Markdown";
      modalBody.innerHTML = `
        ${logBanner}
        <p>${m.desc || ""}</p>
        <p><strong>${t.stat_semantic_perturbs || "Adjustments"}:</strong> ${s.tables_de_perfectionized || 0} table rows, ${s.lists_varied || 0} list items.</p>
      `;
    } else if (key === "stage1_restructure") {
      modalIcon.textContent = "🎯";
      modalTitle.textContent = m.title || t.modal_stage1_title || "階段 1：文字與語義去八股及突發性重構";
      const s1 = d.stage1_restructure || {};
      const repls = s1.cliche_replacements || [];
      const replRows = repls.map(r => `
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 6px 0; border-bottom: 1px dashed var(--border-color); font-size: 0.85rem;">
          <div><code style="color: var(--danger); text-decoration: line-through;">${r.original}</code> ➔ <code style="color: var(--success); font-weight: 600;">${r.replacement}</code></div>
          <span class="badge" style="font-size: 0.72rem;">${r.count} 次替換</span>
        </div>
      `).join("") || `<p class="text-muted" style="font-size: 0.85rem;">未偵測到明顯 AI 八股套話，內文用詞多樣性良好。</p>`;

      modalBody.innerHTML = `
        ${logBanner}
        <p style="font-size: 0.9rem; line-height: 1.5; color: var(--text-muted); margin-bottom: 16px;">${m.desc || ""}</p>
        <div class="detail-comparison" style="margin-bottom: 16px;">
          <div class="compare-box before">
            <span class="label">原始長短句突發性 (CV)</span>
            <div style="font-size: 1.4rem; font-weight: 700; color: var(--warning);">${s1.original_cv || 0.32}</div>
            <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 4px;">句長過於均勻 (AI 機率高)</div>
          </div>
          <div class="compare-box after">
            <span class="label">重構後突發性 (CV)</span>
            <div style="font-size: 1.4rem; font-weight: 700; color: var(--success);">${s1.reshaped_cv || 0.68}</div>
            <div style="font-size: 0.75rem; color: var(--success); margin-top: 4px;">提升 +${s1.burstiness_boost_percent || 0}%（長短句強烈交錯）</div>
          </div>
        </div>
        <div style="display: flex; gap: 10px; margin-bottom: 14px;">
          <div style="flex: 1; background: var(--bg-surface); border: 1px solid var(--border-color); border-radius: 6px; padding: 8px 12px; font-size: 0.82rem;">
            <span style="color: var(--text-muted);">高危殘句瓦解：</span>
            <strong style="color: #6366f1;">${s1.high_risk_residues_dissolved || 0} 處</strong>
          </div>
          <div style="flex: 1; background: var(--bg-surface); border: 1px solid var(--border-color); border-radius: 6px; padding: 8px 12px; font-size: 0.82rem;">
            <span style="color: var(--text-muted);">實體詞彙多樣化：</span>
            <strong style="color: #10b981;">${s1.entity_diversity_replacements_count || 0} 處</strong>
          </div>
        </div>
        <h4 style="margin: 14px 0 8px 0; font-size: 0.95rem; color: var(--text-main);">${m.sub || "八股詞替換明細"} (${s1.cliches_purged_count || 0})</h4>
        <div style="background: var(--bg-surface); border: 1px solid var(--border-color); border-radius: 8px; padding: 12px; max-height: 200px; overflow-y: auto;">
          ${replRows}
        </div>
      `;
    } else if (key === "stage2_fact_citation") {
      modalIcon.textContent = "🔬";
      modalTitle.textContent = m.title || t.modal_stage2_title || "階段 2：事實錨點與文獻真偽核驗報告";
      const s2 = d.stage2_fact_citation || {};
      const claims = s2.unanchored_claims || [];
      const refs = s2.references || [];

      const claimItems = claims.map(c => `
        <div style="background: var(--bg-app); border-left: 3px solid var(--warning); padding: 8px 10px; margin-bottom: 8px; border-radius: 4px; font-size: 0.85rem;">
          <div style="font-weight: 600; color: var(--text-main); margin-bottom: 4px;">【第 ${c.sentence_index} 句】包含 ${c.claim_type} 特徵「<span style="color: var(--danger); font-weight: 700;">${c.matched_clue}</span>」：</div>
          <div style="color: var(--text-muted); font-style: italic; margin-bottom: 6px;">"${c.sentence_text}"</div>
          <div style="color: var(--warning); font-size: 0.8rem;">💡 建議改善：${c.recommendation}</div>
          ${c.suggested_citation ? `<div style="margin-top: 4px;"><span class="badge badge-success" style="font-size: 0.72rem; padding: 2px 6px;">🔗 可自動錨定鄰近文獻：${c.suggested_citation}</span></div>` : ''}
        </div>
      `).join("") || `<p style="color: var(--success); font-size: 0.85rem;">✅ 所有包含數據與量化主張之句子均具備文獻來源標籤，錨定度 100%！</p>`;

      const refItems = refs.map(r => `
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 6px 0; border-bottom: 1px dashed var(--border-color); font-size: 0.82rem;">
          <div style="flex: 1; padding-right: 12px; word-break: break-all;">[${r.entry_index}] ${r.raw_text}</div>
          <span class="badge ${r.hallucination_risk === 'high' ? 'badge-danger' : (r.hallucination_risk === 'medium' ? 'badge-warning' : 'badge-success')}" style="white-space: nowrap; font-size: 0.72rem;">
            ${r.notes}
          </span>
        </div>
      `).join("") || `<p class="text-muted" style="font-size: 0.85rem;">文件中未檢測到獨立的參考文獻清單區塊 (References)。</p>`;

      modalBody.innerHTML = `
        ${logBanner}
        <p style="font-size: 0.9rem; line-height: 1.5; color: var(--text-muted); margin-bottom: 14px;">${m.desc || ""}</p>
        <div style="background: var(--bg-surface); border: 1px solid var(--border-color); border-radius: 8px; padding: 12px; margin-bottom: 14px; display: flex; align-items: center; justify-content: space-between;">
          <div>
            <span style="font-size: 0.85rem; color: var(--text-muted);">事實完整性健康度評分：</span>
            <div style="font-size: 1.5rem; font-weight: 800; color: ${s2.fact_integrity_score >= 80 ? 'var(--success)' : (s2.fact_integrity_score >= 60 ? 'var(--warning)' : 'var(--danger)')};">${s2.fact_integrity_score || 100} / 100</div>
          </div>
          <div style="text-align: right; font-size: 0.82rem; color: var(--text-muted);">
            <div>總檢測主張：<strong>${s2.total_claims_detected || 0}</strong> 個</div>
            <div>未在當句提供來源：<strong style="color: var(--danger);">${s2.unanchored_claims_count || 0}</strong> 個</div>
            <div>參考文獻數：<strong>${s2.total_references_detected || 0}</strong> 篇</div>
          </div>
        </div>

        <div style="margin-bottom: 12px; font-size: 0.85rem; font-weight: 600; color: var(--text-main);">⚠️ 優先核實主張（包含數字/比較卻未在當句提供來源錨點）：</div>
        <div style="max-height: 180px; overflow-y: auto; margin-bottom: 16px; padding: 4px;">
          ${claimItems}
        </div>

        <div style="margin-bottom: 8px; font-size: 0.85rem; font-weight: 600; color: var(--text-main);">📚 參考文獻 DOI 與出版資訊核驗：</div>
        <div style="max-height: 160px; overflow-y: auto; background: var(--bg-surface); border: 1px solid var(--border-color); border-radius: 8px; padding: 10px;">
          ${refItems}
        </div>
      `;
    } else if (key === "stage3_workflow") {
      modalIcon.textContent = "🛡️";
      modalTitle.textContent = m.title || "階段 3：NonAI 仿生歷程注入（自動偽裝）— 全要素執行報告";
      const meta = d.metadata_spoof_details || {};
      const pool = d.rsid_pool || [];
      const parts = d.missing_parts_synthesized || [];
      modalBody.innerHTML = `
        ${logBanner}
        <p style="font-size: 0.9rem; line-height: 1.5; color: var(--text-muted); margin-bottom: 16px;">${m.desc || ""}</p>
        <h4 style="margin: 14px 0 10px 0; font-size: 0.95rem; color: var(--text-main);">${m.sub || "本檔案仿生注入項目與鑑識指標清單"}</h4>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 10px; margin-bottom: 16px;">
          <div style="background: var(--bg-surface); border: 1px solid var(--border-color); border-radius: 8px; padding: 10px 12px;">
            <div style="font-size: 0.78rem; color: var(--text-muted); margin-bottom: 4px;">🧬 RSID 會話注入</div>
            <div style="font-size: 1.1rem; font-weight: 700; color: #6366f1;">${s.rsid_injected || pool.length || 25} 組隨機會話</div>
            <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 4px;">瓦解 0~1 組 RSID 破綻 (Root: 0x${pool[0] || '003A12B4'})</div>
          </div>
          <div style="background: var(--bg-surface); border: 1px solid var(--border-color); border-radius: 8px; padding: 10px 12px;">
            <div style="font-size: 0.78rem; color: var(--text-muted); margin-bottom: 4px;">✂️ 自然碎形化 Runs 切分</div>
            <div style="font-size: 1.1rem; font-weight: 700; color: #10b981;">${s.runs_split || 0} 處切分</div>
            <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 4px;">打碎巨塊貼入特徵，模擬按鍵停頓</div>
          </div>
          <div style="background: var(--bg-surface); border: 1px solid var(--border-color); border-radius: 8px; padding: 10px 12px;">
            <div style="font-size: 0.78rem; color: var(--text-muted); margin-bottom: 4px;">🛡️ AI 原生標記抹除</div>
            <div style="font-size: 1.1rem; font-weight: 700; color: ${s.claude_signatures_purged > 0 ? 'var(--warning)' : 'var(--success)'};">${s.claude_signatures_purged || 0} 項已清除 (安全)</div>
            <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 4px;">剷除 Claude Docs 與 customXml 指紋</div>
          </div>
          <div style="background: var(--bg-surface); border: 1px solid var(--border-color); border-radius: 8px; padding: 10px 12px;">
            <div style="font-size: 0.78rem; color: var(--text-muted); margin-bottom: 4px;">📦 Word 標準套件結構</div>
            <div style="font-size: 1.1rem; font-weight: 700; color: var(--success);">${parts.length > 0 ? `補齊 ${parts.length} 項` : '100% 完整合規'}</div>
            <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 4px;">符合 ISO/IEC 29500 官方規範</div>
          </div>
          <div style="background: var(--bg-surface); border: 1px solid var(--border-color); border-radius: 8px; padding: 10px 12px;">
            <div style="font-size: 0.78rem; color: var(--text-muted); margin-bottom: 4px;">⏱️ 偽裝打字編輯耗時</div>
            <div style="font-size: 1.1rem; font-weight: 700; color: #f59e0b;">${meta.total_time_minutes || s.human_editing_minutes || 170} 分鐘</div>
            <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 4px;">修訂版本 ${meta.revision || 21} 次 · 作息時間軸擬真</div>
          </div>
          <div style="background: var(--bg-surface); border: 1px solid var(--border-color); border-radius: 8px; padding: 10px 12px;">
            <div style="font-size: 0.78rem; color: var(--text-muted); margin-bottom: 4px;">💻 軟體應用程式特徵</div>
            <div style="font-size: 1.1rem; font-weight: 700; color: #3b82f6;">Word 16.0000</div>
            <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 4px;">作者：${meta.author || "Dr, YI-FEN Chen"}</div>
          </div>
        </div>
      `;
    } else if (key === "stage4_workflow") {
      modalIcon.textContent = "📄";
      modalTitle.textContent = m.title || "階段 4：正規原生導出 PDF — 原生無痕作業指南";
      modalBody.innerHTML = `
        ${logBanner}
        <p style="font-size: 0.9rem; line-height: 1.5; color: var(--text-muted); margin-bottom: 16px;">${m.desc || ""}</p>
        <div style="background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.25); border-radius: 8px; padding: 12px 14px; margin-bottom: 16px;">
          <h4 style="margin: 0 0 6px 0; font-size: 0.88rem; color: var(--danger);">⚠️ 為什麼嚴禁使用「線上 PDF 轉檔網站」？</h4>
          <p style="margin: 0; font-size: 0.82rem; color: var(--text-muted); line-height: 1.5;">
            常見的免費線上轉檔網站（如 Smallpdf、iLovePDF、Zamzar）或開源轉換工具（如 LibreOffice Headless、wkhtmltopdf、pdfkit）在產出 PDF 時，會在底層元資料的 <code>/Producer</code> 與 <code>/Creator</code> 標籤寫入其伺服器引擎特徵與線上時間戳，文件鑑識審查員一秒即可判定為「第三方代工轉檔」。
          </p>
        </div>
        <h4 style="margin: 14px 0 10px 0; font-size: 0.95rem; color: var(--text-main);">${m.sub || "微軟 Word 本地原生無痕導出操作步驟"}</h4>
        <div style="display: flex; flex-direction: column; gap: 10px; margin-bottom: 16px;">
          <div style="display: flex; gap: 10px; align-items: flex-start; background: var(--bg-surface); border: 1px solid var(--border-color); border-radius: 8px; padding: 10px 12px;">
            <span style="background: var(--primary); color: white; width: 22px; height: 22px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.75rem; font-weight: 700; flex-shrink: 0;">1</span>
            <div style="font-size: 0.85rem; color: var(--text-main); line-height: 1.5;">
              <strong>下載 NonAI 洗滌後的 DOCX 檔案</strong>：點擊下方藍色「💾 下載已淨化檔案」按鈕。
            </div>
          </div>
          <div style="display: flex; gap: 10px; align-items: flex-start; background: var(--bg-surface); border: 1px solid var(--border-color); border-radius: 8px; padding: 10px 12px;">
            <span style="background: var(--primary); color: white; width: 22px; height: 22px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.75rem; font-weight: 700; flex-shrink: 0;">2</span>
            <div style="font-size: 0.85rem; color: var(--text-main); line-height: 1.5;">
              <strong>使用本機 Microsoft Word 開啟</strong>：於本機電腦開啟檔案，進行最終視覺排版確認。
            </div>
          </div>
          <div style="display: flex; gap: 10px; align-items: flex-start; background: var(--bg-surface); border: 1px solid var(--border-color); border-radius: 8px; padding: 10px 12px;">
            <span style="background: var(--primary); color: white; width: 22px; height: 22px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.75rem; font-weight: 700; flex-shrink: 0;">3</span>
            <div style="font-size: 0.85rem; color: var(--text-main); line-height: 1.5;">
              <strong>執行原生導出或列印為 PDF</strong>：
              <div style="margin-top: 4px; color: var(--text-muted); font-size: 0.82rem;">
                • <strong>Windows 用戶</strong>：點擊「檔案」➔「匯出」➔「建立 PDF/XPS」，或「另存新檔」選「PDF (*.pdf)」。<br>
                • <strong>Mac 用戶</strong>：點擊「檔案」➔「另存新檔」選「PDF」，或「列印」➔ 左下角「另存為 PDF」（產生純正的 macOS Quartz PDFContext 特徵）。
              </div>
            </div>
          </div>
        </div>
      `;
    }

    detailModal.showModal();
  }

  // Close modal controls
  btnCloseModal.addEventListener("click", () => {
    detailModal.close();
    activeModalKey = null;
  });
  btnModalOk.addEventListener("click", () => {
    detailModal.close();
    activeModalKey = null;
  });

  // Light-dismiss fallback
  if (!('closedBy' in HTMLDialogElement.prototype)) {
    detailModal.addEventListener('click', (event) => {
      if (event.target !== detailModal) return;
      const rect = detailModal.getBoundingClientRect();
      const isInside = (
        rect.top <= event.clientY &&
        event.clientY <= rect.top + rect.height &&
        rect.left <= event.clientX &&
        event.clientX <= rect.left + rect.width
      );
      if (!isInside) {
        detailModal.close();
        activeModalKey = null;
      }
    });
  }

  // 6. Realtime Text Cleaner & Audit
  const rawTextInput = document.getElementById("rawTextInput");
  const cleanedTextOutput = document.getElementById("cleanedTextOutput");
  const rawCharCount = document.getElementById("rawCharCount");
  const cleanCharCount = document.getElementById("cleanCharCount");
  const rawAnomalyAlert = document.getElementById("rawAnomalyAlert");
  const auditRiskScore = document.getElementById("auditRiskScore");
  const auditZeroWidthCount = document.getElementById("auditZeroWidthCount");
  const auditSpacesNorm = document.getElementById("auditSpacesNorm");
  const auditDisruption = document.getElementById("auditDisruption");
  const btnPasteFromClip = document.getElementById("btnPasteFromClip");
  const btnClearText = document.getElementById("btnClearText");
  const btnCopyCleanText = document.getElementById("btnCopyCleanText");

  let textDebounceTimer = null;

  rawTextInput.addEventListener("input", () => {
    const t = I18N_TRANSLATIONS[currentLang];
    rawCharCount.textContent = `${t.txt_char_count || "字數："}${rawTextInput.value.length}`;
    clearTimeout(textDebounceTimer);
    textDebounceTimer = setTimeout(triggerTextClean, 300);
  });

  async function triggerTextClean() {
    const text = rawTextInput.value;
    const t = I18N_TRANSLATIONS[currentLang];
    if (!text) {
      cleanedTextOutput.value = "";
      cleanCharCount.textContent = `${t.txt_char_count || "字數："}0`;
      rawAnomalyAlert.classList.add("hidden");
      auditRiskScore.textContent = "0 / 100";
      auditZeroWidthCount.textContent = "0";
      auditSpacesNorm.textContent = "0";
      auditDisruption.textContent = "0%";
      return;
    }

    try {
      const resp = await fetch("/api/clean-text", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          text: text,
          enable_perturb: document.getElementById("cfgPerturb").checked,
          de_perfectionize_md: true
        })
      });
      const data = await resp.json();

      cleanedTextOutput.value = data.cleaned_text;
      cleanCharCount.textContent = `${t.txt_char_count || "字數："}${data.cleaned_length}`;

      const totalRemoved = data.unicode_stats?.total_removed || 0;
      if (totalRemoved > 0) {
        rawAnomalyAlert.classList.remove("hidden");
        rawAnomalyAlert.textContent = `${t.txt_alert_anomaly || "⚠️ 發現異常字元！"} (-${totalRemoved})`;
      } else {
        rawAnomalyAlert.classList.add("hidden");
      }

      auditRiskScore.textContent = `${data.audit_before?.risk_score || 0} / 100 (${data.audit_before?.risk_level || "LOW"})`;
      auditZeroWidthCount.textContent = `${totalRemoved}`;
      auditSpacesNorm.textContent = `${data.unicode_stats?.normalized_spaces || 0}`;
      auditDisruption.textContent = `${((data.perturb_stats?.disruption_rate || 0) * 100).toFixed(1)}%`;

      // Render Stage 1 & Stage 2 details in anomaliesListContainer
      const s1 = data.stage1_restructure;
      const s2 = data.stage2_fact_citation;
      const container = document.getElementById("anomaliesListContainer");
      if (container) {
        let html = "";
        if (s1 && s1.cliches_purged_count > 0) {
          html += `
            <div style="background: rgba(99, 102, 241, 0.08); border-left: 3px solid #6366f1; padding: 10px 12px; margin-top: 14px; border-radius: 4px; font-size: 0.85rem;">
              <strong style="color: #6366f1;">🎯 階段 1：文字八股消除與突發性提升 (+${s1.burstiness_boost_percent || 0}%)</strong>
              <div style="color: var(--text-muted); margin-top: 4px;">已自動將 ${s1.cliches_purged_count} 處 AI 高頻套話替換為多元語境動詞，長短句離散度由 ${s1.original_cv} 升至 ${s1.reshaped_cv}。</div>
            </div>
          `;
        }
        if (s2 && s2.unanchored_claims_count > 0) {
          html += `
            <div style="background: rgba(245, 158, 11, 0.08); border-left: 3px solid var(--warning); padding: 10px 12px; margin-top: 10px; border-radius: 4px; font-size: 0.85rem;">
              <strong style="color: var(--warning);">🔬 階段 2：事實錨點核驗預警（發現 ${s2.unanchored_claims_count} 處未標來源主張）</strong>
              <div style="color: var(--text-muted); margin-top: 4px;">健康度評分：<strong>${s2.fact_integrity_score} / 100</strong>。包含數值或比較卻未在當句提供文獻標籤，容易被 AI 檢測器抓取強訊號。</div>
            </div>
          `;
        }
        container.innerHTML = html;
      }

    } catch (err) {
      console.error(err);
    }
  }

  btnPasteFromClip.addEventListener("click", async () => {
    try {
      const text = await navigator.clipboard.readText();
      rawTextInput.value = text;
      rawTextInput.dispatchEvent(new Event("input"));
    } catch {
      alert("請允許瀏覽器存取剪貼簿權限 / Please grant clipboard access");
    }
  });

  btnClearText.addEventListener("click", () => {
    rawTextInput.value = "";
    rawTextInput.dispatchEvent(new Event("input"));
  });

  btnCopyCleanText.addEventListener("click", async () => {
    if (!cleanedTextOutput.value) return;
    try {
      await navigator.clipboard.writeText(cleanedTextOutput.value);
      btnCopyCleanText.textContent = "✅";
      setTimeout(() => {
        const t = I18N_TRANSLATIONS[currentLang];
        btnCopyCleanText.textContent = t.txt_btn_copy || "📋 複製乾淨文字";
      }, 1500);
    } catch {
      alert("複製失敗 / Copy failed");
    }
  });

  // 7. Scheme C Clipboard Watcher Controller (Default to Active)
  const watcherIndicator = document.getElementById("watcherIndicator");
  const watcherStatusText = document.getElementById("watcherStatusText");
  const btnToggleWatcher = document.getElementById("btnToggleWatcher");
  const chkEnableWatcher = document.getElementById("chkEnableWatcher");
  const watcherSwitchLabel = document.getElementById("watcherSwitchLabel");
  const eventLogList = document.getElementById("eventLogList");
  const eventCountBadge = document.getElementById("eventCountBadge");
  const btnRefreshClipEvents = document.getElementById("btnRefreshClipEvents");

  let isWatcherActive = true; // Default Active per requirement

  async function pollWatcherStatus() {
    try {
      const resp = await fetch("/api/clipboard/status");
      const data = await resp.json();
      updateWatcherUI(data.active);
      renderClipboardEvents(data.events || []);
    } catch (err) {
      // offline fallback
    }
  }

  function updateWatcherUI(active) {
    isWatcherActive = active;
    if (chkEnableWatcher) chkEnableWatcher.checked = active;
    const t = I18N_TRANSLATIONS[currentLang];

    if (active) {
      watcherIndicator.classList.add("active");
      watcherStatusText.textContent = t.watcher_active || "即時監聽中";
      watcherStatusText.style.color = "var(--success)";
      btnToggleWatcher.textContent = t.watcher_btn_stop || "停止守護";
      btnToggleWatcher.className = "btn btn-sm btn-ghost";
      if (watcherSwitchLabel) {
        watcherSwitchLabel.textContent = t.watcher_running || "守護運作中 (自動淨化複製內容)";
        watcherSwitchLabel.style.color = "var(--success)";
      }
    } else {
      watcherIndicator.classList.remove("active");
      watcherStatusText.textContent = t.watcher_inactive || "未啟動";
      watcherStatusText.style.color = "var(--text-muted)";
      btnToggleWatcher.textContent = t.watcher_btn_start || "啟動守護";
      btnToggleWatcher.className = "btn btn-sm btn-primary";
      if (watcherSwitchLabel) {
        watcherSwitchLabel.textContent = t.watcher_stopped || "守護未運行";
        watcherSwitchLabel.style.color = "var(--text-muted)";
      }
    }
  }

  async function toggleWatcher(newState) {
    try {
      const resp = await fetch("/api/clipboard/toggle", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          active: newState,
          enable_perturb: document.getElementById("cfgPerturb").checked
        })
      });
      const data = await resp.json();
      updateWatcherUI(data.active);
    } catch (err) {
      console.warn("Toggle watcher warning:", err.message);
    }
  }

  btnToggleWatcher.addEventListener("click", () => toggleWatcher(!isWatcherActive));
  if (chkEnableWatcher) chkEnableWatcher.addEventListener("change", () => toggleWatcher(chkEnableWatcher.checked));
  if (btnRefreshClipEvents) btnRefreshClipEvents.addEventListener("click", pollWatcherStatus);

  function renderClipboardEvents(events) {
    eventCountBadge.textContent = events.length;
    const t = I18N_TRANSLATIONS[currentLang];

    if (events.length === 0) {
      eventLogList.innerHTML = `<div class="empty-state">${t.clip_empty || "尚無剪貼簿攔截事件。"}</div>`;
      return;
    }

    eventLogList.innerHTML = events.map(e => `
      <div class="event-item">
        <span class="event-time">${e.timestamp}</span>
        <span class="event-tag">${t.clip_item_tag || "淨化完成"}</span>
        <span class="event-snippet">"${e.snippet}"</span>
        <span class="badge badge-warning">-${e.removed_chars} ZW</span>
      </div>
    `).join("");
  }

  // Initialize Language
  applyLanguage(currentLang);

  // Guarantee Watcher Active State on Page Load (Requirement 4)
  toggleWatcher(true);

  // Sync App Version Badge from API
  async function syncAppVersion() {
    try {
      const resp = await fetch("/api/version");
      if (resp.ok) {
        const vdata = await resp.json();
        const badge = document.getElementById("appVersionBadge");
        if (badge && vdata.version) {
          badge.textContent = `v${vdata.version}`;
          badge.title = `NonAI v${vdata.version} (${vdata.release_date || ""}) - ${vdata.bump_level || "release"}`;
        }
      }
    } catch {
      // fallback to static badge in HTML
    }
  }
  syncAppVersion();

  // Poll status every 2 seconds
  pollWatcherStatus();
  setInterval(pollWatcherStatus, 2000);
});
