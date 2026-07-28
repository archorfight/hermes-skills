# 排版发布指南

## 工具选择

| 工具 | 场景 | 备注 |
|------|------|------|
| **`gzh-design` skill** | ⭐ 首选排版 | 主题组件库 + `<span leaf>` 包裹 + 校验脚本 + 预览页。排版质量最高 |
| Raphael Publish (publish.raphael.app) | 备选 | 无需登录，粘贴 Markdown 渲染后复制 |
| mdnice (editor.mdnice.com) | 备选 | 需要扫码登录，CodeMirror 编辑器 |
| 公众号后台 | 最终发布 | 需要登录 |

**首选 `gzh-design` skill**：它是专门为公众号排版的 skill，有红白色系、摸鱼绿、石墨极简等主题，自动章节编号、关键词下划线、引言卡片、目录导航、`<span leaf>` 包裹、校验脚本、预览页生成。手写 HTML 或用 Raphael 达不到这个质量。

### 排版工具决策树

```
有 gzh-design skill？
  ├─ YES → 用 gzh-design（选主题 → 装配 → 校验 → 预览页）
  └─ NO  → publish.html 模式（scripts/publish-article.py → 复制 Markdown → 粘贴到 Raphael）
```

### ⚠️ base64 配图防 double-prefix（2026-07-25 踩坑）

`screenshots/images.json` 的 value **已包含** `data:image/png;base64,` 前缀。

嵌入任何 HTML（无论 gzh-design 还是 publish.html）时**直接用 value**，不要再拼前缀：

```python
# ❌ 导致 "data:image/png;base64,data:image/png;base64,iVBOR..." → 图片不显示
img_src = f"data:image/png;base64,{images[key]}"

# ✅ 正确
img_src = images[key]  # 已有前缀
```

---

## 完整排版流程

### 一键命令（v2 — publish.html 模式）

```bash
# 完整流程：截图 + base64 + 生成 publish.html + 自动打开浏览器
python3 scripts/publish-article.py drafts/xxx-publish

# 已有截图，跳过截图步骤
python3 scripts/publish-article.py drafts/xxx-publish --skip-screenshot

# 只截图不生成 publish.html
python3 scripts/publish-article.py drafts/xxx-publish --screenshot-only
```

脚本会自动：
1. 启动 HTTP 服务，截图 charts.html → PNG
2. PNG 转 base64
3. 生成 `publish.html`（内置复制按钮 + Raphael 链接）
4. `open` 打开浏览器

### 用户操作

1. 在浏览器中点击「📋 复制 Markdown」
2. 点击「🔗 打开 Raphael」链接
3. 粘贴到 Raphael 左侧编辑区
4. 选主题风格，点击「复制到公众号」
5. 打开公众号后台粘贴
6. 上传封面图，发布

---

## 历史踩坑（v1 playwright 注入模式，已弃用）

> 以下记录来自旧版 playwright 自动注入方案。v2 改为本地 publish.html 模式后不再需要这些 workaround，但保留作为参考。

**为什么弃用 v1？** playwright-cli 在 Hermes 环境下有路径权限限制（"outside allowed roots"），写入 `~/.openclaw/workspace-media` 会失败。v2 不依赖 playwright 注入，只用于截图。

- ❌ pbcopy 从 agent 进程调用不可靠
- ❌ playwright headless 模式用户看不到浏览器
- ❌ HTTPS 页面（Raphael）不能 fetch HTTP localhost
- ❌ React textarea 需要 nativeInputValueSetter + dispatchEvent('input')
- ✅ v2 的 publish.html 用 `document.execCommand("copy")` 在用户浏览器里执行，没有这些问题

---

## 配图 HTML 模板规范

配图统一放在 `charts.html`，结构要求：

### ⚠️ 封面必须遵守的比例

**封面比例必须为 `aspect-ratio: 2.35 / 1`**（公众号封面标准比例），宽扁横版。

❌ 错误：正方形封面（`width: 430px; height: 430px`）
❌ 错误：窄高封面
✅ 正确：`width: 100%; max-width: 800px; aspect-ratio: 2.35 / 1;`

### 标准封面 CSS

```css
.cover {
  width: 100%;
  max-width: 800px;
  aspect-ratio: 2.35 / 1;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  /* 深色渐变背景 */
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
  color: #fff;
  padding: clamp(20px, 5vw, 60px);
  position: relative;
  overflow: hidden;
}
.cover h1 {
  font-size: clamp(18px, 4vw, 36px);
  font-weight: 800;
  line-height: 1.4;
  text-align: center;
}
```

### 页面整体布局

```css
body {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px 20px;
  gap: 120px; /* 图与图之间 120px 间距 */
}
```

```html
<body>
  <!-- 封面（不加窗口边框） -->
  <div class="cover">...</div>
  
  <!-- 配图 1（加 macOS 窗口边框） -->
  <div class="window">
    <div class="titlebar">
      <div class="dot dot-red"></div>
      <div class="dot dot-yellow"></div>
      <div class="dot dot-green"></div>
      <div class="titlebar-text">标题</div>
    </div>
    <div class="window-body">...</div>
  </div>
  
  <!-- 更多配图... -->
</body>
```

关键 CSS：
- 使用 `clamp()` 和 `vw` 做响应式
- 每张图之间 `120px` 间距 + 虚线分隔
- `.cover` 选择器用于封面截图
- `.window` 选择器用于配图截图

---

## 文章中配图占位符约定

在 article.md 中使用以下方式标记配图位置：

```
<!-- IMAGE:chart1 -->
```

或使用标准 Markdown 图片语法：

```
![配图描述](chart1)
```

脚本会自动替换为 base64 data URI。
