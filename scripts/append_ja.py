# -*- coding: utf-8 -*-
import json

from scripts.build_full_i18n import DATA

# 4. ja (日本語)
DATA["ja"] = {
    "app_title": "NonAI - AI デジタル指紋・痕跡消去システム",
    "brand_sub": "AI デジタル指紋・透かし・低レイヤーメタデータ完全消去エンジン",
    "watcher_label": "クリップボード監視 (Scheme C)",
    "watcher_active": "リアルタイム監視中",
    "watcher_inactive": "未起動",
    "watcher_btn_start": "保護を開始",
    "watcher_btn_stop": "保護を停止",
    "watcher_running": "保護稼働中 (コピー内容を自動浄化)",
    "watcher_stopped": "保護停止中",
    "tab_files": "📁 ファイル浄化ワークスペース (.docx, .pdf, .md, .txt)",
    "tab_text": "✍️ リアルタイムテキスト＆Hexフォレンジック",
    "tab_clipboard": "📋 クリップボード活動ログ",
    "tab_manual": "📖 操作＆フォレンジック解説書",
    "drop_title": "ファイルをここにドラッグ＆ドロップ、またはクリックして選択",
    "drop_subtitle": "対応フォーマット：Word (.docx)、PDF (.pdf)、Markdown (.md)、プレーンテキスト (.txt)",
    "tag_rsid": "DOCX RSID 生体模倣注入",
    "tag_pdf": "PDF XMP メタデータ偽装",
    "tag_css": "Web CSS ゴースト背景色消去",
    "tag_unicode": "ゼロ幅 Unicode 浄化",
    "adv_title": "⚙️ 高度生体模倣パラメータ設定 (DOCX / PDF / 統計的攪乱)",
    "lbl_author": "偽装文書作成者 (Author)：",
    "hint_author": "Word docProps/core.xml の作成者欄に書き込み",
    "lbl_rsid": "DOCX RSID 履歴セッション注入数：",
    "hint_rsid": "保存回数とタイピング一時停止履歴を再現",
    "lbl_pdf": "PDF 生成ツール偽装ターゲット：",
    "lbl_perturb": "統計的透かし攪乱を有効化 (n-gram切断、類語微調整)",
    "btn_timing": "ℹ️ 推奨タイミング",
    "btn_timing_title": "推奨適用タイミングの解説を表示",
    "timing_popover_heading": "💡 推奨タイミングの解説",
    "timing_author_title": "💡 推奨タイミング：文書作成者の偽装",
    "timing_author_desc": "【使用時期】学術論文やビジネスレポート提出時、プロパティがChatGPTや外部ライブラリとして残るのを防止します。<br>【推奨値】実名、所属機関の略称、またはAuthorを設定。<br>【効果】docProps/core.xml 内の dc:creator と cp:lastModifiedBy を上書き。",
    "timing_rsid_title": "💡 推奨タイミング：DOCX RSID セッション注入",
    "timing_rsid_desc": "【使用時期】文書フォレンジック審査を通過させる必要がある時。AI製Wordは通常RSIDが0〜1組しかなく致命的な痕跡になります。<br>【推奨値】短文は15〜20組、長文論文は25〜40組。<br>【効果】settings.xml と runs に多重セッション鎖を注入し、人間の思考停止リズムを再現。",
    "timing_pdf_title": "💡 推奨タイミング：PDF 生成ツール偽装ターゲット",
    "timing_pdf_desc": "【使用時期】社外へPDFを配布する際、内部で Chromium、Skia、python-pdf-lib が露見するのを防ぎます。<br>【推奨値】Mac利用者は macOS Quartz、Windows利用者は Microsoft Word を推奨。<br>【効果】Producer と Creator を偽装し、XMPストリームを完全除去。",
    "timing_perturb_title": "💡 推奨タイミング：統計的透かし攪乱",
    "timing_perturb_desc": "【使用時期】Google SynthID のグリーンリスト確率透かしやAI検出器への対策が必要な時。<br>【推奨値】常時有効化を強く推奨します。<br>【効果】AI特有の高頻度フレーズを置換し、n-gram連鎖を切断してz-score有意性を無力化。",
    "res_clean_prefix": "✅ 浄化完了：",
    "res_desc": "ファイル構造は人間の執筆生体特徴と清潔なメタデータで再構築されました",
    "btn_download": "💾 浄化済みファイルをダウンロード",
    "stat_rsid_injected": "注入された RSID セッション",
    "stat_runs_split": "Runs 断片化スプリット",
    "stat_ai_purged": "AI 固有署名消去",
    "stat_pkg_synthesized": "Word 標準パッケージ構造",
    "stat_semantic_perturbs": "文体・意味デパターニング",
    "stat_ghost_removed": "ゴーストスタイル/背景色消去",
    "stat_unicode_removed": "ゼロ幅 Unicode 除去",
    "stat_human_minutes": "偽装タイピング執筆時間",
    "stat_app_spoofed": "偽装ソフトウェア名",
    "stat_inspect_hint": "🔍 クリックして実行詳細を表示",
    "unit_sessions": "セッション",
    "unit_splits": "箇所分割",
    "unit_purged": "件消去",
    "unit_parts": "個の標準構成",
    "unit_replacements": "箇所最適化",
    "unit_styles": "箇所消去",
    "unit_chars": "文字",
    "unit_minutes": "分",
    "txt_raw_header": "元テキスト / 貼り付け内容",
    "txt_btn_paste": "📋 クリップボード貼付",
    "txt_btn_clear": "クリア",
    "txt_raw_placeholder": "ChatGPT や Claude 等で生成されたテキストをここに貼り付けてください。不可視コードやメタタグを自動解析します...",
    "txt_char_count": "文字数：",
    "txt_alert_anomaly": "⚠️ 異常文字を検出しました！",
    "txt_clean_header": "浄化・指紋消去結果",
    "txt_btn_copy": "📋 クリーンテキストをコピー",
    "txt_clean_placeholder": "浄化後のテキストがここに表示されます...",
    "txt_status_clean": "純粋・指紋なし",
    "audit_header": "🔬 テキストフォレンジック診断書",
    "audit_risk_level": "AI 識別リスクレベル：",
    "audit_anomalies_found": "検出された異常マーク：",
    "audit_hidden_tags": "隠蔽スタイルタグ：",
    "audit_watermark_entropy": "透かしエントロピー干渉率：",
    "clip_header": "🛡️ システムクリップボード常駐保護 (Scheme C)",
    "clip_desc": "バックグラウンドで動作。ChatGPT、Claude からのコピー時に、メモリ上でゼロ幅文字とゴーストCSSスタイルを自動除去します。",
    "clip_stream_title": "リアルタイム遮断ログ (Recent Intercepts)",
    "clip_btn_refresh": "🔄 更新",
    "clip_empty": "遮断イベントはまだありません。保護を開始後、テキストをコピーするとリアルタイム浄化が確認できます。",
    "clip_item_tag": "浄化完了",
    "manual_sub": "本マニュアルでは、段階的な実行手順、フォレンジックの原理、各パラメータの最適設定を体系的に案内します。",
    "manual_step1_badge": "フェーズ 1",
    "manual_step1_title": "システムクリップボード常駐保護 (Scheme C)",
    "manual_step1_body": "<strong>仕組み：</strong>システム起動時にデフォルトで保護が稼働しています（右上の緑ランプ）。ブラウザからAI生成文章をコピーした瞬間、0.5秒以内にメモリ上で脱水浄化され、背景色や不可視文字を抹消します。",
    "manual_step1_tip": "💡 <strong>ヒント：</strong>Word や書類にそのまま貼り付けても <code>#F7F7F8</code> などのチャット枠背景色が一切残りません。",
    "manual_step2_badge": "フェーズ 2",
    "manual_step2_title": "ファイルドラッグ浄化＆生体模倣 (DOCX / PDF / MD / TXT)",
    "manual_step2_body": "<strong>仕組み：</strong>アップロード枠にファイルをドラッグすると、OpenXML または PDF 辞書再構築エンジンが即座に起動します：",
    "manual_step2_li1": "<strong>DOCX：</strong>20〜40組の RSID セッションを逆注入し、句読点で Runs を自然分割、公式フォント表・設定・テーマを合成し、Claude 固有タグを完全抹消。",
    "manual_step2_li2": "<strong>PDF：</strong>Producer と Creator を公式仕様（macOS Quartz または Word 365）に上書きし、ページ毎の XMP を除去して自然な時間差を再現。",
    "manual_step2_li3": "<strong>Markdown：</strong>機械的すぎるテーブル空白配置を自然な幅に戻し、箇条書きインデントとAIの決まり文句前置き・結びを除去。",
    "manual_step3_badge": "フェーズ 3",
    "manual_step3_title": "フォレンジック詳細検証＆セーフダウンロード",
    "manual_step3_body": "<strong>仕組み：</strong>処理完了後、各メトリクスカードをクリックすると詳細ウィンドウが開き、注入された16進コードや分割サンプルを検証できます。「浄化済みファイルをダウンロード」を押すとブラウザ内メモリ Blob から即座にファイルが保存されます。",
    "faq_header": "💡 AI 指紋と NonAI コア技術に関する FAQ",
    "faq_q1": "Word 文書における RSID の欠陥とは何ですか？",
    "faq_a1": "人間が Word で執筆する際、タイピングの一時停止や編集、保存のたびに <code>document.xml</code> に複数の RSID が刻まれます。AI 生成ファイルは通常これが 0〜1 組しかなく、判定ソフトに即座に見破られます。NonAI は 20〜40 組のセッションを自然に逆注入します。",
    "faq_q2": "AI テキストをコピーすると「ゴースト背景色」が残るのはなぜですか？",
    "faq_a2": "Web の対話枠からコピーする際、<code>&lt;span style=\"background-color: #f7f7f8\"&gt;</code> などの微弱な背景色や特定フォントがクリップボードに混入します。NonAI はコピーの瞬間に純粋なテキストへと脱水処理します。",
    "faq_q3": "統計的透かし (SynthID など) や分類器にどう対抗しますか？",
    "faq_a3": "統計的透かしはグリーンリスト選択確率を利用し、分類器は定型構文や一定の文長を検知します。NonAI は n-gram 結合を切断し、定型対句を崩して文章の自然な長さの揺らぎ（Burstiness）を再現します。",
    "faq_q4": "NonAI は完全なオフラインプライバシーを保証しますか？",
    "faq_a4": "はい。NonAI は完全なローカル処理アーキテクチャを採用しており、ファイル変換やバイナリ生成はすべてお使いの端末やブラウザメモリ内で完結し、外部クラウドに保存されることはありません。",
    "footer_text": "NonAI 2.0 • 100% 完全ローカルオフライン処理 • プライバシー保護と執筆指紋防護",
    "modal_close": "閉じる",
    "modal_details": {
        "rsid": {
            "title": "注入された RSID セッション - フォレンジック解説",
            "desc": "<strong>RSID（Revision Save ID）とは？</strong><br>Word において編集、削除、保存のたびに自動記録される4バイトの16進数識別子です。AI製ファイルはこれが欠如しているか全編単一値であり、フォレンジック検査で真っ先に摘発される欠陥です。",
            "sub": "注入された生体模倣 RSID セッションプール（計 {count} 組）"
        },
        "runs_split": {
            "title": "Runs 断片化スプリット - タイピングリズム再現",
            "desc": "<strong>なぜ Runs 分割が必要なのか？</strong><br>AI ツールは段落全体を単一の連続した <code>&lt;w:r&gt;</code> に詰め込む傾向があります。人間がタイピングする場合、句読点（、。）で自然な思考の一時停止が生じます。NonAI は <strong>{count}</strong> 箇所の句読点で自然に断片化分割しました。",
            "sub": "分割サンプル",
            "sample_desc": "長いテキストノードが自然な人間の入力一時停止間隔で分割されています。"
        },
        "claude_purged": {
            "title": "AI 固有署名消去 - 出所メタタグの完全抹消",
            "desc": "<strong>解決された致命的欠陥：ファイルの自白シグネチャ</strong><br>Claude Docs 等は出力時に <code>docProps/core.xml</code> の <code>&lt;dc:description&gt;</code> に <code>Claude Docs node/...</code> を明記し、<code>customXml/</code> を埋め込みます。検査ツールはこれを推測ではなく確定出所として判定します。",
            "sub": "実行されたフォレンジック消去項目",
            "items": [
                "<strong>タグ消去：</strong><code>&lt;dc:description&gt;</code> を完全除去し、不要なキーワードや主題を消去。",
                "<strong>カスタムパッケージ除去：</strong><code>customXml/</code> と <code>docProps/custom.xml</code> を完全排除。",
                "<strong>全域文字列スキャン：</strong>XML ストリーム全体から <code>Claude Docs</code>、<code>Anthropic</code>、<code>ChatGPT</code> 等の痕跡を抹消。"
            ]
        },
        "pkg_synthesized": {
            "title": "Word 標準パッケージ構造 - 整合性の修復",
            "desc": "<strong>解決された致命的欠陥：公式パッケージ構造の欠落</strong><br>正規の Word で保存されたファイルには、<code>fontTable.xml</code>、<code>webSettings.xml</code>、<code>theme1.xml</code> が必須です。AI ファイルはこれらを欠いており、「Word 詐称」として判定されていました。",
            "sub": "自動合成された Microsoft 標準パッケージ構成",
            "items": [
                "<code>word/fontTable.xml</code>：Calibri、Times New Roman、MS 明朝等の標準フォント表。",
                "<code>word/webSettings.xml</code>：ブラウザ最適化および PNG サポートフラグ。",
                "<code>word/theme/theme1.xml</code>：Office 公式の標準カラーおよびフォントスキーム。",
                "<code>[Content_Types].xml</code> と <code>document.xml.rels</code>：正式なスキーマで関連付け。"
            ]
        },
        "semantic": {
            "title": "文体・意味デパターニング - Transformer 遮断シールド",
            "desc": "<strong>解決された欠陥：ニューラル分類器による機械的特徴検知</strong><br>OmniTraces 等の分類器は、テキストの複雑度（Perplexity）分布や硬直した三段論法を捉えます。NonAI は AI 特有の定型句を自然な学術・専門表現へと再構築します。",
            "sub": "ニューラル撹乱と最適化指標",
            "items": [
                "<strong>AI 定型句・硬直構文の再構築：</strong>計 {replacements} 箇所",
                "<strong>文長バースト性とセミコロンリズム最適化：</strong>計 {reorganized} 節",
                "<strong>N-gram 予測連鎖切断：</strong>SynthID グリーンリストの統計的有意性を中和"
            ]
        },
        "ghost_styles": {
            "title": "ゴーストスタイル/背景色消去 - Web 装飾除去",
            "desc": "<strong>対話枠からのゴースト色：</strong><br>Web からコピーした際に <code>#F7F7F8</code> などの背景色が <code>&lt;w:shd&gt;</code> に残る現象を解消し、純粋な文書スタイルへ復元しました。",
            "sub": "除去されたゴーストスタイル・フォント項目"
        },
        "unicode": {
            "title": "ゼロ幅 Unicode 除去 - 不可視透かしの消去",
            "desc": "<strong>不可視バーコード透かし：</strong><br>一部の AI システムはゼロ幅スペース（ZWSP）等を埋め込んで出所を追跡します。NonAI は全角句読点を保護しながら不可視コードのみを完全に除去します。",
            "before_label": "検出された不可視文字",
            "after_label": "浄化後の状態",
            "clean_status": "100% 清潔な標準 NFC エンコード"
        },
        "human_time": {
            "title": "偽装タイピング執筆時間 - タイムライン再現",
            "desc": "<strong>執筆時間の欠落：</strong><br>AI 製ファイルは <code>&lt;TotalTime&gt;0&lt;/TotalTime&gt;</code> となりがちです。NonAI は文字数に基づき、人間らしい執筆および思考時間を割り当てます。",
            "sub": "生体模倣タイムラインモデル",
            "items": [
                "<strong>推定執筆時間：</strong>{minutes} 分（分速 32〜35 文字＋思考休憩を考慮）",
                "<strong>リビジョン番号：</strong>第 {revision} 版",
                "<strong>作成日時：</strong>{created}",
                "<strong>更新日時：</strong>{modified}"
            ]
        },
        "app_spoofed": {
            "title": "偽装ソフトウェア名 - メタデータの上書き",
            "desc": "<strong>ソフトウェア情報：</strong><br>python-docx 等のライブラリ識別子を正規の Microsoft Office Word プロパティへ置換しました。",
            "code_title": "正規の docProps XML 定義"
        },
        "pdf_producer": {
            "title": "PDF メタデータ＆ XMP 浄化",
            "desc": "<strong>PDF 生成ツールの偽装：</strong><br>wkhtmltopdf や Chromium 等を正規のシステム仮想プリンタ名に置換し、ページ単位の XMP ストリームを除去しました。",
            "orig_producer": "元の Producer",
            "spoofed_producer": "偽装後 Producer",
            "spoofed_creator": "偽装後 Creator"
        },
        "markdown": {
            "title": "Markdown 構造デパターニング - 自然な書式",
            "desc": "<strong>機械的に整いすぎた Markdown：</strong><br>過度に整列された表の空白を自然な簡約スタイルに戻し、箇条書き記号を人間らしく調整します。"
        }
    }
}

print("ja added successfully")
