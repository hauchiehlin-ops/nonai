"""
NonAI Command Line Interface
Usage:
    nonai clean <file_path> [--out <output_path>] [--author <name>]
    nonai watch [--interval <sec>] [--perturb]
    nonai inspect <file_path>
"""

import argparse
import os
import sys
import time
from nonai.core.unicode_cleaner import clean_unicode, inspect_unicode_anomalies
from nonai.core.docx_sanitizer import sanitize_docx
from nonai.core.pdf_sanitizer import sanitize_pdf
from nonai.core.markdown_cleaner import clean_markdown
from nonai.core.semantic_perturb import perturb_text
from nonai.core.detector_audit import audit_text_fingerprints
from nonai.clipboard.watcher import ClipboardWatcher

def handle_clean(args):
    filepath = args.file
    if not os.path.exists(filepath):
        print(f"❌ 錯誤: 找不到檔案 '{filepath}'")
        sys.exit(1)

    ext = os.path.splitext(filepath)[1].lower()
    out_path = args.out

    print(f"🔍 正在清洗: {filepath} ({ext}) ...")

    if ext == ".docx":
        with open(filepath, "rb") as f:
            in_bytes = f.read()
        res = sanitize_docx(in_bytes, author_name=args.author, rsid_session_count=args.rsid_count)
        if not out_path:
            out_path = os.path.splitext(filepath)[0] + "_clean.docx"
        with open(out_path, "wb") as f:
            f.write(res.cleaned_bytes)

        print("✅ DOCX 清洗完成！")
        print(f"   • 注入 RSID 會話數: {res.final_rsid_count} (原為 {res.original_rsid_count})")
        print(f"   • 碎片化 Runs 切分: {res.runs_split} 處")
        print(f"   • 清除幽靈樣式/底色: {res.ghost_styles_removed} 處")
        print(f"   • 移除零寬字元: {res.unicode_chars_removed} 個")
        print(f"   • 偽裝編輯時間: {res.estimated_human_minutes} 分鐘 (Microsoft Office Word)")
        print(f"   💾 已儲存至: {out_path}")

    elif ext == ".pdf":
        with open(filepath, "rb") as f:
            in_bytes = f.read()
        res = sanitize_pdf(in_bytes, author_name=args.author, spoof_target=args.spoof)
        if not out_path:
            out_path = os.path.splitext(filepath)[0] + "_clean.pdf"
        with open(out_path, "wb") as f:
            f.write(res.cleaned_bytes)

        print("✅ PDF 清洗完成！")
        print(f"   • 原 Producer: {res.original_producer}")
        print(f"   • 偽裝 Producer: {res.spoofed_producer}")
        print(f"   • 偽裝 Creator: {res.spoofed_creator}")
        print(f"   • XMP 元資料流清洗: {'已剔除' if res.xmp_cleaned else '無殘留'}")
        print(f"   💾 已儲存至: {out_path}")

    elif ext in (".md", ".markdown"):
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
        res = clean_markdown(text)
        if args.perturb:
            p_res = perturb_text(res.cleaned_text, intensity=0.4)
            final_text = p_res.perturbed_text
        else:
            final_text = res.cleaned_text

        if not out_path:
            out_path = os.path.splitext(filepath)[0] + "_clean.md"
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(final_text)

        print("✅ Markdown 清洗完成！")
        print(f"   • 移除零寬/不可見字元: {res.unicode_chars_removed} 個")
        print(f"   • 表格去完美化調整: {res.tables_de_perfectionized} 行")
        print(f"   • 清單樣式微調: {res.lists_varied} 處")
        print(f"   💾 已儲存至: {out_path}")

    else:
        # Treat as TXT
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
        u_res = clean_unicode(text)
        final_text = u_res.cleaned_text
        if args.perturb:
            p_res = perturb_text(final_text, intensity=0.4)
            final_text = p_res.perturbed_text

        if not out_path:
            out_path = os.path.splitext(filepath)[0] + "_clean.txt"
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(final_text)

        print("✅ 純文字清洗完成！")
        print(f"   • 移除零寬字元: {u_res.total_removed} 個")
        print(f"   • 空格正規化: {u_res.normalized_spaces} 處")
        print(f"   💾 已儲存至: {out_path}")


