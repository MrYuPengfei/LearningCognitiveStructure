# -*- coding: utf-8 -*-
"""
批量调用 MinerU 解析 papers/pdf 全库
- 并发上传 -> 分批建任务(每批 BATCH 个文件) -> 轮询 -> 下载 zip -> 解压
- 断点续跑：已产出 markdown.md 的跳过
- 状态落盘 manifest.json
"""
import os, sys, json, time, zipfile, threading, traceback, shutil, hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mineru_client as mc

# ---- 路径全部由环境变量注入，便于在不同文献库复用 ----
ROOT = os.environ.get("LIT_ROOT", os.getcwd())          # 文献库根目录
PDF_DIR = os.environ.get("LIT_PDF_DIR", os.path.join(ROOT, "pdf"))
PARSE_DIR = os.environ.get("LIT_PARSE_DIR", os.path.join(ROOT, "_parse"))
PAPERSMD = os.environ.get("LIT_MD_DIR", os.path.join(ROOT, "md"))
_SHARD = os.environ.get("MINERU_SHARD", "").replace("/", "_")
MANIFEST = os.path.join(ROOT, "_pipeline",
                        f"manifest_{_SHARD}.json" if _SHARD else "manifest.json")

BATCH = int(os.environ.get("MINERU_BATCH", "10"))
UPLOAD_WORKERS = int(os.environ.get("MINERU_UPLOAD_WORKERS", "4"))
TIER = os.environ.get("MINERU_TIER", "standard")
LIMIT = int(os.environ.get("MINERU_LIMIT", "0"))   # 0 = 全部
MAX_JOBS = int(os.environ.get("MINERU_MAX_JOBS", "0"))  # 0 = 不限

os.makedirs(PARSE_DIR, exist_ok=True)
lock = threading.Lock()
os.makedirs(os.path.join(ROOT, "_pipeline"), exist_ok=True)
LOG = os.path.join(ROOT, "_pipeline", "batch_parse.log")


def logprint(*a):
    """实时日志：同时输出到 stdout 与 batch_parse.log，便于看门狗/人随时查看进度。"""
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
    """原子写：每进程独立临时文件（避免多看门狗并发写同一 .tmp 触发 PermissionError），
    写入失败（WSL2 共享盘偶发锁）重试 5 次。"""
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


def dedupe_pdf_list(files):
    """按内容指纹去重：同一 PDF 若以多个文件名存在，只解析第一个。

    背景（2026-10-23）：papers/pdf 曾有 198 组 MD5 相同的重复文件
    （Anon 命名 vs 真名命名、'a' 后缀、'- 副本'），导致同一篇论文被
    MinerU 重复解析、笔记重复生成。此处前置去重，避免再次发生。
    保留优先级：真名 > 匿名；短名 > 长名。
    """
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
        group.sort(key=lambda n: (n.split("-")[0].lower().startswith("anon"),
                                  "副本" in n, len(n)))
        keep.append(group[0])
        dropped.extend(group[1:])

    if dropped:
        print(f"[dedupe] 内容重复的 PDF：{len(files)} -> {len(keep)}，"
              f"跳过 {len(dropped)} 个")
        for fn in dropped[:10]:
            print(f"   [dup] {fn}")
        if len(dropped) > 10:
            print(f"   ... 另有 {len(dropped) - 10} 个")
    return keep, dropped


def copy_stem_to_papersmd(stem):
    """把 _parse/<stem> 的 markdown.md + images 复制到 papers/md/<stem>_markdown/，
    文件名用 markdown.md，避免覆盖 papers/md 现有 <基名>.md。"""
    src_dir = os.path.join(PARSE_DIR, stem)
    src_md = os.path.join(src_dir, "markdown.md")
    if not os.path.exists(src_md):
        return
    dest_dir = os.path.join(PAPERSMD, stem + "_markdown")
    os.makedirs(dest_dir, exist_ok=True)
    shutil.copy2(src_md, os.path.join(dest_dir, "markdown.md"))
    src_img = os.path.join(src_dir, "images")
    if os.path.isdir(src_img):
        dest_img = os.path.join(dest_dir, "images")
        os.makedirs(dest_img, exist_ok=True)
        for fn in os.listdir(src_img):
            sp = os.path.join(src_img, fn)
            if os.path.isfile(sp):
                shutil.copy2(sp, os.path.join(dest_img, fn))


