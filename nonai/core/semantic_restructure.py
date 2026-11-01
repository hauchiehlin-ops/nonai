"""
Stage 1: Automated Semantic Restructuring & Burstiness Reshaper
Disrupts AI predictability, dismantles cliché transition templates (including standalone
首先/其次/最後/此外 markers), destabilizes uniform sentence lengths via organic in-place
clause decomposition (without canned boilerplate injections), and enforces strict lexical
boundaries to prevent adversarial defense (改寫防禦) triggers.
"""

import math
import random
import re
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Any, Optional

# Extended Lexical De-Patterning Dictionary (ZH & EN)
# NOTE: No replacement value may contain '首先', '其次', '再者', '最後', '此外', '總之', '綜上所述', '總結來說'.
EXPANDED_CLICHE_MAP_ZH: Dict[str, List[str]] = {
    "值得注意的是": ["特別需要留意的是", "在實務檢驗中可發現", "在脈絡上亦須關注", "不容忽視的是"],
    "值得一提的是": ["關鍵的一環在於", "另一個核心焦點在於", "具體觀察顯示", "需要補充說明的是"],
    "不可否認的是": ["平心而論", "就客觀實證來看", "無可爭辯的是", "在客觀檢視下"],
    "毋庸置疑的是": ["確鑿無疑的是", "無可爭辯的是", "平心而論"],
    "毋庸置疑": ["確鑿無疑", "毫無懸念", "實質上已成定論"],
    "總結來說": ["概括全篇脈絡", "總括而論", "就整體視野觀之", "綜合評估後"],
    "綜上所述": ["綜合前述多維分析", "基於以上實證推論", "通盤梳理後", "整體歸納而言"],
    "總結而言": ["整體歸納而言", "綜合上述脈絡", "總括而論"],
    "總而言之": ["通盤歸納來看", "整體觀之", "收束前述觀點"],
    "深入探討": ["周延剖析", "嚴密檢視", "細緻爬梳", "進行針對性考察"],
    "深入分析": ["系統性深究", "層層拆解", "周全考證"],
    "扮演著舉足輕重的角色": ["具決定性樞紐價值", "發揮基石效應", "具有實質引領作用"],
    "扮演著重要的角色": ["發揮核心關鍵功能", "居於關鍵推動地位", "具有不可替代的作用"],
    "扮演著重要角色": ["發揮核心推動效能", "處於關鍵節點", "具有不可替代的作用"],
    "扮演關鍵角色": ["居於核心地位", "掌握關鍵推動力", "決定整體走向"],
    "一把雙刃劍": ["利弊交織的機制", "具有兩面特徵的策略", "具雙向影響之手段"],
    "雙刃劍": ["兼具效益與風險", "存在一體兩面的拉扯", "帶來結構性利弊互見"],
    "顯著提升": ["帶來可觀增長", "實現實質跨越", "呈現大幅上揚", "有效推升"],
    "顯著增加": ["增幅極為明顯", "呈現放量攀升", "達到實質躍升"],
    "顯著改善": ["獲得顯見的優化", "迎來根本性轉機", "呈現正面成效"],
    "全面提升": ["全方位優化", "實現整體跨度改善", "通盤推動升級"],
    "這不僅僅是": ["這不僅止於", "這絕非單純的", "這超越了原本的"],
    "有助於": ["利於驅動", "實質助益於", "能有效促成"],
    "以期達到最佳之效益": ["藉此觀察實務效益", "力求獲致確切改善", "力求落實應用成效"],
    "以期達到之效益": ["以求實質成效", "用以驗證實務效益", "力求發揮實質助益"],
    "以期達到": ["力求促成", "以落實具體", "藉此實現實質"],
    "以期": ["藉此力求", "意在促成", "為此竭力實現"],
    "換言之": ["直言之", "簡言之", "換個角度透視"],
    "在當今數位化時代": ["身處數位轉型深化階段", "面對資訊科技普及的當下", "在數位環境高度成熟的今日"],
    "在當今快節奏的世界中": ["面對步調緊迫的現代環境", "在急速變遷的生活形態下", "在瞬息萬變的局勢中"],
    "為...奠定基礎": ["為...築牢根基", "奠立了長遠的發展基石", "拓展出厚實的實踐底層"],
    "顯而易見": ["客觀檢視下", "實務觀察顯示", "不難發現"],
    "至關重要": ["居關鍵樞紐", "具有實質決定性", "不可或缺"],
    "這項研究旨在": ["在架構規劃上，我們首要聚焦於", "本項工作的核心著眼於", "本案著手於"],
    "旨在探討": ["聚焦考察", "著眼於剖析", "致力於釐清"],
    "具有重要意義": ["深具實質學術與應用價值", "具備關鍵參考份量", "具有深遠實質意涵"],
    "提供了新的視角": ["開拓出不同以往的觀察切面", "帶來嶄新的分析切入點", "拓展了既有討論維度"],
    "有待進一步探討": ["仍需後續實證釐清", "尚待後續深入檢證", "值得在後續工作中持續追蹤"],
    "方法論本身就是主角": [
        "本案的核心亮點在於方法論的創新重構",
        "本計畫將方法架構創新視為核心關鍵",
        "方法論設計本身即為本計畫之主要突破點"
    ],
    "各自嵌入資料探勘核心": [
        "分別導入相應的資料探勘核心模組",
        "各自整合特定的資料科學演算法",
        "分別嵌入專屬的資料探勘演算法核心"
    ],
    "串成一條研究管線": [
        "串聯為連貫的端到端分析架構",
        "構築出系統化的分析流程路徑",
        "整合為一貫的技術分析管線"
    ],
    "各有面對消費者異質性時的盲點": [
        "在處理消費者異質性特徵時普遍存在方法學上的局限",
        "在面對消費者異質性時各有其方法學上的盲區",
        "各具其分析消費者異質性特徵時的限制"
    ],
}

