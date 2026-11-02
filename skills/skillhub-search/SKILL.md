---
name: skillhub-search
version: 1.0.0
display_name: SkillHub 技能检索
display_name_en: SkillHub Skill Search
description: |
  在 SkillHub 平台（WorkBuddy 推荐市场 / BuiltinMarket）发现、检索并安装智能体（Agent）技能。
  基于 skills 列表接口，支持关键词分词搜索、一级标签（一级分类）筛选、关键词与标签的组合检索，以及检索后的安装落地。
  当用户需要在 SkillHub 上"查找 / 搜索 / 按分类浏览 / 推荐 / 安装"技能，或以需求/方法方式提问时使用，例如"找个 xxx 技能""有没有处理 PDF 的 skill""SkillHub 上搜一下 xxx""按分类看技能""办公效率类有哪些技能""推荐一个做数据分析的 skill""这个需求有现成技能吗""如何做 X""找 X 的技能""有能做…的吗"。
description_zh: |
  在 SkillHub 平台（WorkBuddy 推荐市场 / BuiltinMarket）发现、检索并安装智能体（Agent）技能。
  基于 skills 列表接口，支持关键词分词搜索、一级标签（一级分类）筛选、关键词与标签的组合检索，以及检索后的安装落地。
  当用户需要在 SkillHub 上"查找 / 搜索 / 按分类浏览 / 推荐 / 安装"技能，或以需求/方法方式提问时使用，例如"找个 xxx 技能""有没有处理 PDF 的 skill""SkillHub 上搜一下 xxx""按分类看技能""办公效率类有哪些技能""推荐一个做数据分析的 skill""这个需求有现成技能吗""如何做 X""找 X 的技能""有能做…的吗"。
description_en: |
  Discover, search, and install Agent skills on the SkillHub platform (WorkBuddy BuiltinMarket).
  Built on the skills list interface, it supports tokenized keyword search, first-level category (tag) filtering, combined keyword+tag retrieval, and post-search installation.
  Use when the user wants to find, browse by category, recommend, or install a skill on SkillHub, or asks need/method questions such as "how to do X", "find a skill for X", or "is there something that can do ...".
agent_created: true
allowed-tools: workbuddy_marketplace_skill
---

# SkillHub 技能检索 (SkillHub Skill Search)

## 角色与定位

以**技能发现与安装助手**身份工作：在 SkillHub（WorkBuddy 推荐市场）上帮用户"找到、看全、挑准、装好"合适的智能体（Agent）技能。
本技能既能**检索、浏览与推荐**，也能在用户确认后**直接安装**命中技能；鉴权与网络全部由宿主代理，不接触令牌。

核心能力：

1. **关键词分词搜索**：把用户口语化的需求拆成多个检索词，多次查询并合并，提升召回。
2. **一级标签（一级分类）筛选**：按用户指定的大类（如"办公效率""数据分析""开发工具"）过滤结果。
3. **组合检索**：关键词 + 一级标签同时生效（关键词用于召回，标签用于收敛）。
4. **推荐 / 可行性判断**：在结果中挑出最贴合的一个或多个，给出推荐理由；对用户"如何做 X / 有能做…的吗"类提问主动判断是否存在现成技能。
5. **安装落地**：检索结果经用户确认后，调用 `install` action 完成安装（含已安装、需更新等分支处理）。

## 何时使用（触发词）

只要用户表达"在 SkillHub / 推荐市场 / 技能商店里找、搜、看、推荐技能"的意图，即用本技能。按意图分为四类：

### A. 关键词搜索类
- 「找个 xxx 技能」「搜一下 xxx 的 skill」
- 「有没有处理 PDF 的 skill」「有没有做 PPT 的技能」
- 「SkillHub 上搜一下 xxx」「推荐市场里查 xxx」
- 「帮我看看有没有 xxx 相关的能力」

### B. 分类浏览类
- 「按分类看技能」「看看有哪些分类」
- 「办公效率类有哪些技能」「开发工具类有什么 skill」
- 「数据分析类的技能有哪些」「内容创作方向有什么可用技能」

### C. 组合检索类
- 「办公效率类里处理 PDF 的技能」「数据分析分类下做可视化的 skill」
- 「在开发工具里搜一下 git 相关的」

### D. 推荐 / 可行性判断类
- 「推荐一个做数据分析的 skill」「给我推荐个写周报的」
- 「这个需求有现成技能吗」「我这个场景 SkillHub 上能找到对应技能不」
- 「要自动生成会议纪要，有合适的技能吗」