def wait_healthy(max_wait=900):
    """批前健康门控：MinerU 不可达时等待其恢复，最多 max_wait 秒。
    返回 True=健康；False=等待超时（调用方应退出本轮，交给看门狗续跑）。"""
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


def do_upload(fn, attempts=4):
    """上传单文件（带指数退避重试）。WSL2 端口代理偶发重置是主因，
    多数失败可在 2~3 次内恢复；全部失败才抛错给调用方标记 upload_failed。"""
    p = os.path.join(PDF_DIR, fn)
    last = None
    for i in range(attempts):
        try:
            fid, _ = mc.upload_file(p)
            return fn, fid
        except Exception as e:
            last = e
            if i < attempts - 1:
                wait = 3 * (2 ** i)   # 3, 6, 12s
                logprint(f"  [upload-retry {i+1}/{attempts}] {fn[:52]}: {str(e)[:90]}，{wait}s 后重试")
                time.sleep(wait)
    raise last


def pick_output_file_id(of):
    """从 files[].output_files 提取产物 file_id。兼容两种形态：
      - dict: {"zip": {"file_id": ...}, "markdown": {...}}（当前部署）
      - list: [{"purpose": "parse_output", "file_id": ...}, ...]（官方 4.0 artifact 数组）
    """
    if isinstance(of, dict):
        zf = of.get("zip")
        if isinstance(zf, dict) and zf.get("file_id"):
            return zf["file_id"]
        if isinstance(zf, str):
            return zf
        for v in of.values():
            if isinstance(v, dict) and v.get("file_id"):
                return v["file_id"]
            if isinstance(v, str) and v.startswith("file-"):
                return v
        return None
    if isinstance(of, list):
        cand = [it for it in of if isinstance(it, dict) and (it.get("file_id") or it.get("id"))]
        if not cand:
            return None
        for it in cand:
            if it.get("purpose") == "parse_output":
                return it.get("file_id") or it.get("id")
        it = cand[0]
        return it.get("file_id") or it.get("id")
    return None


