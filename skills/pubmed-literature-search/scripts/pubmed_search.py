#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pubmed_search.py — PubMed 文献检索（自包含，零第三方依赖）

两种模式：
  模式 A（关键词）: --query "crispr AND cancer"  [--if-gt 10]
      普通关键词检索，rule 1（1AU+通讯合并）不要求。
  模式 B（人，单位可选）: --author "Su Tao" [--affiliation "Shenzhen Institute"] [--role both|first|last|all]
      rule 2 强制第一步：只要给了 --author，必用导师全名（拼音/汉字）检索，即使不填 --affiliation。
      rule 1/3 强制：1AU+通讯合并全量、__ME__ 高亮本人。
      检索式: ("Name"[1AU] OR "Name"[CRP]) [ AND "Unit"[AD] ]（role=both 默认，满足全量；无单位则不加 AD）
      消歧: 逐篇核对目标作者姓名是否出现在指定作者位次。
            match     = 姓名命中 且 单位子串确认（仅当提供了 --affiliation 才可能）；
            name_only = 仅姓名命中、单位未确认（含"未给单位"与"给了单位但不符"两类，同名异者，待人工核实/排除）；
            excluded  = 检索命中但论文作者列表未找到该姓名（防御）。
            全面性优先：所有论文保留不删，仅标记；报告注明排除/待核篇数。

输出 JSON：每篇含 pmid/year/title/journal/journal_full/journal_canon/ptype/authors/aff/aff_zh/
  doi/abstract（英文原文）/zh/abstract_zh（由 AI 后续补齐）。
  模式 B 额外字段：me_idx / pos(first|last|both|mid) / match_status。
  authors 中本人条目加 "__ME__" 前缀（每篇恰 1 处），供报告 <span class="me"> 渲染。

