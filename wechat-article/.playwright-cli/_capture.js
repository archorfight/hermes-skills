async (page) => {
  await page.goto("http://localhost:8765/charts.html");
  await page.setViewportSize({width: 900, height: 2000});
  await page.waitForTimeout(800);

  // Capture cover
  const cover = await page.$(".cover");
  if (cover) {
    await cover.screenshot({path: "/Users/archer/.agents/skills/wechat-article/drafts/managing-ai-publish/screenshots/cover.png", scale: "css", type: "png"});
  }

  // Capture windows (charts)
  const wins = await page.$$(".window");
  for (let i = 0; i < wins.length; i++) {
    await wins[i].scrollIntoViewIfNeeded();
    await page.waitForTimeout(300);
    await wins[i].screenshot({path: "/Users/archer/.agents/skills/wechat-article/drafts/managing-ai-publish/screenshots/chart" + (i+1) + ".png", scale: "css", type: "png"});
  }

  return "Captured: cover + " + wins.length + " charts";
}