def run_batch(files, manifest):
    """上传一批 + 建一个任务 + 等结果 + 下载解压"""
    t0 = time.time()
    # 服务可用性预检：服务宕机时立即返回哨兵，避免对死服务空转/批量标记失败
    try:
        mc.health(timeout=4, retries=1)
    except mc.ServiceDown:
        logprint("  [service-down] 健康预检失败，本批跳过，交看门狗等待恢复")
        return "service_down"
    results = {}
    with ThreadPoolExecutor(max_workers=UPLOAD_WORKERS) as ex:
        futs = {ex.submit(do_upload, fn): fn for fn in files}
        for fut in as_completed(futs):
            fn = futs[fut]
            try:
                r = fut.result()
                results[r[0]] = r[1]
            except Exception as e:
                logprint(f"  [upload-fail] {fn[:52]}: {str(e)[:150]}")
                with lock:
                    manifest[fn] = {"status": "upload_failed", "error": str(e)[:300]}

    ok = [fn for fn in files if fn in results]
    if not ok:
        return

    try:
        job = mc.create_job([results[fn] for fn in ok], tier=TIER,
                            formats=["markdown", "zip"])
    except Exception as e:
        logprint(f"  [job-create-fail] {str(e)[:150]}")
        with lock:
            for fn in ok:
                manifest[fn] = {"status": "upload_failed", "error": "create_job: " + str(e)[:250]}
        return
    jid = job["job_id"]
    logprint(f"  [job] {jid} 提交 {len(ok)} 篇 (tier={TIER})")
    try:
        j = mc.wait_job(jid, timeout=3600, poll=5.0, verbose=False)
    except mc.ServiceDown as e:
        logprint(f"  [service-down] {jid}: {str(e)[:150]} —— 停止本轮，等待服务恢复")
        with lock:
            for fn in ok:
                manifest[fn] = {"status": "service_down", "job_id": jid}
        return "service_down"
    except mc.JobStalled as e:
        # 卡在 queued/running 不动：已自动取消，标记 stalled 交由重试轮处理，
        # 不再为一个 job 干等 3600s 堵住后面所有任务
        logprint(f"  [stalled] {jid}: {str(e)[:120]}")
        with lock:
            for fn in ok:
                manifest[fn] = {"status": "stalled", "job_id": jid}
        return
    except Exception as e:
        logprint(f"  [job-timeout] {jid}: {e}")
        with lock:
            for fn in ok:
                manifest[fn] = {"status": "job_timeout", "job_id": jid}
        return

    for fr in j.get("files") or []:
        name = fr.get("name")
        st = fr.get("status")
        of = fr.get("output_files") or {}
        fid = pick_output_file_id(of)
        # name 可能是上传时的文件名
        if not fid:
            with lock:
                manifest[name] = {"status": "no_output", "file_status": st}
            logprint(f"  [no-output] {name[:52]} ({st})")
            continue
        target_dir = os.path.join(PARSE_DIR, stem_of(name))
        os.makedirs(target_dir, exist_ok=True)
        zp = os.path.join(target_dir, "_raw.zip")
        try:
            mc.download(fid, zp)
            with zipfile.ZipFile(zp) as z:
                z.extractall(target_dir)
            # 注意：不删除 _raw.zip —— 批量删除会触发沙箱的批量删除保护，导致任务中断。
            # 冗余 zip 约 2GB，磁盘充足，保留以换取可续跑性。
            # 档位标记：只有 standard/advanced 档的产出才允许用于生成笔记
            open(os.path.join(target_dir, "_tier"), "w", encoding="utf-8").write(TIER)
            # 产物校验：markdown.md 必须存在且非空才算解析成功
            md_path = os.path.join(target_dir, "markdown.md")
            md_sz = os.path.getsize(md_path) if os.path.isfile(md_path) else 0
            if md_sz <= 0:
                with lock:
                    manifest[name] = {"status": "empty_output", "job_id": jid, "file_status": st}
                logprint(f"  [empty-md] {name[:52]} 产物为空，标记待重试")
                continue
            try:
                copy_stem_to_papersmd(stem_of(name))
            except Exception as e:
                logprint(f"  [copy-warn] {name[:40]}: {str(e)[:100]}")
            with lock:
                manifest[name] = {"status": "parsed", "job_id": jid,
                                  "file_status": st, "dir": target_dir, "md_bytes": md_sz}
            logprint(f"  [ok] {name[:55]} ({st}, {md_sz}B)")
        except Exception as e:
            with lock:
                manifest[name] = {"status": "download_failed", "error": str(e)[:300]}
            logprint(f"  [dl-fail] {name[:50]}: {str(e)[:120]}")

    # 严格串行：本批（BATCH=1）解压完成后，等 2 秒再让调用方提交下一个解析，
    # 避免高频提交压垮 MinerU。
    logprint(f"  [batch done] {len(ok)} 篇, 用时 {time.time()-t0:.1f}s")
    time.sleep(2)