### E. 需求 / 方法询问类（主动发现技能）
- 「如何做 X」「怎么实现 X」「X 该怎么做」（X 为具体任务，如"如何做数据分析""怎么做 PPT"）
- 「找 X 的技能」「X 这方面有技能吗」「X 相关的 skill 有吗」
- 「有能做 … 的吗」「有什么可以帮我 … 的吗」「能不能帮我搞定 …」

> 类别 E 的提问往往是"以需求/方法为入口"而非"以技能为入口"。处理时：把 X 或"…"解析为检索关键词，先检索 SkillHub；若命中则推荐并询问是否安装，若未命中则如实告知并给出替代建议。

**与安装类技能的关系**：本技能已内置安装能力，可独立完成"检索 → 确认 → 安装"全流程；`marketplace-skill-installer` 仍可作为只做安装的轻量入口。用户只说"找 / 搜 / 看 / 推荐"时先检索；当用户明确表示"装这个 / 安装"或在本技能结果中选定某技能时，由本技能执行安装。

## 工具与数据来源

- **唯一后端接口**：`workbuddy_marketplace_skill`，支持两个 action：
  - `search`：检索技能列表（见"执行逻辑"Step 1–7）。
  - `install`：安装指定技能（见 Step 8）。
  - 鉴权与网络由宿主处理，本技能**禁止**自行构造 HTTP 请求、禁止使用 token / cookie / Authorization。
- **检索入参**：`keyword`（检索词）、`limit`（返回条数，默认 5，检索场景建议 10–20 以提升召回）。
- **安装入参**：`skillId`（必须来自 search 返回的真实命中，禁止臆造）。
- **返回字段**（列表接口契约，详见 `references/skillhub-api.md`）：
  - 必含：`skillId`、`name`、`version`、`description`、`installed`
  - 可选：`updateAvailable`、`category` / `tags` / `firstLevelTag`（一级标签字段，命名以平台实际返回为准）
- **标签来源说明**：若返回结果含分类字段，优先用其做精确标签筛选；若平台未返回分类字段，则退化为"把标签词当作额外关键词，对 `name` + `description` 做文本匹配"，并在回复中向用户说明"分类过滤为近似匹配"。

## 执行逻辑（核心流程）

### Step 1：意图解析
从用户输入中抽取两个槽位：
- **keyword（检索词）**：用户关心的功能/对象，如"PDF""数据分析""会议纪要"。
  - 若用户只说"找个 skill""按分类看技能"而无具体词 → keyword 留空，走纯分类浏览（见 Step 4 分支）。
- **tag（一级标签，可选）**：用户点名的大类，如"办公效率""数据分析""开发工具"。
  - 常见大类归一化：办公效率/效率 → `办公效率`；数据/分析 → `数据分析`；开发/工具 → `开发工具`；内容/创作 → `内容创作`；以此类推。**不要臆造分类名**，只把用户原话作为标签候选。

### Step 2：关键词分词
调用 `scripts/tokenize.py` 对 keyword 做分词，得到：
- `tokens`：拆出的词元（中文按二元组 bigram + 整句；英文按空格/连字符切词 + 整句）。
- `queries`：建议提交的检索串列表（整句优先，其次按相关性排序的词元，最多取前 4 个，控制接口调用次数）。
- 若 keyword 为空，跳过本步，直接进入分类浏览分支。

```bash
python scripts/tokenize.py "处理PDF的技能"
# 输出 JSON: {"keyword":"处理PDF的技能","tokens":["处理","PDF","技能","处理PDF","PDF的","的技能"],"queries":["处理PDF的技能","处理PDF","PDF的","的技能"]}
```

### Step 3：调用列表接口（多次召回 + 合并）
- 对 `queries` 中每个检索串调用一次 search（若 queries 为空则调用一次空 keyword 或 tag 名作为 keyword 拉取全量候选）。
- `limit` 设为 10–20。
- 合并所有返回结果，按 `skillId` **去重**；保留首次出现的记录。
- 任一调用返回 `success: false` → 透传 `error` 并停止；若某次调用 `results: []` 仅表示该词无命中，继续其他词。

### Step 4：一级标签筛选（可选）
- 若用户未提供 tag → 跳过，保留全部候选。
- 若提供 tag：
  1. 优先用结果中的分类字段（`category`/`tags`/`firstLevelTag`）做精确匹配（相等或包含）。
  2. 若无分类字段 → 用 tag 词对 `name`+`description` 做包含匹配（近似）。
  3. 过滤后若为空 → 向用户说明"该分类下未检索到明确匹配"，并退回展示未过滤的相关结果（标注"按关键词相关度"），或建议调整标签/关键词。

### Step 5：组合检索与去重
- 关键词召回 ∩ 标签过滤 = 组合检索结果。
- 已在 Step 3 完成去重；本步仅确保"既命中关键词又命中标签"的结果排在最前。

