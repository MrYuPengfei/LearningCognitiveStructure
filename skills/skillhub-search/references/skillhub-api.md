# SkillHub 列表接口（skills list）契约说明

本文件描述 `skillhub-search` 技能所依赖的 SkillHub（WorkBuddy 推荐市场 / BuiltinMarket）列表接口约定。
接口统一通过内置工具 `workbuddy_marketplace_skill` 访问，支持 `action: "search"`（检索）与 `action: "install"`（安装），鉴权与网络由宿主代理。

> 说明：以下字段基于 `marketplace-skill-installer` 技能已记录的 search / install 返回结构，以及本技能新增的"一级标签筛选"需求整理。
> 一级标签字段的**具体命名以平台实际返回为准**；若平台未返回分类字段，本技能按"近似文本匹配"降级处理（见 SKILL.md Step 4）。

## 请求（search）

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `action` | string | 是 | 固定为 `"search"` |
| `keyword` | string | 否 | 检索词；为空时由宿主决定返回全量或默认候选 |
| `limit` | int | 否 | 返回条数，默认 5；检索场景建议 10–20 以提升召回 |

示例：

```json
{ "action": "search", "keyword": "PDF", "limit": 15 }
```

## 响应（成功）

| 字段 | 类型 | 说明 |
|------|------|------|
| `success` | bool | 是否成功 |
| `results` | array | 技能对象数组，可能为空 `[]` |
| `error`  | string | 仅在 `success: false` 时存在，错误描述 |

## 技能对象字段（results 元素）

| 字段 | 类型 | 必含 | 说明 |
|------|------|------|------|
| `skillId` | string | 是 | 技能唯一内部 id（**不得向用户暴露**） |
| `name` | string | 是 | 技能显示名 |
| `version` | string | 是 | 版本号（语义化版本） |
| `description` | string | 是 | 技能描述 |
| `installed` | bool | 是 | 当前是否已安装 |
| `updateAvailable` | bool | 否 | 已安装时是否有可用更新 |
| `category` / `tags` / `firstLevelTag` | string/array | 否 | 一级标签（分类）字段，**命名以平台实际返回为准**，用于本技能的标签筛选 |

## 一级标签筛选的处理

1. **精确筛选（优先）**：若技能对象含分类字段，且字段值与用户指定的 tag 相等或包含 → 命中。
2. **近似筛选（降级）**：若技能对象不含分类字段 → 将 tag 词对 `name` + `description` 做包含匹配，并在回复中向用户声明"分类过滤为近似匹配"。
3. **空结果处理**：筛选后为空 → 提示"该分类下未检索到明确匹配"，退回展示未过滤的相关结果（标注"按关键词相关度"），或建议调整标签/关键词。

## 错误透传

- `success: false` → 将 `error` 原样透传给用户并停止检索。
- `results: []` → 单个检索词无命中，继续尝试其他检索词；全部词均无命中再告知用户"未找到匹配技能"。

## 请求（install）

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `action` | string | 是 | 固定为 `"install"` |
| `skillId` | string | 是 | 来自 search 返回的命中技能 id（**禁止臆造**，缺失则重新 search） |

示例：

```json
{ "action": "install", "skillId": "<results[i].skillId>" }
```

## 响应（install）

| 字段 | 类型 | 说明 |
|------|------|------|
| `success` | bool | 是否安装成功 |
| `message` | string | 成功时的安装位置与版本描述（展示给用户，**不要**手动拼接路径） |
| `error`   | string | 失败时的错误描述（含错误码前缀） |

## 安装分支与常见错误

| 前置状态（来自 search 结果） | 处理 |
|------|------|
| 未安装（`installed === false`） | 直接调用 install |
| 已安装且最新（`installed === true && updateAvailable === false`） | 告知"已是最新 vX，无需重复安装"，跳过安装 |
| 已安装且有更新（`installed === true && updateAvailable === true`） | 询问用户是否更新，同意后再 install |

| `error` 前缀 | 含义 | 处理 |
|---|---|---|
| `[CONFIG_ERROR]` | 主进程未配置 endpoint | 提示"推荐市场暂未启用，可能需更新客户端" |
| `[BUILTIN_MARKET_ERROR]` | 后端业务错误 | 直接展示 `error` |
| `[UNKNOWN_SKILL_ID]` | install 阶段该 skillId 已不存在 | **不要**重试同一 skillId，重新 search 取新 id 再装 |
| `[DOWNLOAD_ERROR]` | 下载失败 | 提示"下载失败，可能网络/权限问题" |
| `[EXTRACT_ERROR]` | 解压失败 | 提示"解压失败，可清理技能目录后重试" |
| `[INSTALL_ERROR]` | 其他未知 | 直接展示 `error` |
