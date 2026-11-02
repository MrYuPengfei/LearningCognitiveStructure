# MinerU v1 API 速查

Base URL 由 `MINERU_BASE` 指定，默认 `http://127.0.0.1:8000`。

## 全流程

```
POST /v1/uploads                        创建上传槽，返回 upload id
PUT  /v1/uploads/{id}/content           上传 PDF 原始字节（Content-Type: application/octet-stream）
POST /v1/uploads/{id}/complete          提交 sha256sum，服务端校验并落库，返回 file.id
POST /v1/parse/jobs                     用 file_id 列表建解析任务
GET  /v1/parse/jobs/{job_id}            轮询状态与进度
DELETE /v1/parse/jobs/{job_id}          取消（可把卡死的 running 置为 canceled）
GET  /v1/files/{file_id}/content        下载产物（zip 或 markdown）
GET  /v1/health                         健康检查
GET  /v1/usage                          吞吐与限额计量
```

## 各步字段

### 1) 创建上传

请求体：

```json
{"filename": "paper.pdf", "bytes": 1234567,
 "mime_type": "application/pdf", "purpose": "parse",
 "sha256sum": "<hex>"}
```

响应关键字段：`id`（上传槽 id）、`status`、`upload_url`（可能是绝对地址）、`file.id`。

**服务端按 sha256 去重**：若响应 `status == "completed"` 且带 `file.id`，说明该文件此前已上传过，可直接复用，跳过 `PUT`。

`PUT` 与 `complete` 返回 `409` 时均应视为"已存在"，转去读响应里的 `file.id`，不要当失败。

### 2) 建任务

```json
{"files": [{"source": {"type": "file_id", "file_id": "file-xxx"}}],
 "tier": "standard",
 "output_formats": ["markdown", "zip"],
 "ocr_mode": "auto"}
```

- `tier`：`flash`（快、丢结构）/ `standard`（默认，推荐）/ `advanced`（最准、最慢）
- 一次 job 可带多个 `file_id`，服务端串行处理；`BATCH` 就是这里的批量大小
- 响应关键字段：`job_id`

### 3) 轮询

响应关键字段：`status`、`progress.completed` / `progress.total`、`files[]`。

`status` 终态：`completed` / `partial` / `failed` / `canceled`。

`files[]` 每项：`name`（原文件名，用于反推 STEM）、`status`、`output_files`。

### 4) 取产物 file_id（两种部署形态都要兼容）

```python
# dict 形态
{"zip": {"file_id": "file-abc"}, "markdown": {"file_id": "file-def"}}
# list 形态（官方 4.0 artifact 数组）
[{"purpose": "parse_output", "file_id": "file-abc"}, ...]
```

优先取 `zip`；list 形态优先取 `purpose == "parse_output"`，否则取首个带 `file_id` 的项。

### 5) 下载

`GET /v1/files/{file_id}/content` 返回二进制。zip 解压后目录即上文的结构（`markdown.md`、`images/`、若干 `*.json`）。

## 异常分类（决定重试策略）

| 异常 | 判定依据 | 正确反应 |
| --- | --- | --- |
| 瞬时错误 | 消息含 `Remote end closed` / `10054` / `10053` / `10060` / `timed out` / `Connection aborted/reset` | 指数退避重试（2→4→8→16s），最多 4 次 |
| `ServiceDown` | `502` / `503` / `10061` / `actively refused` / `积极拒绝` | **立即停止本轮**，等看门狗；不要在死服务上空转 |
| `JobStalled` | 状态或进度超过 `MINERU_STALL`（默认 300s）未变化 | 已自动 `DELETE` 取消，标记 `stalled`，下一轮重试 |
| `HTTPError` 4xx | 参数错误（如 tier 不支持） | 不重试，直接报错 |

`fast=True` 的调用（health / get_job）一旦判定服务不可用立即抛 `ServiceDown`，用于把"6 分钟才超时"压缩到"20 秒内失败"。

## 排障顺序

1. `curl /v1/health` —— 不通就先修服务，别改脚本。
2. `curl /v1/usage` —— 看是不是撞了限额。
3. 看 `manifest.json` 里失败项的 `status`：
   - `stalled` → 该 PDF 可能过大或有异常结构，单独用 `advanced` 档跑一次
   - `empty_output` → 多半是扫描件且 `ocr_mode` 没生效，试 `ocr_mode: "force"`
   - `upload_failed` → WSL2 端口代理问题，重跑即可
   - `download_failed` → 磁盘满或路径权限
4. 容器日志：`docker logs --tail 200 <mineru-container>`。
5. 卡死任务残留会占住队列，必要时重启容器，再重跑 `batch_parse.py`（磁盘自愈会补回已完成记录）。

## 磁盘与命名约定

- `_parse/<STEM>/_raw.zip` 保留不删：批量删除会触发沙箱批量删除保护并中断任务，且保留 zip 换取可续跑性。
- `_tier` 是纯文本文件，写 `standard` / `advanced` / `flash`。下游必须校验，避免用 `flash` 档产物做公式完整性要求高的工作。
- 交付副本目录名固定 `md/<STEM>_markdown/`，内部文件名固定 `markdown.md`（不要叫 `<STEM>.md`，否则会覆盖历史副本）。
