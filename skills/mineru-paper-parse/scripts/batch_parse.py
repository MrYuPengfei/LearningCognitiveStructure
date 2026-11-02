# -*- coding: utf-8 -*-
"""
批量调用 MinerU 4.1.3 服务把整库 PDF 解析为结构化 Markdown（正文 + LaTeX 公式 + 图片切图）。

流程（适配 4.1.3）：
  POST /v1/tasks 建任务 -> PUT /v1/tasks/{tid}/uploads/{fid} 上传 PDF ->
  GET /v1/tasks/{tid} 轮询 -> GET /v1/files/{fid}/content 下载 zip 解压。

特性：内容指纹去重 -> 按 BATCH 分批建任务 -> 轮询 -> 下载 zip 解压 ->
校验 markdown.md 非空 -> 复制到 md/<STEM>_markdown/ -> 写 manifest.json。
断点续跑：manifest 中 status=="parsed" 跳过；启动做磁盘自愈（_parse 已有非空 markdown 的回填）。
停滞检测：状态/进度超过 MINERU_STALL（默认 300s）未变化则取消任务并标 stalled，下一轮重试。

目录约定：
  <库根>/pdf/<STEM>.pdf
  <库根>/_parse/<STEM>/{markdown.md, images/, *_json.json, _tier, _raw.zip}
  <库根>/md/<STEM>_markdown/{markdown.md, images/}
"""
import os, sys, json, time, zipfile, threading, traceback, shutil, hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mineru_client as mc

ROOT = os.environ.get("LIT_ROOT", os.getcwd())
PDF_DIR = os.environ.get("LIT_PDF_DIR", os.path.join(ROOT, "pdf"))
PARSE_DIR = os.environ.get("LIT_PARSE_DIR", os.path.join(ROOT, "_parse"))
PAPERSMD = os.environ.get("LIT_MD_DIR", os.path.join(ROOT, "md"))
PIPE = os.path.join(ROOT, "_pipeline")
MANIFEST = os.path.join(PIPE, "manifest.json")
LOG = os.path.join(PIPE, "mineru_v41.log")

BATCH = int(os.environ.get("MINERU_BATCH", "1"))
UPLOAD_WORKERS = int(os.environ.get("MINERU_UPLOAD_WORKERS", "4"))
TIER = os.environ.get("MINERU_TIER", "standard")
LIMIT = int(os.environ.get("MINERU_LIMIT", "0"))
ROUNDS = int(os.environ.get("MINERU_RETRY_ROUNDS", "3"))
STALL = int(os.environ.get("MINERU_STALL", "300"))
MAX_JOBS = int(os.environ.get("MINERU_MAX_JOBS", "0"))

os.makedirs(PARSE_DIR, exist_ok=True)
os.makedirs(PIPE, exist_ok=True)
lock = threading.Lock()


def logprint(*a):
    line = " ".join(str(x) for x in a)
    print(line, flush=True)
    try:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(time.strftime("[%m-%d %H:%M:%S] ") + line + "\n")
    except Exception:
        pass


