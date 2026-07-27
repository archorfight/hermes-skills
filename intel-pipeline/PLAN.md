# 一人企业情报系统升级规划 (Intel Pipeline v2)

> 创建：2026-07-27 | 作者：Archer + Hermes
> 状态：**规划阶段，待实施**
> 核心目标：把现有"内容选题导向"的素材系统升级为"一人企业作战情报系统"

---

## 0. 背景与问题

现有素材系统（`auto_pipeline.py` + ChromaDB `content_materials`）每天自动抓取 22 个 RSS 源 → GLM-5.2 评分 → 入库，库内已有 591 条素材。

**三个核心问题：**

1. **标签是单维度** — 只有 `category`（AI编程/出海/一人企业），无法区分"这是痛点信号"还是"这是变现案例"
2. **评分只看选题价值** — 5分="可做公众号选题"，但 Archer 需要的不只是选题，还有需求信号和竞品情报
3. **RSS 源偏新闻资讯** — 缺痛点高发区（Reddit 痛点帖、Indie Hackers 收入帖、X/Twitter 一人企业圈）

---

## 1. RSS 源审计 + 补强

### 1.1 现有 22 源（全部保留）

| 源 | 分类 | 出分表现 |
|---|---|---|
| Hacker News (frontpage) | 编程 | 核心情报源，高频出高分 |
| Hacker News (newest) | 编程 | 同上 |
| Reddit r/SaaS | 一人企业 | 痛点+变现案例密集 |
| Indie Hackers | 一人企业 | 真实收入帖 |
| Product Hunt | 一人企业 | 竞品动态 |
| SaaStr | 出海 | SaaS 方法论 |
| Lenny's Newsletter | 一人企业 | 深度产品/增长 |
| Stripe Blog | 出海 | 支付/商业化 |
| 36氪 | AI | 国内 AI 新闻 |
| 少数派 | 编程 | 国内工具评测 |
| InfoQ | AI | 国内技术深度 |
| TechCrunch AI | AI Industry | 国际 AI 新闻 |
| TechCrunch | 出海 | 国际科技新闻 |
| Y Combinator | 出海 | 创业方法论 |
| Vercel Blog | 编程 | 前端/部署 |
| GitHub Blog | 编程 | 开源动态 |
| OpenAI Blog | AI | 模型发布 |
| Anthropic Blog | AI | 模型发布 |
| OpenClaw Blog | 编程 | 工具动态 |
| 白鲸出海 | 出海 | 国内出海媒体 |
| Reddit r/indiehackers | 一人企业 | 独立开发 |

### 1.2 新增 7 个源

| 源 | RSS URL | 价值 |
|---|---|---|
| Reddit r/Entrepreneur | `https://www.reddit.com/r/Entrepreneur/.rss` | 创业痛点密集 |
| Reddit r/SideProject | `https://www.reddit.com/r/SideProject/.rss` | 独立开发项目展示，竞品+痛点 |
| Reddit r/EntrepreneurRideAlong | `https://www.reddit.com/r/EntrepreneurRideAlong/.rss` | 真实运营复盘 |
| MicroConf | `https://microconf.com/feed` | 一人企业/SaaS 运营深度 |
| Starter Story | `https://starterstory.com/feed` | 真实收入案例（$1K-$100K MRR） |
| Hacker News - Ask HN | `https://hnrss.org/ask` | 痛点帖高发（"I wish there was a tool that..."） |
| Reddit r/Entrepreneur (Hot) | `https://www.reddit.com/r/Entrepreneur/hot/.rss` | 热门创业讨论 |

**RSS 源总数：22 → 29**

---

## 2. 标签体系重构：单维 → 四维

### 现状

```
category (单字段): AI编程 | 一人企业 | 出海 | 编程 | AI | Agent | ...
```

### 升级方案

#### 维度 1：`topic`（主题，替代现有 category）

```
AI编程 | AI工具 | Agent | 出海 | 一人企业 | 商业化 | 方法论 | 趋势
```

8 个固定值，保持简单。

#### 维度 2：`content_type`（内容类型，新增）

```
实操教程 | 变现案例 | 痛点信号 | 竞品动态 | 工具推荐 | 行业趋势 | 方法论
```

这个维度解决"有的是痛点可以用来做需求"——标 `content_type:痛点信号` 的素材自动成为产品候选池。

#### 维度 3：`signal_score`（商业信号强度，新增）

```
0 = 纯资讯，无商业价值
1 = 有参考价值
2 = 有明确痛点/需求/收入数据/可复用方法
3 = 立即可行动（做产品/做内容/做投资）
```

