// NonAI Frontend Controller & Multilingual Engine

document.addEventListener("DOMContentLoaded", () => {
  // Global references
  let lastFileResult = null;
  let activeBlobUrl = null;
  let currentLang = localStorage.getItem("nonai_lang") || "zh-TW";
  let activeModalKey = null;
  let activeTimingKey = null;

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
    const detailModal = document.getElementById("detailModal");
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

  async function handleFileUpload(file) {
    const t = I18N_TRANSLATIONS[currentLang];

    // Client-side payload limit check (Vercel Serverless Function limit is 4.5MB)
    const MAX_FILE_SIZE = 4.2 * 1024 * 1024; // 4.2MB safe threshold
    if (file.size > MAX_FILE_SIZE) {
      const fileSizeMB = (file.size / (1024 * 1024)).toFixed(1);
      const isZh = currentLang.startsWith("zh");
      const errMsg = isZh
        ? `⚠️ 上傳失敗：檔案大小為 ${fileSizeMB} MB，超過雲端伺服器 4.5 MB 單次傳輸限制。\n\n【建議解決方式】\n1. 建議將 Word/PDF 內的高解析度圖片壓縮後再重新上傳。\n2. 或在電腦終端機執行 python run_web.py，享有 100% 完全離線、無檔案大小上限處理！`
        : `⚠️ Upload Failed: File size is ${fileSizeMB} MB, exceeding the 4.5 MB serverless limit.\n\n【Recommendations】\n1. Compress high-resolution images in your document before uploading.\n2. Or run 'python run_web.py' locally for 100% offline processing with no file size limits!`;
      alert(errMsg);
      dropZone.querySelector("h2").textContent = t.drop_title;
      fileInput.value = "";
      return;
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
          const isZh = currentLang.startsWith("zh");
          const errMsg = isZh
            ? "⚠️ 伺服器回傳 413 (Payload Too Large)：檔案超過雲端 4.5 MB 限制。請壓縮文件中的大型圖片後再重試，或於本機執行 python run_web.py。"
            : "⚠️ Server returned 413 (Payload Too Large): The file exceeds the 4.5 MB serverless limit. Please compress images or run locally via 'python run_web.py'.";
          throw new Error(errMsg);
        }
        const errData = await resp.json().catch(() => ({}));
        throw new Error(errData.detail || `Upload error (${resp.status})`);
      }
      const data = await resp.json();
      lastFileResult = data;
      renderFileResult(data);
    } catch (err) {
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
      `;
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

  // 5. Execution Details Modal Logic
  const detailModal = document.getElementById("detailModal");
  const modalTitle = document.getElementById("modalTitle");
  const modalIcon = document.getElementById("modalIcon");
  const modalBody = document.getElementById("modalBody");
  const btnCloseModal = document.getElementById("btnCloseModal");
  const btnModalOk = document.getElementById("btnModalOk");

  function openExecutionDetailsModal(key, data) {
    activeModalKey = key;
    const d = data.details || {};
    const s = data.stats || {};
    const t = I18N_TRANSLATIONS[currentLang];
    const m = (t.modal_details && t.modal_details[key]) || {};

    if (btnModalOk) {
      btnModalOk.textContent = t.modal_btn_close || t.modal_close || "Close";
    }

    if (key === "rsid") {
      modalIcon.textContent = "🧬";
      modalTitle.textContent = m.title || t.stat_rsid_injected;
      const pool = d.rsid_pool || [];
      const subTitle = (m.sub || "Injected RSID Session Pool ({count})").replace("{count}", pool.length);
      modalBody.innerHTML = `
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
        <p>${m.desc || ""}</p>
        <p><strong>${t.stat_semantic_perturbs || "Adjustments"}:</strong> ${s.tables_de_perfectionized || 0} table rows, ${s.lists_varied || 0} list items.</p>
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
