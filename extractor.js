const fs = require('fs');
const Tesseract = require('tesseract.js');

async function extractViaScreenshot(page, screenshotPath = 'page-screenshot.png', currentUrl) {
  console.log('📸 Taking screenshot...');
  await page.screenshot({ path: screenshotPath, fullPage: true });

  console.log('🔍 Running OCR...');
  let ocrData;
  try {
    const res = await Tesseract.recognize(screenshotPath, 'eng', {
      logger: m => process.stdout.write(`OCR progress: ${Math.round(m.progress * 100)}%\r`),
      psm: 6,
    });
    ocrData = res.data;
  } catch (err) {
    console.error('❌ OCR failed:', err);
    ocrData = { text: '', words: [] };
  }

  console.log('📏 Extracting DOM element bounding boxes...');
  const formElements = await page.$$eval('input, textarea, select, button, a', els =>
    els.map(el => {
      const rect = el.getBoundingClientRect();
      return {
        tag: el.tagName.toLowerCase(),
        role: el.getAttribute('role') || null,
        type: el.type || null,
        name: el.name || null,
        id: el.id || null,
        placeholder: el.placeholder || null,
        ariaLabel: el.getAttribute('aria-label') || null,
        innerText: el.innerText?.trim() || null,
        boundingBox: {
          x: rect.x,
          y: rect.y,
          width: rect.width,
          height: rect.height
        }
      };
    })
  );

  const result = {
    url: currentUrl,
    timestamp: Date.now(),
    ocr: {
      textBlocks: (ocrData.text || '').trim().split('\n').filter(Boolean),
      words: (ocrData.words || []).map(w => ({
        text: w.text,
        bbox: w.bbox,
        confidence: w.confidence
      }))
    },
    elements: formElements
  };

  const filePath = 'ui-extracted.json';
  let allData = [];
  if (fs.existsSync(filePath)) {
    try {
      const oldData = fs.readFileSync(filePath, 'utf-8');
      allData = JSON.parse(oldData);
      if (!Array.isArray(allData)) allData = [];
    } catch {
      allData = [];
    }
  }

  const isDuplicate = allData.some(
    item => item.url === result.url && item.timestamp === result.timestamp
  );

  if (!isDuplicate) {
    allData.push(result);
    fs.writeFileSync(filePath, JSON.stringify(allData, null, 2));
    console.log('\n✅ Appended OCR + DOM element data to ui-extracted.json');
  } else {
    console.log('\nℹ️ Duplicate entry detected, skipping append.');
  }

  return result;
}

module.exports = { extractViaScreenshot };
