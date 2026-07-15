// 用法: NODE_PATH=$(npm root -g) node verify/mobile-check.cjs <url>
// 預設用系統 Google Chrome(channel:'chrome');沒裝時 PW_CHANNEL=none 用內建 chromium
const { chromium, devices } = require('playwright');

(async () => {
  const url = process.argv[2] || 'http://localhost:8000/';
  const opts = process.env.PW_CHANNEL === 'none' ? {} : { channel: 'chrome' };
  const browser = await chromium.launch(opts);
  const page = await (await browser.newContext({ ...devices['iPhone 13'] })).newPage();
  await page.goto(url, { waitUntil: 'networkidle' });
  await page.waitForSelector('.card', { timeout: 10000 });
  const cards = await page.locator('.card').count();
  const hscroll = await page.evaluate(
    () => document.documentElement.scrollWidth > window.innerWidth + 1
  );
  await page.getByRole('button', { name: '發文前檢測' }).tap();
  const afterTab = await page.locator('.card').count();
  console.log(JSON.stringify({ cards, hscroll, afterTab }));
  await browser.close();
  if (!cards || hscroll || !afterTab) process.exit(1);
})().catch((e) => {
  console.error(e.message);
  process.exit(1);
});
