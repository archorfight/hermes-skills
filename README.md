# Hermes Skills

> 一人企业出海变现的 Hermes Agent 自定义 Skills 集合。

## Skills 索引

| Skill | 目录 | 说明 | 状态 |
|-------|------|------|------|
| intel-pipeline | [intel-pipeline/](intel-pipeline/) | RSS 自动采集 + 四维标签评分 + 痛点周报 | 🚧 规划中 |
| goal-engineering | [goal-engineering/](goal-engineering/) | 派活前七问自检 + goal 模板 + 验收协议 | ✅ MVP 完成 |
| material-intake | [material-intake/](material-intake/) | 手动入库 + RSS 流水线诊断 | ✅ 已上线 |
| kb-search | [kb-search/](kb-search/) | ChromaDB 全库语义搜索 | ✅ 已上线 |

## 规划文档

- [intel-pipeline 规划](intel-pipeline/PLAN.md) — 四维标签 + RSS 审计 + 痛点周报
- [goal-engineering 规划](../planning/goal-engineering/goal-engineering-skill-planning.md) — 七问自检 + 执行/探索型模板 + 明卷暗卷验收

## 技术栈

- **运行时**: Hermes Agent (Nous Research)
- **数据库**: ChromaDB (向量存储)
- **评分模型**: GLM-5.2 (智谱编程套餐，零成本)
- **定时任务**: Hermes cron

## 用法

Skills 在 `~/.hermes/skills/` 下运行。这个 repo 是**源码管理**，
本地实际运行路径在 `/Users/archer/Desktop/hermes/openclaw-data/` 或 `~/.hermes/skills/`。

```bash
# 同步 skill 到 Hermes 运行目录
cp -r material-intake/ ~/.hermes/skills/material-intake/
```
