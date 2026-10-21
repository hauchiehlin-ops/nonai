# -*- coding: utf-8 -*-
"""
Full Multilingual Dictionary Generator for NonAI
Ensures 100% key symmetry across all 7 languages.
"""

import json
from pathlib import Path

# Load existing base
from scripts.build_full_i18n import DATA

# 3. zh-CN (简体中文)
DATA["zh-CN"] = {
    "app_title": "NonAI - AI 数字指纹与隐藏痕迹消除系统",
    "brand_sub": "AI 数字指纹、水印与底层元数据消除引擎",
    "watcher_label": "剪贴板守护 (Scheme C)",
    "watcher_active": "实时监听中",
    "watcher_inactive": "未启动",
    "watcher_btn_start": "启动守护",
    "watcher_btn_stop": "停止守护",
    "watcher_running": "守护运行中 (自动净化复制内容)",
    "watcher_stopped": "守护未运行",
    "tab_files": "📁 文件净化工作台 (.docx, .pdf, .md, .txt)",
    "tab_text": "✍️ 实时文本与 Hex 鉴识",
    "tab_clipboard": "📋 剪贴板活动日志",
    "tab_manual": "📖 操作与鉴识手册",
    "drop_title": "拖拽文件至此，或点击选择文件",
    "drop_subtitle": "支持格式：Word (.docx)、PDF (.pdf)、Markdown (.md)、纯文本 (.txt)",
    "tag_rsid": "DOCX RSID 仿生注入",
    "tag_pdf": "PDF XMP 元数据伪装",
    "tag_css": "网页 CSS 幽灵底色清除",
    "tag_unicode": "零宽度 Unicode 净化",
    "adv_title": "⚙️ 高级仿生参数设定 (DOCX / PDF / 统计扰动)",
    "lbl_author": "伪装文件作者 (Author)：",
    "hint_author": "写入 Word docProps/core.xml 作者字段",
    "lbl_rsid": "DOCX RSID 历史会话注入数：",
    "hint_rsid": "模拟存盘次数与打字 pause 历程",
    "lbl_pdf": "PDF 生成器伪装目标：",
    "lbl_perturb": "启用统计水印扰动 (打断 n-gram、近义词微调)",
    "btn_timing": "ℹ️ 应用时机",
    "btn_timing_title": "点击查看应用时机说明",
    "timing_popover_heading": "💡 应用时机说明",
    "timing_author_title": "💡 应用时机：伪装文件作者",
    "timing_author_desc": "【何时使用】提交学术论文、商务报告时，避免属性留存为 ChatGPT 或匿名开源库。<br>【建议设置】输入您的真实姓名、机构缩写或设为 Author。<br>【防护效果】覆写 docProps/core.xml 中的 dc:creator 与 cp:lastModifiedBy。",
    "timing_rsid_title": "💡 应用时机：DOCX RSID 历史会话注入",
    "timing_rsid_desc": "【何时使用】需通过文件鉴识审查时。机器生成 Word 通常只有 0~1 组 RSID 致命破绽。<br>【建议设置】短文设为 15~20 组，长篇大作设为 25~40 组。<br>【防护效果】在 settings.xml 与 runs 中注入多节点会话链，模拟真实打字暂停历程。",
    "timing_pdf_title": "💡 应用时机：PDF 生成器伪装目标",
    "timing_pdf_desc": "【何时使用】对外提供 PDF 文件时，防止底层透露 Chromium、Skia 或 python-pdf-lib。<br>【建议选项】Mac 用户推荐选 macOS Quartz，Windows 推荐 Microsoft Word。<br>【防护效果】伪装 Producer 与 Creator 属性并彻底清除 XMP 描述流。",
    "timing_perturb_title": "💡 应用时机：统计水印扰动",
    "timing_perturb_desc": "【何时使用】怀疑内容含有 Google SynthID 绿色词库概率水印，或面临严格 AI 检测时。<br>【建议设置】强烈建议勾选启用。<br>【防护效果】替换 AI 高频套话（如“值得注意的是”），打断 n-gram 链接瓦解 z-score 显著性。",
    "res_clean_prefix": "✅ 已完成净化：",
    "res_desc": "文件结构已完成人手特征伪装与元数据净化",
    "btn_download": "💾 下载已净化文件",
    "stat_rsid_injected": "注入 RSID 历程会话",
    "stat_runs_split": "自然碎形化 Runs 切分",
    "stat_ai_purged": "AI 原生标记抹除",
    "stat_pkg_synthesized": "Word 标准套件结构",
    "stat_semantic_perturbs": "语义与句式去特征化",
    "stat_ghost_removed": "清除网页幽灵样式/底色",
    "stat_unicode_removed": "移除零宽度 Unicode",
    "stat_human_minutes": "伪装打字编辑耗时",
    "stat_app_spoofed": "伪装软件应用程序",
    "stat_inspect_hint": "🔍 点击查看执行详情",
    "unit_sessions": "会话",
    "unit_splits": "处切分",
    "unit_purged": "项已清除",
    "unit_parts": "项标准组件",
    "unit_replacements": "处优化",
    "unit_styles": "处已清除",
    "unit_chars": "字符",
    "unit_minutes": "分钟",
    "txt_raw_header": "原始文本 / 粘贴内容",
    "txt_btn_paste": "📋 粘贴剪贴板",
    "txt_btn_clear": "清空",
    "txt_raw_placeholder": "请在此粘贴来自 ChatGPT、Claude 等 AI 工具生成的文本，系统将自动解析隐形零宽字符与底层标记...",
    "txt_char_count": "字数：",
    "txt_alert_anomaly": "⚠️ 发现异常字符！",
    "txt_clean_header": "净化与去指纹结果",
    "txt_btn_copy": "📋 复制干净文本",
    "txt_clean_placeholder": "净化后文本将显示于此...",
    "txt_status_clean": "纯净无指纹",
    "audit_header": "🔬 文本底层鉴识报告",
    "audit_risk_level": "AI 识别风险等级：",
    "audit_anomalies_found": "检测到异常标记：",
    "audit_hidden_tags": "隐藏样式标签：",
    "audit_watermark_entropy": "水印熵值干扰率：",
    "clip_header": "🛡️ 系统剪贴板实时守护器 (Scheme C)",
    "clip_desc": "常驻于后台，复制 ChatGPT、Claude 回应时，自动在内存中剔除零宽字符并抹平 HTML/CSS 幽灵样式。",
    "clip_stream_title": "实时拦截日志 (Recent Intercepts)",
    "clip_btn_refresh": "🔄 刷新",
    "clip_empty": "暂无剪贴板拦截事件。启动守护后，复制任何文本即可查看实时净化过程。",
    "clip_item_tag": "净化完成",
    "manual_sub": "本手册提供循序渐进的执行步骤、底层运作原理与各功能选项的精准配置建议。",
    "manual_step1_badge": "阶段 1",
    "manual_step1_title": "系统剪贴板实时守护 (Scheme C)",
    "manual_step1_body": "<strong>运作方式：</strong>系统载入时默认处于启用状态（右上角绿灯）。在浏览器中复制任何 AI 文本时，守护程序会在 0.5 秒内自动完成脱水净化，抹去底层的 HTML 幽灵底色与隐形字符。",
    "manual_step1_tip": "💡 <strong>提示：</strong>直接在 Word 或文档中粘贴，内容即为标准纯净文本，不会残留 <code>#F7F7F8</code> 等聊天框 HEX 底色。",
    "manual_step2_badge": "阶段 2",
    "manual_step2_title": "文件拖拽净化与结构仿生 (DOCX / PDF / MD / TXT)",
    "manual_step2_body": "<strong>运作方式：</strong>将文件拖拽至上传区域，系统自动启动 OpenXML 或 PDF 字典重构引擎：",
    "manual_step2_li1": "<strong>DOCX：</strong>逆向注入 20~40 组 RSID 会话池，将长句子依标点符号分形化切分成自然打字节奏的 Runs，合成标准字体表、网页设置与主题，并抹除 Claude/ChatGPT 原生中继标记。",
    "manual_step2_li2": "<strong>PDF：</strong>覆写 Producer 与 Creator 为官方标准（macOS Quartz 或 Word 365），清除逐页 XMP 数据流，并模拟真人时序差。",
    "manual_step2_li3": "<strong>Markdown：</strong>自动打破过度整齐的表格对齐空格，自然化列表缩进，并过滤 AI 对话开头与结尾套话。",
    "manual_step3_badge": "阶段 3",
    "manual_step3_title": "底层鉴识信息检视与安全下载",
    "manual_step3_body": "<strong>运作方式：</strong>处理完成后，点击任一数据卡片即可弹出鉴识详情窗口，检视注入的 16 进制码与切分样例。点击“下载已净化文件”将直接由浏览器原生内存 Blob 对象完成存盘，零延迟且确保文件完整性。",
    "faq_header": "💡 关于 AI 指纹与 NonAI 核心技术问答",
    "faq_q1": "什么是 Word 文档中的 RSID 破绽？",
    "faq_a1": "正常人类撰写 Word 时，每次键盘输入停顿、回溯修改与存盘，都会在 <code>document.xml</code> 中留下数十组不同的修订保存标识符（RSID）。AI 系统直接封装的 DOCX 通常只有 1 组全局 RSID 或完全没有，一眼就会被鉴识程序识别。NonAI 会仿生注入 20~40 组会话并分形化拆分段落。",
    "faq_q2": "为什么复制文本会留下“幽灵底色”？",
    "faq_a2": "从网页对话框反选文本时，剪贴板会夹带 <code>&lt;span style=\"background-color: #f7f7f8\"&gt;</code> 等 HEX 底色与 Inter 特征字体。若直接贴入文档，这些样式会永久存留在底层 XML。NonAI 剪贴板守护可在复制瞬间自动脱水净化。",
    "faq_q3": "如何对抗统计型水印 (如 SynthID) 与神经分类器？",
    "faq_a3": "统计型水印利用伪随机绿色词库（Green List）偏好选词，而分类器专门抓取 AI 刻板套句与固定句长。NonAI 通过打断 n-gram 链接、瓦解僵化排比结构、重构学术套话并注入自然句长突现性（Burstiness），使检测算法的显著性指标失效。",
    "faq_q4": "NonAI 是否保证完全隐私与离线？",
    "faq_a4": "是的。NonAI 采用完全本地离线架构，文件清洗运算与二进制生成全在您的本机电脑或浏览器内部完成，绝不上传云端服务器存储。",
    "footer_text": "NonAI 2.0 • 100% 本地完全离线运算 • 保护您的创作隐私与文本指纹安全",
    "modal_close": "确定关闭",
    "modal_details": {
        "rsid": {
            "title": "注入 RSID 历程会话 - 底层鉴识解析",
            "desc": "<strong>什么是 RSID（修订保存标识符）？</strong><br>RSID 是微软 Word 在用户每次键盘输入停顿、回溯删除或手动保存时自动写入的 4 字节十六进制标签。AI 生成的 Word 文件通常完全缺乏 RSID 或全篇仅有 1 组单一数值，这是鉴识工具首要检查的致命破绽。",
            "sub": "已注入仿生 RSID 会话池（共 {count} 组）"
        },
        "runs_split": {
            "title": "自然分形化 Runs 切分 - 键盘输入节奏模拟",
            "desc": "<strong>为什么需要切分 Runs？</strong><br>AI 工具在导出 DOCX 时，习惯将整段文本塞入单一连续的 <code>&lt;w:r&gt;</code> 节点。人类真实打字时，在标点符号（逗号、句号、顿号）处会产生自然的思考与按键停顿。NonAI 在 <strong>{count}</strong> 处标点断点完成自然分形化切分。",
            "sub": "切分样例样本",
            "sample_desc": "长文本节点已被切分为具备真实人类输入停顿间隔的 Runs 区块。"
        },
        "claude_purged": {
            "title": "AI 原生标记抹除 - 来源指纹彻底铲除",
            "desc": "<strong>已修复致命破绽：文件自首式 AI 标记</strong><br>AI 工具（如 Claude Docs）在导出时会在 <code>docProps/core.xml</code> 的 <code>&lt;dc:description&gt;</code> 字段直接写入 <code>Claude Docs node/...</code>，并植入 <code>customXml/</code>。鉴识工具读取后会直接标注为百分之百确定来源，而非概率推测。",
            "sub": "已执行的鉴识清除项目",
            "items": [
                "<strong>清除标签：</strong>彻底移除 <code>&lt;dc:description&gt;</code>，清空 custom 关键字、分类与主题标签。",
                "<strong>移除自定义包：</strong>全数剔除 <code>customXml/</code> 目录与 <code>docProps/custom.xml</code>。",
                "<strong>全局字符串净化：</strong>全方位扫描 XML 数据流，彻底抹除所有 <code>Claude Docs</code>、<code>Anthropic</code>、<code>ChatGPT</code> 等标记。"
            ]
        },
        "pkg_synthesized": {
            "title": "Word 标准结构合规化 - 套件完整性修复",
            "desc": "<strong>已修复致命破绽：Word 官方套件结构缺漏</strong><br>正版微软 Word 保存文件时，ZIP 封装内必定包含 <code>fontTable.xml</code>（字体表）、<code>webSettings.xml</code>（网页设置）与 <code>theme1.xml</code>（主题色彩）。先前 AI 文件缺少这些文件，导致被判定为“冒用 Word 名称产生”。",
            "sub": "已自动合成的微软标准套件组件",
            "items": [
                "<code>word/fontTable.xml</code>：包含 Calibri、Times New Roman、微软雅黑等标准字体表。",
                "<code>word/webSettings.xml</code>：包含浏览器优化与 PNG 支持标志。",
                "<code>word/theme/theme1.xml</code>：包含微软 Office 官方标准色彩与字体架构。",
                "<code>[Content_Types].xml</code> 与 <code>document.xml.rels</code>：已完成合法架构绑定。"
            ]
        },
        "semantic": {
            "title": "语义与句式去特征化 - Transformer 神经网络护盾",
            "desc": "<strong>已修复破绽：Transformer 分类器特征捕捉</strong><br>类神经检测器（如 OmniTraces INT8）通过文本困惑度分布、句长方差与刻板排比结构来判断。NonAI 将僵化的 AI 套句重构为自然流畅的专业论述，有效打破神经网络特征值。",
            "sub": "神经网络干扰与优化指标",
            "items": [
                "<strong>AI 套话与僵化句式重构：</strong>共 {replacements} 处",
                "<strong>句长突现性与分号节奏优化：</strong>共 {reorganized} 处子句",
                "<strong>N-gram 预测链打碎：</strong>瓦解 SynthID 绿色词库统计显著性"
            ]
        },
        "ghost_styles": {
            "title": "清除网页幽灵样式与底色 - 对话框样式净化",
            "desc": "<strong>对话框粘贴的幽灵底色：</strong><br>从 ChatGPT 或 Claude 网页反选复制时，常会将 <code>#F7F7F8</code> 等灰白色背景色码写入 <code>&lt;w:shd&gt;</code>。NonAI 已彻底剥除孤儿底色样式并还原纯净背景。",
            "sub": "已移除的幽灵样式与字体项目"
        },
        "unicode": {
            "title": "隐形 Unicode 水印净化 - 零宽字符剔除",
            "desc": "<strong>隐形 Unicode 条形码：</strong><br>部分 AI 防伪系统会在文本中随机安插零宽度空格（ZWSP U+200B）、零宽不连字符（ZWNJ U+200C）或字节顺序标记（BOM U+FEFF）。NonAI 彻底剔除隐形标记，同时严格保护中文全角标点。",
            "before_label": "检测到的异常隐形字符",
            "after_label": "净化后状态",
            "clean_status": "100% 纯净标准 NFC 编码"
        },
        "human_time": {
            "title": "伪装打字编辑耗时 - 时间轴仿生构建",
            "desc": "<strong>打字工时破绽：</strong><br>AI 工具导出的文件通常在 <code>docProps/app.xml</code> 留存 <code>&lt;TotalTime&gt;0&lt;/TotalTime&gt;</code>。NonAI 根据文章字数注入合理的人类打字与思考停顿历程。",
            "sub": "仿生时间轴模型",
            "items": [
                "<strong>模拟编辑总耗时：</strong>{minutes} 分钟（以每分钟 32~35 字加上构思停顿推算）",
                "<strong>修订版本号：</strong>第 {revision} 次修订",
                "<strong>创建时间：</strong>{created}",
                "<strong>最后修改时间：</strong>{modified}"
            ]
        },
        "app_spoofed": {
            "title": "伪装软件应用程序 - 元数据重写",
            "desc": "<strong>应用程序元数据：</strong><br>将 python-docx 或开源导出库名称替换为合法的 Microsoft Office Word 属性。",
            "code_title": "合规的 docProps XML 属性"
        },
        "pdf_producer": {
            "title": "PDF 元数据与 XMP 数据流净化",
            "desc": "<strong>PDF 生成器伪装与数据流清理：</strong><br>将开源产制器（如 wkhtmltopdf、Chromium）替换为官方系统虚拟打印机，并彻底清除跨页 XMP 数据流与模拟时间差。",
            "orig_producer": "原始 Producer",
            "spoofed_producer": "伪装后 Producer",
            "spoofed_creator": "伪装后 Creator"
        },
        "markdown": {
            "title": "Markdown 结构去特征化 - 自然排版",
            "desc": "<strong>Markdown 过度完美的对齐特征：</strong><br>AI 输出的 Markdown 表格常有极度精准的空格对齐。NonAI 将其自然化为人类常规的简约排版，并随机调节列表符号。"
        }
    }
}

print("zh-CN added successfully")
