async (page) => {
  await page.goto("https://publish.raphael.app/");
  await page.waitForTimeout(3000);

  try {
    await page.getByRole("button", { name: "Mac" }).click();
    await page.waitForTimeout(500);
  } catch(e) {}

  return "PAGE_READY";
}