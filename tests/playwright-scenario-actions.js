// playwright-discover-routes.spec.js
// Scenario-level AI-driven black-box UI exploration: AI plans all actions for a scenario at once

const { test, chromium } = require('@playwright/test');
const fs = require('fs');
const path = require('path');
const { spawnSync } = require('child_process');
const crypto = require('crypto');

const BASE_URL = 'http://localhost:3001';
const FEATURE_PATH = path.resolve('test_scenarios_test.feature');
// const MAX_ACTIONS_PER_SCENARIO = 10;
const TEST_TIMEOUT = 120_000;

function parseFeatureFile() {
  if (!fs.existsSync(FEATURE_PATH)) return [];
  const content = fs.readFileSync(FEATURE_PATH, 'utf-8');
  const lines = content.split('\n');
  const scenarios = [];
  let current = null;
  for (let line of lines) {
    line = line.trim();
    if (line.startsWith('Scenario:')) {
      if (current) scenarios.push(current);
      current = { name: line.replace('Scenario:', '').trim(), steps: [] };
    } else if (/^(Given|When|Then|And|But)/.test(line)) {
      if (current) current.steps.push(line);
    }
  }
  if (current) scenarios.push(current);
  return { scenarios, featureText: content };
}

function getContentHash(content) {
  return crypto.createHash('md5').update(content).digest('hex');
}

async function extractUIState(page) {
  return await page.evaluate(() => {
    const getFieldInfo = el => ({
      tag: el.tagName.toLowerCase(),
      name: el.name || '',
      id: el.id || '',
      type: el.type || '',
      placeholder: el.placeholder || '',
      label: el.labels && el.labels.length ? el.labels[0].innerText : '',
      value: el.value || ''
    });
    return {
      url: window.location.href,
      headings: Array.from(document.querySelectorAll('h1, h2, h3, h4, h5, h6')).map(e => e.innerText),
      buttons: Array.from(document.querySelectorAll('button')).map(b => ({ text: b.innerText, id: b.id, name: b.name })),
      links: Array.from(document.querySelectorAll('a')).map(a => ({ text: a.innerText, href: a.href })),
      forms: Array.from(document.querySelectorAll('form')).map(f => ({
        id: f.id,
        name: f.name,
        fields: Array.from(f.querySelectorAll('input, select, textarea')).map(getFieldInfo)
      })),
      allFields: Array.from(document.querySelectorAll('input, select, textarea')).map(getFieldInfo)
    };
  });
}


// Overwrite the log file at the start of the run
let logFileInitialized = false;
async function logScenarioAction(scenario, actionIdx, actionObj, uiState) {
  const log = {
    scenario: scenario.name,
    actionIdx,
    action: actionObj || null,
    uiState
  };
  const logStr = JSON.stringify(log, null, 2) + ',\n';
  if (!logFileInitialized) {
    fs.writeFileSync('scenario_actions_log.json', logStr); // overwrite
    logFileInitialized = true;
  } else {
    fs.appendFileSync('scenario_actions_log.json', logStr);
  }
  console.log('Scenario Action Log:', log);
}

// AI: plan all actions for a scenario
async function aiPlanScenarioActions(featureText, scenario, uiState) {
  // Aggressively truncate all prompt parts to fit within LLM context window (max ~2048 tokens)
  const maxFeatureLength = 1000;
  const maxSteps = 5;
  const maxUIStrLength = 1000;
  // Truncate feature file
  let featureTextShort = featureText;
  if (featureText.length > maxFeatureLength) {
    featureTextShort = featureText.slice(0, maxFeatureLength) + '\n...';
  }
  // Truncate scenario steps
  let scenarioStepsShort = scenario.steps.slice(0, maxSteps);
  if (scenario.steps.length > maxSteps) {
    scenarioStepsShort.push('...');
  }
  // Do not truncate actionable UI state: send all buttons, links, and allFields
  let uiStateShort = {
    url: uiState.url,
    headings: uiState.headings,
    buttons: uiState.buttons,
    links: uiState.links,
    forms: uiState.forms,
    allFields: uiState.allFields
  };
  let uiStateStr = JSON.stringify(uiStateShort, null, 2);
  if (uiStateStr.length > maxUIStrLength) {
    uiStateStr = uiStateStr.slice(0, maxUIStrLength) + '\n...';
  }
  const prompt = `You are an expert QA automation AI.\n\nFeature file:\n${featureTextShort}\n\nScenario: ${scenario.name}\n\nScenario steps:\n${scenarioStepsShort.join('\n')}\n\nCurrent UI state (JSON):\n${uiStateStr}\n\nIMPORTANT: You MUST ONLY use button/input/link names, placeholders, and labels that are PRESENT in the provided UI state JSON. Do NOT invent or guess element names. If you cannot find a matching element in the UI state, SKIP that action.\n\nPlan a sequence of actions to execute this scenario. You MUST always fill ALL required fields BEFORE clicking any button. NEVER click any button before all required fields are filled. BAD EXAMPLE (do NOT do this): [click button, then fill fields]. GOOD EXAMPLE (always do this): [fill all fields, then click button]. Prefer filling inputs before clicking any button.\n\nRespond ONLY with a JSON array of actions, e.g.:\n[\n  {\n    \"action\": \"fill\", \"target\": {\"type\": \"input\", \"placeholder\": \"Username\"}, \"value\": \"testuser\"\n  },\n  {\n    \"action\": \"click\", \"target\": {\"type\": \"button\", \"text\": \"Register\"}\n  },\n  ...\n]\n`;
  const ollama = spawnSync('ollama', ['run', 'mistral'], { input: prompt, encoding: 'utf-8' });
  let aiOutput = ollama.stdout.trim();
  const jsonMatch = aiOutput.match(/\[[\s\S]*\]/);
  if (!jsonMatch) return [];
  try { return JSON.parse(jsonMatch[0]); } catch { return []; }
}

