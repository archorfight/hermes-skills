---
name: wechat-article
description: 公众号文章完整生产流程。当用户说"写公众号文章"、"公众号选题"、"写篇公众号"、"发文章"、"给我选题"、"今天写什么"时使用。覆盖从选题、大纲、初稿、审计、微调到发布准备的全流程。定位：一人企业 + AI 编程出海。日更节奏。
---

# 公众号文章生产流程

## 快速上下文

- **定位**：用 AI 编程 + 出海，帮普通人从手艺人变成设计生意的人
- **节奏**：日更（每天 1 篇）
- **读者**：有技术背景的独立开发者、一人企业主、对 AI 应用有实操兴趣的人
- **红线**：不碰政治敏感、黑灰产、纯信息搬运

---

## 每次启动：读取上下文

当用户触发公众号相关需求时，先读以下文件建立上下文：

| 顺序 | 文件 | 用途 |
|------|------|------|
| 1 | `references/content-strategy.md` | 定位、母题、日更节奏、选题库 |
| 2 | `references/published-history.md` | 已发记录，避免重复选题 |
| 3 | `references/style-guide.md` | 写作风格、标题公式、格式规范 |

如果只需要特定环节（如"帮我优化标题"），可以只读对应文件。

---

## 完整流程（按顺序执行，不跳步）

### 第 1 步：选题

**触发**："今天写什么"、"给我选题"、"写篇公众号"

**操作**：
1. 判断今天是星期几，对照日更节奏确定当天的类型和母题
2. 检查数据闭环里的**母题健康度**（content-strategy.md），超标则主动调整
3. **搜索知识库**（强制执行）：`source ~/.openclaw/workspace-planner/kb-venv/bin/activate && python ~/.agents/skills/kb-search/scripts/kb_search.py "[母题关键词]" 3`
   - 命中高质量素材 → 优先基于素材构建选题
   - 搜索结果不相关 → 使用选题库现有卡片
   - 也可以搜 `content_materials` collection 查结构化素材：`python ~/.agents/skills/kb-search/scripts/kb_search.py "[关键词]" 3 -c content_materials`
4. 检查 `published-history.md`，看最近发过什么，避免母题/角度重复
5. 从选题库（content-strategy.md 的选题卡片）中找待发选题，结合知识库素材
6. 给出 3-5 个推荐选题，每个标注素材来源（知识库命中 / 选题库卡片 / 新生成）

**选题红线（2026-07-25 新增）**：

> 如果一个选题的主体是别人的案例/产品/成就，即使素材很好，也要谨慎。Archer 的判断标准：**文章读起来像不像在给那个人打广告？** 如果像，换角度或换选题。

正确姿势：外部素材只做佐证，核心论点和主体必须是你自己的理解和实践。错误姿势：整篇文章围绕别人的案例展开，你的角色只是"转述者"。

**选题去重红线（2026-07-26 新增，2026-07-27 修订）**：

> **选题确定前，必须同时检查四处，确认选题角度未被覆盖：**
> 1. `published-history.md` 最近 30 天的已发标题
> 2. **文件系统草稿**——三个工作区都要查（见下方命令）
> 3. `session_search` 查最近 24h 的公众号写作会话
> 4. **published-history 回填状态**——已发但未回填的文章（用户说的"已发"比 DB 记录准）

**2026-07-27 事故复盘（两次）**：

**事故 1**：Agent 在会话 A 中推荐了 context engineering 选题，用户在会话 B 中让另一个 agent 写完了同一选题。会话 A 的 Agent 不知道，又从头写了一遍——完整跑了选题→初稿→审计→配图→排版→打包，直到用户说"你刚刚才写的"才发现。

**事故 2**：同一会话中，Opus 5 价格砍半那篇文章已经写完打包，用户之后提起"kimi k3 也发了"——published-history 里没有这两篇的记录，Agent 不知道已发，差点重复推荐同方向选题。

