// playwright-discover-routes.spec.js
// Scenario-level AI-driven black-box UI exploration: AI plans all actions for a scenario at once

const { test } = require('@playwright/test');
const fs = require('fs');
const path = require('path');
const { spawnSync } = require('child_process');
const crypto = require('crypto');

const BASE_URL = 'http://localhost:3001';
const FEATURE_PATH = path.resolve('test_scenarios_test.feature');
const MAX_ACTIONS_PER_SCENARIO = 10;
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
  const prompt = `You are an expert QA automation AI.\n\nFeature file:\n${featureText}\n\nScenario: ${scenario.name}\n\nScenario steps:\n${scenario.steps.join('\n')}\n\nCurrent UI state (JSON):\n${JSON.stringify(uiState, null, 2)}\n\nPlan a sequence of up to ${MAX_ACTIONS_PER_SCENARIO} actions to execute this scenario.\nIMPORTANT: If a form needs to be submitted, you MUST always fill ALL required fields BEFORE clicking any submit or next button. NEVER click a submit or next button before all required fields are filled.\nBAD EXAMPLE (do NOT do this): [click submit, then fill fields].\nGOOD EXAMPLE (always do this): [fill all fields, then click submit].\nPrefer filling inputs before clicking buttons in forms.\nRespond ONLY with a JSON array of actions, e.g.:\n[\n  {\n    \"action\": \"fill\", \"target\": {\"type\": \"input\", \"placeholder\": \"Username\"}, \"value\": \"testuser\"\n  },\n  {\n    \"action\": \"click\", \"target\": {\"type\": \"button\", \"text\": \"Register\"}\n  },\n  ...\n]\n`;
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
      for (const btn of btns) {
        const text = await btn.innerText();
        if (text.trim() === actionObj.target.text.trim()) {
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
  } else if (actionObj.action === 'fill' && actionObj.target && actionObj.value !== undefined) {
    let filled = false;
    if (actionObj.target.type === 'input') {
      if (actionObj.target.name) {
        const selector = `[name=\"${actionObj.target.name}\"]`;
        if (await page.$(selector)) {
          await page.fill(selector, actionObj.value);
          await page.waitForTimeout(200);
          filled = true;
        }
      }
      if (!filled && actionObj.target.id) {
        const selector = `#${actionObj.target.id}`;
        if (await page.$(selector)) {
          await page.fill(selector, actionObj.value);
          await page.waitForTimeout(200);
          filled = true;
        }
      }
      if (!filled && actionObj.target.placeholder) {
        const selector = `input[placeholder=\"${actionObj.target.placeholder}\"]`;
        if (await page.$(selector)) {
          await page.fill(selector, actionObj.value);
          await page.waitForTimeout(200);
          filled = true;
        }
      }
      if (!filled && actionObj.target.label) {
        const inputs = await page.$$('input');
        for (const input of inputs) {
          const label = await input.evaluate(el => (el.labels && el.labels.length ? el.labels[0].innerText : ''));
          if (label.trim().toLowerCase() === actionObj.target.label.trim().toLowerCase()) {
            await input.fill(actionObj.value);
            await page.waitForTimeout(200);
            filled = true;
            break;
          }
        }
      }
    }
    return;
  } else if (actionObj.action === 'submit' && actionObj.target) {
    if (actionObj.target.type === 'form' && actionObj.target.id) {
      const form = await page.$(`#${actionObj.target.id}`);
      if (form) {
        await form.evaluate(f => f.submit());
        await page.waitForTimeout(1000);
        return;
      }
    }
  }
}

const { scenarios, featureText } = parseFeatureFile();




test.describe('All scenarios in one session', () => {
  test('run all scenarios sequentially in one browser session', async ({ page }) => {
    test.setTimeout(TEST_TIMEOUT * scenarios.length);
    await page.goto(BASE_URL);
    let uiState = await extractUIState(page);
    for (const scenario of scenarios) {
      // Plan actions for this scenario based on current UI
      const actions = await aiPlanScenarioActions(featureText, scenario, uiState);
      let actionIdx = 0;
      for (const actionObj of actions) {
        if (page.isClosed()) break;
        await executeAction(page, actionObj);
        uiState = await extractUIState(page);
        await logScenarioAction(scenario, actionIdx, actionObj, uiState);
        actionIdx++;
        if (actionIdx >= MAX_ACTIONS_PER_SCENARIO) break;
      }
    }
  });
});
