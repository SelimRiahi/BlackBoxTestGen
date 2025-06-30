const fs = require('fs');

async function tryAutoClick(page, visitedSet = new Set(), uiExtractedFile = 'ui-extracted.json', baseUrl) {
  // 1. Load the extracted UI JSON data (array of pages)
  let data;
  try {
    const raw = fs.readFileSync(uiExtractedFile, 'utf-8');
    data = JSON.parse(raw);
  } catch (e) {
    console.error('Failed to load UI extracted file:', e);
    return null;
  }

  // 2. Find the page data matching current URL or fallback to first page
  const currentUrl = page.url();
  const pageData = data.find(d => d.url === currentUrl) || data[0];
  if (!pageData) {
    console.warn('No UI extracted data found for current page');
    return null;
  }

  // 3. Filter buttons (or clickable elements if you want)
  const buttons = pageData.elements.filter(el => 
    el.tag === 'button' || (el.role && el.role.toLowerCase() === 'button')
  );

  // 4. Sort buttons top-to-bottom, left-to-right (optional)
  buttons.sort((a, b) => {
    if (a.boundingBox.y !== b.boundingBox.y) return a.boundingBox.y - b.boundingBox.y;
    return a.boundingBox.x - b.boundingBox.x;
  });

  // 5. Try clicking each button if not visited
  for (const btn of buttons) {
    const { x, y, width, height } = btn.boundingBox;
    const centerX = x + width / 2;
    const centerY = y + height / 2;

    // Create a unique key from button text and position
    const key = `${btn.innerText || '[no-text]'}::${Math.round(centerX)}::${Math.round(centerY)}`;
    if (visitedSet.has(key)) continue; // skip visited

    visitedSet.add(key);
    console.log(`🧠 Trying to click button "${btn.innerText || '[no-text]'}" at (${centerX.toFixed(0)}, ${centerY.toFixed(0)})`);

    const oldUrl = page.url();
    const oldHtml = await page.content();

    try {
      // Puppeteer click at coordinates relative to viewport
      await page.mouse.click(centerX, centerY);
      // Wait a bit for potential navigation or DOM changes
      await page.waitForTimeout(2500);
    } catch (err) {
      console.warn(`⚠️ Failed to click "${btn.innerText}":`, err.message);
      continue;
    }

    const newUrl = page.url();
    const newHtml = await page.content();

    if (newUrl !== oldUrl || oldHtml !== newHtml) {
      console.log('✅ Navigation or DOM changed.');
      return newUrl;
    }
  }

  console.log('⚠️ No buttons caused navigation or DOM change.');
  return null;
}

module.exports = { tryAutoClick };