EXPANDED_CLICHE_MAP_EN: Dict[str, List[str]] = {
    "delve into": ["examine", "explore", "investigate", "scrutinize", "probe into"],
    "delves into": ["examines", "explores", "investigates", "scrutinizes"],
    "delving into": ["examining", "exploring", "probing", "investigating"],
    "a pivotal role": ["a decisive function", "a central anchor", "an indispensable part"],
    "plays a pivotal role": ["directly steers", "is central to", "decisively influences"],
    "plays an important role": ["is influential", "serves as a backbone", "carries significant weight"],
    "a testament to": ["compelling evidence of", "a clear manifestation of", "proof of"],
    "rich tapestry": ["interwoven framework", "multifaceted landscape", "complex ecosystem"],
    "tapestry": ["mosaic", "interplay", "intricate array", "composite structure"],
    "in conclusion": ["ultimately", "taken together", "broadly speaking", "in the final analysis"],
    "in summary": ["on balance", "in sum", "to distill the core finding", "overall"],
    "it is worth noting that": ["notably,", "significantly,", "one key aspect is that"],
    "it is crucial to note that": ["importantly,", "of particular importance is that"],
    "furthermore": ["beyond this", "equally significant", "meanwhile", "alongside this"],
    "moreover": ["in parallel", "what is more", "alongside this", "building on this"],
    "foster": ["cultivate", "stimulate", "encourage", "drive forward"],
    "harness": ["leverage", "utilize", "deploy", "capitalize on"],
    "beacon": ["touchstone", "guiding benchmark", "reference standard"],
    "cutting-edge": ["contemporary", "state-of-the-art", "novel", "forward-looking"],
    "multifaceted": ["complex", "layered", "multi-dimensional", "nuanced"],
    "not only": ["beyond merely", "not simply"],
    "revolutionize": ["overhaul", "reshape", "redefine"],
    "seamlessly": ["cohesively", "directly", "unobtrusively", "coherently"],
}

# Boundary-Safe Lexical & Entity Diversity Rules (ZH)
# Each entry maps an entity name to (compiled_boundary_regex, list_of_safe_synonyms)
# Strictly prevents compound word corruption (e.g. prevents turning '本研究' into '本本項探討' or '系統性' into '架構機制性').
SAFE_ENTITY_DIVERSITY_RULES_ZH: Dict[str, Tuple[re.Pattern, List[str]]] = {
    "學校": (
        re.compile(r'(?<![各中小大該本貴專夜])學校(?![教育行政長園務友級生])'),
        ["受試院校", "教學現場", "辦學場域", "所屬校方", "該教學機構"]
    ),
    "學生": (
        re.compile(r'(?<![大中小醫研究留女男該本院])學生(?![會群們生證宿])'),
        ["受試學員", "在學青年", "學習者", "參與學員", "修課學子"]
    ),
    "教師": (
        re.compile(r'(?<![種子實習專任兼任指導授課新進資深女男該本])教師(?![節會群們團證])'),
        ["教學人員", "指導師資", "前線教育者", "授課師資", "教學團隊"]
    ),
    "系統": (
        re.compile(r'(?<![資訊教育生態作業醫療評量管理專家決策推薦檢索操作子本該此])系統(?![性化論統工程分析員中內外])'),
        ["平台機制", "整體架構", "此套機制", "運作模組"]
    ),
    "本研究": (
        re.compile(r'本研究(?![者所生院員團隊發案])'),
        ["本計畫", "本項工作", "本案", "此項探討"]
    ),
    "平台": (
        re.compile(r'(?<![跨雲端教學數位社群電商交易開放本該此])平台(?![化上中內外])'),
        ["系統環境", "操作介面", "數位環境", "協同空間"]
    ),
    "機構": (
        re.compile(r'(?<![醫療教育研究政府社福金融慈善學術分支認證主管本該此])機構(?![化性中內外])'),
        ["權責單位", "組織單位", "所屬單位", "實務單位"]
    ),
    "模型": (
        re.compile(r'(?<![語言大預測數學統計回歸結構商業理論決策深度機器生成認知本該此])模型(?![化型中內外])'),
        ["推論架構", "分析框架", "演算模組", "評估架構"]
    ),
    "數據": (
        re.compile(r'(?<![大統計實驗觀測歷史原始個人醫療金融開放本該此])數據(?![庫集化量分析])'),
        ["實證資料", "觀測數值", "統計指標", "量測資料"]
    ),
}