**根因**：①Archer 同时开多个飞书会话并行操作，Agent 各会话独立互不知情；②用户在别的 workspace（如 `~/.openclaw/workspace-media/`）里让另一个 agent 写文章，草稿不在本 skill 默认的 `~/Desktop/hermes/drafts/` 里；③published-history 回填依赖用户告知，但用户经常忘了说。

**强制步骤**（放在 Step 5 互动预判之前）：
1. 读 `published-history.md`，扫描最近 30 天的标题
2. **检查文件系统**（三个工作区都要查）：
   ```bash
   ls -lt ~/.openclaw/workspace-media/draft* 2>/dev/null | head -10
   ls -lt ~/Desktop/hermes/drafts/ 2>/dev/null | head -10
   find ~/.openclaw/workspace-media/ -name "*_排版_*.html" -mtime -7 2>/dev/null | head -10
   ```
3. 如果发现已有同主题的 `article.md` 或排版 HTML，**先告知用户"这个选题在另一个会话已经写过了"**
4. **主动问用户**：最近有没有在别的会话/工具里写过或发过文章？published-history 可能没回填
5. 用户确认"没写过"或"换个角度"后，才进 Step 2（大纲）

**两个工作区**：
- `~/.openclaw/workspace-media/` — Archer 的媒体工作区（另一个 agent/session 可能在这里产出）
- `~/Desktop/hermes/drafts/` — 本 skill 默认的工作目录

**三个工作区**（2026-07-27 更新）：
- `~/.openclaw/workspace-media/` — Archer 的自媒体 workspace（排版 HTML + 文章草稿都可能在这里）
- `~/Desktop/hermes/drafts/` — 本 skill 默认的工作目录
- `~/.openclaw/workspace-media/images/` — 配图也可能存在这里（cover-xxx.png / body-xxx.png 命名模式）

**⚠️ 跨会话上下文恢复红线（2026-07-26 新增）**：

> 当用户在新会话中引用上一次的结果（如"候选一""用第二个选题""上次那个标题"），**必须先 session_search 定位引用的是哪个列表**，不能直接 broadly 搜索。

错误姿势：搜索 broadly（如 `query="候选 keyword niche"`），命中不相关的候选池（如做站方向 vs 公众号选题），浪费时间且用户会质疑"怎么没串"。

正确姿势：`session_search(query="公众号 选题 候选", sort="newest")` → 找到选题推荐所在的具体 session → 如需看推荐详情，`session_search(session_id=<that session>, around_message_id=<the recommendation msg>)` 滚动到具体内容 → 跟用户确认后才继续。

**输出格式**：\n```\n📅 今天是周X → 推荐类型：[类型] | 母题：[母题]\n\n选题 1：[标题]\n简介：[50字]\n角度：[切入点]\n素材来源：[知识库命中 / 选题库卡片 / 新生成]\n实用价值：读者能拿走______（一个方法/一组数据/一个判断）\n情绪价值：读者会感觉到______（被戳中/被激励/被吓到/想反驳）\n\n选题 2：...\n```\n\n**⚠️ 双价值标注说明（2026-07-28 新增）**：实用价值和情绪价值必须逐个选题都写。写不出的那个就是该选题的天花板。两个都写不出 → 直接砍掉这个选题，不要推荐。详见 `references/style-guide.md` 第0条。\n\n等用户选定。

### 第 2 步：大纲

**触发**：用户选定选题后

**操作**：
1. 用标题公式生成 3 个备选标题
2. 写 100 字摘要
3. 列正文结构（3-5 个小标题）
4. 每个小标题的核心观点

等用户确认。

**标题传播力评估（2026-07-26 新增）**：

> 当用户问"哪个标题传播力高"或要求比较多个备选标题时，不要凭感觉选。按历史数据提炼的三因子评估法逐个打分：

