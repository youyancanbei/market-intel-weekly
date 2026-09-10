# market-intel-weekly

把「信息源台账 → 按日期采集 → 情报清单 md → 事实核查 → 邮件周报 HTML」固化为可复用的 Agent 技能（QwenWork / Claude Skills 格式）。适用于算力/半导体等以信息源清单驱动的市场情报周报、日报。

## 目录结构

```
market-intel-weekly/            # 技能本体（含 SKILL.md，可直接放进 skills 目录）
├── SKILL.md                    # 五阶段流程与硬规则
├── reference.md                # 台账字段/去重/链接核验、采集与核查 agent 模板、report.json→HTML
├── .skill-metadata.yaml        # 快捷指令（中英）
├── assets/
│   ├── core_sources.csv        # 86 个已核实 ★核心信息源（算力/半导体）
│   └── logo.png                # 品牌抬头示例 logo（透明底）
└── scripts/
    ├── build_weekly_html.py    # 邮件安全 HTML 生成器（内联样式+table 布局+MSO 注释；支持品牌抬头）
    └── report_example.json     # 生成器输入示例
dist/
└── market-intel-weekly-v1.1.1.skill   # 打包好的可安装包（zip，SKILL.md 在根）
```

## 安装

- **QwenWork**：把 `dist/*.skill` 拖入对话，点「保存技能」；或将 `market-intel-weekly/` 整个目录复制到 `~/.qwenworkcn/skills/`。
- **其他 agent（Claude Skills 等）**：把 `market-intel-weekly/` 目录放到对应 skills 目录即可。

## 生成周报 HTML

```bash
cd market-intel-weekly
python scripts/build_weekly_html.py scripts/report_example.json out.html
```

`report.json` 顶层支持 `logo`/`logo_b64`、`brand_en`、`brand_zh`、`coverage_label` 配置品牌抬头；各 section 用 `layout`（card / kpi+table / table / timeline / callout+card）选版式。详见 `reference.md`。

## 依赖

`python3` + `openpyxl`（建台账）、`Pillow`（logo 抠透明，可选）；采集与核查阶段由 agent 联网检索完成。
