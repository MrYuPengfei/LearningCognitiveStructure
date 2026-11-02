---
name: pubmed-literature-search
display_name: 科研文献搜索助手
display_name_en: PubMed Literature Search
description: "给出关键词、作者或作者单位与时间范围，在 PubMed 全量检索并生成可搜索筛选的文献报告 HTML：每篇标注影响因子（JCR2025 年度值，非文章发表当年 IF）、标题与通讯作者单位中文翻译、PMID 原文链接。附质量门禁，绝不编造。"
description_zh: "给出关键词、作者或作者单位与时间范围，在 PubMed 全量检索并生成可搜索筛选的文献报告 HTML：每篇标注影响因子（JCR2025 年度值，非文章发表当年 IF）、标题与通讯作者单位中文翻译、PMID 原文链接。附质量门禁，绝不编造。"
description_en: "Given keywords, an author, or author+affiliation together with a date range, run a full PubMed search and generate a searchable/filterable literature report HTML: each record is labeled with its impact factor (JCR2025 annual value, not the article's publication-year IF), Chinese translations of the title and corresponding-author affiliation, and a direct PMID link. A quality gate is enforced; nothing is fabricated."
version: 2.1.2
author: 科研民工小鑫
allowed-tools: Bash, Read, Write, Edit, Grep, Glob
---

# 科研文献搜索助手

输入「客户关键词 + 限制」或「作者全名 + 单位」，产出标准文献报告 `pubmed_<slug>_report.html`。
本技能自包含（样式/IF 表/检索脚本/验证器全在本包内），不依赖任何其他技能或外部服务，不污染源技能。

## 两种模式

| 模式 | 触发 | 检索入口 | 适用铁律 |
|---|---|---|---|
| **A 关键词** | 客户只给关键词 | `--query` | 4、5、6 强制；1（1AU+通讯合并）不要求，按正常关键词检索 |
| **B 人（单位可选）** | 客户给「某人」要其文献（可附单位收窄） | `--author` [+ `--affiliation`] | 1、2、3、4、5、6 **全部强制** |

- **只要给了 `--author`，无论是否带 `--affiliation`，都进入模式 B 并强制用全名检索**（rule 2 第一步：先用导师全名（拼音/汉字）检索）。`--affiliation` 仅在"要按单位收窄/消歧"时附加。
- 模式 B 自动执行 `("Name"[1AU] OR "Name"[CRP]) [AND "Unit"[AD]]`（role=both 默认，满足全量 1AU+通讯合并；无单位则不加 AD），并逐篇消歧。
- 报告与脚本对两种模式同一套代码、同一套验证器；差异仅由数据字段（`match_status`/`pos`/`__ME__` 前缀）驱动渲染。

## 铁律（违反即红线，一票否决）

对齐 pubmed-position-links 六铁律，按模式适用：

**4、5、6 任何时候强制（两模式皆然）**
- **4 翻译 ≥95%**：标题中译逐篇给出；有英文摘要时必须给 `abstract_zh` 中译；通讯/本人单位必须有中译。期刊名/专业缩写可保留英文。禁整段未译英文摘要。
- **5 IF 来源唯一且口径固定**：只用本包 `scripts/journal_if_map.json`（**JCR2025 年度版**全量 22643 刊），查表键 = 脚本输出的 `journal_canon` 规范名**精确命中**；未收录期刊（含预印本）不显示指标、打「IF未收录」徽章，绝不编造。禁用 OpenAlex、IF≈、影响因子约 等估算表述。报告必须标注「IF 为 JCR2025 年度值，非文章发表当年 IF」。
- **6 样式逐字节**：`<style>` 从 `scripts/report-style.css` 读取；`<body>` 为纯 `<body>`；禁用 `--ink/--sub/--brand` 等旧变量。

**模式 A 关键词**：rule 1（1AU+通讯合并）不要求，按正常关键词检索即可。

