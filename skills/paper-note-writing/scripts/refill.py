#!/usr/bin/env python3
"""
补位：清理在途表中已写盘/幽灵的条目，按剩余槽位生成新批次。

用法:
    python _pipeline/refill.py            # 只看看有多少空槽
    python _pipeline/refill.py 8          # 生成最多 8 篇的新批次

输出最后一行固定为 `BATCH <path>` 或 `NOOP`，便于外部读取。
"""
import os
import sys
import json
import glob
import datetime

BASE = os.environ.get("NOTE_BASE") or os.getcwd()
# 也可直接传：python status.py <库根目录>
PIPE = os.path.join(BASE, "_pipeline")
MIN_NOTE_BYTES = 500
CAP = int(os.environ.get("NOTE_CONCURRENCY", "16"))


def citekey(stem):
    return stem if stem[0].isdigit() else stem.split("-")[0]


def scan():
    dirs = [os.path.basename(p) for p in glob.glob(os.path.join(BASE, "*")) if os.path.isdir(p)]
    parsed = sorted(d[:-9] for d in dirs if d.endswith("_markdown"))
    written = set()
    for s in parsed:
        d = os.path.join(BASE, s)
        if not os.path.isdir(d):
            continue
        for f in os.listdir(d):
            if f.endswith(".md") and os.path.getsize(os.path.join(d, f)) > MIN_NOTE_BYTES:
                written.add(s)
                break
    return parsed, written


def main():
    want = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    parsed, written = scan()
    parsed_set = set(parsed)

    inflight = []
    seen = set()
    for line in open(os.path.join(PIPE, "inflight.txt"), encoding="utf-8"):
        s = line.split("\t")[0].strip()
        if s and not s.startswith("#") and s not in seen:
            seen.add(s)
            inflight.append(s)

    # 清理：已写盘 / 目录不存在
    kept, dropped = [], []
    for s in inflight:
        if s in written or s not in parsed_set:
            dropped.append(s)
        else:
            kept.append(s)
    with open(os.path.join(PIPE, "inflight.txt"), "w", encoding="utf-8") as fh:
        for s in kept:
            fh.write(f"{s}\t{citekey(s)}\n")

    free = CAP - len(kept)
    print(f"已写 {len(written)}/{len(parsed)} | 在途 {len(kept)} | 空槽 {free} | 清理 {len(dropped)}")
    for d in dropped:
        print(f"   清理: {d}")

    take = max(0, min(want, free))
    if take == 0:
        print("NOOP")
        return

    blocked = set(kept)
    todo = [s for s in parsed if s not in written and s not in blocked]
    picks = todo[:take]
    if not picks:
        print("NOOP")
        return

    seq = datetime.datetime.now().strftime("batch_%Y%m%d_%H%M%S")
    outdir = os.path.join(PIPE, "batches")
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, seq + ".json")
    entries = [{"i": i, "stem": s, "citekey": citekey(s)} for i, s in enumerate(picks)]
    with open(path, "w", encoding="utf-8") as fh:
        json.dump({"batch": seq, "entries": entries}, fh, ensure_ascii=False, indent=1)
    with open(os.path.join(PIPE, "inflight.txt"), "a", encoding="utf-8") as fh:
        for s in picks:
            fh.write(f"{s}\t{citekey(s)}\n")

    print(f"本批 {len(picks)} 篇（在途 → {len(kept)+len(picks)}）")
    for e in entries:
        print(f"  [{e['i']}] {e['citekey']}")
    print(f"BATCH {path}")


if __name__ == "__main__":
    main()
