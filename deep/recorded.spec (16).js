const { test, expect } = require('@playwright/test');

async function Given(page, text, url) {
  if(text === 'I am on the page') {
    await page.goto(url);
  }
}

async function When(page, action, selector, value) {
  if (action === 'enter') await page.fill(selector, value);
  else if (action === 'click') await page.click(selector);
  else if (action === 'check') await page.check(selector);
  else if (action === 'uncheck') await page.uncheck(selector);
}

async function Then(page, text) {
  if (text.startsWith('element with selector "') && text.includes('should be removed')) {
    // Extract selector from the text
    const selectorMatch = text.match(/element with selector "([^"]+)" should be removed/);
    if (selectorMatch) {
      const selector = selectorMatch[1];
      // Wait for DOM to settle after delete operation
      await page.waitForTimeout(500);
      // Verify the specific element is no longer visible
      await expect(page.locator(selector)).toHaveCount(0);
    }
  } else if (text === 'the element should be removed') {
    // Fallback for generic deletion
    await page.waitForTimeout(500);
    await expect(page.locator('body')).toBeVisible();
  } else if (text.startsWith('I should see "') && text.endsWith('"')) {
    const cleanText = text.replace(/^I should see "/, '').replace(/"$/, '');
    await expect(page.locator('text=' + cleanText).first()).toBeVisible();
  } else {
    // Generic fallback
    const cleanText = text.replace(/^I should see /, '').replace(/^"/, '').replace(/"$/, '');
    if (cleanText && cleanText !== 'some expected result') {
      await expect(page.locator('text=' + cleanText).first()).toBeVisible();
    } else {
      await expect(page.locator('body')).toBeVisible();
    }
  }
}

test('Register', async ({ page }) => {
  await Given(page, 'I am on the page', 'http://localhost:3001');
  await When(page, 'enter', '#username-input', `kih`);
  await When(page, 'enter', '#password-input', `kih`);
  await When(page, 'click', '#username-input');
  await When(page, 'click', '#password-input');
  await When(page, 'click', '#register-button');
  await Then(page, `I should see "Login/RegisterRegistration successful! Please login.LoginRegister"`);
});

test('Login', async ({ page }) => {
  await Given(page, 'I am on the page', 'http://localhost:3001');
  await When(page, 'enter', '#username-input', `kih`);
  await When(page, 'enter', '#password-input', `kih`);
  await When(page, 'click', '#username-input');
  await When(page, 'click', '');
  await When(page, 'click', '#password-input');
  await When(page, 'click', '#login-button');
  await Then(page, `I should see "LogoutCreate TaskLowMediumHighSelect CategoryWorkHackedAdd TaskYour TasksNo tasks found"`);
});

test('Add Task', async ({ page }) => {
  await Given(page, 'I am on the page', 'http://localhost:3001');
  await When(page, 'enter', '#username-input', `kih`);
  await When(page, 'enter', '#password-input', `kih`);
  await When(page, 'click', '#username-input');
  await When(page, 'click', '');
  await When(page, 'click', '#password-input');
  await When(page, 'click', '#login-button');
  await When(page, 'enter', '#task-title-input', `azezae`);
  await When(page, 'enter', '#task-description-input', `testozaa`);
  await When(page, 'enter', '#task-priority-select', `medium`);
  await When(page, 'enter', '#task-category-select', `<hidden value>`);
  await When(page, 'enter', '#task-due-date-input', `2026-06-06`);
  await When(page, 'click', '#task-title-input');
  await When(page, 'click', '#task-description-input');
  await When(page, 'click', '#task-priority-select');
  await When(page, 'click', '#task-category-select');
  await When(page, 'click', '#task-due-date-input');
  await When(page, 'click', '#add-task-button');
  await Then(page, `I should see "Your TasksDeleteazezaetestozaaPriority: mediumDue: 06/06/2026Category: Hacked"`);
});

test('Delete', async ({ page }) => {
  await Given(page, 'I am on the page', 'http://localhost:3001');
  await When(page, 'enter', '#username-input', `kih`);
  await When(page, 'enter', '#password-input', `kih`);
  await When(page, 'click', '#username-input');
  await When(page, 'click', '');
  await When(page, 'click', '#password-input');
  await When(page, 'click', '#login-button');
  await When(page, 'click', '#delete-task-68978bb4036ce5784330053a-button');
  await Then(page, `element with selector "#task-68978bb4036ce5784330053a" should be removed`);
});

test('Logout', async ({ page }) => {
  await Given(page, 'I am on the page', 'http://localhost:3001');
  await When(page, 'enter', '#username-input', `kih`);
  await When(page, 'enter', '#password-input', `kih`);
  await When(page, 'click', '#username-input');
  await When(page, 'click', '');
  await When(page, 'click', '#password-input');
  await When(page, 'click', '#login-button');
  await When(page, 'click', '#logout-button');
  await Then(page, `I should see "Login/RegisterLoginRegister"`);
});

