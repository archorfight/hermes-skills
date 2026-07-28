#!/usr/bin/env python3
"""
公众号排版 HTML 生成脚本模板（红白色系）
用法：
  1. 将此文件复制到 drafts/xxx-publish/ 目录
  2. 确保 article.md 和 screenshots/images.json 在同目录
  3. 运行: python3 gen_gzh_html.py
  4. 输出: article_排版_红白色系.html

设计变量在文件顶部，换主题时改这几个颜色即可。
所有文字节点用 <span leaf=""> 包裹，严格遵守公众号平台限制。
"""
import json

# ============ 读取输入 ============
with open("article.md", "r") as f:
    md = f.read()
with open("screenshots/images.json", "r") as f:
    images = json.load(f)

# ============ 设计变量（红白色系）============
MAIN = "#DC2626"
DARK = "#991B1B"
BG_LIGHT = "#FEF2F2"
BG_LIGHTER = "#FEE2E2"
PINK = "#FECACA"
TITLE = "#1C1917"
BODY = "#374151"
MUTED = "#9CA3AF"

# ============ 组件函数 ============
# 每个函数返回一段 HTML 字符串，拼接到 html_parts 列表

def span(text):
    """包裹文字节点（公众号铁律）"""
    return f'<span leaf="">{text}</span>'

def underline(text):
    """淡粉下划线标记（最常用标记样式）"""
    return f'<span style="border-bottom:2px solid {PINK};font-weight:600;">{span(text)}</span>'

def bold(text):
    return f'<strong>{span(text)}</strong>'

def red_bold(text):
    """红色加粗（全文≤5处）"""
    return f'<strong style="color:{MAIN};">{span(text)}</strong>'

def code(text):
    """行内代码"""
    return f'<span style="background:#F3F4F6;color:#1F2937;padding:2px 6px;border-radius:4px;font-size:14px;font-weight:600;">{span(text)}</span>'

def para(text_html):
    """正文段落（15px，行高1.8）"""
    return f'<p style="margin-bottom:20px;font-size:15px;line-height:1.8;text-align:justify;">{text_html}</p>'

def quote_gold(text):
    """金句引用（粉底左竖条，视觉焦点最强）"""
    return f'''<section style="background:{BG_LIGHT};border-radius:0 10px 10px 0;border-left:4px solid {MAIN};padding:18px 22px;margin-bottom:24px;">
  <p style="font-size:16px;font-weight:800;color:{DARK};margin:0;line-height:1.8;">
    {span("「" + text + "」")}
  </p>
</section>'''

def quote_light(text_html):
    """浅红引用块（旁注/Prompt）"""
    return f'''<section style="background:{BG_LIGHT};border-radius:10px;padding:18px 20px;margin-bottom:24px;border:1px solid {PINK};">
  <p style="font-size:15px;color:{BODY};margin:0;line-height:1.8;text-align:justify;">
    {text_html}
  </p>
</section>'''

def img_block(src, caption=None):
    """图片容器（圆角卡片 + 可选说明）"""
    cap = ""
    if caption:
        cap = f'<p style="font-size:12px;color:{MUTED};text-align:center;margin:0 0 24px;">{span("— " + caption)}</p>'
    return f'''<section style="background:#FFF;border-radius:12px;padding:6px;border:1px solid #E5E7EB;box-shadow:0 4px 12px -2px rgba(0,0,0,0.08);margin-bottom:8px;">
  <section style="margin:0;border-radius:8px;overflow:hidden;">
    {span(f'<img src="{src}" style="max-width:100%;height:auto;display:block;margin:0 auto;">')}
  </section>
</section>
{cap}'''

def chapter_header(num, en_tag, cn_title, first=False):
    """章节标题（红底编号 + 英文标签 + 中文标题）"""
    mt = "16px" if first else "48px"
    return f'''<section style="margin-top:{mt};margin-bottom:28px;padding:0 10px;">
  <section style="display:flex;align-items:center;justify-content:space-between;margin-bottom:20px;padding-bottom:14px;border-bottom:3px solid {MAIN};">
    <section style="display:flex;align-items:center;">
      <span style="display:inline-block;background:{MAIN};color:#FFFFFF;font-size:18px;font-weight:900;padding:4px 14px;border-radius:6px;margin-right:14px;line-height:1.3;">{span(num)}</span>
      <section>
        <p style="font-size:10px;color:{MAIN};font-weight:700;letter-spacing:3px;margin:0 0 2px;text-transform:uppercase;">{span(en_tag)}</p>
        <h3 style="font-size:18px;font-weight:800;color:{TITLE};margin:0;letter-spacing:0.5px;">{span(cn_title)}</h3>
      </section>
    </section>
  </section>
</section>'''

def separator():
    """章节分割线（红色渐变）"""
    return f'''<section style="padding:0 10px;">
  <section style="height:1px;background:linear-gradient(to right,transparent,#FCA5A5,#DC2626,#FCA5A5,transparent);margin:0;">{span("<br>")}</section>
</section>'''

def sub_heading(text):
    """子标题（红色左竖条）"""
    return f'<p style="font-size:15px;font-weight:800;color:{TITLE};margin:28px 0 14px;padding-left:10px;border-left:3px solid {MAIN};line-height:1.4;">{span(text)}</p>'

