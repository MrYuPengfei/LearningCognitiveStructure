#!/usr/bin/env python3
"""
论文笔记流水线状态核验（唯一权威来源 = 磁盘）

用法:
    python _pipeline/status.py          # 摘要
    python _pipeline/status.py --list   # 摘要 + 在途明细 + 待派清单

设计原则:
  - 完成与否只看磁盘上是否已有 >500B 的笔记 .md，不看任何代理报告
  - inflight.txt = 已派发但磁盘尚无笔记的 stem（幽灵条目会被识别出来）
  - true_pending.txt = 已解析但磁盘无笔记的全部 stem
"""
import os
import glob
import sys

BASE = os.environ.get("NOTE_BASE") or os.getcwd()
# 也可直接传：python status.py <库根目录>
MIN_NOTE_BYTES = 500
CAP = int(os.environ.get("NOTE_CONCURRENCY", "16"))


def read_lines(path):
    if not os.path.exists(path):
        return []
    out = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line and not line.startswith("#"):
                out.append(line)
    return out


def citekey(stem):
    """STEM 以数字开头 → 整个 STEM；否则取首个 '-' 之前的部分。"""
    return stem if stem[0].isdigit() else stem.split("-")[0]


def scan():
    dirs = [os.path.basename(p) for p in glob.glob(os.path.join(BASE, "*")) if os.path.isdir(p)]
    parsed = sorted(d[:-9] for d in dirs if d.endswith("_markdown"))
    written = {}
    for s in parsed:
        d = os.path.join(BASE, s)
        if not os.path.isdir(d):
            continue
        for f in os.listdir(d):
            if f.endswith(".md"):
                p = os.path.join(d, f)
                try:
                    size = os.path.getsize(p)
                except OSError:
                    continue
                if size > MIN_NOTE_BYTES:
                    written[s] = (f, size)
                    break
    return parsed, written


def main():
    verbose = "--list" in sys.argv
    parsed, written = scan()

    inflight_raw = read_lines(os.path.join(BASE, "_pipeline", "inflight.txt"))
    inflight = []
    seen = set()
    for x in inflight_raw:
        s = x.split("\t")[0]
        if s and s not in seen:
            seen.add(s)
            inflight.append(s)

    pending = [s for s in parsed if s not in written]
    pending_set = set(pending)

    # 幽灵条目：登记在途但既无笔记、也不在待写清单里（通常是目录名拼写错误）
    ghosts = [s for s in inflight if s not in written and s not in pending_set]
    # 已完成但未从在途表移除
    stale = [s for s in inflight if s in written]

    waiting = [s for s in inflight if s not in written]
    available = [s for s in pending if s not in set(waiting)]

    print("=" * 68)
    print("  文献笔记流水线状态")
    print("=" * 68)
    print(f"  已解析         : {len(parsed):>4} 篇")
    print(f"  笔记已写(磁盘)  : {len(written):>4} 篇")
    print(f"  待写总计        : {len(pending):>4} 篇")
    print(f"  在途(已派未落盘): {len(waiting):>4} / 上限 {CAP}")
    print(f"  可立即派发      : {len(available):>4} 篇")
    if stale:
        print(f"  ⚠ 在途表残留(已写盘应清理): {len(stale)}")
    if ghosts:
        print(f"  ⚠ 幽灵在途(需核查/重派): {len(ghosts)}")
    pct = 100.0 * len(written) / len(parsed) if parsed else 0
    bar_n = int(pct / 2.5)
    print(f"  进度            : [{'█' * bar_n}{'░' * (40 - bar_n)}] {pct:.1f}%")
    print("=" * 68)

    if verbose:
        if waiting:
            print("\n【在途明细】")
            for s in waiting:
                print(f"  · {s}")
        if ghosts:
            print("\n【幽灵在途】")
            for s in ghosts:
                print(f"  ✗ {s}")
        if available:
            print(f"\n【待派清单（前 30 / 共 {len(available)}）】")
            for s in available[:30]:
                print(f"  - {s}")

    # 供外部脚本调用
    if "--json" in sys.argv:
        import json
        print(json.dumps({
            "parsed": len(parsed),
            "written": len(written),
            "pending": len(pending),
            "inflight": len(waiting),
            "available": len(available),
            "ghost": ghosts,
            "stale": stale,
        }, ensure_ascii=False))


if __name__ == "__main__":
    main()