def main():
    manifest = load_manifest()
    # 磁盘自愈：任何已在 _parse 落盘 markdown.md（且档位合格）的 stem，
    # 都标记为 parsed，防止看门狗崩溃/并发写导致 manifest 丢失已解析记录。
    pdf_stem_to_fn = {}
    for f in os.listdir(PDF_DIR):
        if f.lower().endswith(".pdf"):
            pdf_stem_to_fn.setdefault(os.path.splitext(f)[0], f)
    reconciled = 0
    if os.path.isdir(PARSE_DIR):
        for stem in os.listdir(PARSE_DIR):
            sp = os.path.join(PARSE_DIR, stem, "markdown.md")
            if not os.path.isfile(sp) or os.path.getsize(sp) <= 0:
                continue
            tf = os.path.join(PARSE_DIR, stem, "_tier")
            if os.path.exists(tf):
                if open(tf, encoding="utf-8").read().strip() not in ("standard", "advanced", "flash"):
                    continue
            fn = pdf_stem_to_fn.get(stem)
            if not fn:
                continue
            if manifest.get(fn, {}).get("status") != "parsed":
                manifest[fn] = {"status": "parsed", "dir": os.path.join(PARSE_DIR, stem),
                                "reconciled": True}
                reconciled += 1
    if reconciled:
        logprint(f"[reconcile] 从磁盘补回 {reconciled} 条已解析记录")
        save_manifest(manifest)
    files = sorted(f for f in os.listdir(PDF_DIR) if f.lower().endswith(".pdf"))
    # 内容指纹去重：同一 PDF 若以多个文件名存在，只解析其中一个，
    # 避免同一篇论文被重复解析、重复生成笔记（2026-10-23 加入）。
    files, dupes = dedupe_pdf_list(files)
    for fn in dupes:
        manifest.setdefault(fn, {"status": "dup_skipped",
                                 "reason": "内容与另一 PDF 完全相同（MD5 去重）"})
    todo = [f for f in files if manifest.get(f, {}).get("status") != "parsed"]
    # 优先处理从未尝试过的新 PDF（不在 manifest 中），历史失败重试项排后面，
    # 避免少量失败项反复占用周期、拖慢新论文的解析进度。
    new_items = [f for f in todo if f not in manifest]
    retry_items = [f for f in todo if f in manifest]
    todo = new_items + retry_items
    shard = os.environ.get("MINERU_SHARD", "")
    if shard:
        i0, n = shard.split("/")
        todo = [f for f in todo if (files.index(f) % int(n)) == int(i0)]
        logprint(f"[shard {shard}] 本分片 {len(todo)} 篇")
    if LIMIT:
        todo = todo[:LIMIT]
    rounds = int(os.environ.get("MINERU_RETRY_ROUNDS", "2"))  # 首轮之后再自动重试失败项的轮数
    logprint(f"总量 {len(files)}, 待处理 {len(todo)}, 档位 {TIER}, "
             f"BATCH={BATCH}, 上传线程 {UPLOAD_WORKERS}, 自动重试轮数 {rounds}")
    if MAX_JOBS:
        todo = todo[:MAX_JOBS * BATCH]
        logprint(f"本次仅处理 {len(todo)} 篇 (MAX_JOBS={MAX_JOBS})")

    t_all = time.time()
    current = todo
    for rnd in range(rounds + 1):
        if not current:
            break
        if rnd > 0:
            logprint(f"\n=== 自动重试轮 {rnd}/{rounds}（{len(current)} 篇失败项）===")
            time.sleep(15)   # 轮间冷却，给 WSL2 代理/MinerU 喘息
        # 批前健康门控：MinerU 挂了就别空转，交给看门狗续跑
        if not wait_healthy(max_wait=900):
            logprint("[health] 等待超时，本轮退出（看门狗会续跑）")
            break
        failed_this_round = []
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
                logprint("  [service-down] MinerU 不可用，提前结束本轮（看门狗会等服务恢复后续跑）")
                return
            # 统计本批结果：仍未 parsed 的进入下一轮重试
            for fn in chunk:
                if manifest.get(fn, {}).get("status") != "parsed":
                    failed_this_round.append(fn)
            done = sum(1 for v in manifest.values() if v.get("status") == "parsed")
            logprint(f"  累计已解析: {done}/{len(files)}   总耗时 {time.time()-t_all:.0f}s")
        current = failed_this_round

    save_manifest(manifest)
    done = sum(1 for v in manifest.values() if v.get("status") == "parsed")
    skipped = sum(1 for v in manifest.values() if v.get("status") == "dup_skipped")
    fail = sum(1 for v in manifest.values()
               if v.get("status") not in ("parsed", "dup_skipped"))
    logprint(f"\n完成: parsed={done}, dup_skipped={skipped}, 仍未成功={fail}, "
             f"总耗时 {(time.time()-t_all)/60:.1f} 分钟")
    if fail:
        from collections import Counter
        c = Counter(v.get("status") for v in manifest.values()
                    if isinstance(v, dict) and v.get("status") not in ("parsed", "dup_skipped"))
        logprint("剩余失败分布: " + ", ".join(f"{k}={v}" for k, v in c.most_common()))


if __name__ == "__main__":
    main()