### Step 6：排序与打分
对最终候选集合按相关度打分并排序（分数高者在前）：
- **名称命中**：token 出现在 `name` 中，权重最高（+3/命中 token）。
- **描述命中**：token 出现在 `description` 中（+1/命中 token）。
- **标签精确命中**：分类字段与 tag 完全匹配（+2）。
- **已安装加成**：`installed === true` 轻微加权（+1），并在展示中标注。
- 同分时按 `version` 降序。

### Step 7：结果呈现
按模式输出（见下"检索模式与呈现规范"）。**不**向用户暴露 `skillId`（内部机器 id）。展示字段限定：`name`、`version`、`description`（前 60 字）、`installed` 状态、推荐理由。

### Step 8：安装落地（按需，需用户确认）
当用户对检索结果中的某个（或某几个）技能表示安装意图（如"装这个""帮我装上""安装第 2 个"），或类别 E 提问后用户接受推荐并要求安装时，执行安装：
1. 取目标技能的 `skillId`（必须来自 Step 3 的真实返回，禁止臆造）。
2. 调用 `install`：
   - `success: true` → 用返回的 `message` 告知安装位置与版本；可提示"在【技能管理】面板可见"。**不要**手动拼接路径。
   - `success: false` → 透传 `error`；若 `error` 含 `[UNKNOWN_SKILL_ID]`，不要重试同一 skillId，重新 search 取新 id 再装。
3. 安装分支（参考 `references/skillhub-api.md`）：
   - 未安装（`installed === false`）→ 直接 install。
   - 已安装且最新（`installed === true && updateAvailable === false`）→ 告知"已是最新 vX，无需重复安装"，跳过。
   - 已安装且有更新（`installed === true && updateAvailable === true`）→ 询问是否更新，同意后再 install。
4. 安装完成后**不要**自行为该技能触发后续动作，交还用户自行启用。

## 检索模式与呈现规范

### 模式 1：纯关键词搜索
- 直接给 Top 5–8 命中，每条含名称、版本、一句话描述、是否已安装。
- 命中为 0 → 告知"未找到直接匹配的技能"，并给出 2–3 个近义检索建议（用 tokenize 的近义词元）。

### 模式 2：纯分类浏览
- 调用 search（keyword 用 tag 名或留空）拉取候选，按分类字段聚合。
- 若平台返回分类字段：列出该分类下的技能清单（名称 + 版本 + 简述）。
- 若未返回分类字段：说明"当前接口未直接提供分类聚合，已按标签词近似筛选"，并展示近似结果。
- 用户问"有哪些分类"而接口未返回分类树时，列出**平台已知常见一级分类**供其选择（仅作引导，不声称穷尽）。

### 模式 3：关键词 + 分类组合
- 先关键词召回，再标签过滤（Step 4），展示交集结果；若交集为空按 Step 4.3 处理。

### 模式 4：推荐 / 可行性判断
- "推荐一个做 X 的 skill" → 用关键词 X 检索，取打分最高的 1 个，给出**推荐理由**（命中了哪些能力点）。
- "这个需求有现成技能吗" → 检索后明确回答"有 / 没有 / 有近似"，并列出对应技能或退而给近义建议。

### 模式 5：需求 / 方法询问（如何做 X / 有能做…的吗）
- 解析 X 或"…"为检索关键词，执行 Step 1–7。
- 命中：推荐最相关技能，并主动询问"是否需要为你安装该技能？"。
- 未命中：明确回答"目前 SkillHub 上暂无现成技能可直接完成 X"，可给出近义检索建议；若 X 属通用对话能力，提示用户可直接对话处理，或建议后续自建技能。

## 边界与约束（硬规则）

- **安装需用户确认**：仅在用户明确表达安装意图（或接受推荐后要求安装）时才调用 `install`；不得擅自静默安装。安装结果以接口返回的 `message` 为准，不臆造路径。
- **禁止伪造**：不臆造 `skillId`、不臆造分类名、不臆造不存在的技能；所有结论必须来自列表接口真实返回。
- **不接触鉴权**：不读取/拼接 token、cookie、Authorization；全部经 `workbuddy_marketplace_skill` 由宿主代理。
- **不主动全量枚举**：除非用户明确想"看全部 / 按分类看"，否则不要一次拉取并罗列所有技能。
- **降级透明**：标签为近似匹配、分类字段缺失等情况，必须在回复中向用户说明，不得伪装为精确结果。

## 资源

- `scripts/tokenize.py`：关键词分词与检索串生成（确定性、可重复）。
- `references/skillhub-api.md`：列表接口（search）入参/返回字段契约与标签字段处理说明。
