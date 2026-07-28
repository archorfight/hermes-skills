#!/usr/bin/env python3
"""
publish-article.py — 公众号文章一键排版发布（v2 — Hermes 版）

生成本地 publish.html，包含文章 + base64 图片 + 复制按钮。
用户在浏览器打开后点击复制，粘贴到 Raphael Publish 即可。

用法:
  python3 scripts/publish-article.py drafts/xxx-publish

  # 只生成截图，不生成 publish.html
  python3 scripts/publish-article.py drafts/xxx-publish --screenshot-only

  # 跳过截图（已有 images.json）
  python3 scripts/publish-article.py drafts/xxx-publish --skip-screenshot
"""

import argparse
import base64
import json
import os
import subprocess
import sys
import time


# ============================================================
# Config
# ============================================================

HTTP_PORT = 8765


# ============================================================
# Utils
# ============================================================

def run(cmd, timeout=30):
    result = subprocess.run(
        cmd, shell=True, capture_output=True, text=True, timeout=timeout
    )
    return result.returncode, result.stdout, result.stderr


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def png_to_data_uri(path):
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    return f"data:image/png;base64,{b64}"


def resize_image(path, max_width=800):
    try:
        from PIL import Image
    except ImportError:
        print(f"  ⚠️ Pillow not installed, skipping resize for {path}")
        return path

    img = Image.open(path)
    if img.width <= max_width:
        return path

    ratio = max_width / img.width
    new_h = int(img.height * ratio)
    img = img.resize((max_width, new_h), Image.LANCZOS)
    img.save(path, "PNG", optimize=True)
    print(f"  ↳ Resized {os.path.basename(path)}: {img.width}x{new_h}")
    return path


def resize_images_in_dir(directory, max_width=800):
    for fname in sorted(os.listdir(directory)):
        if fname.endswith(".png"):
            resize_image(os.path.join(directory, fname), max_width)


# ============================================================
# Step 1: HTTP Server + Screenshot
# ============================================================

