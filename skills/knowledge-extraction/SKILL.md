---
name: knowledge-extraction
display_name: 知识萃取
display_name_en: Knowledge Extraction
description: This skill should be used when a user wants to extract reusable methodology from their tacit experience, successful cases, or expert practices. It applies when the user asks to "萃取这个岗位的精华经验 / 经验萃取 / 把成功案例归纳成方法论 / 最佳实践提炼 / 岗位 SOP 沉淀 / 案例开发 / 高手做法提炼 / 踩坑复盘 / 老员工经验复制 / KT (Knowledge Transfer)". It guides the user through a 5-stage workflow (task decomposition → pain-point mining → experience extraction → model construction → deliverable generation) to turn hidden expertise into transferable, structured knowledge, with built-in quality checks across the "道-法-术-器-坑" layers.
description_zh: 把隐性经验、成功案例、高手做法，提炼成可复制的方法论、SOP 与培训课纲
description_en: Turn tacit experience, successful cases and expert practices into reusable methodology, SOPs and training outlines
version: 1.0.0
author: 张老师
agent_created: true
---

# Knowledge Extraction (知识萃取)

A guided workflow that turns tacit experience into structured, transferable methodology.

## What this skill enables

When a user wants to crystallize their hands-on expertise — whether it's "the way our top salesperson closes deals", "the unspoken steps that make our onboarding smooth", or "the lessons learned from this failed project" — this skill walks them through the **5-stage extraction workflow** and helps them produce the deliverable form they actually need (SOP, training outline, case study, or working model).

The skill does not just dump a template; it asks the right questions at each stage so the user discovers insights they didn't know they had.

## When to trigger

Activate this skill when the user's request matches one or more of these patterns:
- Phrases containing 萃取 / 提炼 / 归纳方法论 / 形成 SOP / 沉淀经验
- "把高手的做法整理出来，让大家都能用"
- "我做了 XX 好几年，想把经验系统化"
- "这次复盘一下，看能形成什么方法论"
- "我要给新人做培训，需要把岗位经验写出来"
- "KT" / "Knowledge Transfer" / "best practice capture"

Do **not** trigger this skill if:
- The user only wants to **write a single document** (no underlying methodology extraction) → handle as normal doc creation.
- The user wants to **summarize or translate** an existing document → no extraction needed.

## Workflow Decision Tree

```
User intent identified
    │
    ├── 1. Confirm scope & deliverable type (SOP / training / case / model)
    │       → see references/methodology.md §1
    │
    ├── 2. Stage 1: Decompose tasks (MECE)
    │       → see references/methodology.md §2
    │       → output: 一级任务清单 + 二级任务清单
    │
    ├── 3. Stage 2: Mine pain points (难点 / 痛点 / 关键点)
    │       → see references/methodology.md §3
    │       → output: 任务×三点分析表
    │
    ├── 4. Stage 3: Extract experience (显性 vs 隐性 forks here)
    │       → explicit: What-How questions
    │       → tacit: Magic-wand questions / STAR / 高峰访谈
    │       → THEN validate: +1-2 more positive cases (find commonality) + 1 negative case (find boundary); if user can't produce more, tell them "案例越多，萃取的越扎实" and proceed
    │       → IF user can't recall ANY case (operational/process-type experience): fall back to "没有具体案例，就描述一下你日常都是如何开展这项工作的" (see below)
    │       → FINALLY after each case, ask 案例反思三问 (see below)
    │       → ALSO harvest tangible assets: ask for 模板 / 工具 / 表单 / 清单 and have the user paste them in (see below)
    │       → see references/methodology.md §4
    │
    ├── 5. Stage 4: Build the model
    │       → 8 建模法 (formula / 2D-matrix / hierarchical / parallelism / acronym / initial-letter / mnemonics / three-character-classic)
    │       → MUST offer 2-3 candidate models built with DIFFERENT methods from the SAME user material; user picks / edits / combines
    │       → see references/model-builder.md (总则) + references/methodology.md §5
    │
    ├── 6. Stage 5: Generate deliverable
    │       → fork based on user's stated output:
    │          • SOP / 操作手册 → references/templates.md §SOP
    │          • 培训课程 / 课纲 → references/templates.md §Course
    │          • 案例 / 高峰体验 → references/templates.md §Case
    │
    └── 7. Quality check (道法术器坑) — MANDATORY & VISIBLE
        → run the 5-layer check AND output a 五层自检报告 in the CHAT reply (✅道/法/术/器/坑 + 综合评分 + 待优化项)
        → 不要只把五层表塞进交付文件里就算完——用户必须一眼看到自检结果
        → see references/quality-checklist.md
```

For each stage: ask the questions listed in the corresponding references file, then summarize the user's answers into the stage's output template before moving to the next stage. Don't skip a stage — even experienced practitioners appreciate the rigor.

