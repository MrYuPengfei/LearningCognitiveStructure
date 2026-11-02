#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
merge_terms.py — 合并各批次识别出的术语 JSON，去重后追加写入 CSV 词表。

输入:
    <批次目录>/batch*.json    每份形如 {"en": ["term", ...], "cn": ["术语", ...]}
    （键名也接受 english / chinese / zh 等常见别名）

输出:
    英文词表与中文词表各一份，纯文本逐行、无表头无引号（沿用既有词表格式）。
    已存在的条目不会被覆盖，只追加新词，顺序为「旧表原序 + 新增」。

用法:
    python merge_terms.py --batches <批次目录> --en <英文csv> --cn <中文csv>
    python merge_terms.py --batches ... --en ... --cn ... --dry-run

处理规则:
    1. clean : 去 BOM、去首尾标点空白、压缩内部空白
    2. 归类 : 按是否含汉字自动分派，修正子代理放错桶的情况
    3. 去重 : 同一表内按小写去重，保留首次出现
    4. 过滤 : 英文去纯符号/纯数字/超长；中文去含句读/超长
    5. 比对 : 与既有 CSV 按小写去重后追加
"""

import argparse
import glob
import io
import json
import os
import re
import sys

CN_RE = re.compile(r"[\u4e00-\u9fff]")
EN_RE = re.compile(r"[A-Za-z]")
STRIP_TAIL = "。．.，,；;：:、 　\t"
MAX_EN = 70
MAX_CN = 40

EN_KEYS = ("en", "eng", "english", "terms_en")
CN_KEYS = ("cn", "zh", "chinese", "terms_cn")


def load_rows(path):
    if not path or not os.path.exists(path):
        return []
    rows = []
    with io.open(path, encoding="utf-8-sig") as fh:
        for line in fh:
            line = line.strip().strip("\ufeff")
            if line:
                rows.append(line)
    return rows


def pick(data, keys):
    for k in keys:
        if isinstance(data, dict) and isinstance(data.get(k), list):
            return data[k]
    return []


def clean(text):
    text = str(text).replace("\ufeff", "").strip()
    text = re.sub(r"\s+", " ", text)
    text = text.rstrip(STRIP_TAIL)
    return text.strip()


def bad_en(term):
    if not term or len(term) > MAX_EN:
        return True
    if not EN_RE.search(term):
        return True
    return bool(re.fullmatch(r"[\W\d_]+", term))


def bad_cn(term):
    if not term or len(term) > MAX_CN:
        return True
    return bool(re.search(r"[，。；、！？；：]", term))


def dedup(rows):
    seen, out = set(), []
    for row in rows:
        key = row.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(row)
    return out


def main():
    ap = argparse.ArgumentParser(description="合并批次术语 JSON 并写入 CSV 词表")
    ap.add_argument("--batches", required=True, help="批次 JSON 所在目录")
    ap.add_argument("--en", required=True, help="英文词表 CSV 路径")
    ap.add_argument("--cn", required=True, help="中文词表 CSV 路径")
    ap.add_argument("--pattern", default="batch*.json", help="批次文件通配符")
    ap.add_argument("--dry-run", action="store_true", help="只统计不写文件")
    args = ap.parse_args()

    files = sorted(glob.glob(os.path.join(args.batches, args.pattern)))
    if not files:
        sys.exit("在 %s 未匹配到 %s" % (args.batches, args.pattern))

    raw_en, raw_cn = [], []
    for path in files:
        try:
            with io.open(path, encoding="utf-8") as fh:
                data = json.load(fh)
        except Exception as exc:
            print("  [warn] 跳过无法解析的 %s: %s" % (os.path.basename(path), exc))
            continue
        raw_en += pick(data, EN_KEYS)
        raw_cn += pick(data, CN_KEYS)

    print("批次文件 %d 份，原始条目：en %d / cn %d" % (len(files), len(raw_en), len(raw_cn)))

    en_rows, cn_rows = [], []
    for item in raw_en:
        item = clean(item)
        if not item:
            continue
        (cn_rows if CN_RE.search(item) else en_rows).append(item)
    for item in raw_cn:
        item = clean(item)
        if item:
            cn_rows.append(item)

    en_rows = [t for t in dedup(en_rows) if not bad_en(t)]
    cn_rows = [t for t in dedup(cn_rows) if not bad_cn(t)]

    old_en = load_rows(args.en)
    old_cn = load_rows(args.cn)
    seen_en = {t.lower() for t in old_en}
    seen_cn = {t.lower() for t in old_cn}
    new_en = [t for t in en_rows if t.lower() not in seen_en]
    new_cn = [t for t in cn_rows if t.lower() not in seen_cn]

    print("既有：en %d 条 / cn %d 条" % (len(old_en), len(old_cn)))
    print("清洗后：en %d 条 / cn %d 条" % (len(en_rows), len(cn_rows)))
    print("与既有重复被过滤：en %d 条 / cn %d 条" % (len(en_rows) - len(new_en), len(cn_rows) - len(new_cn)))
    print("实际新增：en %d 条 / cn %d 条" % (len(new_en), len(new_cn)))

    if args.dry_run:
        print("\n[dry-run] 未写入。新增英文前 30：")
        for t in new_en[:30]:
            print("  ", t)
        print("新增中文前 30：")
        for t in new_cn[:30]:
            print("  ", t)
        return

    # 原子写入：先写同目录临时文件再 os.replace 覆盖，避免中途异常留下截断的词表
    for path, rows in ((args.en, old_en + new_en), (args.cn, old_cn + new_cn)):
        write_atomic(path, rows)
        print("  %s  -> %d 条" % (path, len(rows)))

    print("\n已写入两个词表。")


def write_atomic(path, rows):
    """原子写入：同目录 .tmp -> os.replace，中断不会破坏原文件。

    Windows 上目标文件被编辑器/Excel 占用时 os.replace 会抛 PermissionError，
    此时回退为直接写入，保证功能可用（已读取旧内容，仍为追加语义）。
    """
    tmp = path + ".tmp"
    with io.open(tmp, "w", encoding="utf-8", newline="") as fh:
        for t in rows:
            fh.write(t + "\n")
    try:
        os.replace(tmp, path)
    except PermissionError:
        print("  [warn] %s 被占用，无法原子替换，改为直接写入" % os.path.basename(path))
        with io.open(path, "w", encoding="utf-8", newline="") as fh:
            for t in rows:
                fh.write(t + "\n")
        try:
            os.remove(tmp)
        except OSError:
            pass


if __name__ == "__main__":
    main()
