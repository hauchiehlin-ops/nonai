// NonAI Frontend Controller

document.addEventListener("DOMContentLoaded", () => {
  // Global reference to current processed file result
  let lastFileResult = null;
  let activeBlobUrl = null;

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

      lastFileResult = data;
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
          <span class="title">注入 RSID 歷程會話</span>
          <span class="val">${s.rsid_injected} 組</span>
          <span class="stat-inspect-hint">🔍 點擊查看執行詳情</span>
        </div>
        <div class="stat-box clickable" data-inspect="runs_split">
          <span class="title">自然碎形化 Runs 切分</span>
          <span class="val">${s.runs_split} 處</span>
          <span class="stat-inspect-hint">🔍 點擊查看執行詳情</span>
        </div>
        <div class="stat-box clickable" data-inspect="ghost_styles">
          <span class="title">清除網頁幽靈樣式/底色</span>
          <span class="val">${s.ghost_styles_removed} 處</span>
          <span class="stat-inspect-hint">🔍 點擊查看執行詳情</span>
        </div>
        <div class="stat-box clickable" data-inspect="unicode">
          <span class="title">移除零寬度 Unicode</span>
          <span class="val">${s.unicode_removed} 個</span>
          <span class="stat-inspect-hint">🔍 點擊查看執行詳情</span>
        </div>
        <div class="stat-box clickable" data-inspect="human_time">
          <span class="title">偽裝打字編輯耗時</span>
          <span class="val">${s.human_editing_minutes} 分鐘</span>
          <span class="stat-inspect-hint">🔍 點擊查看執行詳情</span>
        </div>
        <div class="stat-box clickable" data-inspect="app_spoofed">
          <span class="title">偽裝軟體應用程式</span>
          <span class="val" style="font-size: 0.95rem;">${s.application_spoofed}</span>
          <span class="stat-inspect-hint">🔍 點擊查看執行詳情</span>
        </div>
      `;
    } else if (data.file_type === "pdf") {
      fileStatsGrid.innerHTML = `
        <div class="stat-box clickable" data-inspect="pdf_producer">
          <span class="title">原 Producer</span>
          <span class="val" style="font-size: 0.95rem; color: var(--danger);">${s.original_producer}</span>
          <span class="stat-inspect-hint">🔍 點擊查看執行詳情</span>
        </div>
        <div class="stat-box clickable" data-inspect="pdf_producer">
          <span class="title">偽裝 Producer</span>
          <span class="val" style="font-size: 0.95rem; color: var(--success);">${s.spoofed_producer}</span>
          <span class="stat-inspect-hint">🔍 點擊查看執行詳情</span>
        </div>
        <div class="stat-box clickable" data-inspect="pdf_producer">
          <span class="title">偽裝 Creator</span>
          <span class="val" style="font-size: 0.95rem;">${s.spoofed_creator}</span>
          <span class="stat-inspect-hint">🔍 點擊查看執行詳情</span>
        </div>
        <div class="stat-box clickable" data-inspect="pdf_producer">
          <span class="title">XMP 元資料流清洗</span>
          <span class="val">${s.xmp_cleaned ? "已徹底剔除" : "乾淨"}</span>
          <span class="stat-inspect-hint">🔍 點擊查看執行詳情</span>
        </div>
      `;
    } else {
      fileStatsGrid.innerHTML = `
        <div class="stat-box clickable" data-inspect="unicode">
          <span class="title">移除零寬不可見字元</span>
          <span class="val">${s.unicode_removed || 0} 個</span>
          <span class="stat-inspect-hint">🔍 點擊查看執行詳情</span>
        </div>
        <div class="stat-box clickable" data-inspect="markdown">
          <span class="title">表格/清單去完美化</span>
          <span class="val">${(s.tables_de_perfectionized || 0) + (s.lists_varied || 0)} 處</span>
          <span class="stat-inspect-hint">🔍 點擊查看執行詳情</span>
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

  // 3. Execution Details Modal Logic
  const detailModal = document.getElementById("detailModal");
  const modalTitle = document.getElementById("modalTitle");
  const modalIcon = document.getElementById("modalIcon");
  const modalBody = document.getElementById("modalBody");
  const btnCloseModal = document.getElementById("btnCloseModal");
  const btnModalOk = document.getElementById("btnModalOk");

  function openExecutionDetailsModal(key, data) {
    const d = data.details || {};
    const s = data.stats || {};

    if (key === "rsid") {
      modalIcon.textContent = "🧬";
      modalTitle.textContent = "DOCX RSID 歷程會話注入詳情";
      const pool = d.rsid_pool || [];
      modalBody.innerHTML = `
        <p><strong>什麼是 RSID？</strong><br>
        RSID（Revision Save ID）是微軟 Word 在人類編輯過程中，每次存檔、修改、暫停時產生的十六進位標籤。AI 工具直接輸出的 DOCX 檔通常只有 0 組或 1 組全域標籤，這是文件鑑識中最致命的機器生成破綻。</p>

        <h4>本次逆向注入的 RSID 會話池（共 ${pool.length} 組）</h4>
        <div class="detail-badge-list">
          ${pool.map(id => `<span class="detail-badge">0x${id}</span>`).join("")}
        </div>

        <h4>底層 XML 注入點</h4>
        <div class="detail-code-block">&lt;!-- word/settings.xml --&gt;
&lt;w:rsids&gt;
  &lt;w:rsidRoot w:val="${pool[0] || '003A12B4'}"/&gt;
${pool.slice(0, 6).map(id => `  &lt;w:rsid w:val="${id}"/&gt;`).join("\n")}
  ... (其餘 ${Math.max(0, pool.length - 6)} 組會話已完整註冊)
&lt;/w:rsids&gt;</div>

        <p class="text-muted"><small>💡 效果：鑑識軟體檢查 <code>word/document.xml</code> 與 <code>word/settings.xml</code> 時，將判定該文件經歷了 ${pool.length} 次真實人手修改與存檔記錄。</small></p>
      `;
    } else if (key === "runs_split") {
      modalIcon.textContent = "✂️";
      modalTitle.textContent = "自然碎形化 Runs 切分詳情";
      const samples = d.split_samples || [];
      modalBody.innerHTML = `
        <p><strong>為什麼要切分 Runs？</strong><br>
        AI 生成的 Word 文件中，整個長段落往往封裝在單一個 <code>&lt;w:r&gt;&lt;w:t&gt;...&lt;/w:t&gt;&lt;/w:r&gt;</code> 中。真實人類打字時會因為打字停頓、逗號思考、鍵盤按鍵節奏產生數個碎形化 Runs。系統已在 <strong>${s.runs_split} 處</strong> 依標點與語意斷點進行自然拆分。</p>

        <h4>切分執行範例對比（取樣 ${samples.length} 處）</h4>
        ${samples.length > 0 ? samples.map((item, idx) => `
          <div class="compare-box" style="margin-bottom: 12px;">
            <span class="label">切分前（機器單一節點）：</span>
            <div style="color: var(--text-muted); font-size: 0.85rem; margin-bottom: 6px;">${item.original}</div>
            <span class="label" style="color: var(--primary);">切分後（人手節奏碎形化）：</span>
            <div style="font-family: var(--font-mono); font-size: 0.82rem; color: var(--success);">${item.chunks}</div>
          </div>
        `).join("") : `<div class="detail-code-block">已針對全篇長文字節點進行逗號/句號暫停切割，共計完成 ${s.runs_split} 個節點碎形化。</div>`}
      `;
    } else if (key === "ghost_styles") {
      modalIcon.textContent = "🎨";
      modalTitle.textContent = "清除網頁幽靈樣式與底色詳情";
      const items = d.ghost_style_items || [];
      modalBody.innerHTML = `
        <p><strong>什麼是網頁幽靈樣式？</strong><br>
        從 ChatGPT 或 Claude 對話框反白複製時，剪貼簿會將網頁的對話泡泡背景色（例如 <code>#F7F7F8</code>）與字體宣告包入 DOCX 底層的 <code>&lt;w:shd&gt;</code> 標籤。即使螢幕肉眼難以察覺，底層 XML 卻留下了明顯的機器拷貝痕跡。</p>

        <h4>已掃描並拔除的幽靈標籤（共 ${s.ghost_styles_removed} 處）</h4>
        ${items.length > 0 ? `
          <div class="detail-code-block">${items.slice(0, 15).join("\n")}${items.length > 15 ? `\n...另有 ${items.length - 15} 個樣式已完全清除` : ""}</div>
        ` : `
          <div class="detail-code-block">未發現異常的 HEX 背景色或特徵字體，文件底層樣式維持純淨。</div>
        `}
      `;
    } else if (key === "unicode") {
      modalIcon.textContent = "🔍";
      modalTitle.textContent = "隱形 Unicode 與底層浮水印檢測詳情";
      modalBody.innerHTML = `
        <p><strong>隱形 Unicode 字元特徵：</strong><br>
        部分防偽系統會在文字中安插零寬空格（ZWSP <code>U+200B</code>）、零寬不連字（ZWNJ <code>U+200C</code>）、BOM（<code>U+FEFF</code>）等二進位編碼浮水印。這些字元在文字編輯器完全隱形，但檢測程式可直接提取出特徵序列。</p>

        <div class="detail-comparison">
          <div class="compare-box before">
            <span class="label">掃描結果</span>
            <div style="font-size: 1.1rem; font-weight: 700;">${s.unicode_removed || 0} 個隱形標記</div>
          </div>
          <div class="compare-box after">
            <span class="label">處理後狀態</span>
            <div style="font-size: 1.1rem; font-weight: 700; color: var(--success);">100% 純淨標準 NFC</div>
          </div>
        </div>

        <p class="text-muted"><small>💡 系統全面執行安全標準化，已清除所有隱形空白與控制碼，並完整保護中文全形標點符號不被破壞。</small></p>
      `;
    } else if (key === "human_time") {
      modalIcon.textContent = "⏱️";
      modalTitle.textContent = "偽裝打字耗時與編輯歷史詳情";
      const meta = d.metadata_spoof_details || {};
      modalBody.innerHTML = `
        <p><strong>編輯耗時破綻：</strong><br>
        AI 工具一次性輸出的 Word 文件，其 <code>docProps/app.xml</code> 中的 <code>&lt;TotalTime&gt;</code> 通常為 <code>0</code>，且建立時間與修改時間完全相同。這是一眼被鑑識軟體判定為程式生成的常見破綻。</p>

        <h4>仿生工時推算模型</h4>
        <ul>
          <li><strong>推算編輯耗時：</strong> ${meta.total_time_minutes || s.human_editing_minutes} 分鐘（依字數推算 35 WPM + 思考與回讀時間）</li>
          <li><strong>注入修訂次數（Revision）：</strong> 第 ${meta.revision || 12} 次存檔</li>
          <li><strong>偽裝建立時間：</strong> <code>${meta.created_time || "已自動計算"}</code></li>
          <li><strong>偽裝最後修改時間：</strong> <code>${meta.modified_time || "已自動計算"}</code></li>
        </ul>
      `;
    } else if (key === "app_spoofed") {
      modalIcon.textContent = "💻";
      modalTitle.textContent = "偽裝軟體應用程式與元資料詳情";
      const meta = d.metadata_spoof_details || {};
      modalBody.innerHTML = `
        <p><strong>軟體元資料覆寫：</strong><br>
        許多 Python 或 Node 開源庫在打包 DOCX 時，會在 <code>docProps/app.xml</code> 留下 <code>python-docx</code> 或 <code>Apache POI</code> 的指紋。系統已徹底覆寫為微軟官方 Office Word 特徵。</p>

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
      modalTitle.textContent = "PDF 元資料與 XMP 流清洗詳情";
      modalBody.innerHTML = `
        <p><strong>PDF 生成器特徵：</strong><br>
        AI 平台匯出 PDF 時常使用 <code>pdf-lib</code>、<code>Chromium</code>、<code>Skia/PDF</code> 等 Producer 屬性，且在 XMP 內部存留大量函式庫描述流。</p>

        <div class="detail-comparison">
          <div class="compare-box before">
            <span class="label">修改前 Producer</span>
            <div style="font-family: var(--font-mono); font-size: 0.85rem;">${s.original_producer || "None"}</div>
          </div>
          <div class="compare-box after">
            <span class="label">偽裝後 Producer</span>
            <div style="font-family: var(--font-mono); font-size: 0.85rem; color: var(--success);">${s.spoofed_producer}</div>
          </div>
        </div>

        <p><strong>Creator 覆寫為：</strong> <code>${s.spoofed_creator}</code><br>
        <strong>XMP 資料流：</strong> ${s.xmp_cleaned ? "✅ 已徹底自 PDF Root 字典中移除" : "未發現殘留"}</p>
      `;
    } else if (key === "markdown") {
      modalIcon.textContent = "📝";
      modalTitle.textContent = "Markdown 結構去完美化詳情";
      modalBody.innerHTML = `
        <p><strong>去完美化處理：</strong><br>
        AI 輸出的 Markdown 表格常具備機器人等級的對齊空格（例如欄寬完全相等且邊界垂直對齊）。系統已套用啟發式轉換，轉為手打常見的緊湊與非對稱對齊，並自然化多層級清單縮排。</p>
        <p><strong>已處理項目：</strong> 表格對齊 ${s.tables_de_perfectionized || 0} 行，清單樣式調整 ${s.lists_varied || 0} 處。</p>
      `;
    }

    detailModal.showModal();
  }

  // Close modal controls
  btnCloseModal.addEventListener("click", () => detailModal.close());
  btnModalOk.addEventListener("click", () => detailModal.close());

  // Modern Web Guidance: Light-dismiss fallback for browsers without native `closedby`
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

  // 4. Realtime Text Cleaner & Audit
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

  // 5. Scheme C Clipboard Watcher Controller
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
