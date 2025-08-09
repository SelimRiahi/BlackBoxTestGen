const fs = require('fs');
const { chromium } = require('playwright');
const { URL } = require('url');

(async () => {
  // Track start time for metadata
  const startTime = new Date();

  // Initialize browser and context
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext();
  const page = await context.newPage();
  page.on('dialog', dialog => dialog.accept());

  // Data stores
  const apiCalls = new Map();
  const uiElementsMap = new Map();
  const uiStateHistory = [];
  const userFlow = [];
  let currentPageUrl = '';
  let lastAction = 'PAGE_LOAD';
  let lastUIState = null;

  // Helper functions
  const arraysEqual = (a, b) => JSON.stringify(a) === JSON.stringify(b);

  const getApiCallKey = (request) => {
    const url = new URL(request.url());
    return `${request.method()}_${url.pathname}`;
  };

  const logUserFlow = (action) => {
    userFlow.push({
      action,
      timestamp: new Date().toISOString(),
      url: page.url()
    });
    lastAction = action;
  };

  // Enhanced UI capture with state tracking
  const captureUI = async (trigger = 'auto') => {
    currentPageUrl = page.url();
    const currentUI = await page.evaluate((currentUrl) => {
      // Improved element path generation
      function getElementPath(el) {
        const path = [];
        let current = el;
        
        while (current.parentNode && current.parentNode.nodeName !== 'BODY') {
          let selector = current.tagName.toLowerCase();
          
          if (current.id) {
            selector += `#${current.id}`;
          } else if (current.className && typeof current.className === 'string') {
            const firstClass = current.className.split(' ')[0];
            if (firstClass) selector += `.${firstClass}`;
          }
          
          // Add nth-child as fallback
          if (!current.id && !current.className) {
            const siblings = Array.from(current.parentNode.children)
              .filter(c => c.tagName === current.tagName);
            const index = siblings.indexOf(current) + 1;
            if (index > 1) selector += `:nth-child(${index})`;
          }
          
          path.unshift(selector);
          current = current.parentNode;
        }
        
        return path.join(' > ');
      }

      // Enhanced selector generation
      function getSuggestedSelector(el) {
        if (el.id) return `#${el.id}`;
        if (el.name) return `[name="${el.name}"]`;
        if (el.placeholder) return `[placeholder="${el.placeholder}"]`;
        if (el.getAttribute('data-testid')) return `[data-testid="${el.getAttribute('data-testid')}"]`;
        return getElementPath(el);
      }

      // Capture all interactive elements
      const elements = Array.from(document.querySelectorAll(
        'input, button, a, select, textarea, [role="button"], [role="checkbox"], [role="radio"]'
      ));
      
      return elements.map(el => {
        const elementInfo = {
          tag: el.tagName.toLowerCase(),
          selector: getSuggestedSelector(el),
          pageUrl: currentUrl,
          elementPath: getElementPath(el),
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

        // Special handling for different element types
        if (el.tagName.toLowerCase() === 'input') {
          elementInfo.inputType = el.type;
          elementInfo.checked = el.checked;
        } else if (el.tagName.toLowerCase() === 'a') {
          elementInfo.href = el.href;
        } else if (el.tagName.toLowerCase() === 'select') {
          elementInfo.options = Array.from(el.options).map(opt => ({
            value: opt.value,
            text: opt.text,
            selected: opt.selected
          }));
        }

        // Detect section context
        const sectionParent = el.closest('[data-section], section, .section');
        if (sectionParent) {
          elementInfo.section = sectionParent.id || 
                               sectionParent.getAttribute('data-section') || 
                               sectionParent.className.split(' ')[0];
        }

        return elementInfo;
      });
    }, currentPageUrl);

    // Track UI state changes
    if (!lastUIState || !arraysEqual(lastUIState, currentUI)) {
      uiStateHistory.push({
        trigger,
        action: lastAction,
        visibleElements: currentUI.filter(el => el.visible).map(el => el.selector),
        timestamp: new Date().toISOString(),
        url: currentPageUrl
      });
      lastUIState = currentUI;
    }

    // Store elements with enhanced metadata
    currentUI.forEach(element => {
      const elementKey = `${currentPageUrl}_${element.selector}`;
      
      // Detect dynamic elements (like task IDs)
      if (element.id && element.id.match(/(\w+)-[0-9a-f]{24}-(\w+)/)) {
        const match = element.id.match(/(\w+)-([0-9a-f]{24})-(\w+)/);
        element.dynamicProperties = {
          pattern: `${match[1]}-{id}-${match[3]}`,
          exampleId: match[2]
        };
      }

      uiElementsMap.set(elementKey, element);
    });
  };

  // Set up monitoring
  const uiCaptureInterval = setInterval(() => captureUI('interval'), 1000);
  page.on('framenavigated', () => {
    logUserFlow('NAVIGATION');
    captureUI('navigation');
  });
  
  // DOM change observer
  await page.exposeFunction('onDomChange', () => captureUI('dom_change'));
  await page.evaluate(() => {
    new MutationObserver(() => window.onDomChange())
      .observe(document.body, { childList: true, subtree: true, attributes: true });
  });

  // Enhanced API monitoring
  page.on('requestfinished', async (request) => {
    const url = request.url();
    const resourceType = request.resourceType();
    
    if (resourceType === 'xhr' || resourceType === 'fetch') {
      try {
        const response = await request.response();
        if (!response) return;

        const apiKey = getApiCallKey(request);
        const responseBody = await response.text().catch(() => '');

        const apiData = {
          url,
          method: request.method(),
          postData: request.postData(),
          status: response.status(),
          responseBody,
          timestamp: new Date().toISOString(),
          pageContext: currentPageUrl,
          uiStateBefore: lastUIState?.filter(el => el.visible).map(el => el.selector)
        };

        // Store unique API calls or updated responses
        if (!apiCalls.has(apiKey)) {
          apiCalls.set(apiKey, apiData);
          logUserFlow(`API_CALL_${request.method()}`);
        } else if (apiCalls.get(apiKey).responseBody !== responseBody) {
          apiCalls.set(apiKey, apiData);
        }
      } catch (error) {
        console.error('Error processing request:', error);
      }
    }
  });

  // Click handler to track user actions
  await page.exposeFunction('logClick', (selector) => {
    logUserFlow(`CLICK_${selector}`);
  });
  await page.evaluate(() => {
    document.addEventListener('click', (e) => {
      const path = e.composedPath();
      const interactiveEl = path.find(el => 
        ['BUTTON', 'A', 'INPUT', 'SELECT', 'TEXTAREA'].includes(el.tagName)
      );
      if (interactiveEl) {
        const selector = interactiveEl.id ? `#${interactiveEl.id}` : 
                        interactiveEl.className ? `.${interactiveEl.className.split(' ')[0]}` : 
                        interactiveEl.tagName.toLowerCase();
        window.logClick(selector);
      }
    }, true);
  });

  // Start capturing
  await page.goto('http://localhost:3001');
  logUserFlow('INITIAL_LOAD');
  await captureUI('initial');

  console.log('Application loaded. Interact with the page - all actions will be captured.');
  console.log('Press ENTER when done to save results...');

  await new Promise(resolve => process.stdin.once('data', resolve));
  
  // Clean up and save
  clearInterval(uiCaptureInterval);
  
  const result = {
    metadata: {
      appUrl: 'http://localhost:3001',
      captureStart: startTime.toISOString(),
      captureEnd: new Date().toISOString(),
      captureDuration: `${(new Date() - startTime)/1000} seconds`
    },
    apiCalls: Array.from(apiCalls.values()),
    uiElements: Array.from(uiElementsMap.values()),
    uiStateHistory,
    userFlow
  };

  fs.writeFileSync('test_data.json', JSON.stringify(result, null, 2));

  console.log(`Capture complete. Saved:
  - ${apiCalls.size} API calls
  - ${uiElementsMap.size} UI elements
  - ${uiStateHistory.length} UI state changes
  - ${userFlow.length} user actions`);

  await browser.close();
  process.exit(0);
})();