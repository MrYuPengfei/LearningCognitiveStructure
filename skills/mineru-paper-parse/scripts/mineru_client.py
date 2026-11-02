# -*- coding: utf-8 -*-
"""
MinerU API (v1) 客户端 —— WSL2 Docker 中的 MinerU 4.0.0 服务
流程: create upload -> PUT content -> complete -> create job -> poll -> download
仅用标准库，避免额外依赖。
"""
import os, json, time, hashlib, urllib.request, urllib.error, urllib.parse, http.client

BASE = os.environ.get("MINERU_BASE", "http://127.0.0.1:8000")

TRANSIENT = ("Remote end closed", "10054", "10053", "10060",
             "timed out", "Connection aborted", "Connection reset")


class JobStalled(RuntimeError):
    """任务长时间无进展（卡在 queued/running，GPU util 0%），已主动取消。

    背景（2026-10-25）：实测 job 会卡在 queued/running 数小时不动，
    而服务端一次只处理一个任务 -> 后续全部排队。等 3600s 超时代价太大，
    故改为检测停滞即取消，让调用方快速重试下一批。
    """


class ServiceDown(RuntimeError):
    """MinerU 服务端不可用（502/503/连接被拒/卡死）。

    与「单次请求失败」区分开：出现本异常时应立即停止灌任务、交由看门狗
    等待服务恢复，而不是继续空转重试（否则会像 2026-10-24 那样在已卡死的
    服务上反复轮询 6 分钟才判 job_timeout）。
    """


def _is_transient(msg):
    return any(t in str(msg) for t in TRANSIENT) or "503" in str(msg) or "502" in str(msg)


def _is_down(msg):
    s = str(msg)
    return ("502" in s or "503" in s or "10061" in s
            or "actively refused" in s or "积极拒绝" in s)


def _req(method, path, body=None, headers=None, raw=False, timeout=120, retries=4, fast=False):
    """带指数退避重试的请求；raw=True 时 body 较大，重试需重建。

    fast=True 时，一旦判定服务端不可用（502/503/连接被拒）立即抛 ServiceDown，
    供轮询类调用快速失败，避免在死服务上长时间空转。
    """
    last = None
    for attempt in range(max(1, retries)):
        try:
            return _req_once(method, path, body, headers, raw, timeout)
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


def _req_once(method, path, body=None, headers=None, raw=False, timeout=120):
    url = BASE + path
    data = None
    h = dict(headers or {})
    # WSL2 端口代理会在空闲后关闭 keep-alive 连接，复用已关闭连接会触发 10054/Remote end closed。
    # 显式关闭连接，每次请求新建，绕开该问题。
    h.setdefault("Connection", "close")
    if body is not None:
        if isinstance(body, (dict, list)):
            data = json.dumps(body).encode("utf-8")
            h.setdefault("Content-Type", "application/json")
        elif isinstance(body, bytes):
            data = body
            h.setdefault("Content-Type", "application/octet-stream")
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
    """健康检查（官方 V1：GET /v1/health）。快速失败，服务 502 时抛 ServiceDown。"""
    return _req("GET", "/v1/health", timeout=timeout, retries=retries, fast=True)


def usage(timeout=8, retries=1):
    """消费/吞吐计量（官方 V1：GET /v1/usage）。用于批量处理时观察吞吐与限额。"""
    return _req("GET", "/v1/usage", timeout=timeout, retries=retries, fast=True)


def upload_file(pdf_path):
    """上传本地 PDF，返回 file_id"""
    data = open(pdf_path, "rb").read()
    sha = hashlib.sha256(data).hexdigest()
    fn = os.path.basename(pdf_path)
    up = _req("POST", "/v1/uploads", {
        "filename": fn, "bytes": len(data),
        "mime_type": "application/pdf", "purpose": "parse",
        "sha256sum": sha,
    })
    uid = up["id"]
    # 服务端按 sha256 去重：已是 completed 则无需再 PUT
    if up.get("status") == "completed" and (up.get("file") or {}).get("id"):
        return up["file"]["id"], up

    # 若服务提供上传 URL（可能是绝对地址），用之；否则回退到本地路径
    put_path = f"/v1/uploads/{uid}/content"
    uurl = up.get("upload_url")
    if uurl and uurl.startswith("http"):
        target = uurl[len(BASE):] if uurl.startswith(BASE) else "/v1/uploads/%s/content" % uid
        try:
            _req("PUT", target, body=data, timeout=600)
        except RuntimeError as e:
            if "409" not in str(e):
                raise
    else:
        try:
            _req("PUT", put_path, body=data, timeout=600)
        except RuntimeError as e:
            if "409" not in str(e):
                raise
    try:
        comp = _req("POST", f"/v1/uploads/{uid}/complete", {"sha256sum": sha})
    except RuntimeError as e:
        if "409" in str(e):
            comp = up
        else:
            raise
    f = comp.get("file") or {}
    fid = f.get("id")
    if not fid:
        raise RuntimeError(f"未获得 file_id: {json.dumps(comp, ensure_ascii=False)[:500]}")
    return fid, comp


def create_job(file_ids, tier="standard", formats=("markdown", "zip"), ocr_mode="auto"):
    """file_ids: str 或 list[str]"""
    if isinstance(file_ids, str):
        file_ids = [file_ids]
    body = {
        "files": [{"source": {"type": "file_id", "file_id": fid}} for fid in file_ids],
        "tier": tier,
        "output_formats": list(formats),
        "ocr_mode": ocr_mode,
    }
    return _req("POST", "/v1/parse/jobs", body)


def get_job(job_id, timeout=20, retries=1):
    """查询任务状态。短超时 + 快速失败：服务卡死时 20s 内抛错，而不是拖 6 分钟。"""
    return _req("GET", f"/v1/parse/jobs/{job_id}", timeout=timeout, retries=retries, fast=True)


def cancel_job(job_id):
    """取消任务（实测：DELETE /v1/parse/jobs/{id} 可把卡住的 running 置为 canceled）。"""
    return _req("DELETE", f"/v1/parse/jobs/{job_id}", timeout=10, retries=1)


def wait_job(job_id, timeout=1800, poll=5.0, verbose=True, stall=None):
    """轮询直到终态。

    - 服务端不可用（ServiceDown）会立即向上抛，由调用方停止本轮；
    - 停滞超过 stall 秒（默认 MINERU_STALL，300s）则取消任务并抛 JobStalled，
      避免为一个卡死的 job 干等 3600s 而堵住后续所有任务。
    """
    if stall is None:
        stall = int(os.environ.get("MINERU_STALL", "300"))
    t0 = time.time()
    last = None
    last_key = None
    last_change = time.time()
    while time.time() - t0 < timeout:
        j = get_job(job_id)
        st = j.get("status")
        pr = j.get("progress") or {}
        key = (st, pr.get("completed"), pr.get("failed"))
        if key != last_key:
            last_key = key
            last_change = time.time()
        if verbose and st != last:
            print(f"  [job] status={st} progress={pr.get('completed')}/{pr.get('total')}")
            last = st
        if st in ("completed", "partial", "failed", "canceled"):
            return j
        if stall and (time.time() - last_change) > stall:
            try:
                cancel_job(job_id)
            except Exception:
                pass
            raise JobStalled(f"job {job_id} 停滞 {stall}s（status={st}），已取消")
        time.sleep(poll)
    raise TimeoutError(f"job {job_id} 超时 ({timeout}s)")


def download(file_id, out_path):
    content = _req("GET", f"/v1/files/{file_id}/content", raw=True, timeout=900)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "wb") as f:
        f.write(content)
    return out_path, len(content)
