# -*- coding: utf-8 -*-
"""文献报告构建器：报告 = 本脚本 + 富化数据 JSON + 命令行参数。
HTML 骨架/样式引用/JS 渲染逻辑全部内嵌于本脚本，无任何外部模板文件依赖。

用法:
  python build_report.py --data articles_enriched.json \
      --topic "弓形虫入侵机制" --query "toxoplasma gondii AND invasion" \
      --window "2025/01/01 - 2026/09/06" --out report.html [--audit "..."]

输入 JSON: pubmed_search.py 的输出；每篇补齐
  zh(标题中译) aff_zh(单位中译) abstract_zh(摘要中译, 可选)
  ifv/ifq(IF表查得, 未收录为 null)；本人条目在 authors 中以 "__ME__" 前缀标记。

--audit 可选：缺省时自动采用数据内 audit_text（模式A/B 已内嵌），降低手抄出错。
"""
import argparse
import json
import re
import sys
import os
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from pubmed_search import journal_canon  # 复用检索脚本的规范化, 避免规则漂移
except Exception:                            # 检索脚本缺失时降级为简单大写
    def journal_canon(s):
        return re.sub(r"\s+", " ", (s or "").strip().upper()).strip()

POS_LABEL = {"first": "一作", "last": "通讯", "both": "一作+通讯", "mid": "中间作者"}
TPL = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__</title>
<style>__STYLE__</style>
</head>
<body>
<div class="wrap">
  <header class="hero">
    <h1>__TITLE__</h1>
    <div class="sub">时间窗：__WINDOW__</div>
    <div class="meta">数据来源：PubMed（NCBI E-utilities）｜数据截至 __ASOF__｜影响因子：JCR2025 年度值（journal_if_map.json；为 2025 年发布的年度 IF，非文章发表当年 IF；未收录期刊不显示指标）</div>
    <div class="meta">召回审计：__AUDIT__</div>
  </header>
  <div class="stats">
    <div class="stat"><b>__N__</b><span>文献总数</span></div>
    <div class="stat"><b>__NR__</b><span>研究论文</span></div>
    <div class="stat"><b>__NV__</b><span>综述</span></div>
    <div class="stat"><b>__NIF__</b><span>含影响因子(JCR2025)</span></div>
  </div>
  <div class="sec">
    <h2>文章清单（共 __N__ 篇）</h2>
    <div class="bar">
      <input id="kw" type="text" placeholder="搜索标题 / 期刊 / 作者…">
      <select id="fyear"><option value="">全部年份</option></select>
      <select id="ftype"><option value="">全部类型</option><option value="研究">仅研究</option><option value="综述">仅综述</option><option value="其他">其他</option></select>
      <select id="sort"><option value="yd">年份降序</option><option value="ya">年份升序</option><option value="t">标题</option></select>
    </div>
    <div id="list"></div>
  </div>
  <div class="ok">__NOTE__</div>