**模式 B 人（单位可选）（1、2、3 强制）**
- **1 全量**：检索该人近时间窗内**第一作者 + 通讯作者论文合并、一篇不落**（脚本用 1AU+CRP 合并去重）；严禁抽样。
- **2 消歧**：**先用全名检索（rule 2 第一步，单搜人即执行，即使不带单位）**，再用单位收窄。同名论文逐篇核对所属单位，标记：
  - `match` = 姓名命中 **且** 单位确认（token 级连续匹配；目标机构名后紧跟 `of` 者视为「X of Y」型**另一机构**，不算命中，如「浙江大学」不匹配「浙江工业大学」；仅当提供了 `--affiliation` 才可能）；
  - `name_only` = 仅姓名命中、单位未确认（含"未给单位"与"给了单位但不符"两类，均为同名异者，待人工核实）；
  - `excluded` = 检索命中但论文作者列表未找到该姓名（防御）。
  **全面性优先：所有论文保留不删，仅标记；报告注明排除/待核合计篇数。**
- **2.1 全名优先（2026-09-22 新增铁律）**：客户给的是**全名**，就用全名检索；客户给的只有**简写**，才用简写检索。**只要全名可得（客户直接提供、或可确认为其标准全名），就必须用全名检索，严禁降级为简写替代。**（全名与简写不得混用；客户给什么形式就按其形式检索，但有全名时一律以全名为准。）
- **3 作者全名**：作者列表写全名，禁 `et al.`；**本人用 `__ME__` 前缀高亮（每篇恰 1 处）**，渲染为 `<span class="me">`。`aff`/`aff_zh` 只写**本人名下单位**（不拼接其他作者单位）。

0. **全面性优先于标注（最高优先级）**：文献准确且全面第一位。IF 表未收录→文章保留、标「IF未收录」、严禁因查不到 IF 删除。召回链条必须完整可核对。

7. **门禁退出码 0 才可交付**：交付前必跑 `scripts/report_validator.py`。

## 文献清单格式铁律（2026-09-22 同步自背调文献线）

- **全量，禁压缩**：文献清单章节标题不得用「主要论文 / 重点论文 / 代表作 / 代表性 / 精选 / 核心论文 / 简要 / 节选 / 摘录 / 概要」等压缩/抽样词换马甲；用户要全量就要全量，删标题词 = 同罪。
- **DATA 驱动卡片，禁静态表**：文献清单必须 `const DATA=[...]` → `card()` 渲染进 `<div id="list">`，**严禁**把全量写成手写 `<table>` 行式罗列（年份/期刊/标题/PMID 表头那类）。
- **检索过程叙述不进报告**：报告任何位置不得出现「检索式 / hitCount / 并集去重 / 严重漏检 / 全量抓取 / AUTH:」等内部过程词（检索合规由脚本层门禁保证，报告只交付结果）。
- **结构门禁**：`check_literature_format`（在 `scripts/report_validator.py` 内，随 `python scripts/report_validator.py <报告.html>` 一并执行）已机械强制上述三项；存在文献清单章节时任一违规即 exit 1 不可交付。报告只产出 `literature` 一种类型，无需额外传 type 参数。

## 工作流

### 第 1 步 · 明确需求与模式
确认：① 关键词 或 作者全名+单位 ② 时间窗（必填）③ 其他限制（类型/语言/上限，默认 100、上限 500）。
- 只搜主题 → **模式 A**。
- 查「某人」的产出（无论是否带单位）→ **模式 B**：**必须给 `--author` 全名**，脚本强制用全名检索（拼音/汉字皆可）；单位仅作收窄/消歧用，可不给。向客户确认标准全名（中/英）。

### 第 2 步 · 检索

**模式 A（关键词）：**
```
python scripts/pubmed_search.py \
  --query "toxoplasma gondii AND bradyzoite" \
  --mindate 2025/01/01 --maxdate 2026/09/06 \
  --retmax 100 --out articles.json
```
- 客户给 IF 阈值时加 `--if-gt <阈值>`：脚本内查表筛选并打印召回审计（命中/取回/IF表命中/入选/已确定低于阈值/未收录）。`unknown_if` 文章必须保留、标「IF未收录」。