跟现有 `score`（选题价值 1-5）分开。一篇可以是选题 3 分但商业信号 3 分（比如行业趋势文章，不好写公众号但包含关键需求信号）。

#### 维度 4：`tags`（自由标签，新增）

```
#MRR数据 #获客方法 #定价策略 #冷启动 #SEO #Reddit引流
#痛点-SEO工具太贵 #需求-批量内容分发 #竞品-BuzzStream
```

LLM 评分时自由生成，用于后续灵活检索。

### ChromaDB metadata 变更

入库时写入的新字段：

```python
metadatas=[{
    # 现有字段（保留）
    "source": source,
    "title": title[:100],
    "url": url,
    "category": topic,          # 向后兼容，原 category 字段写入 topic 值
    "score": score,             # 选题价值 1-5
    "date": date_str,
    "reason": reason[:200],
    "intake": "auto",

    # 新增字段
    "content_type": content_type,   # 内容类型
    "signal_score": signal_score,   # 商业信号 0-3
    "tags": tags,                   # 自由标签（逗号分隔字符串）
}]
```

---

## 3. 评分 Prompt 升级

### 现有 prompt（仅输出选题价值）

```
你是严格的自媒体选题编辑...
5分=极度契合：直接讲AI编程实操、出海变现案例...
```

### 升级后 prompt（四维并行输出）

```
你是「一人企业出海变现」方向的情报分析官。

对每条内容，输出4个维度：

1. topic（主题）: AI编程/AI工具/Agent/出海/一人企业/商业化/方法论/趋势
2. content_type（类型）: 实操教程/变现案例/痛点信号/竞品动态/工具推荐/行业趋势/方法论
3. score（选题价值1-5）: 作为公众号/知乎/短视频选题的参考价值
   5 = 极度契合：直接讲AI编程实操、出海变现案例、一人企业赚钱方法，可立即做选题
   4 = 高度相关：涉及具体工具/人物/收入数据/方法论，有明确选题参考价值
   3 = 有参考价值：行业趋势/背景知识，可入库备查但优先级低
   2 = 弱相关：沾边但重点在别处
   1 = 无关
4. signal_score（商业信号0-3）: 对做产品/找需求/判断方向的参考价值
   3 = 立即可行动（明确痛点+付费意愿 / 真实收入数据可复用 / 竞品漏洞可打）
   2 = 有明确信号（提到具体痛点/收入/方法，但需深挖）
   1 = 弱信号（行业背景，有间接参考）
   0 = 纯资讯

判定规则：
- 痛点帖（"I wish there was..."、"Why is it so hard to..."）→ content_type=痛点信号, signal_score≥2
- 真实收入帖（带$数字、MRR/ARR）→ content_type=变现案例, signal_score≥2
- 产品发布/竞品分析 → content_type=竞品动态, signal_score=1-2
- 纯新闻（XX公司发布XX）→ signal_score=0
- 泛AI新闻默认 score≤3，除非有可直接借鉴的实操或商业洞察

tags：自由生成1-3个标签，格式如 #关键词，用逗号分隔

只回复JSON数组: [{"i":1,"topic":"一人企业","content_type":"变现案例","score":5,"signal_score":3,"reason":"理由","tags":"#MRR数据,#获客方法"}]
```

### 入库逻辑变更

```python
# 原来只取 score/reason/topic
output.append((int(r.get("score", 0)), r.get("reason", ""), r.get("topic", "")))

# 升级后取全部4维
output.append({
    "score": int(r.get("score", 0)),
    "reason": r.get("reason", ""),
    "topic": r.get("topic", ""),
    "content_type": r.get("content_type", "行业趋势"),
    "signal_score": int(r.get("signal_score", 0)),
    "tags": r.get("tags", ""),
})
```

入库门槛变更：

```python
# 原来：score >= 3 才入库
# 新规则：score >= 3 OR signal_score >= 2 才入库
# （商业信号强的素材即使选题价值一般也要留下来）
```

---

## 4. 痛点周报（Pain Point Weekly）

### 触发方式

新建 Hermes cron job，每周一 9:00 执行。

### 数据源

ChromaDB `content_materials` 中，过去 7 天入库且 `content_type = "痛点信号"` 的所有素材。

### 输出格式