铁律: IF 仅来自 scripts/journal_if_map.json（JCR2025）；未收录不显示、绝不编造。
"""
import argparse
import json
import os
import re
from datetime import datetime
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
SLEEP = 0.4  # 无 API key 限速 3 req/s


def http_get(url, api_key=None, retries=3):
    if api_key:
        sep = "&" if "?" in url else "?"
        url = url + sep + "api_key=" + urllib.parse.quote(api_key)
    last_err = None
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "pubmed-search-assistant/1.0"})
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read().decode("utf-8", errors="replace")
        except Exception as e:  # noqa: BLE001
            last_err = e
            time.sleep(1.5 * (i + 1))
    raise RuntimeError("请求失败(已重试%d次): %s ; 最后错误: %s" % (retries, url[:120], last_err))


def journal_canon(full_title):
    """期刊全称 -> JCR 查表规范名（大写；去副题；去地名括号；去冠词 The；句点转空格）。"""
    s = full_title.strip().upper()
    for sep in (" : ", " = ", ";"):
        if sep in s:
            s = s.split(sep)[0].strip()
    while True:
        s2 = re.sub(r"\s*\([^)]*\)\s*$", "", s).strip()
        if s2 == s or not s2:
            break
        s = s2
    if s.startswith("THE "):
        s = s[4:]
    s = re.sub(r"\s*\([^()]*$", "", s).strip()
    s = s.replace(".", " ")
    return re.sub(r"\s+", " ", s).strip()


def _norm(s):
    """IF 表回退查找用规范化: 大写、&→AND、去掉所有非字母数字字符。"""
    return re.sub(r"[^A-Z0-9]", "", s.upper().replace("&", " AND "))


def load_ifmap(path):
    """加载 IF 表, 兼容两种格式:
    - 旧: {name: {field: value, ...}}
    - 新(体积优化): {"_fields": [...], name: [v1, ...]} 数组按 _fields 顺序还原。
    """
    with open(path, "r", encoding="utf-8-sig") as f:
        raw = json.load(f)
    if not raw:
        return {}
    sample = next(iter(raw.values()))
    if isinstance(sample, dict):
        return raw
    fields = raw.get("_fields") or []
    return {k: dict(zip(fields, v)) for k, v in raw.items()
            if k != "_fields" and isinstance(v, list)}


def if_lookup(ifmap, canon):
    """精确命中优先, 回退到规范化命中; 都失败返回 None(未收录, 不得编造)。"""
    rec = ifmap.get(canon)
    if rec is not None:
        return rec
    idx = getattr(if_lookup, "_idx", None)
    if idx is None:
        idx = if_lookup._idx = {}
        for k, v in ifmap.items():
            idx.setdefault(_norm(k), v)
    return idx.get(_norm(canon))


if_lookup._idx = None


def _norm_tokens(s):
    """姓名拆词并排序（忽略大小写/标点），用于顺序无关比对。"""
    return sorted(t for t in re.sub(r"[^a-z ]", " ", s.lower()).split() if t)


def _name_matches(target, name):
    """鲁棒姓名比对：兼容 (1) 姓/名顺序颠倒 (Su Tao vs Tao Su)；(2) 名字缩写首字母
    (Su T vs Su Tao)。
    前缀匹配**仅当较短一方为单字母（缩写）时**才允许 —— 否则会把不同姓氏误配
    (Jian Li 会错配 Jian Lin / Jian Liu)，导致给错误的人加 __ME__ 高亮。"""
    tt, at = _norm_tokens(target), _norm_tokens(name)
    if not tt or not at:
        return False
    if tt == at:
        return True
    if len(tt) != len(at):
        return False
    for x, y in zip(tt, at):
        if x == y:
            continue
        if len(x) == 1 and y.startswith(x):   # 一方是缩写首字母
            continue
        if len(y) == 1 and x.startswith(y):
            continue
        return False
    return True


def _norm_aff(s):
    """机构名归一：小写、&→and、非字母数字转空格、压缩空白。"""
    s = (s or "").lower().replace("&", " and ")
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


# 目标机构名后紧跟这些词 → 属于「X of Y」型**另一所**机构（如 Zhejiang University of Technology 浙江工业大学）
_AFF_EXT_STOP = {"of"}


def _aff_matches(target, affs):
    """单位比对（rule 2 消歧）：target 须以**完整词序列**出现在某条 aff 中，
    且其后不是阻断词（of），避免把「浙江大学」误配到「浙江工业大学」这类同前缀异机构。
    宁可判为 name_only(待核) 也不误判为 match —— 假阳性会直接违反"同名异者须排除"。"""
    t = _norm_aff(target).split()
    if not t:
        return False
    m = len(t)
    for a in affs:
        at = _norm_aff(a).split()
        for i in range(0, len(at) - m + 1):
            if at[i:i + m] != t:
                continue
            nxt = at[i + m] if i + m < len(at) else None
            if nxt in _AFF_EXT_STOP:
                continue          # 「X of Y」= 另一机构，不算命中
            return True
    return False


def esearch(term, mindate, maxdate, retmax, sort, api_key):
    params = {
        "db": "pubmed",
        "term": term,
        "retmode": "json",
        "retmax": str(retmax),
        "sort": sort,
        "mindate": mindate,
        "maxdate": maxdate,
        "datetype": "pdat",
    }
    url = EUTILS + "/esearch.fcgi?" + urllib.parse.urlencode(params)
    data = json.loads(http_get(url, api_key))
    res = data.get("esearchresult", {})
    if res.get("error"):
        raise RuntimeError("esearch 错误: %s" % res["error"])
    ids = res.get("idlist", [])
    total = int(res.get("count", "0"))
    return ids, total


def _text(el):
    if el is None:
        return ""
    return "".join(el.itertext()).strip()


def parse_article(art, target=None, affiliation=None):
    """art: <PubmedArticle> Element -> dict。
    target/affiliation 非空时进入模式 B 消歧（逐作者位次+单位核对）。"""
    cit = art.find("./MedlineCitation")
    article = cit.find("./Article")
    pmid = _text(cit.find("./PMID"))

    journal_el = article.find("./Journal")
    journal = _text(journal_el.find("./ISOAbbreviation")) or _text(journal_el.find("./Title"))
    journal_full = _text(journal_el.find("./Title")) or journal
    jissue = journal_el.find("./JournalIssue/PubDate")
    year = _text(journal_el.find("./JournalIssue/PubDate/Year")) or _text(
        journal_el.find("./JournalIssue/PubDate/MedlineDate"))
    if not year:
        year = _text(article.find("./ArticleDate/Year"))

    title = _text(article.find("./ArticleTitle"))

    ptypes = [_text(t) for t in article.findall("./PublicationTypeList/PublicationType")]
    joined = ";".join(ptypes)
    if "Review" in joined:
        ptype = "综述"
    elif ("Erratum" in joined or "Retracted Publication" in joined
          or "Retraction of Publication" in joined or "Retraction Notice" in joined):
        ptype = "其他"
    elif "Journal Article" in joined:
        ptype = "研究"
    else:
        ptype = "其他"

    # 摘要（英文原文，多段合并）
    abs_parts = [_text(x) for x in article.findall("./Abstract/AbstractText")]
    abstract = " ".join(p for p in abs_parts if p) or ""

    author_nodes = []
    alist = article.find("./AuthorList")
    if alist is not None:
        author_nodes = alist.findall("./Author")

    authors_out = []
    me_idx = -1
    pos = None
    match_status = None
    aff_target = ""  # 模式 B：仅目标本人单位

    for idx, a in enumerate(author_nodes):
        coll = _text(a.find("./CollectiveName"))
        if coll:
            name = coll
        else:
            last = _text(a.find("./LastName"))
            fore = _text(a.find("./ForeName"))
            name = (fore + " " + last).strip() or last
        affs = [_text(x) for x in a.findall("./AffiliationInfo/Affiliation")]
        authors_out.append(name)

        if target and me_idx == -1 and _name_matches(target, name):
            me_idx = idx
            is_first = (idx == 0)
            is_last = (idx == len(author_nodes) - 1)
            if is_first and is_last:
                pos = "both"
            elif is_first:
                pos = "first"
            elif is_last:
                pos = "last"
            else:
                pos = "mid"
            aff_target = "; ".join(affs)
            if affiliation:
                # 有单位：token 级连续匹配 + 阻断「X of Y」型异机构（rule 2 消歧，防假阳性）
                hit = _aff_matches(affiliation, affs)
                match_status = "match" if hit else "name_only"
            else:
                # 单搜人、未给单位：无法用单位确认身份，所有姓名命中一律标
                # "name_only"(同名异者待核)，由人工逐篇核实单位后决定保留/排除(rule 2)。
                match_status = "name_only"

    if target:
        if me_idx == -1:
            match_status = "excluded"  # 检索命中但论文作者列表中未找到该姓名（防御）
        elif me_idx >= 0:
            authors_out[me_idx] = "__ME__" + authors_out[me_idx]

    # 模式 A：aff 取通讯作者（末位，缺则首位）单位；模式 B：aff 仅取本人单位
    aff, aff_src, corr = "", "none", ""
    if target:
        aff, aff_src = aff_target, "target"
    else:
        if author_nodes:
            pick = author_nodes[-1]
            aff_src = "last"
            if len(author_nodes) == 1:
                aff_src = "only"
            affs = [_text(x) for x in pick.findall("./AffiliationInfo/Affiliation")]
            if affs:
                aff = "; ".join(affs)
                corr = authors_out[-1] if authors_out else ""
            if not aff and author_nodes[0] is not pick:
                affs0 = [_text(x) for x in author_nodes[0].findall("./AffiliationInfo/Affiliation")]
                if affs0:
                    aff = "; ".join(affs0)
                    corr = authors_out[0] if authors_out else ""
                    aff_src = "first"
            if not aff:
                aff_src = "none"

    doi = ""
    for aid in art.findall("./PubmedData/ArticleIdList/ArticleId"):
        if aid.get("IdType") == "doi":
            doi = _text(aid)
            break

    rec = {
        "pmid": pmid,
        "year": year,
        "title": title,
        "journal": journal,
        "journal_full": journal_full,
        "journal_canon": journal_canon(journal_full),
        "ptype": ptype,
        "authors": authors_out,
        "corr": corr,
        "aff": aff,
        "aff_src": aff_src,
        "doi": doi,
        "abstract": abstract,
    }
    if target:
        rec["me_idx"] = me_idx
        rec["pos"] = pos
        rec["match_status"] = match_status
    return rec


def efetch(ids, api_key, target=None, affiliation=None):
    out = []
    B = 200
    for i in range(0, len(ids), B):
        batch = ids[i:i + B]
        url = EUTILS + "/efetch.fcgi?" + urllib.parse.urlencode({
            "db": "pubmed", "id": ",".join(batch), "retmode": "xml",
        })
        xml_text = http_get(url, api_key)
        root = ET.fromstring(xml_text)
        for art in root.findall("./PubmedArticle"):
            try:
                out.append(parse_article(art, target=target, affiliation=affiliation))
            except Exception as e:  # noqa: BLE001
                print("⚠ 解析失败(PMID未知): %s" % e, file=sys.stderr)
        if i + B < len(ids):
            time.sleep(SLEEP)
    return out


def build_person_term(author, affiliation, role):
    """构造模式 B 检索式。role: both(默认,1AU+CRP合并) / first / last / all(FAU)。"""
    if role == "all":
        aterm = '"%s"[FAU]' % author
    elif role == "first":
        aterm = '"%s"[1AU]' % author
    elif role == "last":
        aterm = '"%s"[CRP]' % author
    else:  # both
        aterm = '("%s"[1AU] OR "%s"[CRP])' % (author, author)
    if affiliation:
        return '(%s) AND "%s"[AD]' % (aterm, affiliation)
    return aterm


def _enrich_if(articles, ifmap):
    """为每篇补 IF（ifv/ifq），查表键 = journal_canon；未收录 → None（报告标「IF未收录」）。
    两种模式统一在此自动补，不再依赖人工富化步骤（rule 5：每篇标注影响因子）。"""
    for a in articles:
        rec = if_lookup(ifmap, a.get("journal_canon", ""))
        a["ifv"] = rec.get("if") if rec else None
        a["ifq"] = rec.get("jcr_quartile") if rec else None
    return articles


def _emit(result, args):
    """统一出口：有 --out 就落盘（**含 0 命中情形**），否则打印 stdout。
    修复：0 命中时过去直接 print+exit(0)，--out 被忽略、下游 build_report 拿不到文件。"""
    js = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        out_dir = os.path.dirname(os.path.abspath(args.out))
        if out_dir and not os.path.exists(out_dir):
            os.makedirs(out_dir, exist_ok=True)
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(js)
        print("✓ 命中 %s 篇(窗口内共 %s), 已写入 %s"
              % (len(result.get("articles") or []), result.get("total_in_window"), args.out),
              file=sys.stderr)
    else:
        print(js)


def main():
    ap = argparse.ArgumentParser(description="PubMed 文献检索（关键词 / 人+单位 两种模式）")
    ap.add_argument("--query", default="", help="[模式A] PubMed 语法检索式")
    ap.add_argument("--author", default="", help="[模式B] 导师/作者全名（拼音或汉字）")
    ap.add_argument("--affiliation", default="", help="[模式B] 单位（用于 AD 收窄 + 消歧）")
    ap.add_argument("--role", default="both", choices=["both", "first", "last", "all"],
                    help="[模式B] 检索位次: both=1AU+CRP合并(默认) / first / last / all=FAU")
    ap.add_argument("--mindate", required=True, help="起始日期 YYYY/MM/DD 或 YYYY")
    ap.add_argument("--maxdate", required=True, help="截止日期 YYYY/MM/DD 或 YYYY")
    ap.add_argument("--retmax", type=int, default=100, help="最大返回篇数(默认100, 上限500)")
    ap.add_argument("--sort", default="relevance", choices=["relevance", "pub_date"], help="排序")
    ap.add_argument("--out", default="", help="输出 JSON 路径(缺省打印到 stdout)")
    ap.add_argument("--api-key", default="", help="NCBI API key(可选, 提升限速)")
    ap.add_argument("--if-gt", type=float, default=0.0,
                    help="[模式A] IF 阈值筛选；给出后内嵌 IF 查表 + 召回审计（未收录一律保留）")
    args = ap.parse_args()

    # 模式判定
    mode = "person" if args.author else "keyword"
    if mode == "keyword" and not args.query:
        sys.exit("✗ 模式A 需 --query；模式B 需 --author")

    # 日期格式硬校验
    date_re = re.compile(r"^(\d{4})(/(\d{1,2})(/(\d{1,2}))?)?$")
    for name, val in (("--mindate", args.mindate), ("--maxdate", args.maxdate)):
        m = date_re.match(val.strip())
        if not m:
            print("❌ %s 格式非法: %r (须为 YYYY 或 YYYY/MM/DD)" % (name, val), file=sys.stderr)
            sys.exit(2)
        if m.group(2):
            try:
                datetime.strptime(val.strip().replace("/", "-"), "%Y-%m-%d" if m.group(4) else "%Y-%m")
            except ValueError:
                print("❌ %s 日期不存在: %r" % (name, val), file=sys.stderr)
                sys.exit(2)

    retmax = min(args.retmax, 500)
    api = args.api_key or None

    if_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "journal_if_map.json")

    if mode == "person":
        term = build_person_term(args.author, args.affiliation, args.role)
        ids, total = esearch(term, args.mindate, args.maxdate, retmax, args.sort, api)
        if not ids:
            result = {"mode": "person", "query": term, "mindate": args.mindate, "maxdate": args.maxdate,
                      "total_in_window": total, "fetched": 0, "articles": [],
                      "audit_text": "窗口内命中 %s｜取回 0" % total}
            print("── 消歧审计（必须核对，禁止静默丢弃）──", file=sys.stderr)
            print("   " + result["audit_text"], file=sys.stderr)
            _emit(result, args)
            sys.exit(0)
        articles = efetch(ids, api, target=args.author, affiliation=args.affiliation)
        _enrich_if(articles, load_ifmap(if_path))   # 模式B 也自动补 IF（rule 5）
        match = sum(1 for a in articles if a.get("match_status") == "match")
        name_only = sum(1 for a in articles if a.get("match_status") == "name_only")
        excluded = sum(1 for a in articles if a.get("match_status") == "excluded")
        audit = {
            "mode": "person", "target": args.author, "affiliation": args.affiliation,
            "role": args.role, "term": term,
            "total_in_window": total, "fetched": len(articles),
            "match": match, "name_only": name_only, "excluded": excluded,
            "exclude_total": name_only + excluded,
        }
        if args.affiliation:
            audit_text = ("窗口内命中 %s｜取回 %s｜姓名+单位匹配 %s｜仅姓名命中(同名异者,待核) %s｜"
                         "未确认 %s｜排除/待核合计 %s｜全量(第一作者[1AU]+通讯作者[CRP]合并)"
                         % (total, len(articles), match, name_only,
                            excluded, name_only + excluded))
        else:
            # 单搜人、未给单位：无法用单位确认身份，命中论文全部进入"待核"桶
            audit_text = ("窗口内命中 %s｜取回 %s｜姓名命中(待逐篇核实单位) %s｜未确认 %s｜"
                         "排除/待核合计 %s｜全量(第一作者[1AU]+通讯作者[CRP]合并)"
                         % (total, len(articles), match + name_only,
                            excluded, name_only + excluded))
        result = {"mode": "person", "query": term, "mindate": args.mindate, "maxdate": args.maxdate,
                  "total_in_window": total, "fetched": len(articles),
                  "audit": audit, "audit_text": audit_text, "articles": articles}
        print("── 消歧审计（必须核对，禁止静默丢弃）──", file=sys.stderr)
        print("   " + audit_text, file=sys.stderr)
        if name_only or excluded:
            tag = "（未给单位，须逐篇核实单位后排除）" if not args.affiliation else "（同名异单位/未确认）"
            print("   ⚠ 待核/未确认共 %d 篇%s：须在报告中注明排除篇数，建议人工逐篇核实单位后排除"
                  % (name_only + excluded, tag), file=sys.stderr)
    else:
        ids, total = esearch(args.query, args.mindate, args.maxdate, retmax, args.sort, api)
        if not ids:
            result = {"query": args.query, "mindate": args.mindate, "maxdate": args.maxdate,
                      "total_in_window": total, "fetched": 0, "articles": [],
                      "audit_text": "窗口内命中 %s｜取回 0" % total}
            _emit(result, args)
            sys.exit(0)
        articles = efetch(ids, api)
        _enrich_if(articles, load_ifmap(if_path))   # 模式A 也统一补 IF（rule 5）
        result = {"query": args.query, "mindate": args.mindate, "maxdate": args.maxdate,
                  "total_in_window": total, "fetched": len(articles), "articles": articles}

        # ---------- 模式A: 召回审计（始终输出, 禁止静默漏检） ----------
        audit_text = "窗口内命中 %s｜取回 %s" % (total, len(articles))
        if args.if_gt > 0:
            selected, below, unknown_if = [], [], []
            for a in articles:
                ifv = a.get("ifv")   # 上面已统一补好，这里只做阈值筛选
                if ifv is None:
                    unknown_if.append(a)
                elif ifv > args.if_gt:
                    selected.append(a)
                else:
                    below.append(a)
            audit = {
                "if_threshold": args.if_gt, "total_in_window": total,
                "fetched": len(articles), "if_map_hit": len(articles) - len(unknown_if),
                "if_map_miss": len(unknown_if), "selected": len(selected),
                "below_threshold": len(below),
                "unknown_if_journals": sorted({a["journal_canon"] for a in unknown_if}),
            }
            result["audit"] = audit
            result["selected"] = selected
            result["unknown_if"] = unknown_if
            audit_text = ("窗口内命中 %s｜取回 %s｜IF表命中 %s｜IF>%s入选 %s｜已确定低于阈值 %s｜"
                         "IF表未收录 %s（保留, 不标IF）" % (total, len(articles), audit["if_map_hit"],
                         args.if_gt, len(selected), len(below), len(unknown_if)))
            result["audit_text"] = audit_text
            print("── 召回审计（必须核对，禁止静默丢弃）──", file=sys.stderr)
            print("   " + audit_text, file=sys.stderr)
            if unknown_if:
                print("   ⚠ 以下期刊未收录于 IF 表：其 %d 篇文章须保留并标「IF未收录」，不得删除："
                      % len(unknown_if), file=sys.stderr)
                for j in audit["unknown_if_journals"][:20]:
                    print("     -", j, file=sys.stderr)
        else:
            result["audit_text"] = audit_text
            print("── 召回审计（必须核对，禁止静默丢弃）──", file=sys.stderr)
            print("   " + audit_text, file=sys.stderr)
        if total > len(articles):
            print("   ⚠ 取回数少于窗口内命中数，请提高 --retmax 后重跑", file=sys.stderr)

    _emit(result, args)


if __name__ == "__main__":
    main()