| 因子 | 判断标准 | 历史数据支撑 |
|---|---|---|
| **争议度** | 标题是否包含有人会不同意/想反驳的判断？争议=评论=权重 | 评论最高的文章都有争议锚点 |
| **转发结构** | 标题是否天然适合转发给特定人群？（"X的人看到会说Y"） | 分叉型标题（好消息/坏消息）转发率最高 |
| **缩略图可读性** | 在手机端文章列表里（~15个字宽）能否一眼看明白？ | 具体动作词（"砍半价"）> 模糊词（"这笔账"）> 术语（"成本曲线"） |

输出格式：直接推荐一个，给出≤3条理由（每条对应一个因子），最后给出微调建议（如把模糊词换成具体数字）。不要让用户自己选——用户问"哪个传播力高"就是要你做判断。

### 第 3 步：初稿

**触发**：用户确认大纲后

**操作**：按风格指南写完整初稿，保存到 `drafts/[主题]-publish/article.md`

**字数要求**：
- 方法论：1000-1500 字
- 深度洞察：1500-2500 字
- 个人故事：1000-1500 字

**写作规则**（详见 `references/style-guide.md`）：
- 开头 150 字内：个人实践 + 量化结果 + 痛点共鸣
- 主体：教程型为主，避免大量列表
- 结尾 100-150 字：强引导 CTA（加好友/加群/回复关键词）
- 格式：局部加粗关键词（非整句）、`> ` 引用块用于金句/原话/指令、`` ` `` 行内代码包裹工具名、分隔线 ≤ 3 处

**配图占位符（必须同步插入）**：
- 写初稿时同步生成配图 HTML（`charts.html`），并在文章中用 `<!-- IMAGE:chart1 -->` 标记每张配图的位置
- 占位符放在正文对应段落之后，不要写完再补
- **每篇文章至少 2 张内容配图**（封面 + 2-3 张内容配图）。1 张配图太单薄，深度洞察类尤其需要可视化核心观点
- **文章涉及 Archer 自己的产品/网站时，必须加真实网站截图**（2026-07-28 Archer 明确要求"你也弄点网站的截图放到文章里，配图丰富点"）。用 Playwright Python API 截取线上页面，跟信息图搭配使用——信息图讲框架/数据，截图讲"这东西真的上线了"
- 封面不需要在正文中插入占位符（单独上传）
- 示例：
  ```markdown
  核心方法很简单：三个模型分别审查同一个 PR，然后交叉比对。

  <!-- IMAGE:chart1 -->

  三个不同架构的模型都指着同一个地方说"有问题"，那误报率就接近零了。
  ```

### 第 4 步：审计

**触发**：初稿完成后

**操作**：先执行**价值前置评估**（在7部分审计之前），再按 `references/audit-framework.md` 执行 7 部分审计。\n\n**价值前置评估（2026-07-28 新增）**：\n\n读完初稿后，先回答两个问题：\n\n| 维度 | 打分标准 | 分值 (1-10) |\n|------|----------|------|\n| 实用价值 | 读者看完能做什么之前做不了的事？有可复用的框架/清单/数据吗？ | |\n| 情绪价值 | 读者看完会有什么强烈感受？有没有一句话让他想截图转发？ | |\n\n传播力预估 = 实用 × 情绪。两个都 ≥7 才有爆文基础。\n\n- 两个都 ≤4 → 建议重写或换选题\n- 一个 ≤4 → 标记为本文天花板，审计时重点修复这个维度\n- 两个都 ≥7 → 继续走审计7部分\n\n**审计 7 部分**：
1. 致命盲点
2. 崩盘预测
3. 病灶溯源
4. 可信度 X 光片
5. 定位一致性检查
6. 手术方案（标题重写 + 逐段改写）
7. 生存红线 + 终审评分

发给用户。

### 第 5 步：人工微调

**默认等用户改完再继续**，但用户可能说"我不修了，你继续"——这时**自动把审计步骤（第4步）发现的问题全部打上初稿**，然后直接进入终检，不再等用户手动编辑。

**自动修复流程**（当用户跳过微调时）：
1. 把审计报告里每个"手术方案"逐条 patch 到 article.md
2. 如果有 charts.html，同步更新其中的数据/文字
3. 跑一遍终检确认修复没有引入新问题
4. 直接进第6步截图

提醒用户（仅在用户选择手动微调时）：
- 加入 1-2 处个人经历或观点
- 调整 2-3 句表达，让语气更像自己
- 检查数据和案例是否准确

### 第 5.5 步：终检（发布前最后检查）

**触发**：人工微调完成后、排版之前

**操作**：自动执行以下检查清单，逐项报告通过/不通过。

#### 内容质量
- [ ] 标题有具体数字/人物/事件（对照爆款公式）
- [ ] 开头150字内有钩子+痛点共鸣
- [ ] 无AI味句式残留（"这不是段子"、"听起来很专业对吧"、过度排比、翻译腔）
- [ ] 个人经历真实（跟MEMORY/历史文章不矛盾）
- [ ] 无未替换的占位符（`IMAGE:chart`、`截图：xxx`）
- [ ] 分隔线≤3处
- [ ] 引用块密度够（每300字至少一个）
- [ ] 段落不超3行（约60字）
- [ ] 结尾CTA具体、不煽情
- [ ] 字数在目标范围内

#### 封面图
- [ ] 封面比例2.35:1
- [ ] 封面尺寸≥600px宽
- [ ] 封面文字缩略图下可读（用Pillow模拟100px宽缩略图验证）
- [ ] 封面视觉在公众号文章列表里醒目

#### 配图
- [ ] 每张配图在macOS窗口边框内（红黄绿三圆点+标题栏）
- [ ] 配图文字清晰可读（字体≥12px）
- [ ] 配图位置在对应段落附近
- [ ] **配图数量≥2张内容配图**（封面+2-3张内容配图，1张不够——2026-07-25 Archer 明确反馈"一个配图够了吗"）
- [ ] 截图用 `--selector` 精确截取，无大面积留白
- [ ] GLM-4V 自动质检已通过（窗口边框+内容占比>70%+文字清晰）

#### 格式规范
- [ ] 无有序/无序列表（`-` 或 `1. 2. 3.`）
- [ ] 无整句加粗（只加粗关键词）
- [ ] 工具名用行内代码包裹
- [ ] 每个 `<!-- IMAGE:chartN -->` 都有对应截图文件
- [ ] article-plain.txt 已同步更新

**输出格式**：
```
✅ 通过 / ❌ 不通过 — [检查项]：[说明]
```

不通过项自动修复。修复不了的标记为"需人工确认"，发给用户。

#### 价值验证（发布前最后一关 · 2026-07-28 新增）
- [ ] 能用一句话说出读者能拿走什么吗？
- [ ] 能用一句话说出读者看完会有什么感觉吗？

答不上来，不发。

---

### 第 6 步：发布准备

> ⚠️ **排版工具 = `gzh-design` skill，不是本目录的 publish-article.py + Raphael**
> `gzh-design` 是专门的公众号排版引擎，有主题组件库（红白色系、石墨极简风等）、校验脚本、预览页生成。排版时加载 `gzh-design` skill 并按其工作流执行，不要用本 skill 的 `publish-article.py` 走 Raphael 注入老路。

1. 文章中用 `<!-- IMAGE:chartN -->` 标记配图位置（每篇至少 2-4 张：封面 + 1-3 张内容配图，单张配图太单薄）
2. **封面 + 所有配图合并到一个 `charts.html` 文件**，不要生成 cover.html 或多个文件
3. 每张图之间用 `120px` 间距 + 虚线分隔，标注「封面」「配图 1」「配图 2」…
4. 每张**配图**（不含封面）必须包裹在 macOS 窗口边框中（红黄绿三圆点 + 标题栏 + 圆角），封面不加框
5. 所有图表 HTML 必须适配移动端（viewport meta + clamp/vw 响应式）
6. 所有文件放 `drafts/[主题]-publish/`
7. `open` 该文件夹

#### 6a. 配图 HTML 模板（必须使用）

配图内容必须包裹在以下 macOS 窗口边框结构中，**不得裸截图**：

```html
<!-- 每张配图的标准结构 -->
<div class="window">
  <div class="titlebar">
    <div class="dot red"></div>
    <div class="dot yellow"></div>
    <div class="dot green"></div>
    <span class="titlebar-text">窗口标题</span>
  </div>
  <div class="content">
    <!-- 配图内容 -->
  </div>
