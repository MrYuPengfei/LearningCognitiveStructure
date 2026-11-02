#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
extract_pages.py — 从「图片型 PDF」中抽出页面图片，供视觉识别使用。

适用场景：PDF 由截图/扫描图合并而成（如 img2pdf、Pillow 导出），无文本层，
pypdf 的 extract_text() 逐页返回空串。此时必须先把页面还原成图片。

用法:
    python extract_pages.py <pdf路径> --out <输出目录> [--tag A] [--max-width 1700]
    python extract_pages.py <pdf目录> --out <输出目录> --all      # 处理目录下所有 PDF

输出:
    <输出目录>/<tag>_<页码3位>.jpg     每页一张，长边不超过 --max-width

注意:
    - 默认优先取每页第一张内嵌图（这类 PDF 每页恰好一张整页图）。
    - 同一批内容的多个 PDF（如 xxx.pdf 与 xxx_compressed.pdf）应只传一个，
      否则会重复识别、浪费算力。可先用 --probe 查看各 PDF 页数与首页文本长度来甄别。
"""

import argparse
import glob
import io
import os
import sys

try:
    from pypdf import PdfReader
except ImportError:
    sys.exit("缺少依赖：pip install pypdf pillow")

try:
    from PIL import Image
except ImportError:
    sys.exit("缺少依赖：pip install pillow")


def probe(pdf_path):
    """探查 PDF 是否含文本层，返回 (页数, 首页文本长度)。"""
    reader = PdfReader(pdf_path)
    try:
        head = reader.pages[0].extract_text() or ""
    except Exception:
        head = ""
    return len(reader.pages), len(head.strip())


def extract(pdf_path, out_dir, tag, max_width, quality=88):
    os.makedirs(out_dir, exist_ok=True)
    reader = PdfReader(pdf_path)
    written, skipped = 0, 0

    for idx, page in enumerate(reader.pages):
        try:
            images = page.images
        except Exception as exc:
            print("  [warn] 第 %d 页取图失败: %s" % (idx + 1, exc))
            skipped += 1
            continue

        if not images:
            skipped += 1
            continue

        try:
            pil = Image.open(io.BytesIO(images[0].data))
            pil.load()
        except Exception as exc:
            print("  [warn] 第 %d 页解码失败: %s" % (idx + 1, exc))
            skipped += 1
            continue

        # 统一转 RGB，避免 P/LA/RGBA 模式在另存时异常
        pil = pil.convert("RGB")
        w, h = pil.size
        if max_width and w > max_width:
            pil = pil.resize((max_width, max(1, int(h * max_width / w))), Image.LANCZOS)

        dst = os.path.join(out_dir, "%s_%03d.jpg" % (tag, idx))
        pil.save(dst, "JPEG", quality=quality)
        written += 1

    return len(reader.pages), written, skipped


def main():
    ap = argparse.ArgumentParser(description="从图片型 PDF 抽取页面图片")
    ap.add_argument("target", help="PDF 文件路径，或配合 --all 时的目录路径")
    ap.add_argument("--out", required=True, help="输出目录")
    ap.add_argument("--tag", default=None, help="文件名前缀，默认取 PDF 文件名主干")
    ap.add_argument("--max-width", type=int, default=1700, help="长边上限像素，0 表示不缩放")
    ap.add_argument("--quality", type=int, default=88, help="JPEG 质量")
    ap.add_argument("--all", action="store_true", help="处理目录下所有 PDF")
    ap.add_argument("--probe", action="store_true", help="只探查页数与首页文本长度，不抽图")
    args = ap.parse_args()

    if args.probe:
        targets = ([args.target] if os.path.isfile(args.target)
                   else sorted(glob.glob(os.path.join(args.target, "*.pdf"))))
        for path in targets:
            n, tlen = probe(path)
            kind = "有文本层" if tlen > 0 else "纯图片(需视觉识别)"
            print("%-46s %4d 页  首页文本 %5d 字  -> %s"
                  % (os.path.basename(path), n, tlen, kind))
        return

    if args.all or os.path.isdir(args.target):
        targets = sorted(glob.glob(os.path.join(args.target, "*.pdf")))
    else:
        targets = [args.target]

    if not targets:
        sys.exit("未找到 PDF：%s" % args.target)

    total = 0
    for path in targets:
        n, tlen = probe(path)
        stem = os.path.splitext(os.path.basename(path))[0]
        tag = args.tag or stem[:12]
        if tlen > 0:
            print("%s 含文本层(%d 字)，通常无需抽图；如仍需抽图请确认。" % (stem, tlen))
        pages, written, skipped = extract(path, args.out, tag, args.max_width, args.quality)
        total += written
        print("%-46s %4d 页 -> 抽出 %4d 张 (跳过 %d)  前缀=%s"
              % (os.path.basename(path), pages, written, skipped, tag))

    print("\n合计写出 %d 张图片 -> %s" % (total, os.path.abspath(args.out)))
    print("下一步：分批派发子代理逐张识别，批次结果写成 {\"en\":[...],\"cn\":[...]} 的 JSON。")


if __name__ == "__main__":
    main()