def load_manifest():
    if os.path.exists(MANIFEST):
        try:
            return json.load(open(MANIFEST, encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_manifest(m):
    tmp = MANIFEST + f".tmp.{os.getpid()}"
    for _ in range(5):
        try:
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(m, f, ensure_ascii=False, indent=1)
            os.replace(tmp, MANIFEST)
            return
        except PermissionError:
            time.sleep(0.5)
        except Exception:
            try:
                os.remove(tmp)
            except Exception:
                pass
            raise


def stem_of(fn):
    return os.path.splitext(fn)[0]


def md5_of(path, chunk=1 << 20):
    h = hashlib.md5()
    with open(path, "rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def dedupe(files):
    by_hash = {}
    for fn in files:
        p = os.path.join(PDF_DIR, fn)
        try:
            h = md5_of(p)
        except OSError:
            continue
        by_hash.setdefault(h, []).append(fn)
    keep, dropped = [], []
    for h, group in by_hash.items():
        if len(group) == 1:
            keep.append(group[0])
            continue
        group.sort(key=lambda n: (n.split("-")[0].lower().startswith("anon"), "副本" in n, len(n)))
        keep.append(group[0])
        dropped.extend(group[1:])
    if dropped:
        logprint(f"[dedupe] {len(files)} -> {len(keep)}，跳过 {len(dropped)} 个重复")
    return keep, dropped


def copy_to_md(stem):
    src = os.path.join(PARSE_DIR, stem)
    smd = os.path.join(src, "markdown.md")
    if not os.path.exists(smd):
        return
    dest = os.path.join(PAPERSMD, stem + "_markdown")
    os.makedirs(dest, exist_ok=True)
    shutil.copy2(smd, os.path.join(dest, "markdown.md"))
    simg = os.path.join(src, "images")
    if os.path.isdir(simg):
        dimg = os.path.join(dest, "images")
        os.makedirs(dimg, exist_ok=True)
        for fn in os.listdir(simg):
            sp = os.path.join(simg, fn)
            if os.path.isfile(sp):
                shutil.copy2(sp, os.path.join(dimg, fn))


def wait_task(tid, timeout=3600, poll=5.0):
    t0 = time.time()
    last_key = None
    last_change = time.time()
    last_status = None
    while time.time() - t0 < timeout:
        j = mc.get_task(tid)
        st = j.get("status")
        pr = j.get("progress") or {}
        key = (st, pr.get("completed"), pr.get("failed"))
        if key != last_key:
            last_key = key
            last_change = time.time()
        if st != last_status:
            logprint(f"  [task] status={st} progress={pr.get('completed')}/{pr.get('total')}")
            last_status = st
        if st in ("completed", "partial", "failed", "canceled"):
            return j
        if STALL and (time.time() - last_change) > STALL:
            try:
                mc.cancel_task(tid)
            except Exception:
                pass
            raise mc.JobStalled(f"task {tid} 停滞 {STALL}s（status={st}），已取消")
        time.sleep(poll)
    raise TimeoutError(f"task {tid} 超时 ({timeout}s)")


def run_batch(files, manifest):
    t0 = time.time()
    try:
        mc.health(timeout=4, retries=1)
    except mc.ServiceDown:
        logprint("  [service-down] 健康预检失败，本批跳过")
        return "service_down"

    meta = []
    pdf_data = {}
    for fn in files:
        p = os.path.join(PDF_DIR, fn)
        data = open(p, "rb").read()
        meta.append({"file_name": fn, "bytes": len(data),
                     "sha256sum": hashlib.sha256(data).hexdigest()})
        pdf_data[fn] = data
    try:
        created = mc.create_task(meta, TIER, formats=("default",), ocr_mode="auto")
    except Exception as e:
        logprint(f"  [create-fail] {str(e)[:150]}")
        for fn in files:
            with lock:
                manifest[fn] = {"status": "upload_failed", "error": "create_task: " + str(e)[:250]}
        return
    tid = created["task_id"]
    name_by_fid = {f["file_id"]: f["file_name"] for f in created.get("files", [])}

    for f in created.get("files", []):
        fid, fn = f["file_id"], f["file_name"]
        try:
            mc.upload_file(tid, fid, pdf_data[fn], timeout=600)
        except Exception as e:
            logprint(f"  [upload-fail] {fn[:52]}: {str(e)[:150]}")
            with lock:
                manifest[fn] = {"status": "upload_failed", "error": str(e)[:300]}

    logprint(f"  [task] {tid} 提交 {len(files)} 篇 (tier={TIER})")

    try:
        j = wait_task(tid)
    except mc.ServiceDown as e:
        logprint(f"  [service-down] {tid}: {str(e)[:150]}")
        for fn in files:
            with lock:
                manifest[fn] = {"status": "service_down", "task_id": tid}
        return "service_down"
    except mc.JobStalled as e:
        logprint(f"  [stalled] {tid}: {str(e)[:120]}")
        for fn in files:
            with lock:
                manifest[fn] = {"status": "stalled", "task_id": tid}
        return
    except Exception as e:
        logprint(f"  [task-timeout] {tid}: {e}")
        for fn in files:
            with lock:
                manifest[fn] = {"status": "job_timeout", "task_id": tid}
        return

    for fr in (j.get("files") or []):
        fid = fr.get("file_id")
        fn = name_by_fid.get(fid) or fr.get("file_name")
        fstatus = fr.get("status")
        if fstatus in ("completed", "partial"):
            stem = stem_of(fn)
            target = os.path.join(PARSE_DIR, stem)
            os.makedirs(target, exist_ok=True)
            zp = os.path.join(target, "_raw.zip")
            try:
                content = mc.download(fid)
                with open(zp, "wb") as f:
                    f.write(content)
                with zipfile.ZipFile(zp) as z:
                    z.extractall(target)
                open(os.path.join(target, "_tier"), "w", encoding="utf-8").write(TIER)
                md_path = os.path.join(target, "markdown.md")
                md_sz = os.path.getsize(md_path) if os.path.isfile(md_path) else 0
                if md_sz <= 0:
                    with lock:
                        manifest[fn] = {"status": "empty_output", "task_id": tid}
                    logprint(f"  [empty-md] {fn[:52]} 产物为空，待重试")
                    continue
                try:
                    copy_to_md(stem)
                except Exception as e:
                    logprint(f"  [copy-warn] {fn[:40]}: {str(e)[:100]}")
                with lock:
                    manifest[fn] = {"status": "parsed", "task_id": tid, "dir": target, "md_bytes": md_sz}
                logprint(f"  [ok] {fn[:55]} ({fstatus}, {md_sz}B)")
            except Exception as e:
                with lock:
                    manifest[fn] = {"status": "download_failed", "error": str(e)[:300]}
                logprint(f"  [dl-fail] {fn[:50]}: {str(e)[:120]}")
        else:
            with lock:
                manifest[fn] = {"status": "failed", "task_id": tid, "file_status": fstatus}
            logprint(f"  [file-fail] {fn[:52]} ({fstatus})")

    logprint(f"  [batch done] {len(files)} 篇, 用时 {time.time()-t0:.1f}s")
    time.sleep(2)


def wait_healthy(max_wait=900):
    t0 = time.time()
    first = True
    while time.time() - t0 < max_wait:
        try:
            d = mc.health()
            if isinstance(d, dict) and d.get("status") == "ok":
                return True
        except Exception:
            pass
        if first:
            logprint(f"  [health] MinerU 暂不可达，等待恢复（最多 {max_wait}s）…")
            first = False
        time.sleep(10)
    return False


def main():
    manifest = load_manifest()
    pdf_stem_to_fn = {}
    for f in os.listdir(PDF_DIR):
        if f.lower().endswith(".pdf"):
            pdf_stem_to_fn.setdefault(stem_of(f), f)
    reconciled = 0
    if os.path.isdir(PARSE_DIR):
        for stem in os.listdir(PARSE_DIR):
            sp = os.path.join(PARSE_DIR, stem, "markdown.md")
            if not os.path.isfile(sp) or os.path.getsize(sp) <= 0:
                continue
            tf = os.path.join(PARSE_DIR, stem, "_tier")
            if os.path.exists(tf) and open(tf, encoding="utf-8").read().strip() not in ("standard", "advanced", "flash"):
                continue
            fn = pdf_stem_to_fn.get(stem)
            if not fn:
                continue
            if manifest.get(fn, {}).get("status") != "parsed":
                manifest[fn] = {"status": "parsed", "dir": os.path.join(PARSE_DIR, stem), "reconciled": True}
                reconciled += 1
    if reconciled:
        logprint(f"[reconcile] 从磁盘补回 {reconciled} 条已解析记录")
        save_manifest(manifest)

    files = sorted(f for f in os.listdir(PDF_DIR) if f.lower().endswith(".pdf"))
    files, dupes = dedupe(files)
    for fn in dupes:
        manifest.setdefault(fn, {"status": "dup_skipped", "reason": "内容 MD5 去重"})
    todo = [f for f in files if manifest.get(f, {}).get("status") != "parsed"]
    new_items = [f for f in todo if f not in manifest]
    retry_items = [f for f in todo if f in manifest]
    todo = new_items + retry_items
    if LIMIT:
        todo = todo[:LIMIT]
    if MAX_JOBS:
        todo = todo[:MAX_JOBS * BATCH]
    logprint(f"总量 {len(files)}, 待处理 {len(todo)}, 档位 {TIER}, BATCH={BATCH}, 自动重试轮数 {ROUNDS}")

    t_all = time.time()
    current = todo
    for rnd in range(ROUNDS + 1):
        if not current:
            break
        if rnd > 0:
            logprint(f"\n=== 自动重试轮 {rnd}/{ROUNDS}（{len(current)} 篇）===")
            time.sleep(15)
        if not wait_healthy(max_wait=900):
            logprint("[health] 等待超时，本轮退出")
            break
        failed = []
        for i in range(0, len(current), BATCH):
            chunk = current[i:i + BATCH]
            logprint(f"\n=== 轮{rnd} 批次 {i//BATCH+1}/{(len(current)+BATCH-1)//BATCH} ({len(chunk)} 篇) ===")
            res = None
            try:
                res = run_batch(chunk, manifest)
            except Exception:
                traceback.print_exc()
            save_manifest(manifest)
            if res == "service_down":
                logprint("  [service-down] 提前结束本轮")
                return
            for fn in chunk:
                if manifest.get(fn, {}).get("status") != "parsed":
                    failed.append(fn)
            done = sum(1 for v in manifest.values() if v.get("status") == "parsed")
            logprint(f"  累计已解析: {done}/{len(files)}  总耗时 {time.time()-t_all:.0f}s")
        current = failed

    save_manifest(manifest)
    done = sum(1 for v in manifest.values() if v.get("status") == "parsed")
    skipped = sum(1 for v in manifest.values() if v.get("status") == "dup_skipped")
    fail = sum(1 for v in manifest.values() if v.get("status") not in ("parsed", "dup_skipped"))
    logprint(f"\n完成: parsed={done}, dup_skipped={skipped}, 仍未成功={fail}, 总耗时 {(time.time()-t_all)/60:.1f} 分钟")
    if fail:
        from collections import Counter
        c = Counter(v.get("status") for v in manifest.values()
                    if isinstance(v, dict) and v.get("status") not in ("parsed", "dup_skipped"))
        logprint("剩余失败分布: " + ", ".join(f"{k}={v}" for k, v in c.most_common()))


if __name__ == "__main__":
    main()
