---
name: market-intel-weekly
name_en: Market Intelligence Weekly Report
name_zh: 市场情报周报流水线
description: End-to-end pipeline that maintains a curated information-source library, collects dated news across it, produces a markdown intelligence list, fact-checks flagged items, and renders an email-ready weekly HTML report. Use when the user asks to build/refresh a market-intel or industry weekly/daily report from a source list, or mentions 市场情报, 行业周报/日报, 信息源清单, 舆情周报, 采集/核查.
description_en: End-to-end pipeline: curated source library -> dated news collection -> markdown intel list -> fact-check -> email-ready weekly HTML.
description_zh: 从信息源清单出发，按日期采集新闻、生成情报清单 md、事实核查待核项，再产出可邮件发送的周报 HTML。用于生成市场情报/行业周报、日报、舆情汇总。
argument-hint: Give the reporting window (e.g. 上周四到今天) and, if any, the source-library file and focus topics.
argument-hint-en: Give the reporting window (e.g. last Thursday to today) and, if any, the source-library file and focus topics.
argument-hint-zh: 给出时间区间（如“上周四到今天”），如有信息源清单/关注方向请附上。
user-invocable: true
---

# 市场情报周报流水线

把"信息源清单 → 采集 → 情报清单 → 核查 → 邮件周报"固化为可复用流程。适用于算力/半导体等以**信息源台账**驱动的市场情报周报/日报。五个阶段，按需执行（用户可只跑其中几步）。

## 何时用哪一步

| 用户诉求 | 走哪个阶段 |
|---|---|
| 把两份文档/一批信息源整理成可采集的台账 | 阶段 1 建信息源库 |
| 基于核心源采集某段时间的信息、生成清单 | 阶段 2 采集 + 阶段 3 生成 md |
| 核实清单里存疑的数据/型号/份额 | 阶段 4 事实核查 |
| 生成/更新可邮件发送的周报 HTML | 阶段 5 生成周报 HTML |

先确认**报告时间区间**：用 `date` 取今天，再推算"上周四/上周X"到今天的准确日期，勿凭记忆。

---

## 阶段 1 · 建立信息源库（一次性/维护）

输入是任意把信息源列成的文档（Word/PDF/表格）。产出一个 Excel 台账 + 核心源清单。

1. 读文档，抽取每条来源的：名称、链接、渠道（官网/公众号/数据库…）、来源类别、产业环节、国家/地区、优先级、关注重点、引用热度。
2. 跨来源**去重合并**：同一名称+同一渠道跨文档合并为一行；同一主体的"官网"与"微信公众号"是两个采集渠道，分两行保留。
3. 用 `xlsx` 技能产出：按来源类别分 sheet + 全部总表 + 说明/字段字典 + 统计。缺链接的可按可信官方域名补齐并**标注为"整理补充(推断)"**；补的链接做 HTTP 核验（并发 `python` 探测，区分 可访问/受限(403·TLS)/超时/DNS失败/无链接；境外站受限≠失效）。
4. 导出**核心清单**（★核心源，如 `assets/core_sources.csv` 是本行业已核实的 86 个核心源，可直接复用/增补）。

台账字段与去重/核验细则见 [reference.md](reference.md)。

## 阶段 2 · 采集（按区间并行检索）

以核心源为框架、按**产业环节/主题**切分，**并行派发多个 research agent**（`general-purpose`，各自 WebSearch/WebFetch）。常见主题簇：政策与出口管制 / 供需·价格·供应链 / AI 基础设施·数据中心·云 / 能源电力 / 模型·Agent·开源 / 厂商动态 / 资本市场·采购·招投标 / 海外媒体。

**每个 agent 的硬规则**（照抄，避免幻觉）：
- 只收录**发布时间落在区间内、且有真实来源 URL** 的事件；日期不明确或窗口外一律丢弃（可单列"窗口外高相关"备查）。
- 每条给：日期、事件标题、要点、来源(名称+URL)、以及一句 `→ 对××意味着`（本领域固定"对本国/本公司意味着什么"这一列）。
- 厂商公告/官方数据/交易所披露优先；"据知情人士/外媒曝"须标注未经证实；SEO 博客/股吧/百科的型号·参数·跑分默认不采信。

采集 agent 提示词模板见 [reference.md](reference.md)。

## 阶段 3 · 生成情报清单 md

汇总去重、按产业环节分节。结构：`一、本周主线(概览)` → 若干主题节 → `上周补充` → `采集与可信度说明`。每条含 日期·来源链接·要点·`→ 含义`。清单模板见 [reference.md](reference.md)。**存疑项就地标〔待核/媒体口径/转引〕**，为阶段 4 备好清单。

## 阶段 4 · 事实核查（对待核项）

对阶段 3 标出的存疑项，**并行派发核查 agent**，逐项判定：✅属实 / 🟡部分属实(修正或剥离未经证实数字) / ⚫无法证实·传闻(降级或删除)。优先厂商官方、交易所/政府官网、权威媒体一手；凡只在 CSDN/SEO/股吧出现的一律"未经证实"。产出《事实核查报告》（判定+证据+处理建议），并把更正**回写**到清单与周报，删掉如"某量化政策口径"这类查无出处的断言。核查报告模板与 agent 提示见 [reference.md](reference.md)。

## 阶段 5 · 生成邮件周报 HTML（用脚本，勿手写）

把清单整理成 `report.json`（结构化条目 + 每节版式），运行生成器产出邮件安全 HTML：

```bash
python scripts/build_weekly_html.py report.json 周报.html
```

生成器已实现：概览面板、政策卡片、KPI 指标块+表格、厂商**时间线**、能源 callout、模型可信度表格、资本表格；全内联样式 + table 布局 + MSO 条件注释，兼容 Gmail/Outlook/QQ。版式选型、`report.json` schema 见脚本头部与 [reference.md](reference.md)。校验：表格标签配平、`grep` 确认应删的解说段已移除。发布为网页用 `qw-pages`（静态：目录根放 `index.html` 再 `qwenwork_pages_publish`）；仅当用户明确要求发布时才发。

## 交付与注意

- 交付前 `date` 校准区间；核心数字标可信度；厂商/份额/型号类多为媒体来源，进对外物料前二次核实。
- 默认中文输出。三件套产物：信息源库(.xlsx)、情报清单(.md)、周报(.html)，可另附核查报告(.md)。
