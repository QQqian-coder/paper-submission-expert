#!/usr/bin/env python3
"""期刊匹配加权打分：按 range / quality / speed / cost 四项权重排序候选期刊。"""

import argparse
import json
import sys

WEIGHTS = {
    "scope_fit": 0.40,
    "quality_fit": 0.30,
    "speed": 0.15,
    "cost": 0.15,
}


def clamp(value, low=1, high=5):
    try:
        value = float(value)
    except (TypeError, ValueError):
        return None
    return max(low, min(high, value))


def speed_score(weeks):
    weeks = float(weeks)
    if weeks <= 4:
        return 5.0
    if weeks <= 8:
        return 4.0
    if weeks <= 12:
        return 3.0
    if weeks <= 16:
        return 2.0
    return 1.0


def cost_score(apc_usd):
    apc_usd = float(apc_usd)
    if apc_usd <= 0:
        return 5.0
    if apc_usd <= 1000:
        return 4.0
    if apc_usd <= 2000:
        return 3.0
    if apc_usd <= 3000:
        return 2.0
    return 1.0


def band(score):
    if score >= 4.2:
        return "冲刺"
    if score >= 3.4:
        return "主投"
    if score >= 2.6:
        return "备选"
    return "不建议"


def risks(item, scope_fit):
    flags = []
    if scope_fit <= 2:
        flags.append("范围不匹配")
    accept_rate = item.get("accept_rate")
    if accept_rate is not None and float(accept_rate) < 0.10:
        flags.append("录用率低")
    if float(item.get("review_weeks", 0)) > 16:
        flags.append("周期长")
    if float(item.get("apc_usd", 0)) > 3000:
        flags.append("费用高")
    if not str(item.get("indexing", "")).strip():
        flags.append("索引待核实")
    return "、".join(flags) if flags else "无"


def evaluate(item):
    name = str(item.get("name", "")).strip()
    if not name:
        raise ValueError("存在缺少 name 字段的期刊条目")

    scope_fit = clamp(item.get("scope_fit"))
    quality_fit = clamp(item.get("quality_fit"))
    if scope_fit is None or quality_fit is None:
        raise ValueError(f"{name} 缺少 scope_fit 或 quality_fit（1-5）")

    review_weeks = item.get("review_weeks", 12)
    apc_usd = item.get("apc_usd", 0)
    s_score = speed_score(review_weeks)
    c_score = cost_score(apc_usd)

    total = (
        scope_fit * WEIGHTS["scope_fit"]
        + quality_fit * WEIGHTS["quality_fit"]
        + s_score * WEIGHTS["speed"]
        + c_score * WEIGHTS["cost"]
    )
    total = round(total, 2)

    return {
        "name": name,
        "indexing": str(item.get("indexing", "")).strip() or "待核实",
        "scope_fit": scope_fit,
        "quality_fit": quality_fit,
        "review_weeks": float(review_weeks),
        "apc_usd": float(apc_usd),
        "accept_rate": item.get("accept_rate"),
        "speed_score": s_score,
        "cost_score": c_score,
        "total": total,
        "band": band(total),
        "risk": risks(item, scope_fit),
        "notes": str(item.get("notes", "")).strip(),
    }


def render_table(rows):
    lines = [
        "| 期刊 | 索引 | 契合 | 质量 | 周期(周) | 版面费(USD) | 总分 | 档位 | 风险 |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        lines.append(
            "| {name} | {indexing} | {scope_fit:.0f} | {quality_fit:.0f} | {weeks:g} | {apc:g} | {total:.2f} | {band} | {risk} |".format(
                name=r["name"],
                indexing=r["indexing"],
                scope_fit=r["scope_fit"],
                quality_fit=r["quality_fit"],
                weeks=r["review_weeks"],
                apc=r["apc_usd"],
                total=r["total"],
                band=r["band"],
                risk=r["risk"],
            )
        )
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="期刊匹配加权打分")
    parser.add_argument("input", help="候选期刊 JSON 文件路径")
    parser.add_argument("--json", action="store_true", help="输出 JSON 而非表格")
    args = parser.parse_args()

    try:
        with open(args.input, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except FileNotFoundError:
        sys.exit(f"找不到文件：{args.input}")
    except json.JSONDecodeError as exc:
        sys.exit(f"JSON 解析失败：{exc}")

    journals = data.get("journals") if isinstance(data, dict) else data
    if not isinstance(journals, list) or not journals:
        sys.exit("输入需包含非空的 journals 数组")

    try:
        rows = sorted((evaluate(item) for item in journals), key=lambda r: r["total"], reverse=True)
    except ValueError as exc:
        sys.exit(str(exc))

    if args.json:
        print(json.dumps({"weights": WEIGHTS, "journals": rows}, ensure_ascii=False, indent=2))
        return

    print(render_table(rows))
    top = rows[0]
    print(f"\n结论：优先主投 {top['name']}（{top['total']:.2f}，{top['band']}）。")


if __name__ == "__main__":
    main()
