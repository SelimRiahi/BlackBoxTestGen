// crawler.js
const { chromium } = require('playwright');
const fs = require('fs');
const { execSync } = require('child_process');
const { extractViaScreenshot } = require('./extractor');
const { fillFormSmart } = require('./formFiller');
const { tryAutoClick } = require('./smartClicker');



async function crawlAndFill(startUrl) {
   const filePath = 'ui-extracted.json';
try {
  fs.writeFileSync(filePath, '[]');
  console.log('🧹 Cleared ui-extracted.json for a fresh crawl session.');
} catch (err) {
  console.error('❌ Failed to clear ui-extracted.json:', err.message);
}



  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();

  let currentUrl = startUrl;
  const visitedPages = new Map();

  while (true) {
    console.log(`\n🌐 Navigating to: ${currentUrl}`);
    await page.goto(currentUrl, { waitUntil: 'networkidle' });

    const result = await extractViaScreenshot(page, 'page-screenshot.png', currentUrl);

    console.log('🧠 Running extract-ui.py...');
    try {
      execSync('python extract-ui.py', { stdio: 'inherit' });
    } catch (e) {
      console.error('❌ Python script error:', e.message);
      break;
    }

    const fillFile = 'filled_inputs.txt';
    if (!fs.existsSync(fillFile)) {
      console.log('⚠️ filled_inputs.txt not found. Stopping.');
      break;
    }

    const fillLines = fs
      .readFileSync(fillFile, 'utf-8')
      .split('\n')
      .map(line => line.trim())
      .filter(line => /^\d+\..+?:\s*.+$/.test(line));

    if (fillLines.length === 0) {
      console.log('⚠️ No usable lines in filled_inputs.txt. Stopping.');
      break;
    }

    const fillData = {};
    for (const line of fillLines) {
      const match = line.match(/^\d+\.(.+?):\s*(.+)$/);
      if (match) fillData[match[1].trim()] = match[2].trim();
    }

    await fillFormSmart(page, fillData, result.elements, result.ocr.words);

    if (!visitedPages.has(currentUrl)) {
      visitedPages.set(currentUrl, new Set());
    }
    const clickedButtons = visitedPages.get(currentUrl);

    const clickedElements = visitedPages.get(currentUrl) || new Set();
visitedPages.set(currentUrl, clickedElements);

const newUrl = await tryAutoClick(page, clickedElements);

if (newUrl && newUrl !== currentUrl) {
  currentUrl = newUrl;
  continue; // go to next page
} else {
  console.log('🛑 No more actionable elements found. Stopping.');
  break;
}


    if (!navigated && clickedButtons.size === buttons.length) {
      console.log('🛑 All buttons tried, no navigation, stopping.');
      break;
    }
  }

  await browser.close();
  console.log('\n✅ Finished crawling and filling.');
}

// CLI usage
const startUrl = process.argv[2] || 'http://localhost:3001';
crawlAndFill(startUrl);
