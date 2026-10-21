// NonAI Frontend Controller & Multilingual Engine

document.addEventListener("DOMContentLoaded", () => {
  // Global references
  let lastFileResult = null;
  let activeBlobUrl = null;
  let currentLang = localStorage.getItem("nonai_lang") || "zh-TW";

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
      document.getElementById(targetId)?.classList.add("active");
    });
  });

  // Helper: Base64 to Blob for robust client-side downloads
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

  // 3. Drag & Drop File Upload
  const dropZone = document.getElementById("dropZone");
  const fileInput = document.getElementById("fileInput");
  const fileResultCard = document.getElementById("fileResultCard");
  const fileStatsGrid = document.getElementById("fileStatsGrid");
  const resFileName = document.getElementById("resFileName");
  const btnDownload = document.getElementById("btnDownload");

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

  fileInput.addEventListener("change", () => {
    if (fileInput.files.length > 0) {
      handleFileUpload(fileInput.files[0]);
    }
  });

  async function handleFileUpload(file) {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("author", document.getElementById("cfgAuthor").value || "Author");
    formData.append("rsid_count", document.getElementById("cfgRsidCount").value || 25);
    formData.append("pdf_spoof", document.getElementById("cfgPdfSpoof").value || "macOS");
    formData.append("enable_perturb", document.getElementById("cfgPerturb").checked);

    const t = I18N_TRANSLATIONS[currentLang];
    dropZone.querySelector("h2").textContent = t.drop_title || "正在進行底層淨化與指紋重構...";

    try {
      const resp = await fetch("/api/clean-file", {
        method: "POST",
        body: formData
      });
      if (!resp.ok) throw new Error("處理失敗");
      const data = await resp.json();

      lastFileResult = data;
      renderFileResult(data);
    } catch (err) {
      alert("檔案處理時發生錯誤：" + err.message);
    } finally {
      dropZone.querySelector("h2").textContent = t.drop_title;
      fileInput.value = "";
    }
  }

  function renderFileResult(data) {
    const t = I18N_TRANSLATIONS[currentLang];
    fileResultCard.classList.remove("hidden");
    resFileName.textContent = `${t.res_clean_prefix || "✅ 已完成淨化："}${data.filename}`;

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
          <span class="val">${s.rsid_injected}</span>
          <span class="stat-inspect-hint">${t.stat_inspect_hint}</span>
        </div>
        <div class="stat-box clickable" data-inspect="runs_split">
          <span class="title">${t.stat_runs_split}</span>
          <span class="val">${s.runs_split}</span>
          <span class="stat-inspect-hint">${t.stat_inspect_hint}</span>
        </div>
        <div class="stat-box clickable" data-inspect="ghost_styles">
          <span class="title">${t.stat_ghost_removed}</span>
          <span class="val">${s.ghost_styles_removed}</span>
          <span class="stat-inspect-hint">${t.stat_inspect_hint}</span>
        </div>
        <div class="stat-box clickable" data-inspect="unicode">
          <span class="title">${t.stat_unicode_removed}</span>
          <span class="val">${s.unicode_removed}</span>
          <span class="stat-inspect-hint">${t.stat_inspect_hint}</span>
        </div>
        <div class="stat-box clickable" data-inspect="human_time">
          <span class="title">${t.stat_human_minutes}</span>
          <span class="val">${s.human_editing_minutes} min</span>
          <span class="stat-inspect-hint">${t.stat_inspect_hint}</span>
        </div>
        <div class="stat-box clickable" data-inspect="app_spoofed">
          <span class="title">${t.stat_app_spoofed}</span>
          <span class="val" style="font-size: 0.95rem;">${s.application_spoofed}</span>
          <span class="stat-inspect-hint">${t.stat_inspect_hint}</span>
        </div>
      `;
    } else if (data.file_type === "pdf") {
      fileStatsGrid.innerHTML = `
        <div class="stat-box clickable" data-inspect="pdf_producer">
          <span class="title">Original Producer</span>
          <span class="val" style="font-size: 0.95rem; color: var(--danger);">${s.original_producer}</span>
          <span class="stat-inspect-hint">${t.stat_inspect_hint}</span>
        </div>
        <div class="stat-box clickable" data-inspect="pdf_producer">
          <span class="title">Spoofed Producer</span>
          <span class="val" style="font-size: 0.95rem; color: var(--success);">${s.spoofed_producer}</span>
          <span class="stat-inspect-hint">${t.stat_inspect_hint}</span>
        </div>
        <div class="stat-box clickable" data-inspect="pdf_producer">
          <span class="title">Spoofed Creator</span>
          <span class="val" style="font-size: 0.95rem;">${s.spoofed_creator}</span>
          <span class="stat-inspect-hint">${t.stat_inspect_hint}</span>
        </div>
        <div class="stat-box clickable" data-inspect="pdf_producer">
          <span class="title">XMP Metadata Stream</span>
          <span class="val">${s.xmp_cleaned ? "Purged" : "Clean"}</span>
          <span class="stat-inspect-hint">${t.stat_inspect_hint}</span>
        </div>
      `;
    } else {
      fileStatsGrid.innerHTML = `
        <div class="stat-box clickable" data-inspect="unicode">
          <span class="title">${t.stat_unicode_removed}</span>
          <span class="val">${s.unicode_removed || 0}</span>
          <span class="stat-inspect-hint">${t.stat_inspect_hint}</span>
        </div>
        <div class="stat-box clickable" data-inspect="markdown">
          <span class="title">Markdown De-perfection</span>
          <span class="val">${(s.tables_de_perfectionized || 0) + (s.lists_varied || 0)}</span>
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
    const d = data.details || {};
    const s = data.stats || {};
    const t = I18N_TRANSLATIONS[currentLang];

    if (key === "rsid") {
      modalIcon.textContent = "🧬";
      modalTitle.textContent = `${t.stat_rsid_injected} - Forensic Breakdown`;
      const pool = d.rsid_pool || [];
      modalBody.innerHTML = `
        <p><strong>What is RSID (Revision Save ID)?</strong><br>
        RSID is a 4-byte hexadecimal identifier generated by Microsoft Word for each user editing, backspacing, or save action. AI-generated Word documents typically lack RSID or contain only 1 uniform RSID across the whole file.</p>

        <h4>Injected RSID Session Pool (${pool.length} Sessions)</h4>
        <div class="detail-badge-list">
          ${pool.map(id => `<span class="detail-badge">0x${id}</span>`).join("")}
        </div>

        <h4>Underlying OpenXML Injection (word/settings.xml)</h4>
        <div class="detail-code-block">&lt;!-- word/settings.xml --&gt;
&lt;w:rsids&gt;
  &lt;w:rsidRoot w:val="${pool[0] || '003A12B4'}"/&gt;
${pool.slice(0, 6).map(id => `  &lt;w:rsid w:val="${id}"/&gt;`).join("\n")}
  ... (${Math.max(0, pool.length - 6)} additional sessions registered)
&lt;/w:rsids&gt;</div>
      `;
    } else if (key === "runs_split") {
      modalIcon.textContent = "✂️";
      modalTitle.textContent = `${t.stat_runs_split} - Keystroke Simulation`;
      const samples = d.split_samples || [];
      modalBody.innerHTML = `
        <p><strong>Why split runs?</strong><br>
        AI exports write entire paragraphs into a single continuous <code>&lt;w:r&gt;</code> run. Human typing generates multiple fragmented runs because of pauses at commas and periods. NonAI split long runs at <strong>${s.runs_split}</strong> punctuation pause points.</p>

        <h4>Run Splitting Samples (${samples.length} Samples)</h4>
        ${samples.length > 0 ? samples.map((item, idx) => `
          <div class="compare-box" style="margin-bottom: 12px;">
            <span class="label">Before (Machine Single Node):</span>
            <div style="color: var(--text-muted); font-size: 0.85rem; margin-bottom: 6px;">${item.original}</div>
            <span class="label" style="color: var(--primary);">After (Human Fragmented Runs):</span>
            <div style="font-family: var(--font-mono); font-size: 0.82rem; color: var(--success);">${item.chunks}</div>
          </div>
        `).join("") : `<div class="detail-code-block">Long text nodes divided into natural typing pause intervals.</div>`}
      `;
    } else if (key === "ghost_styles") {
      modalIcon.textContent = "🎨";
      modalTitle.textContent = `${t.stat_ghost_removed} - Ghost Styling Purge`;
      const items = d.ghost_style_items || [];
      modalBody.innerHTML = `
        <p><strong>What is Ghost Styling?</strong><br>
        Copying from ChatGPT or Claude interfaces pastes web bubble background colors (e.g. <code>#F7F7F8</code>) into <code>&lt;w:shd&gt;</code> tags. NonAI strips all orphan shading and restores clean document styling.</p>

        <h4>Removed Style Elements (${s.ghost_styles_removed} Items)</h4>
        ${items.length > 0 ? `
          <div class="detail-code-block">${items.slice(0, 15).join("\n")}${items.length > 15 ? `\n...and ${items.length - 15} more` : ""}</div>
        ` : `
          <div class="detail-code-block">No anomalous HEX background colors detected. Document styling is pristine.</div>
        `}
      `;
    } else if (key === "unicode") {
      modalIcon.textContent = "🔍";
      modalTitle.textContent = `${t.stat_unicode_removed} - Zero-Width Character Audit`;
      modalBody.innerHTML = `
        <p><strong>Invisible Unicode Watermarks:</strong><br>
        Certain watermarking systems insert zero-width spaces (ZWSP U+200B), non-joiners (ZWNJ U+200C), or BOM (U+FEFF) as binary barcodes. NonAI purges all hidden marks while strictly preserving standard CJK punctuation.</p>

        <div class="detail-comparison">
          <div class="compare-box before">
            <span class="label">Detected Anomalies</span>
            <div style="font-size: 1.1rem; font-weight: 700;">${s.unicode_removed || 0} characters</div>
          </div>
          <div class="compare-box after">
            <span class="label">Post-Purge Status</span>
            <div style="font-size: 1.1rem; font-weight: 700; color: var(--success);">100% Clean Standard NFC</div>
          </div>
        </div>
      `;
    } else if (key === "human_time") {
      modalIcon.textContent = "⏱️";
      modalTitle.textContent = `${t.stat_human_minutes} - Editing Timeline`;
      const meta = d.metadata_spoof_details || {};
      modalBody.innerHTML = `
        <p><strong>Typing Duration Vulnerability:</strong><br>
        AI exports typically leave <code>&lt;TotalTime&gt;0&lt;/TotalTime&gt;</code> in <code>docProps/app.xml</code>. NonAI injects a calculated human typing duration.</p>

        <h4>Biomimetic Model</h4>
        <ul>
          <li><strong>Estimated Duration:</strong> ${meta.total_time_minutes || s.human_editing_minutes} minutes (based on 35 WPM + thinking intervals)</li>
          <li><strong>Revision Count:</strong> Revision #${meta.revision || 12}</li>
          <li><strong>Spoofed Creation:</strong> <code>${meta.created_time || "Calculated"}</code></li>
          <li><strong>Spoofed Modification:</strong> <code>${meta.modified_time || "Calculated"}</code></li>
        </ul>
      `;
    } else if (key === "app_spoofed") {
      modalIcon.textContent = "💻";
      modalTitle.textContent = `${t.stat_app_spoofed} - Metadata Overwrite`;
      const meta = d.metadata_spoof_details || {};
      modalBody.innerHTML = `
        <p><strong>Application Metadata:</strong><br>
        Replaced library signatures (e.g. python-docx) with genuine Microsoft Office Word properties.</p>

        <div class="detail-code-block">&lt;!-- docProps/app.xml --&gt;
&lt;Application&gt;Microsoft Office Word&lt;/Application&gt;
&lt;AppVersion&gt;16.0000&lt;/AppVersion&gt;
&lt;DocSecurity&gt;0&lt;/DocSecurity&gt;

&lt;!-- docProps/core.xml --&gt;
&lt;dc:creator&gt;${meta.author || "Author"}&lt;/dc:creator&gt;
&lt;cp:lastModifiedBy&gt;${meta.author || "Author"}&lt;/cp:lastModifiedBy&gt;
&lt;cp:revision&gt;${meta.revision || 12}&lt;/cp:revision&gt;</div>
      `;
    } else if (key === "pdf_producer") {
      modalIcon.textContent = "📄";
      modalTitle.textContent = "PDF Metadata & XMP Stream Purge";
      modalBody.innerHTML = `
        <div class="detail-comparison">
          <div class="compare-box before">
            <span class="label">Original Producer</span>
            <div style="font-family: var(--font-mono); font-size: 0.85rem;">${s.original_producer || "None"}</div>
          </div>
          <div class="compare-box after">
            <span class="label">Spoofed Producer</span>
            <div style="font-family: var(--font-mono); font-size: 0.85rem; color: var(--success);">${s.spoofed_producer}</div>
          </div>
        </div>
        <p><strong>Spoofed Creator:</strong> <code>${s.spoofed_creator}</code><br>
        <strong>XMP Stream Status:</strong> ${s.xmp_cleaned ? "✅ Purged from catalog root" : "Clean"}</p>
      `;
    } else if (key === "markdown") {
      modalIcon.textContent = "📝";
      modalTitle.textContent = "Markdown Structure De-perfection";
      modalBody.innerHTML = `
        <p>Transformed robotic aligned table columns into natural human hand-typed formats and varied list indentation.</p>
        <p><strong>Adjustments:</strong> ${s.tables_de_perfectionized || 0} table rows, ${s.lists_varied || 0} list items.</p>
      `;
    }

    detailModal.showModal();
  }

  // Close modal controls
  btnCloseModal.addEventListener("click", () => detailModal.close());
  btnModalOk.addEventListener("click", () => detailModal.close());

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
      if (!isInside) detailModal.close();
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

  // Poll status every 2 seconds
  pollWatcherStatus();
  setInterval(pollWatcherStatus, 2000);
});
