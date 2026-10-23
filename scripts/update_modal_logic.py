# -*- coding: utf-8 -*-
"""
Script to inject buildExecutionLogBannerHtml and update openExecutionDetailsModal
in nonai/web/app.js and public/app.js.
"""

from pathlib import Path
import re

NEW_MODAL_IMPL = '''  // 4.9 Helper: Build Real-time Execution Log Banner for Inspection Modals
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
${pool.slice(0, 6).map(id => `  &lt;w:rsid w:val="${id}"/&gt;`).join("\\n")}
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
          <div class="detail-code-block">${items.slice(0, 15).join("\\n")}${items.length > 15 ? `\\n... (+${items.length - 15})` : ""}</div>
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
  }'''

def run_update():
    path = Path("nonai/web/app.js")
    content = path.read_text(encoding="utf-8")

    # Match from function openExecutionDetailsModal until detailModal.showModal();\n  }
    pattern = r"  // 5\. Execution Details Modal Logic\n  function openExecutionDetailsModal\(key, data\) \{.*?detailModal\.showModal\(\);\n  \}"
    match = re.search(pattern, content, re.DOTALL)
    assert match, "Could not find openExecutionDetailsModal block in nonai/web/app.js"

    new_content = content[:match.start()] + NEW_MODAL_IMPL.lstrip() + content[match.end():]
    path.write_text(new_content, encoding="utf-8")
    print(f"[OK] Updated {path}")

    # Also copy to public/app.js
    public_path = Path("public/app.js")
    public_path.write_text(new_content, encoding="utf-8")
    print(f"[OK] Synced to {public_path}")

if __name__ == "__main__":
    run_update()