// Execute a single action
async function executeAction(page, actionObj) {
  if (!actionObj) return;
  if (actionObj.action === 'click' && actionObj.target) {
            if (actionObj.target.type === 'button' && actionObj.target.text) {
                const btns = await page.$$('button');
                // 1. Try exact text match
                for (const btn of btns) {
                    const text = await btn.innerText();
                    if (text.trim() === actionObj.target.text.trim()) {
                        await btn.click();
                        await page.waitForTimeout(500);
                        return;
                    }
                }
                // 2. Try exact name or id match if provided
                if (actionObj.target.name) {
                    for (const btn of btns) {
                        const name = await btn.getAttribute('name');
                        if (name && name.trim() === actionObj.target.name.trim()) {
                            await btn.click();
                            await page.waitForTimeout(500);
                            return;
                        }
                    }
                }
                if (actionObj.target.id) {
                    for (const btn of btns) {
                        const id = await btn.getAttribute('id');
                        if (id && id.trim() === actionObj.target.id.trim()) {
                            await btn.click();
                            await page.waitForTimeout(500);
                            return;
                        }
                    }
                }
                // 3. Fuzzy/partial text match (case-insensitive, includes or included by)
                const desired = actionObj.target.text.trim().toLowerCase();
                for (const btn of btns) {
                    const text = (await btn.innerText()).trim().toLowerCase();
                    if (text && (text.includes(desired) || desired.includes(text))) {
                        await btn.click();
                        await page.waitForTimeout(500);
                        return;
                    }
                }
    } else if (actionObj.target.type === 'link' && actionObj.target.text) {
      const links = await page.$$('a');
      for (const link of links) {
        const text = await link.innerText();
        if (text.trim() === actionObj.target.text.trim()) {
          await link.click();
          await page.waitForTimeout(500);
          return;
        }
      }
    }
  } else if (actionObj.action === 'fill' && actionObj.target) {
    // Fallback: if value is missing, provide a default
    let value = actionObj.value;
    if (value === undefined || value === null) {
      const ph = (actionObj.target.placeholder || '').toLowerCase();
      const name = (actionObj.target.name || '').toLowerCase();
      if (ph.includes('user') || name.includes('user')) value = 'testuser';
      else if (ph.includes('pass') || name.includes('pass')) value = 'testpass';
      else if (ph.includes('title')) value = 'Test Title';
      else if (ph.includes('desc')) value = 'Test Description';
      else if (ph.includes('date')) value = '2025-07-08';
      else value = 'test';
    }
    let filled = false;
    if (actionObj.target.type === 'input') {
      // Try all standard selectors first
      if (actionObj.target.name) {
        const selector = `[name=\"${actionObj.target.name}\"]`;
        if (await page.$(selector)) {
          await page.fill(selector, value);
          await page.waitForTimeout(200);
          filled = true;
        }
      }
      if (!filled && actionObj.target.id) {
        const selector = `#${actionObj.target.id}`;
        if (await page.$(selector)) {
          await page.fill(selector, value);
          await page.waitForTimeout(200);
          filled = true;
        }
      }
      if (!filled && actionObj.target.placeholder) {
        const selector = `input[placeholder=\"${actionObj.target.placeholder}\"]`;
        if (await page.$(selector)) {
          await page.fill(selector, value);
          await page.waitForTimeout(200);
          filled = true;
        }
      }
      if (!filled && actionObj.target.label) {
        const inputs = await page.$$('input');
        for (const input of inputs) {
          const label = await input.evaluate(el => (el.labels && el.labels.length ? el.labels[0].innerText : ''));
          if (label.trim().toLowerCase() === actionObj.target.label.trim().toLowerCase()) {
            await input.fill(value);
            await page.waitForTimeout(200);
            filled = true;
            break;
          }
        }
      }
      // Fallback: fuzzy match placeholder if still not filled
      if (!filled && actionObj.target.placeholder) {
        const desired = actionObj.target.placeholder.trim().toLowerCase();
        const allInputs = await page.$$('input, textarea');
        for (const input of allInputs) {
          const ph = (await input.getAttribute('placeholder')) || '';
          if (ph && ph.trim().toLowerCase().includes(desired)) {
            await input.fill(value);
            await page.waitForTimeout(200);
            filled = true;
            break;
          }
        }
        // Try partial match (e.g. "Task Name" vs "Title")
        if (!filled) {
          for (const input of allInputs) {
            const ph = (await input.getAttribute('placeholder')) || '';
            if (desired && ph && (desired.includes(ph.trim().toLowerCase()) || ph.trim().toLowerCase().includes(desired))) {
              await input.fill(value);
              await page.waitForTimeout(200);
              filled = true;
              break;
            }
          }
        }
      }
    }
    return;
  }
}

