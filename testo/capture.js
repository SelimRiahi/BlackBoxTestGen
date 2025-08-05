const fs = require('fs');
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  page.on('dialog', dialog => dialog.accept());

  const apiCalls = [];
  const uiElementsMap = new Map();

  const captureUI = async () => {
    const currentUI = await page.evaluate(() => {
      function getSuggestedSelector(el) {
        if (el.id) return `#${el.id}`;
        if (el.name) return `[name="${el.name}"]`;
        if (el.placeholder) return `[placeholder="${el.placeholder}"]`;
        if (el.innerText) return `${el.tagName.toLowerCase()}:contains("${el.innerText.trim()}")`;
        return el.tagName.toLowerCase();
      }

      const elements = Array.from(document.querySelectorAll('input, button, a, select, textarea'));
      
      return elements.map(el => {
        return {
          tag: el.tagName.toLowerCase(),
          selector: getSuggestedSelector(el),
          disabled: el.disabled,
          visible: !!(el.offsetWidth || el.offsetHeight || el.getClientRects().length),
          timestamp: new Date().toISOString(),
          ...(el.id && { id: el.id }),
          ...(el.className && { class: el.className }),
          ...(el.name && { name: el.name }),
          ...(el.type && { type: el.type }),
          ...(el.placeholder && { placeholder: el.placeholder }),
          ...(el.value && { value: el.value }),
          ...(el.innerText && { text: el.innerText.trim() }),
          ...(el.getAttribute('role') && { role: el.getAttribute('role') }),
          ...(Object.keys(el.dataset).length > 0 && { dataset: { ...el.dataset } })
        };
      });
    });

    currentUI.forEach(element => uiElementsMap.set(element.selector, element));
  };

  const uiCaptureInterval = setInterval(captureUI, 1000);
  page.on('framenavigated', captureUI);
  
  await page.exposeFunction('onDomChange', captureUI);
  await page.evaluate(() => {
    new MutationObserver(() => window.onDomChange())
      .observe(document.body, { childList: true, subtree: true, attributes: true });
  });

  page.on('requestfinished', async (request) => {
    const url = request.url();
    const resourceType = request.resourceType();
    
    if (resourceType === 'xhr' || resourceType === 'fetch') {
      try {
        const response = await request.response();
        if (!response) return;

        apiCalls.push({
          url,
          method: request.method(),
          postData: request.postData(),
          status: response.status(),
          responseBody: await response.text().catch(() => ''),
          timestamp: new Date().toISOString()
        });
      } catch (error) {
        console.error('Error processing request:', error);
      }
    }
  });

  await page.goto('http://localhost:3001');
  await captureUI();

  console.log('Application loaded. Interact with the page - all UI states will be captured.');
  console.log('Press ENTER when done to save results...');

  await new Promise(resolve => process.stdin.once('data', resolve));
  
  clearInterval(uiCaptureInterval);
  fs.writeFileSync('api_calls.json', JSON.stringify(apiCalls, null, 2));
  fs.writeFileSync('ui_elements.json', JSON.stringify(
    Array.from(uiElementsMap.values()), null, 2));

  console.log(`Capture complete. Saved ${apiCalls.length} API calls and ${uiElementsMap.size} UI elements.`);
  await browser.close();
  process.exit(0);
})();