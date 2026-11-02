#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
report_validator.py — pubmed搜文献助手 报告质量验证器（独立版，零第三方依赖）
用法: python report_validator.py <report.html> [--ifmap journal_if_map.json]
退出码 0 = 通过(可交付); 非0 = 存在红线/门禁失败(❌ 打印原因)

本验证器为「关键词文献报告」专用，与学术人才背调团及其验证器互不依赖：
  - 无 __ME__/候选人强制检查（客户指定追踪作者时才校验一致性）
  - IF 防编造：报告内所有 ifv 必须与本包 journal_if_map.json 精确命中一致
"""
import json
import os
import re
import sys

# ---- 净化词(冗余客套/不确定表述, 0 命中才可通过) ----
PURGE_WORDS = [
    "综上所述", "值得注意的是", "此外", "另外", "总体而言", "不难看出", "由此可见",
    "需要指出的是", "值得一提的是", "不难发现", "客观上", "主观上",
    "一定程度上", "简而言之", "归根到底", "一言以蔽之", "毫不意外", "顺带一提",
    "话说回来", "据不完全统计", "可能约为", "预计大约",
]
# ---- 禁用 CSS 变量(旧模板残留) ----
FORBIDDEN_CSS_VARS = ["--ink", "--sub", "--brand"]
# ---- IF/来源 红线词(禁用估算类表述) ----
RED_LINE_WORDS = ["OpenAlex", "IF≈", "篇均被引", "据公开资料推测", "网传", "疑似", "IF约", "影响因子约"]

# ---- 软文字/方法学核算 门禁(内部过程叙述, 0 命中才可通过; 2026-09-22 同步自背调文献线) ----
SOFT_TEXT_SECTION = [   # h2 章节标题含这些词 => 整段禁止(内部过程叙述)
    "检索口径", "同名消歧", "漏检反查", "对账式",
    "同名异人排除", "（简要）", "不计入一作", "不计入通讯",
    # 压缩/抽样类标题词（2026-09-22 用户定性：「主要论文」「重点论文」与「简要」同罪）
    "主要论文", "重点论文", "代表作", "精选", "核心论文",
]
SOFT_TEXT_INLINE = [    # 正文任意位置出现即禁止(内部过程叙述)
    "漏检反查", "放宽 AFF 探针", "放宽 AFF 仅作漏检探针",
    "检索口径与同名消歧", "完全对账", "三段式对账", "对账式与漏检反查",
    # 检索过程叙述词族（2026-09-22 用户定性：检索式表/hitCount/并集去重/漏检核算
    # 属内部过程噪声，交付物禁止出现）
    "检索式", "hitCount", "并集去重", "严重漏检", "全量抓取", "AUTH:",
]

# ---- 文献清单结构门禁(2026-09-22) ----
# 文献清单章节标题「正信号」关键词：含这些即判定为文献清单章节。
LIT_SECTION_KW = ["完整文献清单", "文献清单", "文章清单", "论文清单"]
# 文献清单章节标题「负信号」关键词：与「完整文献清单」互斥，属压缩/抽样换马甲，一票否决。
LIT_COMPRESS_KW = [
    "主要论文", "重点论文", "代表作", "代表性", "精选", "核心论文",
    "简要", "节选", "摘录", "概要",
]

CJK = re.compile(r"[\u4e00-\u9fff]")


def load_ifmap(path):
    """加载 IF 表, 兼容两种格式(与 pubmed_search.load_ifmap 保持一致):
    - 旧: {name: {field: value, ...}}
    - 新(体积优化): {"_fields": [...], name: [v1, ...]} → 还原为字典
    """
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8-sig") as f:  # utf-8-sig 兼容带/不带 BOM
        raw = json.load(f)
    if not raw:
        return raw
    sample = next(iter(raw.values()))
    if isinstance(sample, dict):
        return raw
    fields = raw.get("_fields") or []
    return {k: dict(zip(fields, v)) for k, v in raw.items()
            if k != "_fields" and isinstance(v, list)}


_NORM_IDX = {}


def _norm(s):
    """规范化: 大写、&→AND、去非字母数字。消除逗号/撇号/连字符/AND vs & 差异。"""
    return re.sub(r"[^A-Z0-9]", "", s.upper().replace("&", " AND "))


def _if_norm_index(ifmap):
    """IF 表规范化索引(惰性构建, 仅用于查表回退, 不影响防编造判定)。"""
    if not _NORM_IDX:
        for k, v in ifmap.items():
            _NORM_IDX.setdefault(_norm(k), v)
    return _NORM_IDX


def _is_lit_section(title):
    """判定 h2 标题是否为「文献清单」章节（正信号）。"""
    t = title.strip()
    if any(k in t for k in LIT_SECTION_KW):
        return True
    # 刘赤式: "一作/通讯文章清单" —— 含 一作 + 通讯 + 清单
    if "一作" in t and "通讯" in t and "清单" in t:
        return True
    return False


def check_soft_text(html):
    """软文字门禁(2026-09-22)：内部过程叙述 0 命中才可通过。
      (a) h2 章节标题含 SOFT_TEXT_SECTION 词 => 禁止（整段属内部过程叙述）；
      (b) 正文任意位置出现 SOFT_TEXT_INLINE 词 => 禁止。
    报告只交付结果；检索合规由脚本层门禁保证，不在报告里叙述过程。"""
    errors = []
    for m in re.finditer(r"<h2\b[^>]*>(.*?)</h2>", html, re.S | re.I):
        title = re.sub(r"<[^>]+>", "", m.group(1)).strip()
        for kw in SOFT_TEXT_SECTION:
            if kw in title:
                errors.append("✗ 软文字门禁: 章节标题含内部过程/压缩词 %r（%s）—— 须删去该词"
                              % (kw, title))
    for kw in SOFT_TEXT_INLINE:
        if kw in html:
            errors.append("✗ 软文字门禁: 正文出现内部过程叙述词 %r（报告只交付结果，不叙述检索过程）" % kw)
    return errors


def check_literature_format(html, rtype="literature"):
    """结构门禁（2026-09-22）：文献报告的「文献清单」段必须 DATA 驱动
    交互卡片，禁止手写静态 <table> 行式罗列、禁止压缩/抽样标题。

    设计原则：仅当报告**存在**文献清单章节时才生效；无文献清单章节一律放行。
    文献清单章节存在时，强制三项：
        (a) 标题禁压缩词（主要论文/重点论文/代表作/代表性/精选/核心论文/简要/节选/摘录/概要）；
        (b) 章节内禁手写 <table> 行式罗列（把全量清单写成静态表属偷懒，一票否决）；
        (c) 必须 const DATA + #list 容器驱动（缺即非 DATA 驱动）。
    该门禁锁的是交付**结构本身**（比"限词"更稳）：只要结构正确，个别措辞差异
    （如「文章清单（共 N 篇）」vs「完整文献清单（一作 + 通讯 N 篇全量）」）均放行。
    """
    errors = []
    # 切分 h2 章节
    h2_spans = [(m.start(), m.end(), re.sub(r"<[^>]+>", "", m.group(1)).strip())
                for m in re.finditer(r"<h2\b[^>]*>(.*?)</h2>", html, re.S | re.I)]
    lit_sections = [(i, s, e, t) for i, (s, e, t) in enumerate(h2_spans) if _is_lit_section(t)]
    if not lit_sections:
        return errors  # 无文献清单章节：放行

    for i, s, e, title in lit_sections:
        # (a) 压缩/抽样标题词
        for kw in LIT_COMPRESS_KW:
            if kw in title:
                errors.append("✗ 结构门禁: 文献清单标题含压缩/抽样词 %r（%s）—— 须展开为全量文献清单"
                              % (kw, title))
        # (b) 章节内手写 <table> 行式罗列
        end = h2_spans[i + 1][0] if i + 1 < len(h2_spans) else len(html)
        seg = html[s:end]
        if re.search(r"<table\b", seg, re.I) and re.search(r"<tr\b", seg, re.I):
            errors.append("✗ 结构门禁: 文献清单章节 %r 内出现手写 <table> 行式罗列——"
                          "须改为 const DATA + #list 交互卡片" % title)

    # (c) 全局须 DATA 驱动: const DATA + #list 容器
    if not re.search(r"const DATA", html):
        errors.append("✗ 结构门禁: 文献清单章节存在但未检测到 const DATA——须 DATA 驱动卡片")
    if not re.search(r'id="list', html):
        errors.append("✗ 结构门禁: 文献清单章节存在但未检测到 id=\"list\" 容器——须 #list 渲染卡片")
    return errors


def check(path, ifmap):
    errors = []
    if not os.path.exists(path):
        return ["❌ 文件不存在: " + path]
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        html = f.read()

    # 1) 基本结构闭合
    if not html.strip().lower().startswith("<!doctype html"):
        errors.append("✗ 缺少 <!DOCTYPE html> 声明")
    for tag in ["html", "head", "body", "style"]:
        o = len(re.findall(r"<%s[ >]" % tag, html, re.I))
        c = len(re.findall(r"</%s>" % tag, html, re.I))
        if o != c:
            errors.append("✗ <%s> 开合不平衡 (开%d/合%d)" % (tag, o, c))

    # 2) body 纯净(无属性)
    if re.search(r"<body[^>]", html, re.I):
        errors.append("✗ <body> 带属性, 须为纯 <body>")

    # 3) 禁用 CSS 变量
    for v in FORBIDDEN_CSS_VARS:
        if v in html:
            errors.append("✗ 使用了禁用 CSS 变量 %s" % v)

    # 4) 净化词 0 命中
    for w in PURGE_WORDS:
        if re.search(w, html):
            errors.append("✗ 命中净化词: %s" % w)

    # 5) 红线词 0 命中
    for w in RED_LINE_WORDS:
        if w in html:
            errors.append("✗ 命中红线词: %s" % w)

    # 5.6) 软文字门禁(内部过程叙述 0 命中) + 文献清单结构门禁(2026-09-22 同步自背调文献线)
    errors.extend(check_soft_text(html))
    errors.extend(check_literature_format(html, "literature"))

    # 6) DATA 数据逐篇校验
    m_data = re.search(r"const DATA\s*=\s*(\[.*?\]);", html, re.S)
    if not m_data:
        errors.append("✗ 未找到 const DATA=[...] 数据块")
        return errors
    try:
        arr = json.loads(m_data.group(1))
    except Exception as e:
        errors.append("✗ DATA 不是合法 JSON: %s" % e)
        return errors

    n = len(arr)
    # 6a) h2 篇数三处一致
    m_h2 = re.search(r"文章清单（共\s*(\d+)\s*篇）", html)
    if m_h2 and n and int(m_h2.group(1)) != n:
        errors.append("✗ h2 篇数(%s) ≠ DATA 篇数(%d)" % (m_h2.group(1), n))

    bad_zh = bad_corr_aff = bad_if = bad_abs = 0
    for it in arr:
        title = str(it.get("title", ""))
        zh = str(it.get("zh", ""))
        # 6b) 标题中译: 含中文且与原题不同
        if not zh or not CJK.search(zh) or zh.strip() == title.strip():
            bad_zh += 1
        # 6c) 通讯作者单位中译: 有单位就必须有中译
        aff = str(it.get("aff", "")).strip()
        aff_zh = str(it.get("aff_zh", "")).strip()
        if aff and not CJK.search(aff_zh):
            bad_corr_aff += 1
        # 6c-2) 摘要中译(rule 4): 有英文摘要就必须有中文翻译
        abs_en = str(it.get("abstract", "")).strip()
        abs_zh = str(it.get("abstract_zh", "")).strip()
        if abs_en and (not abs_zh or not CJK.search(abs_zh)):
            bad_abs += 1
        # 6d) IF 防编造: ifv 必须与映射表精确命中(键=journal_canon 规范名)
        ifv = it.get("ifv")
        if ifv is not None and ifmap is not None:
            key = str(it.get("journal_canon") or it.get("journal_full") or it.get("journal", "")).strip().upper()
            rec = ifmap.get(key)
            if rec is None:  # 规范化回退: 消除 JCR 键与 PubMed 全称的写法差异(逗号/撇号/连字符/AND vs &)
                nk = _norm(key)
                idx = _if_norm_index(ifmap)
                rec = idx.get(nk)
            if rec is None:  # 兼容未带 journal_canon 的旧报告: 退回 full 再试
                raw = str(it.get("journal_full") or it.get("journal", "")).strip().upper()
                raw = re.sub(r"\s*\([^)]*\)\s*$", "", raw).strip()
                if raw.startswith("THE "):
                    raw = raw[4:]
                raw2 = re.sub(r"\s+", " ", raw.replace(".", " ")).strip()
                rec = ifmap.get(raw2) or _if_norm_index(ifmap).get(_norm(raw2))
            if rec is None or rec.get("if") is None or float(rec["if"]) != float(ifv):
                bad_if += 1

    # 翻译率门禁：≤5% 未译（即 ≥95% 已译）即放行；超过 5% 才判不合格（与 SKILL.md「翻译≥95%」铁律一致）
    if bad_zh and n and bad_zh > n * 0.05:
        errors.append("✗ 标题翻译率 %d/%d 低于 95%%（缺失 %d 篇中译）" % (n - bad_zh, n, bad_zh))
    if bad_abs and n and bad_abs > n * 0.05:
        errors.append("✗ 摘要翻译率 %d/%d 低于 95%%（%d 篇缺 abstract_zh）" % (n - bad_abs, n, bad_abs))
    if bad_corr_aff:
        errors.append("✗ %d 篇通讯作者单位缺中文翻译" % bad_corr_aff)
    if bad_if:
        errors.append("✗ %d 篇 ifv 与 journal_if_map.json 不符(IF 编造红线)" % bad_if)

    # 6d-2) IF 口径标注: 有任何 ifv 就必须写明 JCR2025 年度值口径
    if any(it.get("ifv") is not None for it in arr):
        if "JCR2025" not in html:
            errors.append("✗ 缺少 IF 来源标注(JCR2025)")
        if "非文章发表当年" not in html:
            errors.append("✗ 缺少 IF 口径标注(须写明「非文章发表当年 IF」)")

    # 6d-3) 铁律5 补强: 全篇未标 IF 时, 若其中任何一篇的期刊其实在 IF 表内 → 判定为漏标。
    #       只查"表内能查到却没标"的情形, 不会误伤"确实全都不在表内"（如全是新刊/预印本）。
    if n and ifmap is not None and not any(it.get("ifv") is not None for it in arr):
        missed = 0
        for it in arr:
            key = str(it.get("journal_canon") or it.get("journal_full")
                      or it.get("journal", "")).strip().upper()
            if ifmap.get(key) or _if_norm_index(ifmap).get(_norm(key)):
                missed += 1
        if missed:
            errors.append("✗ 全篇未标影响因子, 但其中 %d 篇期刊在 IF 表内 → 富化漏标(铁律5: 每篇须标 IF)"
                          % missed)

    # 6e) PMID 进入链接: DATA 逐篇须有 pmid, 且 PubMed 链接模板存在
    no_pmid = sum(1 for it in arr if not str(it.get("pmid", "")).strip())
    has_pubmed_link = "pubmed.ncbi.nlm.nih.gov/" in html
    if n and (no_pmid or not has_pubmed_link):
        errors.append("✗ %d 篇缺 PMID 或 PubMed 原文链接模板缺失, 每篇须有进入链接" % no_pmid)

    # 6f) 召回审计(防静默漏检): 报告必须写明检索链路, 否则不许出报告
    #     关键词模式查 命中/取回/入选；人+单位模式查 取回/匹配/排除/待核
    is_person = any(it.get("match_status") for it in arr)
    m_audit = re.search(r"召回审计：(.{0,500}?)</div>", html, re.S)
    if n:
        if not m_audit or not m_audit.group(1).strip() or "__AUDIT__" in m_audit.group(1):
            errors.append("✗ 缺少召回审计行(禁止静默漏检)")
        else:
            aud = m_audit.group(1)
            if is_person:
                # 取回 始终必填
                if "取回" not in aud:
                    errors.append("✗ 召回审计行(人检索模式)缺少「取回」数据")
                if "匹配" in aud:
                    # 给了单位：应含 匹配/排除/待核
                    for kw in ("匹配", "排除", "待核"):
                        if kw not in aud:
                            errors.append("✗ 召回审计行(人+单位模式)缺少「%s」数据" % kw)
                else:
                    # 单搜人、未给单位：命中论文全部待核, 文案用"姓名命中(待核单位)"
                    if "待核" not in aud:
                        errors.append("✗ 召回审计行(单搜人模式)缺少「待核」数据")
            else:
                # 关键词模式: 命中/取回 始终必填; 入选 仅在用了 --if-gt 才要求
                for kw in ("命中", "取回"):
                    if kw not in aud:
                        errors.append("✗ 召回审计行(关键词模式)缺少「%s」数据" % kw)
                if "入选" in aud and "IF" not in aud:
                    errors.append("✗ 召回审计行(关键词模式)含「入选」但缺 IF 口径说明")

    # 6g) __ME__ 高亮一致性: 模式B 中, 本人已确认的论文(match/name_only)每篇恰1处 __ME__;
    #     excluded(同名未确认, 本人不在作者列表)无 __ME__, 计入排除篇数但不应高亮。
    #     仅在 DATA 数组内统计(避免 JS 源码字面量 "__ME__" 被误算)。
    if is_person:
        conf = sum(1 for it in arr if it.get("match_status") in ("match", "name_only"))
        me = sum(1 for it in arr if any(str(a).startswith("__ME__") for a in it.get("authors", [])))
        if me != conf:
            errors.append("✗ __ME__ 高亮数(%d) ≠ 已确认论文数(%d, 排除同名异者后), 每篇确认论文须恰1处" % (me, conf))

    # 7) 铁律门禁（修复 ③/④）：et al.(rule3) / 全面性优先(rule0) / 全量(rule1) / 全名优先(rule2.1)
    # 仅扫描 DATA 内容或报告声明性文字，不依赖脚本运行日志。
    # 7a) rule 3: 作者列表禁 et al.（仅扫 DATA authors，避免误伤报告正文"禁 et al."说明）
    bad_etal = 0
    for it in arr:
        for _a in (it.get("authors") or []):
            if re.search(r"et\s*al\.?", str(_a), re.I):
                bad_etal += 1
                break
    if bad_etal:
        errors.append("✗ %d 篇作者列表含 et al.（铁律3：作者须写全名，禁 et al.）" % bad_etal)

    # 7b) rule 0: 报告正文不得出现"已剔除/静默删除"等删文声称（全面性优先，报告不擅自删文）
    if "已剔除" in html:
        errors.append("✗ 正文出现「已剔除」（铁律0：全面性优先，报告不得声称已删文）")
    if re.search(r"未收录.{0,4}(删除|剔除)", html):
        errors.append("✗ 正文出现「未收录即删除/剔除」（铁律0/铁律5：未收录须保留并标 IF未收录，不得删除）")

    # 7c) rule 1 + rule 2.1：仅对模式 B（人检索, is_person）报告生效
    if is_person:
        if "第一作者" not in html or "通讯作者" not in html:
            errors.append("✗ 模式B报告未声明全量检索口径（第一作者[1AU]+通讯作者[CRP]合并, 铁律1）")
        if "全名检索" not in html:
            errors.append("✗ 模式B报告未声明全名检索（铁律2.1：须用客户提供全名, 禁降级缩写）")

    return errors


def main():
    if len(sys.argv) < 2:
        print("用法: report_validator.py <file.html> [--ifmap journal_if_map.json]")
        sys.exit(2)
    path = sys.argv[1]
    ifmap_path = ""
    if "--ifmap" in sys.argv:
        ifmap_path = sys.argv[sys.argv.index("--ifmap") + 1]
    else:
        cand = os.path.join(os.path.dirname(os.path.abspath(__file__)), "journal_if_map.json")
        ifmap_path = cand
    ifmap = load_ifmap(ifmap_path)
    if ifmap is None:
        # 失败关闭：IF 表是本包自带的，缺失说明安装不完整；此时跳过校验会让编造的 IF 蒙混过关
        print("❌ 未找到 IF 映射表(%s)，IF 防编造校验无法进行，拒绝放行。" % ifmap_path)
        print("   请确认 scripts/journal_if_map.json 与本脚本同目录，或用 --ifmap <路径> 指定。")
        sys.exit(1)
    errs = check(path, ifmap)
    if errs:
        print("❌ 验证未通过:")
        for e in errs:
            print("  " + e)
        sys.exit(1)
    print("✅ 验证通过: 结构闭合 / 净化词0 / 红线0 / 翻译达标 / 单位中译 / IF防编造 / PMID链接齐全")
    sys.exit(0)


if __name__ == "__main__":
    main()