def ensure_http_server(directory, port=HTTP_PORT):
    rc, out, _ = run(f"lsof -ti:{port}", timeout=5)
    if rc == 0 and out.strip():
        run(f"lsof -ti:{port} | xargs kill 2>/dev/null", timeout=5)
        time.sleep(0.5)

    subprocess.Popen(
        ["python3", "-m", "http.server", str(port), "--directory", directory],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(1)
    rc, _, _ = run(f"curl -s -o /dev/null -w '%{{http_code}}' http://localhost:{port}/", timeout=5)
    return rc == 0


def screenshot_charts(html_path, outdir):
    """Use playwright-cli to screenshot charts from HTML."""
    html_dir = os.path.dirname(os.path.abspath(html_path))
    html_file = os.path.basename(html_path)

    ensure_dir(outdir)

    if not ensure_http_server(html_dir, HTTP_PORT):
        print("ERROR: Failed to start HTTP server", file=sys.stderr)
        sys.exit(1)

    # Navigate to the page
    run("playwright-cli close 2>/dev/null || true", timeout=5)
    rc, _, err = run(f'playwright-cli open "http://localhost:{HTTP_PORT}/{html_file}"', timeout=15)
    if rc != 0:
        print(f"WARN: open failed: {err.strip()}", file=sys.stderr)

    time.sleep(1)

    # Screenshot cover
    rc, out, err = run(f'playwright-cli screenshot ".cover" --filename "{outdir}/cover.png"', timeout=15)
    if rc == 0:
        print(f"  ↳ cover.png captured")
    else:
        print(f"  ⚠️ cover screenshot failed: {err.strip()}")

    # Screenshot each .window element
    chart_idx = 1
    while True:
        out_name = f"chart{chart_idx}.png"
        rc, out, err = run(
            f'playwright-cli screenshot ".window >> nth={chart_idx - 1}" --filename "{outdir}/{out_name}"',
            timeout=15
        )
        if rc != 0:
            # Try without nth (first .window already captured or only one)
            if chart_idx == 1:
                rc, out, err = run(
                    f'playwright-cli screenshot ".window" --filename "{outdir}/{out_name}"',
                    timeout=15
                )
            if rc != 0:
                break
        print(f"  ↳ {out_name} captured")
        chart_idx += 1
        if chart_idx > 10:  # safety limit
            break

    return chart_idx > 1


# ============================================================
# Step 2: Generate images.json
# ============================================================

def generate_images_json(outdir):
    images = {}
    for fname in sorted(os.listdir(outdir)):
        if not fname.endswith(".png"):
            continue
        key = fname.replace(".png", "")
        images[key] = png_to_data_uri(os.path.join(outdir, fname))

    json_path = os.path.join(outdir, "images.json")
    with open(json_path, "w") as f:
        json.dump(images, f)

    print(f"Generated images.json ({len(images)} images, {os.path.getsize(json_path)//1024}KB)")
    return images


# ============================================================
# Step 3: Generate publish.html
# ============================================================

def generate_publish_html(draft_dir, article_path, images):
    """Generate a self-contained publish.html with copy buttons."""

    with open(article_path, "r") as f:
        article = f.read()

    # Replace IMAGE placeholders with markdown img + base64
    # ⚠️ images.json values already include "data:image/png;base64," prefix
    # Do NOT add it again — double prefix causes images to not render
    used_keys = []
    for key, b64 in images.items():
        if key == "cover":
            continue
        placeholder = f"<!-- IMAGE:{key} -->"
        if placeholder in article:
            article = article.replace(placeholder, f"\n![{key}]({b64})\n")
            used_keys.append(key)

    # Escape for embedding in HTML textarea
    article_escaped = article.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    cover_path = os.path.join(draft_dir, "screenshots", "cover.png")

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>复制到公众号</title>
<style>
  body {{
    font-family: -apple-system, BlinkMacSystemFont, sans-serif;
    max-width: 900px;
    margin: 0 auto;
    padding: 40px 20px;
    background: #f9fafb;
    color: #1f2937;
  }}
  .header {{
    text-align: center;
    margin-bottom: 32px;
  }}
  .header h1 {{
    font-size: 24px;
    margin: 0 0 8px;
  }}
  .header p {{
    color: #6b7280;
    font-size: 14px;
  }}
  .btn-row {{
    display: flex;
    gap: 12px;
    justify-content: center;
    margin: 24px 0;
    flex-wrap: wrap;
  }}
  .btn {{
    padding: 12px 28px;
    font-size: 15px;
    border: none;
    border-radius: 10px;
    cursor: pointer;
    font-weight: 600;
    transition: transform 0.1s;
  }}
  .btn:hover {{ transform: translateY(-1px); }}
  .btn-primary {{ background: #6366f1; color: #fff; }}
  .btn-secondary {{ background: #10b981; color: #fff; }}
  .btn-link {{
    padding: 12px 28px;
    font-size: 15px;
    background: #e5e7eb;
    color: #374151;
    border-radius: 10px;
    text-decoration: none;
    display: inline-flex;
    align-items: center;
  }}
  textarea {{
    width: 100%;
    height: 200px;
    margin-top: 16px;
    border: 1px solid #d1d5db;
    border-radius: 10px;
    padding: 12px;
    font-family: monospace;
    font-size: 12px;
    resize: vertical;
  }}
  .preview {{
    margin-top: 24px;
    padding: 24px;
    border: 1px solid #d1d5db;
    border-radius: 10px;
    background: #fff;
    line-height: 1.8;
    font-size: 15px;
  }}
  .preview img {{ max-width: 100%; border-radius: 8px; }}
  .alert {{
    position: fixed;
    top: 20px;
    left: 50%;
    transform: translateX(-50%);
    background: #6366f1;
    color: #fff;
    padding: 12px 24px;
    border-radius: 8px;
    font-size: 14px;
    opacity: 0;
    transition: opacity 0.3s;
    z-index: 999;
  }}
  .alert.show {{ opacity: 1; }}
</style>
</head>
<body>

<div class="header">
  <h1>✅ 文章已就绪</h1>
  <p>共 {len(article)} 字符，{len(used_keys)} 张配图</p>
</div>

<div class="btn-row">
  <button class="btn btn-primary" onclick="copyMarkdown()">📋 复制 Markdown</button>
  <button class="btn btn-secondary" onclick="copyHTML()">📋 复制渲染 HTML</button>
  <a class="btn-link" href="https://publish.raphael.app/" target="_blank">🔗 打开 Raphael</a>
</div>

<div class="btn-row" style="margin-top:0">
  <a class="btn-link" href="screenshots/cover.png" target="_blank">🖼️ 查看封面图</a>
</div>

<textarea id="article" readonly>{article_escaped}</textarea>

<div class="preview" id="rendered"></div>

<div class="alert" id="alert"></div>

<script>
const md = document.getElementById("article").value;
const rendered = document.getElementById("rendered");

// Simple markdown to HTML for preview
function md2html(md) {{
  let html = md;
  // images (data URIs)
  html = html.replace(/!\\[([^\\]]*)\\]\\((data:image[^)]+)\\)/g, '<img src="$2" alt="$1" />');
  // headers
  html = html.replace(/^### (.+)$/gm, '<h3>$1</h3>');
  html = html.replace(/^## (.+)$/gm, '<h2>$1</h2>');
  html = html.replace(/^# (.+)$/gm, '<h1>$1</h1>');
  // bold
  html = html.replace(/\\*\\*([^*]+)\\*\\*/g, '<strong>$1</strong>');
  // blockquote
  html = html.replace(/^> (.+)$/gm, '<blockquote>$1</blockquote>');
  // hr
  html = html.replace(/^---$/gm, '<hr>');
  // inline code
  html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
  // paragraphs (split by double newline, skip block elements)
  const blocks = html.split(/\\n\\n+/);
  html = blocks.map(b => {{
    if (b.startsWith('<')) return b;
    return '<p>' + b.replace(/\\n/g, '<br>') + '</p>';
  }}).join('\\n');
  return html;
}}

rendered.innerHTML = md2html(md);

function showAlert(msg) {{
  const el = document.getElementById('alert');
  el.textContent = msg;
  el.classList.add('show');
  setTimeout(() => el.classList.remove('show'), 2000);
}}

function copyMarkdown() {{
  const ta = document.getElementById("article");
  ta.removeAttribute("readonly");
  ta.select();
  document.execCommand("copy");
  ta.setAttribute("readonly", "");
  showAlert("✅ Markdown 已复制！粘贴到 Raphael 左侧编辑区即可。");
}}

function copyHTML() {{
  const html = rendered.innerHTML;
  navigator.clipboard.write(html).then(() => {{
    showAlert("✅ HTML 已复制！可直接粘贴到公众号后台编辑器。");
  }}).catch(() => {{
    // Fallback
    const ta = document.createElement('textarea');
    ta.value = html;
    document.body.appendChild(ta);
    ta.select();
    document.execCommand('copy');
    document.body.removeChild(ta);
    showAlert("✅ HTML 已复制！");
  }});
}}
</script>

</body>
</html>'''

    out_path = os.path.join(draft_dir, "publish.html")
    with open(out_path, "w") as f:
        f.write(html)

    print(f"\n✅ publish.html generated ({len(article)} chars, {len(used_keys)} images)")
    return out_path


# ============================================================
# Main
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="公众号文章一键排版发布 (v2)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument("draft_dir", help="Draft directory")
    parser.add_argument("--screenshot-only", action="store_true")
    parser.add_argument("--skip-screenshot", action="store_true")
    parser.add_argument("--max-width", type=int, default=800)
    parser.add_argument("--no-open", action="store_true", help="Don't auto-open browser")
    args = parser.parse_args()

    draft_dir = os.path.abspath(args.draft_dir)
    article_path = os.path.join(draft_dir, "article.md")
    charts_path = os.path.join(draft_dir, "charts.html")
    screenshots_dir = os.path.join(draft_dir, "screenshots")

    if not os.path.exists(article_path):
        print(f"ERROR: article.md not found in {draft_dir}", file=sys.stderr)
        sys.exit(1)

    # Step 1: Screenshot
    if not args.skip_screenshot:
        if not os.path.exists(charts_path):
            print("No charts.html found, skipping screenshots")
        else:
            print("📸 Step 1: Capturing screenshots...")
            screenshot_charts(charts_path, screenshots_dir)

    # Step 2: Resize
    if args.max_width > 0 and os.path.isdir(screenshots_dir):
        print(f"📐 Resizing images (max {args.max_width}px)...")
        resize_images_in_dir(screenshots_dir, args.max_width)

    # Step 3: images.json
    images = {}
    if os.path.isdir(screenshots_dir):
        images = generate_images_json(screenshots_dir)

    if args.screenshot_only:
        print("\n✅ Screenshots done.")
        return

    # Step 4: Generate publish.html
    print("\n📄 Step 2: Generating publish.html...")
    publish_path = generate_publish_html(draft_dir, article_path, images)

    # Step 5: Open in browser
    if not args.no_open:
        run(f'open "{publish_path}"', timeout=5)

    cover_path = os.path.join(screenshots_dir, "cover.png")

    print(f"""
{'='*50}
✅ publish.html 已生成并打开！

👉 接下来：
   1. 点击「复制 Markdown」按钮
   2. 打开 Raphael Publish（按钮已内置链接）
   3. 粘贴到左侧编辑区
   4. 选主题风格，点击「复制到公众号」
   5. 打开公众号后台粘贴
   6. 上传封面图：{cover_path}
   7. 发布
{'='*50}
""")


if __name__ == "__main__":
    main()
