await (async (page) => {
  await page.goto("https://publish.raphael.app/");
  await page.waitForTimeout(3000);
  return "Raphael loaded";
})(page);
