---
name: journal-fit
display_name: "期刊匹配与投稿回复"
display_name_en: "Journal Fit and Submission Response"
description: "Use when the user asks to choose a target journal, score journal fit, draft a cover letter, or answer reviewer comments point by point."
description_zh: "为稿件做期刊匹配打分，生成投稿信，并按照审稿意见组织逐条回复信。"
description_en: "Scores journal fit, drafts cover letters, and structures point-by-point reviewer responses."
version: 1.0.0
author: "论文投稿专家工作室"
examples_zh: ["帮我给这篇论文匹配 3 本合适的期刊", "根据我的论文写一封投稿信", "帮我逐条回复审稿意见"]
examples_en: ["Match three suitable journals for this paper", "Write a cover letter for my paper", "Help me respond to reviewer comments point by point"]
---

# 期刊匹配与投稿回复

把「选刊」和「回复审稿」从凭感觉变成可复核的打分与清单。

## 何时使用

- 用户要给一篇论文找目标期刊，或比较几本候选期刊。
- 用户要写或改投稿信（cover letter）。
- 用户收到审稿意见，需要写回复信（response letter）或决定转投。

## 一、选刊打分

### 输入
先补齐四项，缺一项就追问，不要凭空假设：

1. 论文画像：核心贡献一句话、创新类型、方法强度（1–5）、数据规模（1–5）、写作成熟度（1–5）。
2. 候选期刊：名称、收录索引、中科院分区、近两年同主题发文情况。
3. 约束：审稿周期上限、版面费预算、是否接受预警名单期刊。
4. 目标：毕业、职称、项目结题，决定「稳妥优先」还是「冲高优先」。

### 打分口径
固定四项权重，不随意调整：

| 维度 | 权重 | 说明 |
|---|---|---|
| 范围契合度 scope_fit | 40% | 近两年是否发过同主题文章，读者是否关心这个问题 |
| 质量匹配度 quality_fit | 30% | 期刊层级与稿件完成度是否对等，避免明显高攀或低就 |
| 周期 speed | 15% | 4 周内 5 分，8 周内 4 分，12 周内 3 分，16 周内 2 分，更长 1 分 |
| 成本 cost | 15% | 无版面费 5 分，1000 美元内 4 分，2000 美元内 3 分，3000 美元内 2 分，更高 1 分 |

加权公式：`总分 = scope_fit × 0.40 + quality_fit × 0.30 + speed × 0.15 + cost × 0.15`

档位：4.2 及以上为冲刺，3.4–4.2 为主投，2.6–3.4 为备选，2.6 以下不建议。

### 用脚本算
把候选期刊整理成 JSON，调用脚本得到排序表：

```bash
python3 scripts/journal_fit_score.py candidates.json
```

JSON 结构：

```json
{
  "journals": [
    {
      "name": "Journal Name",
      "indexing": "SCIE",
      "scope_fit": 5,
      "quality_fit": 4,
      "review_weeks": 8,
      "apc_usd": 0,
      "accept_rate": 0.15,
      "notes": "近两年发过 12 篇同主题"
    }
  ]
}
```

加 `--json` 输出机器可读结果。脚本只做加权与风险标记，不替代对期刊官网的核实。

### 输出
一张排序表，每行包含：期刊名、索引、契合度、质量匹配、周期、版面费、总分、档位、风险提示。表后给一句话结论：主投哪本、冲刺哪本、备选哪本，以及最可能被拒的理由。

## 二、投稿信

套用 `templates/cover_letter.md`，一页以内，四段：

1. 投稿意向：稿件题目、类型、对应期刊栏目。
2. 为什么是这本刊：引用该刊近两年的具体文章或栏目定位，说明读者契合。
3. 贡献：三句话讲清问题、方法、结论，带一个关键数字。
4. 合规声明：未一稿多投、全体作者同意、无利益冲突、数据可用性。

不要写「贵刊影响因子高」「我们非常崇拜」这类空话，也不要重复摘要。

## 三、审稿回复

套用 `templates/response_letter.md`，先分类再动笔：

| 类型 | 处理方式 |
|---|---|
| 必须改 | 明确改了什么、改在哪、结果有何变化 |
| 可以改 | 接受并补充，说明补充内容 |
| 需要解释 | 先复述对方关切，再给证据或范围说明 |
| 不合理 | 礼貌说明理由，给替代方案 |

每条回复固定四段：意见原文 → 我们的理解 → 具体修改 → 修改位置（页码/行号）。编号与审稿人一致，一条不漏。开头一段总述本轮三件关键修改，结尾一段感谢。

## 四、被拒之后

先判断是「期刊不匹配」还是「稿件硬伤」：

- 审稿人认可贡献但说 scope 不符 → 换刊，不改稿。
- 方法或数据被质疑 → 补分析，不降档硬投。
- 多位审稿人指向同一缺陷 → 视为硬伤，先修再投。

输出转投方案：目标刊、需要修改的章节、预计周期。

## 红线

- 不编造期刊影响因子、录用率、审稿周期，缺失就标注「需核实」。
- 不生成虚假参考文献、不伪造审稿人、不代写论文主体。
- 不承诺录用，不提供代投或买卖版面建议。
