#!/usr/bin/env python3
"""
笔记库质量审计（只认磁盘，不看代理报告）

用法:
    python _pipeline/audit.py            # 摘要
    python _pipeline/audit.py --verbose  # 列出全部问题
    python _pipeline/audit.py --fix-img  # 修复坏图链接（从 _markdown/images 复制缺失图）

检查项
------
1. 字数：NOTE_GUIDE 定「典型篇幅 4000–12000 字」，故 <4000 记为不足，<6000 记为偏短（仅提示）
2. 结构：H1 / 附录 A / 附录 B / 二级章节数
3. 图片：正文 `![](images/x)` 引用的文件是否真实存在于该笔记目录
4. 冗余：目录下是否残留非 citekey 开头的临时 .md

注意：定位笔记文件必须用 citekey 规则（STEM 首段），
不能按 os.listdir 顺序取第一个 .md —— 否则会误读到 _appendixA_table.md 之类的中间产物。
"""
import os
import re
import shutil
import sys

BASE = os.environ.get("NOTE_BASE") or os.getcwd()
# 也可直接传：python status.py <库根目录>
SHORT_HINT = 6000
SHORT_FAIL = 4000


def citekey(stem: str) -> str:
    return stem if stem[0].isdigit() else stem.split("-")[0]


def parsed_stems():
    out = []
    for d in os.listdir(BASE):
        p = os.path.join(BASE, d)
        if os.path.isdir(p) and d.endswith("_markdown"):
            out.append(d[:-9])
    return sorted(out)


def find_note(stem):
    """按 citekey 规则定位笔记文件（忽略中间产物）。"""
    d = os.path.join(BASE, stem)
    if not os.path.isdir(d):
        return None
    ck = citekey(stem)
    cands = [f for f in os.listdir(d)
             if f.endswith(".md") and f.startswith(ck) and os.path.getsize(os.path.join(d, f)) > 500]
    if cands:
        return os.path.join(d, cands[0])
    return None


def audit():
    res = {
        "total": 0, "chars": [], "under_fail": [], "under_hint": [],
        "no_h1": [], "no_appendixA": [], "no_appendixB": [], "few_sections": [],
        "bad_img": [], "stray_md": [],
    }
    for stem in parsed_stems():
        note = find_note(stem)
        if not note:
            continue
        res["total"] += 1
        d = os.path.dirname(note)
        t = open(note, encoding="utf-8", errors="ignore").read()

        cjk = len(re.findall(r"[\u4e00-\u9fff]", t))
        res["chars"].append(cjk)
        if cjk < SHORT_FAIL:
            res["under_fail"].append((stem, cjk))
        elif cjk < SHORT_HINT:
            res["under_hint"].append((stem, cjk))

        if not re.search(r"^#\s+\S", t, re.M):
            res["no_h1"].append(stem)
        if not re.search(r"附录\s*A", t):
            res["no_appendixA"].append(stem)
        if not re.search(r"附录\s*B", t):
            res["no_appendixB"].append(stem)
        if len(re.findall(r"^##\s+", t, re.M)) < 6:
            res["few_sections"].append(stem)

        # 去掉行内代码与代码块后再找图片引用：
        # 笔记正文里常有 `![](images/xxx.jpg)` 这类**举例说明**（放在反引号里），
        # 它们不是真实嵌入，计入会造成误报。
        stripped = re.sub(r"```.*?```", "", t, flags=re.S)
        stripped = re.sub(r"`[^`\n]*`", "", stripped)
        for rel in re.findall(r"!\[[^\]]*\]\((images/[^)]+)\)", stripped):
            if not os.path.exists(os.path.join(d, rel)):
                res["bad_img"].append((stem, rel))

        ck = citekey(stem)
        for f in os.listdir(d):
            if f.endswith(".md") and not f.startswith(ck):
                res["stray_md"].append((stem, f))
    return res


def fix_images(res):
    """从 _markdown/images/ 复制缺失的图片到笔记目录 images/。"""
    fixed = missed = 0
    for stem, rel in res["bad_img"]:
        base = os.path.basename(rel)
        src = os.path.join(BASE, stem + "_markdown", "images", base)
        dst_dir = os.path.join(BASE, stem, "images")
        dst = os.path.join(dst_dir, base)
        if os.path.exists(dst):
            continue
        if os.path.exists(src):
            os.makedirs(dst_dir, exist_ok=True)
            shutil.copy2(src, dst)
            fixed += 1
        else:
            missed += 1
            print(f"  ✗ 源目录也无此图，需人工处理: {stem[:40]} -> {base}")
    return fixed, missed


def main():
    res = audit()
    c = sorted(res["chars"])
    n = res["total"]
    print("=" * 66)
    print("  笔记库质量审计")
    print("=" * 66)
    print(f"  笔记总数        : {n}")
    if c:
        print(f"  中文字数        : min={c[0]}  p25={c[n//4]}  中位={c[n//2]}  "
              f"p75={c[n*3//4]}  max={c[-1]}")
    print(f"  篇幅不足(<4000) : {len(res['under_fail'])}   [NOTE_GUIDE 定 4000–12000 为典型区间]")
    print(f"  偏短(4000-6000) : {len(res['under_hint'])}   [在典型区间内，仅提示]")
    print(f"  缺 H1           : {len(res['no_h1'])}")
    print(f"  缺附录 A        : {len(res['no_appendixA'])}")
    print(f"  缺附录 B        : {len(res['no_appendixB'])}")
    print(f"  二级章节 < 6    : {len(res['few_sections'])}")
    print(f"  坏图链接        : {len(res['bad_img'])}")
    print(f"  残留临时 .md    : {len(res['stray_md'])}")
    print("=" * 66)

    if "--fix-img" in sys.argv:
        fixed, missed = fix_images(res)
        print(f"\n  已修复坏图链接: {fixed} 个；源目录缺失需人工处理: {missed} 个")

    if "--verbose" in sys.argv:
        for key in ["under_fail", "no_h1", "no_appendixA", "no_appendixB", "few_sections", "stray_md"]:
            if res[key]:
                print(f"\n【{key}】")
                for x in res[key][:25]:
                    print(f"   {str(x)[:88]}")
        if res["bad_img"]:
            print(f"\n【bad_img 前 20】")
            for s, r in res["bad_img"][:20]:
                print(f"   {s[:44]:46} {r}")


if __name__ == "__main__":
    main()
