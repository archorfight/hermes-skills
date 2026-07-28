async (page) => {
  // Chart 1 - events
  await page.evaluate(() => document.querySelectorAll(".window")[0].scrollIntoView({block:"center"}));
  await page.waitForTimeout(300);
  await page.locator(".window").first().screenshot({path:"/Users/archer/.agents/skills/wechat-article/drafts/ai-hongliu-publish/screenshots/chart1-events.png", scale:"css", type:"png"});
  
  // Chart 2 - formula
  await page.evaluate(() => document.querySelectorAll(".window")[1].scrollIntoView({block:"center"}));
  await page.waitForTimeout(300);
  await page.locator(".window").nth(1).screenshot({path:"/Users/archer/.agents/skills/wechat-article/drafts/ai-hongliu-publish/screenshots/chart2-formula.png", scale:"css", type:"png"});
  
  // Chart 3 - traps
  await page.evaluate(() => document.querySelectorAll(".window")[2].scrollIntoView({block:"center"}));
  await page.waitForTimeout(300);
  await page.locator(".window").nth(2).screenshot({path:"/Users/archer/.agents/skills/wechat-article/drafts/ai-hongliu-publish/screenshots/chart3-traps.png", scale:"css", type:"png"});
  
  return "All 3 charts captured";
}