**Pacing rule:** Complete stage-by-stage, not all at once. After each stage, recap the output and confirm before proceeding. The user often revises earlier answers when they see the structure emerging.

## Core principles to apply throughout

- **提问引导，不要替用户回答。** 这是用户立下的硬规则。每个 stage 默认走 Q&A：先抛 3-5 个关键问题让用户自己答，再把他/她的回答结构化整理成模板。**用户没说"请直接写出来"之前，不输出断言、结论、表格内容**。这一条比什么都优先——它决定了萃取是否真"长出来"。
- **道法术器坑**: Every extraction should reach all five layers — 道 (essence), 法 (rules), 术 (techniques), 器 (tools), 坑 (caveats). Most users stop at 术; push for 器 and 坑. **器 不只是"用什么工具"，还要主动讨要用户手上的现成资产（模板 / 表单 / 清单）并让对方粘贴进来——那是已经沉淀好的显性知识，复用成本最低。**
- **显性 / 隐性 fork**: Ask "can you write this down on paper, or is it a feel / instinct?" — what they think vs what they do often diverge, and that's where the gold is.
- **做了 / 做好 / 做到极致**: Three granularities. Align expectations before extracting — "do" ≠ "do well" ≠ "do at expert level."
- **MECE & 动宾结构**: Both for tasks (≤10 chars each) and for the methodology (mutually exclusive, collectively exhaustive).

## Question-led workflow contract

**Applies to all 5 stages — including Stage 1 task decomposition.** Never pre-list tasks for the user. The agent's role is question-setter and mirror, not author.

### Onboarding rule: start easy, deepen gradually

**不要一次性甩 5 个大问题**。开场只问**一个最容易回答的轻问题**，让对方开口；后续再根据回答渐进深化。开场前可在心里备好追问路径，但**每次只问一层**。

两种推荐开场路径（任选其一）：

1. **开放式问（轻问题起步）**——适合能结构化表达的用户。
   - 例子："你与甲方沟通一般有哪些环节？"
   - 例子："你做 XX 这件事一般会经过哪几步？"
   - 例子："如果让你教一个新同事做这件事，你会先讲什么、再讲什么？"
   - 然后根据用户的回答，自然引出：哪些环节最关键 / 哪个环节最让你头疼 / 那个环节具体怎么做的——一层层深入。

2. **案例切入（讲故事起步）**——适合不善抽象、但有具体经验的用户。
   - "能描述一次和客户沟通的具体经历吗？从头到尾，越具体越好。"
   - 拿到故事后，**AI 帮用户拆解环节、归纳方法**，但拆出来的环节要回到用户那里**确认是否就是他心里的拆法**——而不是直接当作定论。

**何时用哪个**：用户能结构化表达 → 路径 1；用户更习惯讲故事 / 怕抽象 → 路径 2。两个都不是强制的，是默认起点；如果用户一上来就给了大量素材，按素材自由组合即可。

### Stage-by-stage rule

对每个 stage：

1. **按本 stage 的深度问 1-3 个问题**（按上面 onboarding rule 控制颗粒度）。
2. **等**用户回答。**不替填模板**。
3. **把用户回答镜像回本 stage 的输出模板**，请他/她确认或修订。
4. **确认后才进下一个 stage**。

例外（用户可用一句话切换到填空模式）：
- "直接给我模板 / 我口述你整理 / 帮我写出来"
- 用户回答极简（如只回 1-2 字），可以再多问 1-2 个澄清题，依然**不要替答**。

### Stage 1 起步模板（替代任何"AI 直接列任务清单"的做法）

按路径 1 起步：
1. "你与 XX 沟通一般会经过哪几个环节？想到几个说几个，不用很整齐。"

按路径 2 起步：
1. "能描述一次你最近和 XX 沟通的具体经历吗？从头到尾，按时间顺序，越具体越好。"

收完第一层回答后，再判断要不要问"哪些环节最关键 / 哪个最让你头疼 / 那次卡在哪里"——不要在第一问前就预设好追问清单。

### 案例反思三问（Stage 3 收尾必做，用户经验）

**描述完一个案例还不算完。** 每个核心案例（尤其主案例与反例）听完经过后，必须补问这 3 问——它们把萃取从"复述经历"推进到"反思经历"，是"做了 → 做好 → 做到极致"的跃迁入口：

1. **成功的关键点是什么？** —— 让用户自己**归因**。做了什么 ≠ 为什么成；他说出的"关键点"往往就是方法论的**道与法**。
2. **如果再做一遍，哪里需要改进？** —— 挖出**坑 / 优化点**，直接可用于 SOP 的"坑"层。
3. **过程中最挑战的是什么？除了这个案例中的做法，还可以采取哪些举措应对？** —— ① 识别**真瓶颈**；② **扩展招式库**（一个挑战挖出 2-3 条备选路径，避免路径依赖）。这是**扩量器**：可轻推"还有别的思路吗"，但不硬凑。

