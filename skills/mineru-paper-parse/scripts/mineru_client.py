# -*- coding: utf-8 -*-
"""
MinerU API (v1) 客户端 —— 适配 MinerU 4.1.3 服务（Docker 镜像 mineru:4）。

4.1.3 与 4.0 的关键差异（本客户端针对 4.1.3）：
  - 无独立的 /v1/uploads 建槽步骤；改为：POST /v1/tasks 建任务（同时拿到 task_id 与每文件的 file_id）
  - 上传：PUT /v1/tasks/{task_id}/uploads/{file_id}（原始 PDF 字节，Content-Type: application/octet-stream）
  - 建任务/轮询/取消：/v1/tasks 系列（非 /v1/parse/jobs）
  - 下载产物：GET /v1/files/{file_id}/content（file_id 即输入文件 file_id），返回 zip
  - output_formats 仅支持 default/docx/html/latex（"default" 即 markdown + images + json 的 zip 包）

仅用标准库，避免额外依赖。兼容 WSL2 端口代理空闲断连：每次请求强制 Connection: close。
"""
import os, json, time, hashlib, urllib.request, urllib.error

BASE = os.environ.get("MINERU_BASE", "http://127.0.0.1:8000")

TRANSIENT = ("Remote end closed", "10054", "10053", "10060",
             "timed out", "Connection aborted", "Connection reset")
DOWN = ("502", "503", "10061", "actively refused", "积极拒绝")


class JobStalled(RuntimeError):
    """任务长时间无进展（卡在 queued/running，GPU util 0%），已主动取消。"""
    pass


class ServiceDown(RuntimeError):
    """MinerU 服务端不可用（502/503/连接被拒/卡死）。"""
    pass


def _is_transient(msg):
    return any(t in str(msg) for t in TRANSIENT) or "503" in str(msg) or "502" in str(msg)


def _is_down(msg):
    s = str(msg)
    return any(k in s for k in DOWN)


def _req(method, path, body=None, raw=False, timeout=120, retries=4, fast=False):
    last = None
    for attempt in range(max(1, retries)):
        try:
            return _req_once(method, path, body, raw, timeout)
        except Exception as e:
            last = e
            if _is_down(e):
                if fast or attempt == retries - 1:
                    raise ServiceDown(f"{method} {path} -> {str(e)[:200]}")
            if not _is_transient(e) or attempt == retries - 1:
                raise
            wait = 2 * (2 ** attempt)
            print(f"    [retry {attempt+1}/{retries}] {method} {path[:60]} 等待 {wait}s ... ({str(e)[:80]})")
            time.sleep(wait)
    raise last


def _req_once(method, path, body=None, raw=False, timeout=120):
    url = BASE + path
    data = None
    h = {"Connection": "close"}
    if body is not None:
        if isinstance(body, (dict, list)):
            data = json.dumps(body).encode("utf-8")
            h["Content-Type"] = "application/json"
        elif isinstance(body, bytes):
            data = body
            h["Content-Type"] = "application/octet-stream"
    req = urllib.request.Request(url, data=data, headers=h, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            content = r.read()
            if raw:
                return content
            txt = content.decode("utf-8", "ignore")
            try:
                return json.loads(txt)
            except Exception:
                return txt
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "ignore")
        raise RuntimeError(f"{method} {path} -> HTTP {e.code}: {detail[:800]}")
    except Exception as e:
        raise RuntimeError(f"{method} {path} -> {e}")


def health(timeout=6, retries=1):
    """健康检查（GET /v1/health）。服务 502 时抛 ServiceDown。"""
    return _req("GET", "/v1/health", timeout=timeout, retries=retries, fast=True)


def usage(timeout=8, retries=1):
    return _req("GET", "/v1/usage", timeout=timeout, retries=retries, fast=True)


def create_task(files_meta, tier="standard", formats=("default",), ocr_mode="auto"):
    """建任务。files_meta: [{"file_name","bytes","sha256sum"}, ...]
    返回 {task_id, status, files:[{file_id, file_name, status, upload:{...}}]}。
    file_id 用于后续 PUT 上传与最终下载。"""
    body = {"tier": tier, "ocr_mode": ocr_mode,
            "output_formats": list(formats), "files": files_meta}
    return _req("POST", "/v1/tasks", body, timeout=30)


def upload_file(task_id, file_id, data, timeout=600):
    """上传 PDF 原始字节（PUT）。"""
    path = f"/v1/tasks/{task_id}/uploads/{file_id}"
    _req("PUT", path, body=data, timeout=timeout)


def get_task(task_id, timeout=20, retries=1):
    """查询任务状态（GET /v1/tasks/{id}）。fast=True 时服务卡死快速失败。"""
    return _req("GET", f"/v1/tasks/{task_id}", timeout=timeout, retries=retries, fast=True)


def cancel_task(task_id):
    """取消任务（POST /v1/tasks/{id}/cancel）。"""
    return _req("POST", f"/v1/tasks/{task_id}/cancel", timeout=15, retries=2)


def download(file_id, out_path=None):
    """下载产物 zip（GET /v1/files/{file_id}/content）。file_id 即输入文件 file_id。"""
    content = _req("GET", f"/v1/files/{file_id}/content", raw=True, timeout=900)
    if out_path:
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "wb") as f:
            f.write(content)
        return out_path, len(content)
    return content