ENTITY_DIVERSITY_MAP_EN: Dict[str, List[str]] = {
    "school": ["academic institution", "educational setting", "the campus", "learning center"],
    "student": ["learner", "participant", "attendee", "undergraduate"],
    "teacher": ["instructor", "educator", "pedagogue", "academic staff"],
    "system": ["framework", "architecture", "platform mechanism", "functional module"],
    "research": ["investigation", "inquiry", "empirical inquiry", "study project"],
    "platform": ["digital environment", "infrastructure", "operational system"],
}


@dataclass
class RestructureMetrics:
    original_sentence_count: int
    reshaped_sentence_count: int
    original_mean_len: float
    reshaped_mean_len: float
    original_std_dev: float
    reshaped_std_dev: float
    original_cv: float  # std_dev / mean
    reshaped_cv: float
    burstiness_boost_percent: float
    cliches_purged_count: int
    cliche_replacements: List[Dict[str, Any]]
    rules_of_three_disrupted: int
    short_punchy_sentences_created: int
    high_risk_residues_dissolved: int = 0
    entity_diversity_replacements_count: int = 0
    entity_diversity_details: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class RestructureResult:
    cleaned_text: str
    metrics: RestructureMetrics


def _neutralize_discourse_transitions(text: str) -> Tuple[str, int, List[Dict[str, Any]]]:
    """
    Eliminates generic AI discourse transition markers ('首先', '其次', '再者', '最後', '此外')
    whether they occur in a single paragraph or across separate paragraphs/sentences.
    Guarantees zero self-contamination with other flagged transition markers.
    """
    res = text
    total_purged = 0
    replacements_log: List[Dict[str, Any]] = []

    # 1. Multi-sentence Rule-of-Three within the same text block (allowing multiple clauses between markers)
    r3_zh = re.compile(
        r'首先[，,、]\s*(?P<s1>[\s\S]{2,220}?)[。.]\s*其次[，,、]\s*(?P<s2>[\s\S]{2,220}?)[。.]\s*(?:再者[，,、]\s*(?P<s2b>[\s\S]{2,220}?)[。.]\s*)?最後[，,、]\s*(?P<s3>[\s\S]{2,220}?)[。.]'
    )
    def _sub_r3_zh(m):
        nonlocal total_purged
        total_purged += 1
        s1 = m.group("s1").strip()
        s2 = m.group("s2").strip()
        s2b = m.group("s2b")
        s3 = m.group("s3").strip()
        if s2b:
            return f"在起始層面，{s1}。進一層面來看，{s2}。延伸而言，{s2b.strip()}。至於最終收束階段，{s3}。"
        return f"在起始層面，{s1}。進一層面來看，{s2}。至於最終收束階段，{s3}。"

    res = r3_zh.sub(_sub_r3_zh, res)

    # English Rule-of-Three
    r3_en = re.compile(
        r'\bFirst(?:ly)?[,:]\s*(?P<s1>[^.]+?)[.]\s*Second(?:ly)?[,:]\s*(?P<s2>[^.]+?)[.]\s*(?:Third(?:ly)?|Finally|Lastly)[,:]\s*(?P<s3>[^.]+?)[.]',
        re.IGNORECASE
    )
    def _sub_r3_en(m):
        nonlocal total_purged
        total_purged += 1
        return f"At the outset, {m.group('s1').strip()}. In tandem, {m.group('s2').strip()}. In the culminating phase, {m.group('s3').strip()}."

    res = r3_en.sub(_sub_r3_en, res)

    # 2. Standalone / Cross-Paragraph Discourse Markers ('首先', '其次', '再者', '最後', '此外')
    transition_rules = [
        (
            "首先",
            re.compile(r'(?:^|(?<=[。！？!?\n；;：:]))\s*首先[，,、]\s*'),
            ["在起始階段，", "從基礎層面來看，", "首要焦點在於，", "就第一項維度而言，", "在架構起點上，", "先就核心脈絡觀之，"]
        ),
        (
            "首先",
            re.compile(r'(?<=[，,、])\s*首先(?=[探討分析檢視建立透過針對由將以從在是為著手聚焦])'),
            ["先期", "第一階段先", "首要"]
        ),
        (
            "首先",
            re.compile(r'(?:^|(?<=[。！？!?\n；;：:]))\s*首先(?=[探討分析檢視建立透過針對由將以從在是為著手聚焦])'),
            ["先期", "首要工作在於", "第一階段先"]
        ),
        (
            "其次",
            re.compile(r'(?:^|(?<=[。！？!?\n；;：:，,]))\s*其次[，,、]\s*'),
            ["進一層面來看，", "接續的關鍵在於，", "在第二個維度上，", "順此脈絡推進，", "對應的另一面向為，", "緊接著在方法銜接上，"]
        ),
        (
            "其次",
            re.compile(r'(?:^|(?<=[。！？!?\n；;：:，,]))\s*其次(?=[探討分析檢視建立透過針對由將以從在是為則])'),
            ["繼而", "次一階段", "接續"]
        ),
        (
            "再者",
            re.compile(r'(?:^|(?<=[。！？!?\n；;：:，,]))\s*再者[，,、]\s*'),
            ["更進一步來看，", "在延伸層面上，", "由縱深角度觀之，", "在進階環節中，"]
        ),
        (
            "最後",
            re.compile(r'(?:^|(?<=[。！？!?\n；;：:，,]))\s*最後[，,、]\s*'),
            ["在最終環節，", "至於收束層面，", "落實到終端階段，", "在壓軸的整合階段，", "歸結至最終步驟，", "邁入收尾階段時，"]
        ),
        (
            "最後",
            re.compile(r'(?:^|(?<=[。！？!?\n；;：:，,]))\s*最後(?=[探討分析檢視建立透過針對由將以從在是為則進整歸驗證完成])'),
            ["最終", "在終端階段", "至收尾階段"]
        ),
        (
            "此外",
            re.compile(r'(?:^|(?<=[。！？!?\n；;：:，,]))\s*此外[，,、]\s*'),
            ["在此之外，", "並行考量的是，", "與此呼應的是，", "從旁支脈絡觀之，", "若將視野擴及周邊面向，", "在相應的配套層面，"]
        ),
        (
            "此外",
            re.compile(r'(?:^|(?<=[。！？!?\n；;：:，,]))\s*此外(?=[亦也還更尚在針對於對])'),
            ["在此之外", "與此同時", "並行考量下"]
        ),
    ]

    for label, pat, choices in transition_rules:
        idx_counter = 0
        def _repl(m, ch_list=choices, lbl=label):
            nonlocal total_purged, idx_counter
            chosen = ch_list[idx_counter % len(ch_list)]
            idx_counter += 1
            total_purged += 1
            replacements_log.append({
                "original": lbl,
                "replacement": chosen,
                "count": 1,
                "lang": "zh"
            })
            return chosen

        res = pat.sub(_repl, res)

    return res, total_purged, replacements_log


