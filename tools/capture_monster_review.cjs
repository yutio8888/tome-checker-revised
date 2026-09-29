// Render real browser pages after images and fonts load; do not edit creature pixels.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const config = JSON.parse(fs.readFileSync(0, 'utf8'));
const {chromium} = require(config.playwright);

(async () => {
  const browser = await chromium.launch({
    executablePath: config.browser,
    headless: true,
    args: ['--no-sandbox', '--disable-gpu', '--allow-file-access-from-files'],
  });
  const report = {deviceScaleFactor: 1, runtimeScreenshot: false, pages: []};
  try {
    for (const job of config.jobs) {
      const page = await browser.newPage({viewport: {width: 1440, height: 1100}, deviceScaleFactor: 1});
      const failures = [];
      page.on('pageerror', err => failures.push(err.message));
      page.on('requestfailed', req => failures.push(req.url() + ': ' + req.failure()?.errorText));
      await page.goto(job.url, {waitUntil: 'load', timeout: 15000});
      for (const [selector, value] of Object.entries(job.select || {})) {
        await page.selectOption(selector, value);
      }
      await page.evaluate(async () => {
        await document.fonts.ready;
        await Promise.all(Array.from(document.images, img => img.decode()));
      });
      const count = await page.locator('article').count();
      if (count !== job.count) throw new Error(`Expected ${job.count} cards, got ${count}: ${job.url}`);
      if (failures.length) throw new Error(failures.join('\n'));
      const checks = await page.evaluate(() => ({
        loadedImages: Array.from(document.images).filter(img => img.naturalWidth > 0).length,
        badImages: Array.from(document.images).filter(img => !img.naturalWidth).map(img => img.src),
        sampleSizes: Array.from(document.querySelectorAll('.samples img')).map(img => ({
          natural: img.naturalWidth, displayed: img.getBoundingClientRect().width,
        })),
      }));
      if (checks.badImages.length) throw new Error('Missing images: ' + checks.badImages.join(', '));
      if (checks.sampleSizes.some(s => s.displayed > 0 && s.displayed !== s.natural)) {
        throw new Error('Small-size samples are not displayed at their native pixel size');
      }
      await page.screenshot({path: job.file, fullPage: true});
      const bytes = fs.readFileSync(job.file);
      if (bytes.length < 10000) throw new Error('Unexpectedly empty capture: ' + job.file);
      report.pages.push({file: path.basename(job.file), cards: count, ...checks,
        sha256: crypto.createHash('sha256').update(bytes).digest('hex')});
      console.log(job.file);
      await page.close();
    }
    fs.writeFileSync(config.report, JSON.stringify(report, null, 2) + '\n');
  } finally {
    await browser.close();
  }
})().catch(err => {console.error(err); process.exitCode = 1;});