def handle_watch(args):
    print("🛡️  NonAI 剪貼簿守護程式已啟動 (Scheme C)")
    print("📋 正在監聽系統剪貼簿 (按 Ctrl+C 停止)...")
    if args.perturb:
        print("⚡ 已啟用輕量語意擾動 (破壞統計型浮水印)")

    def log_event(event):
        print(f"[{event.timestamp}] ⚡ 攔截並淨化剪貼簿內容！")
        print(f"   • 剔除隱形字元: {event.invisible_chars_removed} 個")
        print(f"   • 正規化空格: {event.spaces_normalized} 處")
        print(f"   • 摘要: \"{event.snippet}\"")
        print("   • 狀態: 已清除 HTML/CSS 幽靈樣式與零寬字元")

    watcher = ClipboardWatcher(
        poll_interval=args.interval,
        enable_perturbation=args.perturb,
        on_event_callback=log_event
    )
    watcher.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        watcher.stop()
        print("\n👋 剪貼簿守護程式已停止。")


def handle_inspect(args):
    filepath = args.file
    if not os.path.exists(filepath):
        print(f"❌ 錯誤: 找不到檔案 '{filepath}'")
        sys.exit(1)

    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()

    anomalies = inspect_unicode_anomalies(text)
    audit = audit_text_fingerprints(text)

    print(f"📊 檔案鑑識分析: {filepath}")
    print(f"   • 整體 AI 指紋風險等級: {audit.risk_level} (評分: {audit.overall_risk_score}/100)")
    print(f"   • 發現隱形 Unicode 字元數: {len(anomalies)}")
    for a in anomalies[:5]:
        print(f"     - 位置 {a['index']}: {a['char_hex']} ({a['name']})")
    if len(anomalies) > 5:
        print(f"     ... 另有 {len(anomalies) - 5} 個異常字元")

    print("\n💡 建議處理方案:")
    for rec in audit.recommendations:
        print(f"   - {rec}")


def main():
    parser = argparse.ArgumentParser(description="NonAI: 消除 AI 指紋與隱藏痕跡的工具")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Clean command
    p_clean = subparsers.add_parser("clean", help="清洗指定檔案 (.docx, .pdf, .md, .txt)")
    p_clean.add_argument("file", help="檔案路徑")
    p_clean.add_argument("--out", "-o", help="輸出路徑 (預設為 原檔名_clean)")
    p_clean.add_argument("--author", default="Author", help="偽裝作者名稱")
    p_clean.add_argument("--rsid-count", type=int, default=25, help="DOCX RSID 會話數")
    p_clean.add_argument("--spoof", choices=["macOS", "Word"], default="macOS", help="PDF 偽裝目標")
    p_clean.add_argument("--perturb", action="store_true", help="啟用統計浮水印擾動")
    p_clean.set_defaults(func=handle_clean)

    # Watch command (Scheme C)
    p_watch = subparsers.add_parser("watch", help="啟動系統剪貼簿守護背景程式 (Scheme C)")
    p_watch.add_argument("--interval", type=float, default=0.5, help="輪詢間隔 (秒)")
    p_watch.add_argument("--perturb", action="store_true", help="自動進行輕量語意擾動")
    p_watch.set_defaults(func=handle_watch)

    # Inspect command
    p_inspect = subparsers.add_parser("inspect", help="鑑識檔案中的 AI 殘留與指紋特徵")
    p_inspect.add_argument("file", help="檔案路徑")
    p_inspect.set_defaults(func=handle_inspect)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
