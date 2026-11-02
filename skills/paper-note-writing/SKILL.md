---
name: paper-note-writing
description: 为整库已解析论文批量撰写结构化中文研究笔记（一~十一节 + 公式汇总附录 + 图表索引），以滚动派单维持固定并发，并只以磁盘落盘为完成判据。适用于几十到上千篇论文需要逐篇出深度笔记、且要求公式全收、不得编造、可断点续跑的长期批量任务。当用户提到「论文笔记」「文献笔记」「给每篇论文写笔记」「批量精读」「研究笔记流水线」时使用。
agent_created: true
---

# 论文研究笔记批量化撰写

## 用途

把 `<库根>` 下已由 MinerU 解析好的论文（`<STEM>_markdown/markdown.md`）逐篇变成中文深度笔记，输出到与解析目录平级的 `<STEM>/<citekey>-<中文译名>.md`。

这不是"写一篇笔记"的技能，而是**把几百上千篇笔记跑完**的技能。难点不在写作质量，在于：派单不打爆 RPC、并发不撞天花板、完成判据不被代理的自述报告骗到、断点可续。

## 前置条件

- 每篇论文已有 `<库根>/<STEM>_markdown/markdown.md`（没有就先用 `mineru-paper-parse` 解析）
- `<库根>/_pipeline/` 下已就位：
  - `NOTE_GUIDE.md` —— 写作规范（本 skill 的 `references/note-guide.md` 是模板）
  - `WRITER_BRIEF.md` —— 子代理简报（本 skill 的 `assets/writer-brief-template.md` 是模板）
  - `status.py` / `refill.py` / `audit.py` —— 本 skill 的 `scripts/`

## 目录约定

```
<库根>/
├── <STEM>_markdown/markdown.md     输入：解析全文
├── <STEM>_markdown/images/         输入：图片切图（含未在正文引用的公式/表格切图）
├── <STEM>/<citekey>-<中文译名>.md   输出：笔记（目录下只放这一个 .md）
└── _pipeline/
    ├── NOTE_GUIDE.md  WRITER_BRIEF.md
    ├── inflight.txt                在途：每行 `STEM<TAB>citekey`
    ├── true_pending.txt            待写清单
    └── batches/batch_<seq>.json    批次文件：{"entries":[{"i":0,"stem":"…","citekey":"…"}]}
```

**citekey 规则（两种情形，务必分清）**：

- STEM 以**字母**开头（`Chen2020SimpleDeep-...`）→ citekey = 第一个 `-` 之前的部分
- STEM 以**数字**开头（`1609.02907_Kipf-Welling_GCN`）→ **整个 STEM** 就是 citekey，不要按连字符截断

## 核心工作流

### 第 1 步：定规范（只做一次，但决定全部产出质量）

把 `references/note-guide.md` 复制成 `<库根>/_pipeline/NOTE_GUIDE.md`，把 `assets/writer-brief-template.md` 复制成 `WRITER_BRIEF.md`，按课题替换占位。

规范里必须写死的三件事：

1. **章节模板**：一、基本信息 → 二、一句话概括 → 三、研究问题与动机 → 四、记号与预备知识 → 五、方法 → 六、理论分析 → 七、实验设计 → 八、实验结果 → 九、相关工作 → 十、结论 → 十一、批判性评价 → 附录 A 公式汇总 → 附录 B 图表索引
2. **公式全收**：行内 `$...$`、独立 `$$...$$`、保留 `\tag{n}`、逐符号解释、附录 A 列全表
3. **篇幅口径**：按"典型 4000–12000 字、宁详勿略"写。**写"不设上限"而不是"≥6000 字"** —— 把它设成硬门槛会让审计把大量合规产出误判为缺陷（见「审计判据」）

### 第 2 步：生成批次并把 STEM 落盘（不要自己转发目录名）

```bash
cd <库根>
export NOTE_BASE=$PWD
python _pipeline/refill.py 16        # 清理已完成/幽灵条目 + 按空槽生成批次
```

`refill.py` 输出末尾会有 `BATCH <path>`。批次文件内容形如：

```json
{"batch":"batch_20261101_205523","entries":[{"i":0,"stem":"…","citekey":"…"}]}
```

**为什么必须走批次文件**：STEM 常长达 90–110 字符，终端打印会被宽度截断。曾把 `print(f"{s[:66]:68}")` 的截断串当成真实 STEM 派发，一次产出 3 条"幽灵在途"（目录根本不存在）。**任何情况下都不要手工转录长 STEM**，让子代理自己从批次文件按索引读。

### 第 3 步：派单（prompt 必须短）

每个子代理的 prompt 固定三行，**不要**把规范全文塞进去：

```
第一步：完整读取 <库根>\_pipeline\WRITER_BRIEF.md。
第二步：读取 <库根>\_pipeline\batches\<batch>.json，取其中 i=<N> 的条目，得到 stem 与 citekey 作为参数。
第三步：严格按简报执行，完成该篇论文的中文研究笔记。
完成后仅回复一行：OK <STEM> <字数>
```

规范全文进 prompt 会触发 `400 [PacRpcClient] request timed out` 与 `429 频率限制`；外置成简报文件后，连续 16 次派发零超时。

并发上限由 `NOTE_CONCURRENCY`（默认 16）控制。用后台方式启动（`run_in_background`），不要让主代理同步等——每篇 10–30 分钟，同步等会把回合拖死。

### 第 4 步：只认磁盘，不认报告

