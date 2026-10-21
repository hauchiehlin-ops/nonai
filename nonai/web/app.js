// NonAI Frontend Controller

document.addEventListener("DOMContentLoaded", () => {
  // 1. Navigation Tabs
  const tabBtns = document.querySelectorAll(".tab-btn");
  const tabPanels = document.querySelectorAll(".tab-panel");

  tabBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      tabBtns.forEach(b => b.classList.remove("active"));
      tabPanels.forEach(p => p.classList.remove("active"));
      btn.classList.add("active");
      const targetId = btn.getAttribute("data-tab");
      document.getElementById(targetId)?.classList.add("active");
    });
  });

  // 2. Drag & Drop File Upload
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

    dropZone.querySelector("h3").textContent = "正在進行底層淨化與指紋重構...";

    try {
      const resp = await fetch("/api/clean-file", {
        method: "POST",
        body: formData
      });
      if (!resp.ok) throw new Error("處理失敗");
      const data = await resp.json();

      renderFileResult(data);
    } catch (err) {
      alert("檔案處理時發生錯誤：" + err.message);
    } finally {
      dropZone.querySelector("h3").textContent = "拖曳檔案至此，或點擊選擇檔案";
      fileInput.value = "";
    }
  }

  function renderFileResult(data) {
    fileResultCard.classList.remove("hidden");
    resFileName.textContent = `✅ 已完成淨化：${data.filename}`;
    btnDownload.href = `/api/download/${data.file_id}`;
    btnDownload.setAttribute("download", data.filename);

    fileStatsGrid.innerHTML = "";
    const s = data.stats;

    if (data.file_type === "docx") {
      fileStatsGrid.innerHTML = `
        <div class="stat-box">
          <span class="title">注入 RSID 歷程會話</span>
          <span class="val">${s.rsid_injected} 組</span>
        </div>
        <div class="stat-box">
          <span class="title">自然碎形化 Runs 切分</span>
          <span class="val">${s.runs_split} 處</span>
        </div>
        <div class="stat-box">
          <span class="title">清除網頁幽靈樣式/底色</span>
          <span class="val">${s.ghost_styles_removed} 處</span>
        </div>
        <div class="stat-box">
          <span class="title">移除零寬度 Unicode</span>
          <span class="val">${s.unicode_removed} 個</span>
        </div>
        <div class="stat-box">
          <span class="title">偽裝打字編輯耗時</span>
          <span class="val">${s.human_editing_minutes} 分鐘</span>
        </div>
        <div class="stat-box">
          <span class="title">偽裝軟體應用程式</span>
          <span class="val" style="font-size: 0.95rem;">${s.application_spoofed}</span>
        </div>
      `;
    } else if (data.file_type === "pdf") {
      fileStatsGrid.innerHTML = `
        <div class="stat-box">
          <span class="title">原 Producer</span>
          <span class="val" style="font-size: 0.95rem; color: var(--danger);">${s.original_producer}</span>
        </div>
        <div class="stat-box">
          <span class="title">偽裝 Producer</span>
          <span class="val" style="font-size: 0.95rem; color: var(--success);">${s.spoofed_producer}</span>
        </div>
        <div class="stat-box">
          <span class="title">偽裝 Creator</span>
          <span class="val" style="font-size: 0.95rem;">${s.spoofed_creator}</span>
        </div>
        <div class="stat-box">
          <span class="title">XMP 元資料流清洗</span>
          <span class="val">${s.xmp_cleaned ? "已徹底剔除" : "乾淨"}</span>
        </div>
      `;
    } else {
      fileStatsGrid.innerHTML = `
        <div class="stat-box">
          <span class="title">移除零寬不可見字元</span>
          <span class="val">${s.unicode_removed || 0} 個</span>
        </div>
        <div class="stat-box">
          <span class="title">表格/清單去完美化</span>
          <span class="val">${(s.tables_de_perfectionized || 0) + (s.lists_varied || 0)} 處</span>
        </div>
      `;
    }

    fileResultCard.scrollIntoView({ behavior: "smooth" });
  }

  // 3. Realtime Text Cleaner & Audit
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
    rawCharCount.textContent = `字數：${rawTextInput.value.length}`;
    clearTimeout(textDebounceTimer);
    textDebounceTimer = setTimeout(triggerTextClean, 300);
  });

  async function triggerTextClean() {
    const text = rawTextInput.value;
    if (!text) {
      cleanedTextOutput.value = "";
      cleanCharCount.textContent = "字數：0";
      rawAnomalyAlert.classList.add("hidden");
      auditRiskScore.textContent = "0 / 100";
      auditZeroWidthCount.textContent = "0 個";
      auditSpacesNorm.textContent = "0 處";
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
      cleanCharCount.textContent = `字數：${data.cleaned_length}`;

      // Update Audit UI
      const totalRemoved = data.unicode_stats?.total_removed || 0;
      if (totalRemoved > 0) {
        rawAnomalyAlert.classList.remove("hidden");
        rawAnomalyAlert.textContent = `⚠️ 發現 ${totalRemoved} 個隱藏零寬字元！`;
      } else {
        rawAnomalyAlert.classList.add("hidden");
      }

      auditRiskScore.textContent = `${data.audit_before?.risk_score || 0} / 100 (${data.audit_before?.risk_level || "LOW"})`;
      auditZeroWidthCount.textContent = `${totalRemoved} 個`;
      auditSpacesNorm.textContent = `${data.unicode_stats?.normalized_spaces || 0} 處`;
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
      alert("請允許瀏覽器存取剪貼簿權限");
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
      btnCopyCleanText.textContent = "✅ 已複製！";
      setTimeout(() => btnCopyCleanText.textContent = "📋 複製乾淨文字", 1500);
    } catch {
      alert("複製失敗");
    }
  });

  // 4. Scheme C Clipboard Watcher Controller
  const watcherIndicator = document.getElementById("watcherIndicator");
  const watcherStatusText = document.getElementById("watcherStatusText");
  const btnToggleWatcher = document.getElementById("btnToggleWatcher");
  const chkEnableWatcher = document.getElementById("chkEnableWatcher");
  const watcherSwitchLabel = document.getElementById("watcherSwitchLabel");
  const eventLogList = document.getElementById("eventLogList");
  const eventCountBadge = document.getElementById("eventCountBadge");
  const btnRefreshClipEvents = document.getElementById("btnRefreshClipEvents");

  let isWatcherActive = false;

  async function pollWatcherStatus() {
    try {
      const resp = await fetch("/api/clipboard/status");
      const data = await resp.json();
      updateWatcherUI(data.active);
      renderClipboardEvents(data.events || []);
    } catch (err) {
      // offline or server restarted
    }
  }

  function updateWatcherUI(active) {
    isWatcherActive = active;
    chkEnableWatcher.checked = active;

    if (active) {
      watcherIndicator.classList.add("active");
      watcherStatusText.textContent = "即時監聽中";
      watcherStatusText.style.color = "var(--success)";
      btnToggleWatcher.textContent = "停止守護";
      btnToggleWatcher.className = "btn btn-sm btn-ghost";
      watcherSwitchLabel.textContent = "守護運作中 (自動淨化複製內容)";
      watcherSwitchLabel.style.color = "var(--success)";
    } else {
      watcherIndicator.classList.remove("active");
      watcherStatusText.textContent = "未啟動";
      watcherStatusText.style.color = "var(--text-muted)";
      btnToggleWatcher.textContent = "啟動守護";
      btnToggleWatcher.className = "btn btn-sm btn-primary";
      watcherSwitchLabel.textContent = "守護未運行";
      watcherSwitchLabel.style.color = "var(--text-muted)";
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
      alert("切換剪貼簿守護狀態失敗：" + err.message);
    }
  }

  btnToggleWatcher.addEventListener("click", () => toggleWatcher(!isWatcherActive));
  chkEnableWatcher.addEventListener("change", () => toggleWatcher(chkEnableWatcher.checked));
  btnRefreshClipEvents.addEventListener("click", pollWatcherStatus);

  function renderClipboardEvents(events) {
    eventCountBadge.textContent = events.length;
    if (events.length === 0) {
      eventLogList.innerHTML = '<div class="empty-state">尚無剪貼簿攔截事件。啟動守護後，複製任何文字即可查看即時淨化過程。</div>';
      return;
    }

    eventLogList.innerHTML = events.map(e => `
      <div class="event-item">
        <span class="event-time">${e.timestamp}</span>
        <span class="event-tag">淨化完成</span>
        <span class="event-snippet">"${e.snippet}"</span>
        <span class="badge badge-warning">-${e.removed_chars} 零寬</span>
      </div>
    `).join("");
  }

  // Poll status every 2 seconds
  pollWatcherStatus();
  setInterval(pollWatcherStatus, 2000);
});