</div>
<script>
const DATA=__DATA__;
const esc=s=>String(s==null?"":s).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const P={"研究":["b-both","研究"],"综述":["b-last","综述"],"其他":["b-first","其他"]};
function card(it){
  const badges=[];
  badges.push('<span class="badge b-first" style="font-weight:700">'+esc(it.year)+'</span>');
  const pt=P[it.ptype]||P["其他"];
  badges.push('<span class="badge '+pt[0]+'" style="font-weight:700">'+pt[1]+'</span>');
  if(it.pos) badges.push('<span class="badge b-last" style="font-weight:700">'+esc(it.pos)+'</span>');
  if(it.ifv!=null) badges.push('<span class="if-badge">IF '+it.ifv+' · '+esc(it.ifq||"")+'</span>');
  else badges.push('<span class="badge b-first" title="该期刊未被 JCR2025 收录或不在本包 IF 表内，无法判定影响因子，文章予以保留">IF未收录</span>');
  const authors=it.authors.map(a=>a.startsWith("__ME__")?'<span class="me">'+esc(a.slice(5))+'</span>':esc(a)).join("、");
  const aff=it.aff_zh?('通讯作者单位：'+esc(it.aff_zh)+(it.aff?'<span class="aff-en">（'+esc(it.aff)+'）</span>':"")):(it.aff?esc(it.aff):"作者单位未收录");
  const abs=it.abstract_zh?('<div class="zh">'+esc(it.abstract_zh)+'</div>'):"";
  const doi=it.doi?'｜<a href="https://doi.org/'+esc(it.doi)+'" target="_blank" rel="noopener">DOI</a>':"";
  return '<div class="card" data-pmid="'+esc(it.pmid)+'">'
    +'<div>'+badges.join("")+'</div>'
    +'<h3>'+esc(it.title)+'</h3>'
    +'<div class="zh">'+esc(it.zh)+'</div>'
    +abs
    +'<div class="jmeta">'+esc(it.journal)+'｜<a href="https://pubmed.ncbi.nlm.nih.gov/'+esc(it.pmid)+'/" target="_blank" rel="noopener">PMID '+esc(it.pmid)+'</a>'+doi+'</div>'
    +'<div class="authors">'+authors+'</div>'
    +'<div class="aff">'+aff+'</div>'
    +'</div>';
}
function apply(){
  const kw=document.getElementById("kw").value.trim().toLowerCase();
  const fy=document.getElementById("fyear").value;
  const ft=document.getElementById("ftype").value;
  const so=document.getElementById("sort").value;
  let arr=DATA.filter(it=>{
    if(fy&&String(it.year)!==fy) return false;
    if(ft&&it.ptype!==ft) return false;
    if(kw){const blob=[it.title,it.zh,it.journal,it.authors.join("、"),it.aff,it.aff_zh].join(" ").toLowerCase();if(!blob.includes(kw))return false;}
    return true;
  });
  if(so==="yd") arr.sort((a,b)=>String(b.year).localeCompare(String(a.year)));
  else if(so==="ya") arr.sort((a,b)=>String(a.year).localeCompare(String(a.year)));
  else if(so==="t") arr.sort((a,b)=>a.title.localeCompare(b.title));
  const box=document.getElementById("list");
  box.innerHTML=arr.length?arr.map(card).join(""):'<div class="empty">没有符合条件的文章</div>';
}
(function(){
  const yrs=[...new Set(DATA.map(i=>String(i.year)))].sort().reverse();
  const fy=document.getElementById("fyear");
  yrs.forEach(y=>{const o=document.createElement("option");o.value=y;o.textContent=y;fy.appendChild(o);});
  ["kw","fyear","ftype","sort"].forEach(id=>document.getElementById(id).addEventListener("input",apply));
  apply();
})();
</script>
</body>
</html>
"""

REQUIRED = ["pmid", "year", "title", "journal", "journal_canon",
            "ptype", "authors", "aff", "doi"]
WARN = ["zh", "aff_zh"]


def _note_for(data, audit_text):
    """模式感知的说明文字（消歧口径 / 通讯作者口径）。"""
    is_person = any(it.get("match_status") for it in data)
    if is_person:
        match = sum(1 for it in data if it.get("match_status") == "match")
        name_only = sum(1 for it in data if it.get("match_status") == "name_only")
        excluded = sum(1 for it in data if it.get("match_status") == "excluded")
        return ("检索模式：人+单位（全名检索 + 单位收窄 + 逐篇消歧）。姓名命中合计 %d 篇："
                "其中 %d 篇身份确认（match，姓名+单位均命中）、%d 篇仅姓名命中待核单位（name_only，同名异者，须逐篇核实后排除）、"
                "%d 篇未确认（excluded）；按全面性优先原则均予保留，已在上文召回审计标注排除/待核合计篇数。"
                "本人以 <span class=\"me\">高亮</span> 标出，作者全名列出（禁 et al.）。"
                "全量检索口径：第一作者[1AU] + 通讯作者[CRP] 合并去重、一篇不落（rule 1）；"
                "以客户提供的全名检索，未降级为缩写（rule 2.1）。"
                % (match + name_only + excluded, match, name_only, excluded))
    # 关键词模式说明：仅陈述报告客观内容，不做无证据的"已核查/已剔除"断言。
    # 相关性核查是准入前的人工步骤（技能第 3 步），脚本只如实呈现检索结果，不擅自删文。
    return ("通讯作者口径：默认取末位作者及其单位（aff_src=last；唯一作者为 only；末位缺单位时回退首位作者并标记 first）。"
            "相关性核查为准入前的人工步骤（技能第 3 步），本脚本仅如实呈现检索结果，不对文献做机制学相关性判定；"
            "凡被检索命中的文献均予保留，仅在数据层标记待核/排除，报告不擅自删文（全面性优先, rule 0）。"
            "预印本（如 bioRxiv）不在 JCR 收录范围，不显示影响因子。")


def main():
    ap = argparse.ArgumentParser(description="文献报告构建器（无模板文件依赖）")
    ap.add_argument("--data", required=True, help="富化后的文章 JSON（pubmed_search.py 输出，兼容包裹/纯数组）")
    ap.add_argument("--topic", required=True, help="报告主题（hero 标题）")
    ap.add_argument("--query", default="", help="实际使用的 PubMed 检索式（留空则取数据内 query）")
    ap.add_argument("--window", required=True, help="时间窗显示文本, 如 2025/01/01 - 2026/09/06")
    ap.add_argument("--audit", default="", help="召回审计文本(可选, 缺省自动取数据内 audit_text)")
    ap.add_argument("--out", required=True, help="输出 HTML 路径")
    ap.add_argument("--asof", default=date.today().strftime("%Y-%m"), help="数据截至 YYYY-MM(默认当前月)")
    ap.add_argument("--css", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "report-style.css"))
    args = ap.parse_args()

    if not os.path.exists(args.data):
        sys.exit("✗ 数据文件不存在: %s\n  请先运行 pubmed_search.py --out <该路径> 生成检索结果" % args.data)
    try:
        with open(args.data, "r", encoding="utf-8-sig") as f:
            raw = json.load(f)
    except json.JSONDecodeError as e:
        sys.exit("✗ 数据文件不是合法 JSON: %s (%s)" % (args.data, e))
    # 兼容两种输入: 纯文章数组, 或 pubmed_search.py --out 输出的 {"query"/"audit_text":..., "articles":[...]} 包裹结构
    if isinstance(raw, dict):
        payload = raw.get("articles")
        if not args.query:
            args.query = raw.get("query", "") or raw.get("audit", {}).get("term", "")
        if not args.audit:
            args.audit = raw.get("audit_text", "")
    else:
        payload = raw
    data = payload if isinstance(payload, list) else None
    if not data:
        sys.exit("✗ 数据为空或非数组")

    for i, it in enumerate(data):
        if not it.get("journal_canon"):
            src = it.get("journal_full") or it.get("journal")
            if src:
                it["journal_canon"] = journal_canon(src)
        miss = [k for k in REQUIRED if k not in it]
        if miss:
            sys.exit("✗ 第 %d 篇(pmid=%s)缺必需字段: %s" % (i + 1, it.get("pmid", "?"), ",".join(miss)))
        w = [k for k in WARN if k not in it]
        if w:
            print("⚠ 第 %d 篇(pmid=%s)缺 %s, 已置空(验证器会拦截翻译不达标)" % (i + 1, it.get("pmid", "?"), ",".join(w)))
            for k in w:
                it[k] = None
        # pos 中文标签
        if it.get("pos") and it["pos"] in POS_LABEL:
            it["pos"] = POS_LABEL[it["pos"]]

    n = len(data)
    nr = sum(1 for it in data if it["ptype"] == "研究")
    nv = sum(1 for it in data if it["ptype"] == "综述")
    nif = sum(1 for it in data if it.get("ifv") is not None)

    if not os.path.exists(args.css):
        sys.exit("✗ 样式缺失: %s (包内 scripts/report-style.css 不可删)" % args.css)
    with open(args.css, "r", encoding="utf-8-sig") as f:
        css = f.read().strip()

    title = args.topic + "文献报告"
    # DATA 嵌进 <script> 前把 "<" 转成 \u003c，避免标题/摘要里出现 </script> 等破坏页面（JSON 语义不变）
    data_json = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
    html = (TPL
            .replace("__STYLE__", css)
            .replace("__TITLE__", title)
            .replace("__QUERY__", args.query or "（人+单位检索）")
            .replace("__WINDOW__", args.window)
            .replace("__ASOF__", args.asof)
            .replace("__AUDIT__", args.audit or "（未提供审计文本）")
            .replace("__NOTE__", _note_for(data, args.audit))
            .replace("__NR__", str(nr))
            .replace("__NV__", str(nv))
            .replace("__NIF__", str(nif))
            .replace("__N__", str(n))
            .replace("__DATA__", data_json))

    with open(args.out, "w", encoding="utf-8") as f:
        f.write(html)
    print("✓ 报告已生成: %s (%d 篇: 研究 %d / 综述 %d / 其他 %d, 含IF %d)" %
          (args.out, n, nr, nv, n - nr - nv, nif))

    # ---- 门禁（修复 ②：组装后不经核实验就出结果）----
    # 强制跑报告验证器；未通过则文件已生成供检查, 但退出码非0, 视为未达交付标准。
    try:
        from report_validator import load_ifmap as _load_ifmap, check as _validate_report
    except Exception as e:
        print("❌ 未找到 report_validator.py（须与本脚本同目录），门禁无法运行，拒绝放行: %s" % e)
        sys.exit(1)
    _ifmap_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "journal_if_map.json")
    _ifmap = _load_ifmap(_ifmap_path)
    if _ifmap is None:
        print("❌ 未找到 IF 映射表(%s)，门禁无法运行（IF 防编造缺失），拒绝放行。" % _ifmap_path)
        sys.exit(1)
    _errs = _validate_report(args.out, _ifmap)
    if _errs:
        print("❌ 门禁未通过（报告已生成供检查，但未达交付标准）:")
        for _e in _errs:
            print("  " + _e)
        sys.exit(1)
    print("✓ 门禁通过（结构闭合/净化词0/红线0/翻译达标/单位中译/IF防编造/PMID链接/召回审计/"
          "全名禁et al./全量retrieval口径声明），可交付。")


if __name__ == "__main__":
    main()