def _dissolve_high_risk_residues(text: str) -> Tuple[str, int]:
    """
    Identifies and dismantles high-confidence AI residue sentences (60%~90% neural probability patterns),
    such as rigid tripartite structures, instrumental passive chains, and formulaic academic frames.
    Replaces them with active scholarly prose, varied pacing, and decomposed independent propositions.
    """
    dissolved_count = 0
    res = text

    # Pattern 1: 本研究旨在(?P<g1>.+?)，(進而|並)(?P<g2>.+?)，以期達到(?P<g3>.+?)之(?P<tail>效益|成效|目的|成果)
    p1 = re.compile(
        r'(?:本研究|本計畫|本論文|本研究案)?旨在(?P<g1>[^，。！？]+?)，(?:進而|並|同時)?(?P<g2>[^，。！？]+?)，以期達到(?P<g3>[^，。！？]+?)之(?:效益|成效|目的|成果|目標)',
        re.IGNORECASE
    )
    def _sub_p1(m):
        nonlocal dissolved_count
        dissolved_count += 1
        g1 = m.group("g1").strip()
        g2 = m.group("g2").strip()
        g3 = m.group("g3").strip()
        return f"在架構規劃上，我們首要聚焦於{g1}。後續分析則著重{g2}，藉此驗證{g3}的實際運作成效"
    res = p1.sub(_sub_p1, res)

    # Pattern 2: 旨在...，進而...，以期...
    p2 = re.compile(
        r'旨在(?P<g1>[^，。！？]+?)，(?:進而|並)?(?P<g2>[^，。！？]+?)，以期(?P<g3>[^，。！？]+?)(?=[。！？\n])',
        re.IGNORECASE
    )
    def _sub_p2(m):
        nonlocal dissolved_count
        dissolved_count += 1
        g1 = m.group("g1").strip()
        g2 = m.group("g2").strip()
        g3 = m.group("g3").strip()
        return f"主要著眼於{g1}，同時循序開展{g2}，藉以具體檢視{g3}"
    res = p2.sub(_sub_p2, res)

    # Pattern 3: 為此，本研究(將|透過)...以達到...
    p3 = re.compile(
        r'為此[，,]\s*(?:本研究|本計畫|本專案)?(?:將)?透過(?P<g1>[^，。！？]+?)，(?:以|用以)?達到(?P<g2>[^，。！？]+?)之(?P<tail>效益|成效|目的|成果|目標)',
        re.IGNORECASE
    )
    def _sub_p3(m):
        nonlocal dissolved_count
        dissolved_count += 1
        g1 = m.group("g1").strip()
        g2 = m.group("g2").strip()
        return f"為此，我們在方法設計上採取{g1}，力求落實{g2}的具體評估"
    res = p3.sub(_sub_p3, res)

    # Pattern 4: Instrumental chain: 透過/藉由 G1，得以/能夠/有效 G2，進而/並 G3
    p4 = re.compile(
        r'(?:透過|藉由|經由)(?P<g1>[^，。！？]{3,35})，(?P<subj>本研究|本計畫|我們|團隊)?(?:得以|能夠|可以|有效|進一步)(?P<g2>[^，。！？]{3,40})，(?:並|進而|同時|從而)(?P<g3>[^，。！？]{3,40})'
    )
    def _sub_p4(m):
        nonlocal dissolved_count
        dissolved_count += 1
        g1 = m.group("g1").strip()
        subj = (m.group("subj") or "").strip()
        g2 = m.group("g2").strip()
        g3 = m.group("g3").strip()
        prefix = f"{subj}以" if subj else "以"
        return f"{prefix}{g1}作為切入支點，直接促成{g2}；在此基礎上，亦能具體落實{g3}"
    res = p4.sub(_sub_p4, res)

    # Pattern 5: Paired Not-only / But-also: 不僅(僅)(是) G1，(同時)(更/更是/也/亦/還) G2
    p5 = re.compile(
        r'不僅(?:僅)?(?:是)?(?P<g1>[^，。；！？]{2,35})，(?:同時)?(?:更是|更|也|亦|還)(?P<g2>[^，。；！？]{2,45})'
    )
    def _sub_p5(m):
        nonlocal dissolved_count
        dissolved_count += 1
        g1 = m.group("g1").strip()
        g2 = m.group("g2").strip()
        return f"除{g1}之外，在延伸層面上亦體現為{g2}"
    res = p5.sub(_sub_p5, res)

    # Pattern 6: 隨著 G1 的(快速/持續)發展/普及/演進，G2
    p6 = re.compile(
        r'隨著(?P<g1>[^，。！？]{2,28})的(?:快速|蓬勃|持續|深入|廣泛|不斷|日益)?(?P<v>發展|演進|普及|推進|增加|提升|變遷|轉型|成熟)，(?P<g2>[^。！？]{4,60})'
    )
    def _sub_p6(m):
        nonlocal dissolved_count
        dissolved_count += 1
        g1 = m.group("g1").strip()
        v = m.group("v").strip()
        g2 = m.group("g2").strip()
        return f"面對{g1}持續{v}的局勢，{g2}"
    res = p6.sub(_sub_p6, res)

    # Pattern 7: 為 G1 提供了(重要/寶貴/堅實)的(參考/基礎/依據/方向)
    p7 = re.compile(
        r'為(?P<g1>[^，。！？]{2,25})提供(?:了)?(?P<adj>重要|關鍵|寶貴|堅實|全新|具體|有效|科學|系統性|實質)?(?:的|之)(?P<noun>參考依據|理論基礎|實證基礎|實務指引|決策參考|發展方向|分析架構|解決方案|基礎|依據|參考)'
    )
    def _sub_p7(m):
        nonlocal dissolved_count
        dissolved_count += 1
        g1 = m.group("g1").strip()
        adj = (m.group("adj") or "實質").strip()
        noun = m.group("noun").strip()
        return f"可作為{g1}推展時的{adj}{noun}"
    res = p7.sub(_sub_p7, res)

    # English Pattern 1: aims to ... in order to ... thereby achieving ...
    p_en = re.compile(
        r'\b(?:This study|This project|This research)?\s*aims to\s+(?P<g1>[^,.]+?),\s*(?:thereby|in order to)\s+(?P<g2>[^,.]+?),\s*(?:thereby achieving|so as to achieve)\s+(?P<g3>[^.]+?)\b',
        re.IGNORECASE
    )
    def _sub_p_en(m):
        nonlocal dissolved_count
        dissolved_count += 1
        g1 = m.group("g1").strip()
        g2 = m.group("g2").strip()
        g3 = m.group("g3").strip()
        return f"Our operational inquiry centers primarily on {g1}. Through this lens, we examine {g2} while assessing tangible outcomes in {g3}"
    res = p_en.sub(_sub_p_en, res)

    return res, dissolved_count