const { scenarios, featureText } = parseFeatureFile();




test.describe('All scenarios in one session', () => {
  test('run all scenarios sequentially in one browser session', async () => {
    const browser = await chromium.launch({ headless: false });
    const context = await browser.newContext();
    const page = await context.newPage();
    test.setTimeout(TEST_TIMEOUT * scenarios.length);
    await page.goto(BASE_URL);
    // Clean up cookies and storage to ensure a fresh state
    await page.context().clearCookies();
    await page.evaluate(() => {
      localStorage.clear();
      sessionStorage.clear();
    });
    let uiState = await extractUIState(page);
    for (const scenario of scenarios) {
      try {
        // Ensure page is open
        if (page.isClosed()) {
          page = await context.newPage();
          await page.goto(BASE_URL);
          await page.context().clearCookies();
          await page.evaluate(() => {
            localStorage.clear();
            sessionStorage.clear();
          });
          uiState = await extractUIState(page);
        }

        // Refresh UI state by navigating to the relevant page for each scenario
        if (scenario.name.toLowerCase().includes('register')) {
          await page.goto(BASE_URL + '/register');
          await page.waitForTimeout(500);
          uiState = await extractUIState(page);
        } else if (scenario.name.toLowerCase().includes('log in')) {
          await page.goto(BASE_URL + '/login');
          await page.waitForTimeout(500);
          uiState = await extractUIState(page);
          // If already logged in, log out
          const logoutBtn = await page.$('button:text("Logout"), a:text("Logout")');
          if (logoutBtn) {
            await logoutBtn.click();
            await page.waitForTimeout(1000);
            uiState = await extractUIState(page);
          }
        } else if (scenario.name.toLowerCase().includes('task creation')) {
          await page.goto(BASE_URL + '/tasks/new');
          await page.waitForTimeout(500);
          uiState = await extractUIState(page);
        } else if (scenario.name.toLowerCase().includes('view tasks')) {
          await page.goto(BASE_URL + '/tasks');
          await page.waitForTimeout(500);
          uiState = await extractUIState(page);
        }

        // Plan actions for this scenario based on current UI
        let actions = await aiPlanScenarioActions(featureText, scenario, uiState);

        // Filter actions: only keep actions whose targets exist in the current UI state
        function actionTargetExists(action, uiState) {
          if (!action || !action.target) return false;
          // Fuzzy/partial match for buttons
          if (action.target.type === 'button' && action.target.text) {
            const desired = action.target.text.trim().toLowerCase();
            return (uiState.buttons || []).some(b => {
              const btnText = (b.text || '').trim().toLowerCase();
              return btnText && (btnText === desired || btnText.includes(desired) || desired.includes(btnText));
            });
          }
          // Fuzzy/partial match for links
          if (action.target.type === 'link' && action.target.text) {
            const desired = action.target.text.trim().toLowerCase();
            return (uiState.links || []).some(l => {
              const linkText = (l.text || '').trim().toLowerCase();
              return linkText && (linkText === desired || linkText.includes(desired) || desired.includes(linkText));
            });
          }
          // Fuzzy/partial match for input placeholders
          if (action.target.type === 'input' && action.target.placeholder) {
            const desired = action.target.placeholder.trim().toLowerCase();
            return (uiState.allFields || []).some(f => {
              const ph = (f.placeholder || '').trim().toLowerCase();
              return ph && (ph === desired || ph.includes(desired) || desired.includes(ph));
            });
          }
          // Add more types as needed
          return true;
        }
        actions = actions.filter(action => actionTargetExists(action, uiState));

        // For login scenarios, statically set username and password fields if present
        if (scenario.name.toLowerCase().includes('log in')) {
          actions = actions.map(action => {
            if (action.action === 'fill' && action.target && action.target.type === 'input') {
              if ((action.target.placeholder || '').toLowerCase().includes('user')) {
                return { ...action, value: 'samer' };
              }
              if ((action.target.placeholder || '').toLowerCase().includes('pass')) {
                return { ...action, value: '123123' };
              }
            }
            return action;
          });
        }
        let actionIdx = 0;
        if (actions.length === 0) {
          // Log skipped scenario
          await logScenarioAction(scenario, actionIdx, null, uiState);
        }
        for (const actionObj of actions) {
          if (page.isClosed()) break;
          await executeAction(page, actionObj);
          uiState = await extractUIState(page);
          await logScenarioAction(scenario, actionIdx, actionObj, uiState);
          actionIdx++;
        }
      } catch (err) {
        console.error(`Error in scenario "${scenario.name}":`, err);
        // Optionally log error to your log file here
      }
    }
    await browser.close();
  });
});
