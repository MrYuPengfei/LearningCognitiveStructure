#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SkillHub 关键词分词与检索串生成器。

输入一个口语化检索词（可能含中文、英文、数字、标点混合），
输出结构化 JSON：
  - keyword: 归一化后的原词
  - tokens : 拆出的词元列表（用于相关度打分与多词召回）
  - queries: 建议提交给 skills 列表接口的检索串（整句优先，最多前 4 个）

设计目标：确定性、可重复、无第三方依赖，便于 Skill 内多次调用。

分词策略：
  - 归一化：转小写，去除首尾及中间多余空白，剥离常见标点。
  - 含 CJK：保留整句；对连续 CJK 字符生成 bigram（二元组）词元；
            同时提取其中的 ASCII 连续片段（如 "PDF"、"git"）作为独立词元。
  - 纯 ASCII：按空格 / 连字符 / 下划线切词，保留整句与单词。
  - queries 顺序：整句优先（召回最相关），其后按词元长度降序取前若干，
            控制接口调用次数（默认最多 4 个检索串）。
"""

import sys
import json
import re

CJK_RE = re.compile(r"[\u4e00-\u9fff]")
ASCII_TOKEN_RE = re.compile(r"[a-zA-Z0-9]+")
SEP_RE = re.compile(r"[\s\-_/\\,，。、；;:：!！?？().（）\[\]【】]+")
PUNCT_RE = re.compile(r"[^\w\u4e00-\u9fff]+")


def normalize(text: str) -> str:
    """小写化并去除标点与多余空白。"""
    text = text.lower()
    text = PUNCT_RE.sub(" ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def cjk_bigrams(s: str) -> list:
    """对连续 CJK 串生成二元组词元。"""
    out = []
    for i in range(len(s) - 1):
        bg = s[i:i + 2]
        if CJK_RE.match(bg[0]) and CJK_RE.match(bg[1]):
            out.append(bg)
    return out


def extract_tokens(norm: str) -> list:
    """从归一化文本中提取词元（去重、保序）。"""
    tokens = []
    seen = set()

    # 1) 完整归一化句子（作为最强检索串）
    if norm:
        tokens.append(norm)
        seen.add(norm)

    # 2) ASCII 连续片段（英文词 / 数字，如 PDF、git、123）
    for m in ASCII_TOKEN_RE.findall(norm):
        if m not in seen:
            tokens.append(m)
            seen.add(m)

    # 3) CJK 二元组
    cjk_runs = re.findall(r"[\u4e00-\u9fff]+", norm)
    for run in cjk_runs:
        for bg in cjk_bigrams(run):
            if bg not in seen:
                tokens.append(bg)
                seen.add(bg)

    # 4) 纯中文整段（较长时作为补充检索串）
    for run in cjk_runs:
        if len(run) >= 2 and run not in seen:
            tokens.append(run)
            seen.add(run)

    return tokens


def build_queries(tokens: list, max_queries: int = 4) -> list:
    """从词元中挑选建议检索串：整句优先，其后按长度降序。"""
    # 第一个通常是整句，优先保留
    queries = []
    if tokens:
        queries.append(tokens[0])

    rest = tokens[1:]
    # 长词元通常更具体、相关度更高，优先
    rest_sorted = sorted(rest, key=lambda t: len(t), reverse=True)
    for t in rest_sorted:
        if t not in queries:
            queries.append(t)
        if len(queries) >= max_queries:
            break
    return queries


def tokenize(keyword: str, max_queries: int = 4) -> dict:
    norm = normalize(keyword or "")
    tokens = extract_tokens(norm)
    queries = build_queries(tokens, max_queries) if norm else []
    return {
        "keyword": norm,
        "tokens": tokens,
        "queries": queries,
    }


def main():
    if len(sys.argv) < 2:
        print(json.dumps(
            {"error": "usage: tokenize.py <keyword> [max_queries]"},
            ensure_ascii=False,
        ))
        sys.exit(1)

    keyword = sys.argv[1]
    max_q = 4
    if len(sys.argv) >= 3:
        try:
            max_q = int(sys.argv[2])
        except ValueError:
            pass

    result = tokenize(keyword, max_q)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