def _reduce_entity_repetition(text: str, char_window: int = 250) -> Tuple[str, int, List[Dict[str, Any]]]:
    """
    Suppresses excessive repetition of specific noun entities (e.g., '學校', '學生', '系統')
    using strict lexical boundary regexes so compound words (e.g. '本研究', '大學生', '系統性')
    are NEVER corrupted and adversarial defense ('改寫防禦') is never triggered.
    """
    total_replacements = 0
    details = []
    res = text

    # Process Chinese entities with strict boundary regexes
    for entity, (boundary_pat, syn_list) in SAFE_ENTITY_DIVERSITY_RULES_ZH.items():
        matches = list(boundary_pat.finditer(res))
        if len(matches) < 2:
            continue

        syn_pool = syn_list.copy()
        new_chars = []
        last_idx = 0
        last_rep_pos = -9999

        for i, m in enumerate(matches):
            start, end = m.start(), m.end()
            new_chars.append(res[last_idx:start])

            # Keep the very first mention to anchor the concept
            if i == 0:
                new_chars.append(entity)
                last_rep_pos = start
            else:
                if (start - last_rep_pos) <= char_window or i % 2 == 1:
                    chosen_syn = syn_pool[(i - 1) % len(syn_pool)]
                    new_chars.append(chosen_syn)
                    total_replacements += 1
                    details.append({
                        "entity": entity,
                        "replacement": chosen_syn,
                        "position": start
                    })
                else:
                    new_chars.append(entity)
                last_rep_pos = start

            last_idx = end

        new_chars.append(res[last_idx:])
        res = "".join(new_chars)

    # Process English entities
    for entity, syn_list in ENTITY_DIVERSITY_MAP_EN.items():
        pattern = re.compile(rf'\b{re.escape(entity)}\b', re.IGNORECASE)
        matches = list(pattern.finditer(res))
        if len(matches) < 2:
            continue

        syn_pool = syn_list.copy()
        new_chars = []
        last_idx = 0
        last_rep_pos = -9999

        for i, m in enumerate(matches):
            start, end = m.start(), m.end()
            new_chars.append(res[last_idx:start])
            orig_word = m.group(0)

            if i == 0:
                new_chars.append(orig_word)
                last_rep_pos = start
            else:
                if (start - last_rep_pos) <= char_window or i % 2 == 1:
                    chosen_syn = syn_pool[(i - 1) % len(syn_pool)]
                    if orig_word[0].isupper():
                        chosen_syn = chosen_syn.capitalize()
                    new_chars.append(chosen_syn)
                    total_replacements += 1
                    details.append({
                        "entity": entity,
                        "replacement": chosen_syn,
                        "position": start
                    })
                else:
                    new_chars.append(orig_word)
                last_rep_pos = start

            last_idx = end

        new_chars.append(res[last_idx:])
        res = "".join(new_chars)

    return res, total_replacements, details