def intro_card(highlight1, middle, highlight2, ending):
    """开头引言卡片（白底红色光晕）"""
    return f'''<section style="margin:10px 10px 32px;background:#ffffff;border-radius:12px;box-shadow:0 4px 24px -4px rgba(220,38,38,0.15);padding:28px 24px 22px;overflow:hidden;">
  <p style="font-size:42px;color:{MAIN};font-weight:900;margin:0;line-height:0.6;">{span("\u201c")}</p>
  <p style="font-size:16px;font-weight:800;color:{TITLE};margin:12px 0 8px;line-height:1.75;padding-left:4px;">
    <span style="background:{MAIN};color:#FFFFFF;padding:2px 8px;border-radius:4px;">{span(highlight1)}</span>
    {span(middle)}
    <span style="background:{MAIN};color:#FFFFFF;padding:2px 8px;border-radius:4px;">{span(highlight2)}</span>
    {span(ending)}
  </p>
</section>'''

def toc_3col(item1, item2, item3):
    """前言导读（3列目录卡片）"""
    items = ""
    for num, text in [("01", item1), ("02", item2), ("03", item3)]:
        mr = "margin-right:8px;" if num != "03" else ""
        items += f'''<section style="flex:1;background:{BG_LIGHT};border-radius:10px;padding:16px 12px;{mr}text-align:center;border:1px solid {BG_LIGHTER};">
      <p style="display:inline-block;background:{MAIN};color:#FFFFFF;font-size:12px;font-weight:800;padding:2px 10px;border-radius:4px;margin:0 0 8px;">{span(num)}</p>
      <p style="font-size:13px;font-weight:700;color:{TITLE};margin:0;">{span(text)}</p>
    </section>'''
    return f'<section style="padding:0 10px 32px;"><p style="font-size:14px;color:{MUTED};margin:0 0 14px;letter-spacing:1px;">{span("\U0001f4cc 本文看点")}</p><section style="display:flex;justify-content:space-between;">{items}</section></section>'

def end_divider():
    """END 结尾分割线"""
    return f'''<section style="padding:0 10px;">
  <section style="text-align:center;margin:0 0 32px;">
    <section style="display:flex;align-items:center;justify-content:center;">
      <span style="height:2px;width:60px;background:linear-gradient(to right,transparent,{MAIN});margin-right:12px;">{span("<br>")}</span>
      <span style="font-size:11px;color:{MAIN};letter-spacing:3px;font-weight:700;">{span("END")}</span>
      <span style="height:2px;width:60px;background:linear-gradient(to left,transparent,{MAIN});margin-left:12px;">{span("<br>")}</span>
    </section>
  </section>
</section>'''

def sign_off(paragraphs):
    """尾部签名区（paragraphs 是 HTML 字符串列表）"""
    inner = "\n  ".join(f'<p style="margin-bottom:20px;font-size:15px;line-height:1.8;text-align:justify;">{p}</p>' for p in paragraphs)
    return f'<section style="padding:0 10px;">\n  {inner}\n</section>'

# ============ 装配 HTML ============
# 参考 article.md 内容，按章节顺序拼装。
# 这是手工映射——每篇文章内容不同，需要根据 article.md 调整。
# 以下是骨架示例（实际使用时替换为文章内容）：

html_parts = []

# 全局容器
html_parts.append(f'<section style="max-width:677px;margin:0 auto;background:#ffffff;font-family:-apple-system,BlinkMacSystemFont,\'PingFang SC\',\'Hiragino Sans GB\',\'Microsoft YaHei\',sans-serif;color:{BODY};line-height:1.75;letter-spacing:0.5px;overflow-x:hidden;">')

# 1. 引言卡片
html_parts.append(intro_card("高亮词1", "中间文字", "高亮词2", "结尾。"))

# 2. 前言正文
html_parts.append('<section style="padding:0 10px;">')
html_parts.append(para(span("前言段落1...")))
html_parts.append(para(span("前言段落2...") + underline("关键词")))
html_parts.append(quote_gold("金句内容"))
html_parts.append(img_block(images.get("chart1", "")))  # chart1 图片
html_parts.append('</section>')

# 3. 前言导读
html_parts.append(toc_3col("看点一", "看点二", "看点三"))

# 4-N. 章节（示例：第一章）
html_parts.append(chapter_header("01", "EN_TAG", "章节标题", first=True))
html_parts.append('<section style="padding:0 10px;">')
html_parts.append(para(span("正文内容...")))
html_parts.append(sub_heading("子标题"))
html_parts.append(para(span("子标题下内容...")))
html_parts.append('</section>')

# 章节之间用 separator()
# html_parts.append(separator())
# html_parts.append(chapter_header("02", "EN_TAG", "第二章标题"))
# ...

# 末章用 ∞ + THE END
# html_parts.append(chapter_header("∞", "THE END", "结语标题"))

# END 分割线 + 签名区
html_parts.append(end_divider())
html_parts.append(sign_off([
    span("感谢你看到这里..."),
    span("互动钩子..."),
    span("点个") + f'<strong style="color:{MAIN};">{span("关注")}</strong>' + span("，具体预告..."),
]))

# 全局容器结束
html_parts.append('</section>')

# 输出
final_html = "\n".join(html_parts)
with open("article_排版_红白色系.html", "w") as f:
    f.write(final_html)

print(f"HTML: {len(final_html)} chars, {final_html.count('leaf=')} spans, {final_html.count('<section')} sections")
print("Done: article_排版_红白色系.html")