```bash
python _pipeline/status.py            # 摘要：已写/待写/在途/幽灵/进度
python _pipeline/status.py --list     # 加在途明细与待派清单
```

`status.py` 的完成判据是"该目录下存在 > 500B 的 `.md`"，与代理说什么无关。**代理报告完成不算完成，代理报失败也不一定失败** —— 实测有代理报"RPC timeout"但文件其实已落盘。

### 第 5 步：滚动作业直到清零

```bash
python _pipeline/refill.py 16   # 清理 + 补位
# 按 BATCH 派发 → 等待 → 再 refill → 再派发
```

每轮只补"空出来的槽"，不要一次 plan 超过剩余槽位。重复直到 `status.py` 的待写为 0。

### 第 6 步：终审

```bash
python _pipeline/audit.py                # 摘要
python _pipeline/audit.py --verbose      # 列出问题明细
python _pipeline/audit.py --fix-img      # 自动补拷缺失图片
```

## 关键坑位

| 现象 | 根因 | 处置 |
| --- | --- | --- |
| `400 request timed out` / `429 频率限制`，派单大面积失败 | 单个 prompt 塞了完整规范（数 KB） | 规范外置到 `WRITER_BRIEF.md`，派单只给 3 个参数 |
| `20 of 20 agents running`，新派单被拒 | 框架并发硬上限 20，且**已完成的代理仍占槽位** | 对已完成代理发 `shutdown_request` 释放；`TaskStop` 对 completed 状态无效（报 "not running"） |
| 频繁撞并发上限 | 每轮都新建代理 | 用 `SendMessage` 给已完成代理**续派**新论文：不占新槽位，且复用其已加载的规范上下文 |
| 在途表里出现目录不存在的条目 | 用了截断的显示串当 STEM | 一律走批次文件；`refill.py` 会自动剔除幽灵条目 |
| 全库审计报「329 篇无 H1」等大面积误报 | 按 `os.listdir` 顺序取第一个 `.md`，读到了 `_appendixA_table.md` 之类中间产物 | 用 citekey 前缀定位笔记文件（`audit.py` 已内置） |
| 审计报坏图链接，但图片其实都在 | 笔记正文用反引号举了 `![](images/xxx.jpg)` 的语法例子 | 匹配图片前先剥掉代码块与行内代码（`audit.py` 已内置） |
| 审计把大量笔记判为"篇幅不足" | 把"典型 4000–12000"误当"≥6000 硬门槛" | 审计阈值对齐规范原文：<4000 记不足、4000–6000 仅提示 |
| 代理凭空编造一篇不存在的论文 | 派单给了猜出来的 STEM | `WRITER_BRIEF.md` 里加硬性前置检查：输入文件不存在就立即回 `OK <STEM> 0` 并说明，绝不补写 |
| 同一篇被重复写 | 失败重试与正常派单撞车 | 简报里的防重复守卫：输出文件已存在且 >1KB 就直接返回，不覆盖 |
| 图片引用了却打不开 | 图片在 `_markdown/images/` 但没拷到笔记目录 | `audit.py --fix-img` 自动补拷 |
| 笔记明明写了，`status.py` 却仍报"在途" | 子代理把输出写进了**短名目录**（`Lin2018SGD/`）而非 STEM 全名目录（`Lin2018SGD-Don't-Use-…/`） | `status.py` 只按 `<STEM>/` 找文件。简报里要强调"用完整 STEM 建目录，不能只写 citekey"；发现后 `os.rename` 迁移，并全库排查"目录名与解析 STEM 不符" |
| 代理自述"内存不足/无法完成"，但文件其实已在 | 代理的失败自述不可靠，且可能写错位置 | 凡代理报失败，**先 `ls` 目标目录（含短名变体）再判断**；`TaskOutput` 报 "no running background tasks" 只说明进程已退，不说明没产出 |

## 质量红线（写进规范、写进简报、也写进终审）

1. **不得编造**：数字、引用、实验结果必须与原文一致；未说明就写"原文未明确说明"
2. **原文疑点如实标注，不自行"修正"**：公式残缺、编号不一致、数量链不闭合、定理无证明 —— 标注位置并说明
3. **公式一个都不能漏**：这是硬性项，附录 A 要能逐条对上原文编号
4. **图片只引用真实存在的文件**，附录 B 仍按原文登记图表编号
5. **不得整段照抄英文**，必须中文复述

## 可选的加固手段

- **OCR 交叉核验**：MinerU 会把一行公式拆成两块、把 `θ` 认成 `0`、把表头串行。对关键论文用 `pdftotext -layout` + 300dpi 页面图核对，按原图还原并在文中标注"MinerU OCR 拆分有误，已按原图更正"。
- **著录核对**：文件名与正文可能不是同一篇（实测遇到文件名挂 A 作者、正文实为 B 论文的情况）。发现时按正文著录，并在笔记「一、基本信息」里注明原文件名。
- **看板**：把 `status.py` 的输出渲染成 HTML 进度页，便于长跑时观察。

## 资源

- `scripts/status.py` — 磁盘真相核验：已写/待写/在途/幽灵/进度；`--list` 列明细
- `scripts/refill.py` — 清理在途表（已完成 + 幽灵）+ 按空槽生成批次文件（`BATCH <path>`）
- `scripts/audit.py` — 全库审计：结构、篇幅、坏图、残留临时文件；`--fix-img` 自动补图
- `references/note-guide.md` — 写作规范模板（章节结构、公式要求、语言要求、质量红线）
- `assets/writer-brief-template.md` — 子代理简报模板（含防编造与防重复守卫）