def _split_into_sentences(text: str) -> List[str]:
    """Splits text into sentences for both Chinese and English while preserving basic boundaries."""
    parts = re.split(r'([。！？!?；;]\s*)', text)
    sentences = []
    i = 0
    while i < len(parts):
        s = parts[i]
        if i + 1 < len(parts):
            punc = parts[i + 1]
            sentences.append((s + punc).strip())
            i += 2
        else:
            if s.strip():
                sentences.append(s.strip())
            i += 1
    return [s for s in sentences if s]


def _calc_burstiness(sentences: List[str]) -> Tuple[float, float, float]:
    """Calculates Mean length, Standard Deviation, and Coefficient of Variation (CV)."""
    if not sentences:
        return 0.0, 0.0, 0.0
    lengths = [len(s) for s in sentences]
    mean_val = sum(lengths) / len(lengths)
    if len(lengths) <= 1 or mean_val == 0:
        return mean_val, 0.0, 0.0
    variance = sum((x - mean_val) ** 2 for x in lengths) / (len(lengths) - 1)
    std_dev = math.sqrt(variance)
    cv = std_dev / mean_val
    return round(mean_val, 2), round(std_dev, 2), round(cv, 4)


def restructure_semantics_and_burstiness(
    text: str,
    target_cv: float = 0.70,
    enable_cliche_purge: bool = True,
    enable_burstiness_boost: bool = True,
    enable_high_risk_residue_dissolve: bool = True,
    enable_entity_diversity: bool = True
) -> RestructureResult:
    """
    Performs Stage 1 Automated Semantic Restructuring:
    1. Dissolves high-risk residue templates (60%-90% probability patterns like '旨在...進而...以期...').
    2. Neutralizes generic discourse transitions ('首先', '其次', '再者', '最後', '此外') across paragraphs.
    3. Replaces AI clichés with natural human academic and discursive phrasing.
    4. Suppresses excessive repetition of specific noun entities with strict boundary guards.
    5. Re-shapes sentence lengths organically via in-place clause splitting (without canned boilerplate sentences).
    """
    if not text or not text.strip():
        empty_metrics = RestructureMetrics(0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0, [], 0, 0, 0, 0, [])
        return RestructureResult(text, empty_metrics)

    orig_sentences = _split_into_sentences(text)
    orig_mean, orig_std, orig_cv = _calc_burstiness(orig_sentences)

    processed_text = text
    cliche_replacements = []
    cliches_purged = 0
    rules_of_three = 0
    high_risk_dissolved = 0
    entity_replacements = 0
    entity_details = []

    # Step 0: Dissolve High-Risk Residue Templates
    if enable_high_risk_residue_dissolve:
        processed_text, high_risk_dissolved = _dissolve_high_risk_residues(processed_text)

    # Step 1: Lexical De-Patterning (Discourse Transitions + AI Cliché Purge)
    if enable_cliche_purge:
        # Step 1a: Neutralize '首先', '其次', '再者', '最後', '此外' and Rule-of-Three
        processed_text, trans_purged, trans_logs = _neutralize_discourse_transitions(processed_text)
        if trans_purged > 0:
            rules_of_three += trans_purged
            cliches_purged += trans_purged
            cliche_replacements.extend(trans_logs)

        # Step 1b: Chinese clichés
        for cliche, replacements in EXPANDED_CLICHE_MAP_ZH.items():
            if cliche in processed_text:
                count = processed_text.count(cliche)
                chosen = random.choice(replacements)
                processed_text = processed_text.replace(cliche, chosen)
                cliches_purged += count
                cliche_replacements.append({
                    "original": cliche,
                    "replacement": chosen,
                    "count": count,
                    "lang": "zh"
                })

        # Step 1c: English clichés
        for cliche, replacements in EXPANDED_CLICHE_MAP_EN.items():
            pattern = re.compile(rf'\b{re.escape(cliche)}\b', re.IGNORECASE)
            matches = pattern.findall(processed_text)
            if matches:
                chosen = random.choice(replacements)
                processed_text = pattern.sub(chosen, processed_text)
                count = len(matches)
                cliches_purged += count
                cliche_replacements.append({
                    "original": cliche,
                    "replacement": chosen,
                    "count": count,
                    "lang": "en"
                })

    # Step 1d: Boundary-Safe Entity Diversity & Repetition Suppression
    if enable_entity_diversity:
        processed_text, entity_replacements, entity_details = _reduce_entity_repetition(processed_text)

    # Step 2: Organic Burstiness Reshaper (In-Place Clause Splitting without Boilerplate Injections)
    short_sentences_created = 0
    if enable_burstiness_boost:
        paragraphs = processed_text.split('\n')
        reshaped_paragraphs = []

        zh_split_conjunctions = [
            ('，進而', '藉此'),
            ('，並進一步', '同時進一步'),
            ('，並', '同時'),
            ('，且', '而且'),
            ('，同時', '在此同時，'),
            ('，藉此', '藉以'),
            ('，從而', '進而'),
            ('，因而', '因此'),
            ('，然而', '不過，'),
            ('，使得', '這也讓'),
        ]

        for para in paragraphs:
            if not para.strip():
                reshaped_paragraphs.append(para)
                continue

            para_sentences = _split_into_sentences(para)
            new_para_sentences = []

            for s in para_sentences:
                # 1. Check for long compound Chinese sentences (> 36 chars) with natural clause breaks
                if len(s) > 36 and any(c[0] in s for c in zh_split_conjunctions):
                    for conj, lead in zh_split_conjunctions:
                        if conj in s:
                            parts = s.split(conj, 1)
                            if len(parts[0].strip()) >= 8 and len(parts[1].strip()) >= 6:
                                p1 = parts[0].strip() + "。"
                                tail = parts[1].strip()
                                p2 = (lead + tail) if not tail.startswith(("這", "此", "同時", "不過")) else tail
                                new_para_sentences.extend([p1, p2])
                                short_sentences_created += 1
                                break
                    else:
                        new_para_sentences.append(s)

                # 2. Check for long multi-comma Chinese sentences (>= 3 commas, > 42 chars) to create natural short-long contrast
                elif len(s) > 42 and s.count("，") >= 3:
                    clauses = s.split("，")
                    # Split after the first or last clause to produce a short punchy sentence + longer detailed sentence
                    if len(clauses[0]) >= 7 and len(clauses[0]) <= 18:
                        p1 = clauses[0].strip() + "。"
                        p2 = "，".join(clauses[1:]).strip()
                        new_para_sentences.extend([p1, p2])
                        short_sentences_created += 1
                    else:
                        mid = len(clauses) // 2
                        p1 = "，".join(clauses[:mid]).strip() + "。"
                        p2 = "，".join(clauses[mid:]).strip()
                        new_para_sentences.extend([p1, p2])
                        short_sentences_created += 1

                # 3. Check for long compound English sentences (> 26 words) with conjunctions
                elif len(s.split()) > 26 and any(conj in s for conj in [', and ', ', which ', ', but ', ', whereas ']):
                    for conj in [', and ', ', which ', ', but ', ', whereas ']:
                        if conj in s:
                            parts = s.split(conj, 1)
                            p1 = parts[0].strip() + "."
                            lead_word = "In turn, " if conj in [', and ', ', which '] else "Conversely, "
                            p2 = lead_word + parts[1].strip()[0].upper() + parts[1].strip()[1:]
                            new_para_sentences.extend([p1, p2])
                            short_sentences_created += 1
                            break
                    else:
                        new_para_sentences.append(s)
                else:
                    new_para_sentences.append(s)

            # Local entropy check: If paragraph still has uniform sentence lengths (local_cv < 0.42),
            # decompose the longest comma-separated sentence in-place rather than injecting disconnected boilerplate!
            _, _, local_cv = _calc_burstiness(new_para_sentences)
            if len(new_para_sentences) >= 2 and local_cv < 0.42:
                longest_idx = max(range(len(new_para_sentences)), key=lambda idx: len(new_para_sentences[idx]))
                longest_s = new_para_sentences[longest_idx]
                if "，" in longest_s and len(longest_s) >= 24:
                    c_parts = longest_s.split("，", 1)
                    if len(c_parts[0].strip()) >= 5 and len(c_parts[1].strip()) >= 5:
                        s_short = c_parts[0].strip() + "。"
                        s_rest = c_parts[1].strip()
                        new_para_sentences[longest_idx:longest_idx + 1] = [s_short, s_rest]
                        short_sentences_created += 1

            is_pure_ascii = all(ord(c) < 128 for c in para)
            reshaped_paragraphs.append(" ".join(new_para_sentences) if is_pure_ascii else "".join(new_para_sentences))

        processed_text = "\n".join(reshaped_paragraphs)

    # Calculate final reshaped metrics
    final_sentences = _split_into_sentences(processed_text)
    reshaped_mean, reshaped_std, reshaped_cv = _calc_burstiness(final_sentences)

    boost_ratio = round(((reshaped_cv - orig_cv) / max(orig_cv, 0.001)) * 100, 1)

    metrics = RestructureMetrics(
        original_sentence_count=len(orig_sentences),
        reshaped_sentence_count=len(final_sentences),
        original_mean_len=orig_mean,
        reshaped_mean_len=reshaped_mean,
        original_std_dev=orig_std,
        reshaped_std_dev=reshaped_std,
        original_cv=orig_cv,
        reshaped_cv=reshaped_cv,
        burstiness_boost_percent=boost_ratio,
        cliches_purged_count=cliches_purged,
        cliche_replacements=cliche_replacements,
        rules_of_three_disrupted=rules_of_three,
        short_punchy_sentences_created=short_sentences_created,
        high_risk_residues_dissolved=high_risk_dissolved,
        entity_diversity_replacements_count=entity_replacements,
        entity_diversity_details=entity_details[:20]
    )

    return RestructureResult(cleaned_text=processed_text, metrics=metrics)
