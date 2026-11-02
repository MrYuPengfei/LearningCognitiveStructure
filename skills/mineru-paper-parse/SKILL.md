---
name: mineru-paper-parse
description: 用本地 MinerU 服务把整库 PDF 论文批量解析为结构化 Markdown（正文 + LaTeX 公式 + 图片切图），供后续阅读、检索或撰写笔记使用。适用于需要把几十到上千篇 PDF 一次性转成可检索文本、且要求公式不失真的场景；也适用于排查解析任务卡死、产物为空、重复解析等常见故障。当用户提到「MinerU」「解析 PDF 库」「PDF 转 Markdown」「论文批量 OCR」「公式识别」时使用。
agent_created: true
---

# MinerU 论文批量解析

## 用途

把一批 PDF 论文通过自建 MinerU 服务（默认 `http://127.0.0.1:8000`，v1 API）解析成 Markdown 目录树，保留 LaTeX 公式与图片切图，并支持断点续跑、内容去重、服务看门狗。

典型结果形态：

```
<库根>/
├── pdf/                                   原始 PDF
├── _parse/<STEM>/                         解析中间产物
│   ├── markdown.md                        正文（含 $...$、$$...$$ 公式与 ![](images/…) 引用）
│   ├── images/                            图片切图 + 公式切图 + 表格切图
│   ├── middle_json.json  model_output.json  structured_content.json
│   └── _tier                              解析档位（standard / advanced / flash）
└── md/<STEM>_markdown/                    对外交付副本（markdown.md + images/）
```

`<STEM>` = PDF 文件名去扩展名，是全流程的主键，**不要改名**。

## 前置条件

1. MinerU 服务已启动且 `/v1/health` 返回 `{"status": "ok"}`。先自检：
   ```bash
   curl -s http://127.0.0.1:8000/v1/health
   ```
2. `scripts/mineru_client.py` 与 `scripts/batch_parse.py` 在本 skill 的 `scripts/` 下，仅依赖标准库。
3. 磁盘留足空间：中间产物约为 PDF 体积的 3–5 倍（含 zip 与切图）。

## 快速开始

```bash
export LIT_ROOT=/path/to/your/library          # 库根目录
export LIT_PDF_DIR=$LIT_ROOT/pdf               # 可选，默认 $LIT_ROOT/pdf
export LIT_PARSE_DIR=$LIT_ROOT/_parse          # 可选
export LIT_MD_DIR=$LIT_ROOT/md                 # 可选，交付副本目录
export MINERU_BASE=http://127.0.0.1:8000
export MINERU_TIER=standard                    # standard / advanced / flash
export MINERU_BATCH=10                         # 每个 job 提交的篇数
export MINERU_UPLOAD_WORKERS=4
export MINERU_RETRY_ROUNDS=2                   # 首轮后自动重试失败项的轮数

python scripts/batch_parse.py
```

脚本行为：内容指纹去重 → 按 `BATCH` 分批上传建 job → 轮询 → 下载 zip 解压 → 校验 `markdown.md` 非空 → 复制到 `md/<STEM>_markdown/` → 写 `manifest.json`。

断点续跑：`manifest.json` 中 `status == "parsed"` 的跳过；同时每次启动会做**磁盘自愈**，凡 `_parse/<STEM>/markdown.md` 已存在且非空的，回填为已解析，防止 manifest 丢失导致重复解析。

## 关键坑位（按踩坑频率排序）

| 现象 | 根因 | 处置 |
| --- | --- | --- |
| job 卡在 `queued`/`running` 数小时不动，GPU 占用 0% | 服务端单任务串行，个别 PDF 触发死锁 | 客户端在停滞超过 `MINERU_STALL`（默认 300s）后自动 `DELETE` 取消任务并抛 `JobStalled`，交由下一轮重试。**不要**设 3600s 超时干等——那会堵死后面所有任务 |
| `502/503` 或连接被拒，日志刷屏重试 | MinerU 容器挂了 | 客户端抛 `ServiceDown`，`batch_parse.py` 立即结束本轮并交由看门狗等待恢复。**不要在死服务上继续灌任务** |
| `Connection reset` / `10054 Remote end closed` | WSL2 端口代理空闲后关闭 keep-alive 连接 | `mineru_client._req_once` 强制 `Connection: close`，每次新建连接 |
| 同一篇论文被解析两次、笔记重复 | 同一 PDF 以多个文件名存在（匿名命名 / `副本` / `a` 后缀） | 启动时按 MD5 去重，保留优先级：真名 > 匿名，短名 > 长名 |
| `markdown.md` 存在但 0 字节 | 解析"成功"但产物为空 | 校验字节数，标记 `empty_output` 进入重试 |
| `output_files` 解析不出 `file_id` | 不同部署返回 dict 或 list 两种形态 | `pick_output_file_id()` 双形态兼容 |

其余细节（上传/建任务/产物 `file_id` 的字段形态、分片、`_tier` 校验）见 `references/api.md`。

## 产物质量的两条硬规则

1. **只认 `standard` 及以上档位**。`flash` 档会丢公式结构，不能用于要求公式完整的下游任务。`_tier` 文件记录档位，下游应当校验。
2. **图片分三类，正文引用只覆盖第一类**。MinerU 会把公式切图（`*_equation_*.jpg`）和表格截图（`*_table_*.jpg`）一并导出到 `images/`，但**正文 `markdown.md` 里没有对应 `![]()` 引用**。实测全库 6226 张图未被引用，其中 67% 是公式切图、31% 是表格截图。

   因此判断"原文有没有这张图"**不能只看 markdown 引用**，必须 `ls images/`。公式切图是核对 LaTeX 转写是否正确的最有力证据（配合 `pdftotext -layout` 交叉验证）。

## 交叉核验（可选但强烈建议）

MinerU 的 OCR 会误切公式与表格（把一行公式拆成两块、把 `θ` 认成 `0`、表头串行）。对关键论文建议三重核对：

```bash
# 1) PDF 原生文本层（表格与公式在 layout 模式下位置最接近原版）
pdftotext -layout paper.pdf - | sed -n '120,220p'
# 2) 300dpi 页面图，人眼核对切图边界
pdftoppm -r 300 -f 3 -l 3 -png paper.pdf page
# 3) 与 images/ 下的 *_equation_*.jpg 对照
```

发现 OCR 误切时，笔记/正文按**原图**还原，并在文中标注"此处 MinerU OCR 拆分有误，已按原图更正"。

## 常用变体

- **只跑前 N 篇**：`MINERU_LIMIT=20 python scripts/batch_parse.py`
- **多进程分片**：`MINERU_SHARD=0/3`、`1/3`、`2/3` 各起一个进程（会自动使用 `manifest_0_3.json` 等独立清单）
- **换档位重解析**：删除 `_parse/<STEM>/` 与 manifest 中该条，再以 `MINERU_TIER=advanced` 运行
- **只看状态**：读 `manifest.json`，按 `status` 分组统计（`parsed` / `stalled` / `service_down` / `upload_failed` / `empty_output` / `dup_skipped`）

## 资源

- `scripts/mineru_client.py` — v1 API 客户端：上传、建 job、轮询、取消、下载；含重试、`ServiceDown`/`JobStalled` 语义
- `scripts/batch_parse.py` — 批量编排：去重、分片、断点续跑、磁盘自愈、交付副本复制
- `references/api.md` — v1 API 全流程字段说明与故障排查速查表