**模式 B（人，单位可选）：**
```
# 单搜人（无单位）：照样强制全名检索，命中论文全部进入"待核"桶，需人工逐篇核实单位
python scripts/pubmed_search.py \
  --author "Su Tao" \
  --mindate 2020/01/01 --maxdate 2026/09/06 \
  --role both --retmax 500 --out person.json

# 带单位收窄：命中且单位子串确认者标 match，其余标 name_only(待核)
python scripts/pubmed_search.py \
  --author "Su Tao" --affiliation "Shenzhen Institute" \
  --mindate 2020/01/01 --maxdate 2026/09/06 \
  --role both --retmax 500 --out person.json
```
- `--role`：both(默认,1AU+CRP合并) / first / last / all(FAU)。消歧后每篇带 `match_status`/`pos`/`me_idx`，本人条目在 `authors` 中以 `__ME__` 前缀标记。
- 脚本打印**消歧审计**（窗口内命中/取回/姓名+单位匹配 或 未给单位时的"姓名命中(待核单位)" / 仅姓名命中(同名异者,待核)/未确认/排除待核合计）。同名异单位论文保留并注明排除篇数。

### 第 3 步 · 核查、翻译与查表补齐
- **相关性核查（模式 A）**：逐篇抓摘要确认检索目标有实质角色；命名关联（CtIP=CtBP-interacting protein）、词形误命中（BARS/bars）、仅背景提及三类分别剔除/标注。
- **消歧复核（模式 B）**：**未给 `--affiliation` 时，全部命中论文均落入 `name_only`（待核）桶，必须逐篇核对单位后才能排除同名异者**；给了单位后，对仍为 `name_only`/`excluded` 的篇逐一核对单位，确认是否为同名异者（建议排除），并在交付说明记录排除篇数。
- 逐篇补齐：`zh`（标题中译）、`abstract_zh`（摘要中译，rule 4）、`aff_zh`（单位中译；模式 B 仅译本人单位）。`ifv/ifq` **两种模式均已由检索脚本自动查表填入**，只需复核（未收录期刊为 null，报告标「IF未收录」）。

### 第 4 步 · 组装报告（脚本参数化，无模板文件依赖）
```
python scripts/build_report.py \
  --data articles_enriched.json \
  --topic "弓形虫入侵机制" \
  --window "2025/01/01 - 2026/09/06" \
  --out pubmed_<slug>_report.html
```
- `--audit` **可选**：缺省自动采用数据内 `audit_text`（模式 A/B 已内嵌），降低手抄出错。
- HTML 骨架/样式/JS 渲染全部内嵌，无外部模板依赖；AI 只做第 3 步翻译与查表。
- **build_report 写盘后会自动跑第 5 步门禁并以退出码为准**：门禁未通过则退出码非 0、报告文件保留供检查但视为未达交付标准，不得直接交付。

### 第 5 步 · 门禁（退出码 0 才可交付）
```
python scripts/report_validator.py <报告.html>
```
校验：结构闭合、禁用变量/净化词/红线词 0、翻译≥95%（标题+摘要）、单位中译、IF 防编造、PMID 链接、**召回审计行存在且模式对应（关键词：命中/取回/入选；人检索：取回/匹配或姓名命中(待核)/排除/待核）**、`__ME__` 高亮数 = 已确认论文数（模式 B）。

## 文件结构

```
pubmed-search-assistant/
├── SKILL.md                          # 技能定义
├── references/
│   └── 文献报告模板规格.md            # 报告结构规格（人类可读, 组装以 build_report.py 为准）
└── scripts/
    ├── pubmed_search.py              # 检索（关键词 / 人(单位可选) 双模式, 零依赖）
    ├── build_report.py               # 报告构建器（骨架内嵌, 参数化）
    ├── report-style.css              # 样式母版（构建器读取, 禁改）
    ├── journal_if_map.json           # JCR2025 IF 全量映射表（紧凑数组, load_ifmap 兼容新旧格式）
    └── report_validator.py           # 报告质量门禁
```
脚本用 `os.path.dirname(__file__)` 定位同目录资源，解压到任意目录即可运行，无绝对路径/第三方依赖（Python 3.8+）。

## 边界
- 仅检索与报告生成，不代替客户做文献评价结论。
- 模式 B 消歧为「机器标记 + 人工复核」：脚本给出 match/name_only/excluded 与排除篇数，最终排除由人定，机器不擅自删文。
- PubMed 未收录内容（非生物医学、部分会议文献）不保证命中；`total_in_window` 大于 `retmax` 时提示收窄或提高上限。