> 三问依然是**提问**，不是 AI 自答——继续遵守"提问引导，不替用户断言"的总规则。详见 references/methodology.md §4。

### 无案例兜底（Stage 3，用户经验）

**当对方想不出案例时，不要停,也不要判他"没经验"——换一种问法。** 很多课题本身是操作性 / 流程性的（"如何做体系规划""如何设计一个方案""如何搭建指标体系"），这类经验以"日常做法"而非"具体事件"的形式存在。

一旦用户答不出案例，立刻切到：

> **"如果没有实际案例，就描述一下你日常都是如何开展这项工作的？"**

然后沿"流程"往下问：从哪一步开始 → 平时走哪几步 → 有无固定模板 / 框架 → 每次特别注意哪里 → 做到什么程度才算可交付。用户讲完流程后，可再请他"就按这个流程，回忆最近一次做的时候哪一步最费脑"，往往能把流程描述重新变回案例素材。

反思三问问法微调：①"这套做法里最关键的是哪一步？"②"再优化一次会改哪里？"③"这套做法最怕遇到什么情况？还能怎么应对？"

> **判定**：案例型经验 → STAR / 高峰访谈；操作型经验 → 日常流程描述 + 步骤复盘。产出物**同等有效**，只是入口不同。

### 实物资产采集：模板 / 工具 / 表单（Stage 3 必做，用户经验）

**要的不仅是"脑子里的做法"，还有"手上现成的资产"。** 模板、工具、表单、清单、话术卡、检查表是**已经沉淀过的显性知识**，属于"器"层最硬的素材——新人拿到就能用。只挖口头描述、不收这些资产，等于丢掉最容易复用的部分。

**时机**：① 用户一提到"我们有固定的表 / 有个模板"→ **立刻顺势要**；② Stage 3 收尾**必问一次**兜底。

**话术**：
> "做这件事，您平时有没有现成的**模板 / 工具 / 表单 / 清单**？如果有，**直接粘进来**——这是萃取成果里最有价值的部分之一，新人拿到就能用。"
> （对方说"很粗"→"粗也没关系，先粘过来，我们一起看它为什么这么设计。"）

**收到后三步加工（不要只是收录）：**
1. **入"器"层**：原文进交付物附录，标注"可直接复用"；区分"**可直接拿走用**"（模板）与"**需理解才能用**"（判断标准）。
2. **模板解剖（最值钱）**：栏目 = 他的关注要素，栏目顺序 = 流程顺序。逐栏问"为什么填 / 不填会怎样 / 怎么判断填得好"，把**显性表单**反推出**隐性判断标准**，补进"术"层。
3. **沿用 or 升级**：现成的直接沿用并标注来源；确有空缺才建议增补，且**先说清原设计意图**再谈改进。

**说"没有模板"也不尴尬**："那太好了，我们正好可以把它做出来。" —— 基于用户已有素材**反向生成**草案交用户改（内容是用户的，形态是 AI 的工艺，同 Stage 4 多候选原则）。**绝不 AI 凭空造**。

> 问"有没有模板"是**低门槛高回报**的一问：答"有"白得一份现成资产；答"没有"也顺势引出了下一个交付物。详见 references/methodology.md §4。

## Resources

### references/
- `methodology.md` — Full stage-by-stage methodology, including question scripts and output templates for each of the 5 stages.
- `model-builder.md` — The 8 思维模型构建法 with selection guidance and worked examples.
- `templates.md` — Ready-to-fill templates for SOP, training outline, and case-study deliverables.
- `quality-checklist.md` — 道法术器坑 self-check; deliverables that fail this checklist need revision.
- `case-example.md` — A worked-through example (银行客户经理/销售 拜访客户) that runs end-to-end; reference it when the user gets stuck.

### scripts/
(Empty by design — this skill is workflow-driven, not script-driven. The deliverable is captured in conversation and then written into the user's chosen file type via the normal WorkBuddy doc/sheet/slide creation flow.)

### assets/
(Empty. No external assets needed.)

## Final notes for the agent running this skill

- **Stay in the user's domain language.** Don't introduce 建模法 / 高峰访谈 jargon until the user has bought into the goal. Natural questions work best in early stages.
- **Synthesize, don't just record.** Each stage's output should be summarized into the standard template structure — bullet points under headers the user can paste anywhere.
- **Cross-reference the case-example** when the user says "I'm stuck" or "what does this look like in practice?" — it covers every stage.
- **End with the quality checklist — visibly.** Run 道法术器坑 on the final deliverable AND show the 自检报告 in the chat reply (五层 ✅ + 综合评分 + 待优化项). Embedding the table inside the file does NOT satisfy this — the user must see the check in the conversation itself.