</div>

<style>
.window {
  width: min(90vw, 640px);
  background: #fff;
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 4px 24px rgba(0,0,0,0.12);
}
.titlebar {
  display: flex; align-items: center;
  padding: 10px 14px; background: #f0f0f0;
  border-bottom: 1px solid #e0e0e0;
}
.dot { width: 11px; height: 11px; border-radius: 50%; margin-right: 7px; }
.dot.red { background: #ff5f57; }
.dot.yellow { background: #febc2e; }
.dot.green { background: #28c840; }
.titlebar-text { margin-left: 6px; font-size: 12px; color: #999; }
.content { padding: clamp(20px, 4vw, 36px) clamp(24px, 5vw, 40px); }
</style>
```

**封面结构**（不加窗口边框）：
```html
<div class="cover">
  <!-- 封面内容，比例 2.35:1 -->
</div>
```

#### 6b. 截图规则（必须遵守）

> ⚠️ **2026-07-26 更新：优先用 Playwright Python API，不用 playwright-cli。**
> `playwright-cli` 需要先 `open` 再 `screenshot`（两步），且不支持 `--url` 参数。
> Playwright Python API（`sync_playwright` + `locator.screenshot()`）一步到位，更可靠。

**前置条件**（一次性）：
```bash
source /Users/archer/Desktop/hermes/openclaw-data/kb-venv/bin/activate
playwright install chromium  # 首次需要，后续跳过
```

**截图脚本**（用 execute_code 或 terminal 跑 Python）：
```python
from playwright.sync_api import sync_playwright
import json, base64, os

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 900, "height": 1200})
    page.goto("http://localhost:8766/charts.html")
    page.wait_for_timeout(1500)

    # 封面
    page.locator(".cover").screenshot(path="screenshots/cover.png")

    # 配图（逐个截取所有 .window）
    windows = page.locator(".window")
    for i in range(windows.count()):
        windows.nth(i).screenshot(path=f"screenshots/chart{i+1}.png")

    # 生成 images.json（base64，含 data:image/png;base64, 前缀）
    images = {}
    for name in ["cover.png", "chart1.png", "chart2.png"]:
        with open(f"screenshots/{name}", "rb") as f:
            key = name.replace(".png", "")
            images[key] = f"data:image/png;base64,{base64.b64encode(f.read()).decode()}"
    with open("screenshots/images.json", "w") as f:
        json.dump(images, f)

    browser.close()
```

**HTTP 服务**：用 `terminal(background=true)` 启动，不是 foreground `&`：

> ⚠️ **2026-07-27 踩坑：foreground `python3 -m http.server 8766 &` 会被 Hermes 拒绝**（"Foreground command uses '&' backgrounding"）。必须用 `terminal(background=true)` 启动 HTTP 服务。
```python
terminal(command="cd drafts/xxx-publish && python3 -m http.server 8766", background=True)
```

**playwright-cli 备选**（Python API 不可用时）：
1. 先 `playwright-cli open "http://localhost:8766/charts.html"`
2. 再 `playwright-cli screenshot ".cover" --filename screenshots/cover.png`

#### 6c. 配图自动质检（每张截图后必须执行）

截完每张配图后，**自动调用视觉模型验证**（⚠️ 2026-07-25 更新：`browser_vision` 可能返回 429/权限不足，此时改用 `mcp_zhipu_vision_analyze_image` 作为质检工具，同样有效）：

**方法一：智谱 MCP（推荐，稳定）**
```
mcp_zhipu_vision_analyze_image
  image_source="<截图路径>"
  prompt="检查这张配图：1.是否有macOS窗口边框（红黄绿三圆点+标题栏）？2.是否有大面积留白（内容占比是否>70%）？3.文字是否清晰可读？4.内容是什么？请回答：通过/不通过，并说明原因。"
```

**方法二：browser_vision（可能 429）**
```bash
mcporter --config <mcporter_config> call glm-vision analyze_image \
  image_source="<截图路径>" \
  prompt="检查这张配图：1.是否有macOS窗口边框（红黄绿三圆点+标题栏）？2.是否有大面积留白（内容占比是否>70%）？3.文字是否清晰可读？4.内容是什么？请回答：通过/不通过，并说明原因。"
```

**质检标准：**
- ✅ macOS 窗口边框存在（封面除外）
- ✅ 内容占比 > 70%，无大面积留白
- ✅ 文字清晰可读
- ❌ 任一项不通过 → 自动调整 HTML 并重新截图，**最多重试 2 次**
- ❌ 重试 2 次仍不通过 → 标记"需人工确认"，发给用户

**⚠️ Vision 质检假阴性交叉验证（2026-07-28 踩坑）**

`mcp_zhipu_vision_analyze_image` 有时会**误报"没有 macOS 窗口边框"**——即使截图实际包含红黄绿三圆点。原因可能是截图区域较小或模型注意力偏差。

**交叉验证方法**：当 vision 报告"不通过"但你确信 HTML 有 `.window` + 三圆点结构时，用 PIL 像素分析验证：

```python
from PIL import Image
img = Image.open("screenshots/chartN.png")
w, h = img.size
top = img.crop((0, 0, w, 40))  # 顶部40px区域
colors = top.getcolors(maxcolors=100000)
if colors:
    red = any(c for c in colors if c[1][0] > 240 and c[1][1] < 120 and c[1][2] < 120)
    yellow = any(c for c in colors if c[1][0] > 240 and c[1][1] > 150 and c[1][2] < 80)
    green = any(c for c in colors if c[1][0] < 100 and c[1][1] > 180 and c[1][2] > 80)
    print(f"红:{'有' if red else '无'} 黄:{'有' if yellow else '无'} 绿:{'有' if green else '无'}")
```

三个颜色都有 → 窗口边框存在，判定**通过**。PIL 需要 `pip install Pillow`。

**封面质检（标准不同）：**
- ✅ 比例约 2.35:1
- ✅ 文字在缩略图下可读
- ✅ 无窗口边框

也可直接用一键脚本：
```bash
# 完整流程（截图+注入）
python3 scripts/publish-article.py drafts/[主题]-publish

# 只截图
python3 scripts/publish-article.py drafts/[主题]-publish --screenshot-only

# 跳过截图，直接注入
python3 scripts/publish-article.py drafts/[主题]-publish --skip-screenshot
```

#### 7b. 排版（委托 `gzh-design` skill）

> ⚠️ **排版必须走 `gzh-design` skill**，不要自己手写 HTML 或用 `publish-article.py` 的 publish.html 模式。
> `gzh-design` 有完整的主题组件库（红白色系、摸鱼绿、石墨极简等）、`<span leaf>` 包裹、校验脚本、预览页生成——自己手写达不到这个质量。

**步骤**：

1. 用 `skill_view(name='openclaw-imports/gzh-design')` 加载排版 skill
2. 按 `gzh-design` 的工作流执行：选主题 → 读组件库 → 装配 HTML → 校验 → 生成预览页
3. **配图嵌入**：从 `screenshots/images.json` 读取 base64，嵌入到排版 HTML 的 `<img src="...">` 中
4. 跑校验：`python3 <gzh-design skill path>/scripts/validate_gzh_html.py <生成的.html>`
5. 生成预览页：`python3 <gzh-design skill path>/scripts/wrap_preview.py <校验通过的.html>`
6. `open` 打开预览页

**用户操作**：
1. 在浏览器预览页中查看排版效果
2. 点右上角「复制到公众号」
3. 公众号后台 ⌘+V 粘贴
4. 上传封面图：`screenshots/cover.png`
5. 发布

**发布后回填数据**：发表日期、阅读量、点赞、转发 → 更新 `published-history.md`

**配图 base64 防 double-prefix（2026-07-25 踩坑）**

`screenshots/images.json` 里的 value **已经包含** `data:image/png;base64,` 前缀。

嵌入 HTML 时**不要再加**：
```python
# ❌ 错误：double prefix，图片不显示
img_src = f"data:image/png;base64,{images[key]}"

# ✅ 正确：直接用
img_src = images[key]
```

**排版 HTML 生成：Python 脚本 > delegate_task（2026-07-28 实践，两次修订）**

当文章配图 ≥ 3 张时，base64 数据总 size 超过 100KB，直接在主 agent 里生成 HTML 会超出 token 限制或被截断。

**推荐方式：`write_file` 写 Python 生成脚本 → `terminal` 执行**

> 📎 模板脚本：`templates/gen_gzh_html.py` — 包含红白色系所有组件函数（引言卡、章节标题、正文段落、引用块、图片容器、签名区等），复制到工作目录后按文章内容修改装配部分即可。

1. 用 `write_file` 写一个 `gen_html.py` 到 `drafts/xxx-publish/` 目录，脚本内定义所有主题组件函数（引言卡、章节标题、正文段落、引用块、图片容器等）
2. 脚本读 `article.md` + `screenshots/images.json`，按主题组件库规则拼 HTML，输出到 `article_排版_红白色系.html`
3. 用 `terminal` 执行 `python3 gen_html.py`（秒级完成，320KB HTML）
4. 主 agent 跑 `validate_gzh_html.py` 校验 + `wrap_preview.py` 生成预览页

这种方式比 delegate_task 更快（秒级 vs 3分钟+超时）、更可控（主 agent 全程可见），且不依赖子 agent 的 write_file 落盘。

**⚠️ 不推荐 `delegate_task` 做排版**：2026-07-28 实测，delegate_task 委托排版装配超过 3 分钟未完成（子 agent 处理大量 base64 数据慢）。改用 Python 脚本方式后秒级完成。

**⚠️ 不推荐 `execute_code` 写产物文件**：execute_code 在 sandbox 环境运行，写入的文件路径不落盘到实际目录。且 cron_mode 下被 blocked。用 `write_file`（写脚本）+ `terminal`（执行脚本）替代。

**execute_code 写文件落 sandbox（2026-07-27 踩坑）**

> ⚠️ `execute_code` 工具在 sandbox 环境里运行，写入的文件路径**不会落盘到你指定的实际目录**——它落在 sandbox 的临时目录里。后续 `find` 或 `ls` 在目标目录里找不到文件。

**错误姿势**：用 `execute_code` 生成 HTML 并 `write` 到 `drafts/xxx/article_排版.html`——文件实际写在 sandbox temp dir，不在 drafts 目录里。

**正确姿势**：
1. 用 `write_file` 工具写文件（它直接写实际路径，不经过 sandbox）
2. 如果文件内容包含大 base64 数据需要 Python 拼接，用 `write_file` 写一个带占位符（如 `{{CHART1_B64}}`）的模板，再用 `terminal` 跑 Python 脚本做字符串替换
3. 绝不依赖 `execute_code` 写产物文件——它只适合读+计算+输出到 stdout

#### 备选：publish.html 模式（无 gzh-design 时的 fallback）

如果 `gzh-design` skill 不可用，可用 `scripts/publish-article.py` 生成简单的 publish.html（Markdown 格式 + 复制按钮 → 粘贴到 Raphael）：

```bash
python3 scripts/publish-article.py drafts/[主题]-publish --skip-screenshot
```

但这是 fallback，排版质量和公众号兼容性不如 `gzh-design`。

---

## 发布后：自进化更新

每篇文章发布后，Agent 自动执行：

| 步骤 | 操作 | 写入文件 |
|------|------|----------|
| 1 | 追加发表记录（日期+标题+母题+类型+字数） | `published-history.md` |
| 2 | 标记选题库状态（⬜→✅） | `content-strategy.md` |
| 3 | 更新统计数字（总篇数、母题分布等） | `published-history.md` |
| 4 | 回填数据表现（阅读量/点赞/转发，如有） | `published-history.md` |

### 每周复盘（建议周日）

| 步骤 | 操作 |
|------|------|
| 1 | 分析本周文章数据表现 |
| 2 | 哪类选题/标题/母题表现好 → 优先推荐同类 |
| 3 | 哪类表现差 → 降低优先级或调整角度 |
| 4 | 选题库不足时 → 基于数据 + 热点扩充新选题 |
| 5 | 发现新的标题公式/写作技巧 → 更新 `style-guide.md` |

---

## 参考文档索引

| 文件 | 内容 | 何时读 |
|------|------|--------|
| `references/style-guide.md` | 标题公式、排版规则、写作规范、HKR、金字塔、费曼 | 写初稿/优化文章时 |
| `references/content-strategy.md` | 定位、5大母题、日更节奏、选题库（含状态） | 选题/判断当天该写什么时 |
| `references/published-history.md` | 已发记录、母题分布统计、数据表现 | 选题/避免重复/复盘时 |
| `references/audit-framework.md` | 文章审计 7 部分框架 | 审计文章时 |
| `references/article-example-honest-ship-report.md` | 诚实交付复盘型文章范例（256关键词文） | 写产品复盘/做站总结类文章时 |
| `references/publishing-guide.md` | 排版发布完整指南、踩坑记录、工具对比 | 排版发布时 |
| `scripts/publish-article.py` | 一键排版发布 v2（截图+base64+生成 publish.html） | 排版发布时 |

---

## 快捷触发

| 用户说 | 触发步骤 |
|--------|----------|
| "今天写什么"、"给我选题" | 第 1 步 |
| "展开大纲"、"写大纲" | 第 2 步 |
| "写初稿"、"按大纲写" | 第 3 步 |
| "审计"、"检查这篇文章" | 第 4 步 |
| "配图"、"生成配图" | 第 6 步 |
| "排版"、"发布"、"复制到公众号" | 第 7 步（→ 委托 `gzh-design` skill） |
| "帮我写篇公众号文章" | 第 1-3 步 |
| "完整流程"、"全流程" | 第 1-7 步 |
| "终检"、"最终检查" | 第 5.5 步 |

---

## 核心心法

**先说人话（费曼），先说重点（金字塔），教程涨粉（数据），H+K+R 做好内容。**

---

_更新时间：2026-07-28 | 排版委托 gzh-design skill + 配图≥2张 + 选题红线（不给别人打广告）+ base64 防 double-prefix + vision 质检 MCP fallback + 跨会话上下文恢复红线 + 标题传播力三因子评估法 + 截图优先用 Playwright Python API + 审计后用户可跳过微调（auto-apply fixes）+ 选题去重查文件系统（防并行会话重复写同一选题）+ execute_code 写文件落 sandbox 需用 write_file 替代 + HTTP server 用 background terminal + 选题去重检查四个工作区 + published-history 主动问用户回填状态 + 产品类文章必须加真实网站截图 + 排版 HTML 用 Python 脚本生成（替代 delegate_task）+ vision 质检假阴性用 PIL 像素分析交叉验证 | 日更节奏 | 自进化_