```markdown
# 🔍 一人企业痛点周报 (2026-07-27 ~ 2026-08-02)

本周捕获痛点信号 N 条，聚合为 M 个痛点主题。

## 痛点 Top 5（按出现频率）

### 1. #痛点-SEO工具太贵 （出现4次）
- 来源：Reddit r/SaaS ×2, Hacker News ×1, Indie Hackers ×1
- 典型原文："Ahrefs costs $200/mo and I only use 20% of it..."
- 关联标签：#定价策略 #获客方法
- **信号强度：⭐⭐⭐** — 明确付费意愿 + 现有方案不满

### 2. #痛点-内容分发耗时 （出现3次）
...

## 本周新增变现案例

| 金额 | 产品 | 方法 | 来源 |
|---|---|---|--- |
| $1,297/月 | 社媒排期 CLI | 卖工作流教程不卖功能 | Reddit |
| $300 MRR | AI Chatbot 平台 | 印度市场也能转化 | Reddit |
```

### Cron 配置

```yaml
schedule: "0 9 * * 1"  # 每周一 9:00
skills: ["material-intake"]
prompt: |
  生成本周痛点周报。从 ChromaDB content_materials 中查询过去7天
  content_type=痛点信号 的素材，按 tags 中的 #痛点-XXX 聚合，
  按出现频率排序，取 Top 5。
  同时汇总 content_type=变现案例 的素材，提取收入数据。
  格式见 PLAN.md 第4节。
```

---

## 5. 历史数据回填

对现有 591 条素材跑一次批量重评，补上 3 个新字段（`content_type`、`signal_score`、`tags`）。

### 方案

```python
# backfill_scores.py
# 1. 从 ChromaDB 拉全部 591 条
# 2. 每 15 条一批，送 GLM-5.2 重新评分（用新 prompt）
# 3. 更新 metadata，补充 content_type / signal_score / tags
# 4. 原有 score 保留不动（向后兼容）
```

### 注意事项

- GLM-5.2 走智谱编程套餐，不扣费
- 必须加 `"thinking": {"type": "disabled"}`
- 批量 15 条/次，591 条约需 40 次 API 调用
- 跑完后验证：每条都有 content_type 和 signal_score

---

## 6. 实施路径

| 步骤 | 内容 | 改什么 | 工作量 | 状态 |
|---|---|---|---|---|
| 1 | RSS 源补强 | `auto_pipeline.py` RSS_FEEDS 加 7 个新源 | 配置改动 | 待实施 |
| 2 | 评分 prompt 升级 | `auto_pipeline.py` score_batch_with_llm() prompt + 入库逻辑 | 核心改动 | 待实施 |
| 3 | 历史数据回填 | 新建 `backfill_scores.py`，批量重评 591 条 | 脚本 + 跑一轮 | 待实施 |
| 4 | 痛点周报 cron | 新建 Hermes cron job，每周一 9:00 | 新 cron | 待实施 |
| 5 | material-intake skill 更新 | 同步新字段到 skill 文档 | skill patch | 待实施 |
| 6 | kb_search.py 升级 | 搜索结果展示新字段 | 脚本改动 | 待实施 |

### 优先级

1. **先做步骤 1+2** — RSS 源 + 评分升级，明天 8 点 cron 就能用新体系
2. **再做步骤 3** — 历史回填，让老素材也有新标签
3. **最后做步骤 4** — 痛点周报，等有足够 `content_type=痛点信号` 数据后再启动

---

## 7. 文件清单

| 文件 | 路径 | 说明 |
|---|---|---|
| 本规划 | `~/Desktop/hermes/intel-pipeline/PLAN.md` | 完整规划文档 |
| RSS 流水线 | `~/Desktop/hermes/openclaw-data/rss-monitor/auto_pipeline.py` | 待改造 |
| 手动入库 | `~/Desktop/hermes/openclaw-data/rss-monitor/intake.py` | 待同步改造 |
| 入库脚本 wrapper | `~/Desktop/hermes/openclaw-data/rss-monitor/run_pipeline.sh` | 不变 |
| 知识库搜索 | `~//archer/Desktop/hermes/openclaw-data/kb_search.py` | 待升级 |
| ChromaDB | `~/Desktop/hermes/openclaw-data/kb_data_shared/` | 结构不变，metadata 加字段 |
| Cron Job (日报) | Hermes cron `12c307034269`，每天 8:00 | prompt 待更新 |
| Cron Job (周报) | 新建，每周一 9:00 | 待创建 |

---

## 8. 关键约束

- **评分模型**：GLM-5.2（智谱编程套餐 `/api/coding/paas/v4`），不扣费；必须加 `thinking:disabled`
- **DeepSeek**：仅 fallback，`deepseek-v4-flash`
- **API Key**：从 `/Users/archer/Desktop/hermes/ai-directory/video-summarizer/worker/.dev.vars` 读取，不内联 `$()`（Hermes 安全扫描器会截断）
- **飞书 wiki**：必须用智谱 reader MCP 抓取，不能用 requests
- **ChromaDB**：单库 `kb_data_shared`，collection `content_materials`
