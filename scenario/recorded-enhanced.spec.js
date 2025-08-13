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
    const selectorMatch = text.match(/element with selector "([^"]+)" should be removed/);
    if (selectorMatch) {
      const selector = selectorMatch[1];
      await page.waitForTimeout(500);
      await expect(page.locator(selector)).toHaveCount(0);
    }
  } else if (text.includes('should still be visible')) {
    const selectorMatch = text.match(/element with selector "([^"]+)" should still be visible/);
    if (selectorMatch) {
      const selector = selectorMatch[1];
      await expect(page.locator(selector)).toBeVisible();
    }
  } else if (text.includes('required') || text.includes('empty')) {
    const errorSelectors = [
      'text=required', 'text=Required', 'text=empty', 'text=Empty',
      'text=mandatory', 'text=Mandatory', '[class*="error"]',
      '[class*="required"]', '[role="alert"]'
    ];
    let errorFound = false;
    for (const selector of errorSelectors) {
      try {
        await expect(page.locator(selector).first()).toBeVisible({ timeout: 2000 });
        errorFound = true; break;
      } catch (e) { /* Continue */ }
    }
    if (!errorFound) throw new Error('No required/empty field error found');
  } else if (text.includes('invalid') || text.includes('format')) {
    const validationSelectors = [
      'text=invalid', 'text=Invalid', 'text=validation', 'text=Validation',
      'text=format', 'text=Format', '[class*="validation"]',
      '[class*="invalid"]', '[class*="error"]'
    ];
    let validationFound = false;
    for (const selector of validationSelectors) {
      try {
        await expect(page.locator(selector).first()).toBeVisible({ timeout: 2000 });
        validationFound = true; break;
      } catch (e) { /* Continue */ }
    }
    if (!validationFound) throw new Error('No validation error found');
  } else if (text.includes('error message')) {
    const errorSelectors = [
      'text=error', 'text=Error', '[class*="error"]',
      '[role="alert"]', '[class*="alert"]'
    ];
    let errorFound = false;
    for (const selector of errorSelectors) {
      try {
        await expect(page.locator(selector).first()).toBeVisible({ timeout: 2000 });
        errorFound = true; break;
      } catch (e) { /* Continue */ }
    }
    if (!errorFound) throw new Error('No error message found');
  } else if (text.startsWith('I should see "') && text.endsWith('"')) {
    const cleanText = text.replace(/^I should see "/, '').replace(/"$/, '');
    await expect(page.locator('text=' + cleanText).first()).toBeVisible();
  } else {
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
  await When(page, 'enter', '#username-input', `cvb`);
  await When(page, 'enter', '#password-input', `cvb`);
  await When(page, 'click', '#register-button');
  await Then(page, `I should see "Login/RegisterRegistration successful! Please login.LoginRegister"`);
});

test('Register - Empty Fields Failure', async ({ page }) => {
  await Given(page, 'I am on the page', 'http://localhost:3001');
  await When(page, 'enter', '#username-input', ``);
  await When(page, 'enter', '#password-input', ``);
  await When(page, 'click', '#register-button');
  await Then(page, `I should see "required" or "empty" error message`);
});

test('Register - Invalid Data Failure', async ({ page }) => {
  await Given(page, 'I am on the page', 'http://localhost:3001');
  await When(page, 'enter', '#username-input', `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`);
  await When(page, 'enter', '#password-input', `123`);
  await When(page, 'click', '#register-button');
  await Then(page, `I should see "invalid" or "format" error message`);
});

test('Register - Incomplete Form Failure', async ({ page }) => {
  await Given(page, 'I am on the page', 'http://localhost:3001');
  await When(page, 'enter', '#username-input', `cvb`);
  await When(page, 'click', '#register-button');
  await Then(page, `I should see "required field" error message`);
});

test('Login', async ({ page }) => {
  await Given(page, 'I am on the page', 'http://localhost:3001');
  await When(page, 'enter', '#username-input', `cvb`);
  await When(page, 'enter', '#password-input', `cvb`);
  await When(page, 'click', '#login-button');
  await Then(page, `I should see "LogoutCreate TaskLowMediumHighSelect CategoryWorkHackedAdd TaskYour TasksNo tasks found"`);
});

test('Login - Empty Fields Failure', async ({ page }) => {
  await Given(page, 'I am on the page', 'http://localhost:3001');
  await When(page, 'enter', '#username-input', ``);
  await When(page, 'enter', '#password-input', ``);
  await When(page, 'click', '#login-button');
  await Then(page, `I should see "required" or "empty" error message`);
});

test('Login - Invalid Data Failure', async ({ page }) => {
  await Given(page, 'I am on the page', 'http://localhost:3001');
  await When(page, 'enter', '#username-input', `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`);
  await When(page, 'enter', '#password-input', `123`);
  await When(page, 'click', '#login-button');
  await Then(page, `I should see "invalid" or "format" error message`);
});

test('Login - Incomplete Form Failure', async ({ page }) => {
  await Given(page, 'I am on the page', 'http://localhost:3001');
  await When(page, 'enter', '#username-input', `cvb`);
  await When(page, 'click', '#login-button');
  await Then(page, `I should see "required field" error message`);
});

test('Add Task', async ({ page }) => {
  await Given(page, 'I am on the page', 'http://localhost:3001');
  await When(page, 'enter', '#username-input', `cvb`);
  await When(page, 'enter', '#password-input', `cvb`);
  await When(page, 'click', '#login-button');
  await When(page, 'enter', '#task-title-input', `tazeazd`);
  await When(page, 'enter', '#task-description-input', `descrip`);
  await When(page, 'enter', '#task-priority-select', `medium`);
  await When(page, 'enter', '#task-category-select', `<hidden value>`);
  await When(page, 'enter', '#task-due-date-input', `2026-06-06`);
  await When(page, 'click', '#add-task-button');
  await Then(page, `I should see "Your TasksDeletetazeazddescripPriority: mediumDue: 06/06/2026Category: Hacked"`);
});

test('Add Task - Empty Fields Failure', async ({ page }) => {
  await Given(page, 'I am on the page', 'http://localhost:3001');
  await When(page, 'enter', '#username-input', ``);
  await When(page, 'enter', '#password-input', ``);
  await When(page, 'click', '#login-button');
  await When(page, 'enter', '#task-title-input', ``);
  await When(page, 'enter', '#task-description-input', ``);
  await When(page, 'enter', '#task-priority-select', ``);
  await When(page, 'enter', '#task-category-select', ``);
  await When(page, 'enter', '#task-due-date-input', ``);
  await When(page, 'click', '#add-task-button');
  await Then(page, `I should see "required" or "empty" error message`);
});

test('Add Task - Invalid Data Failure', async ({ page }) => {
  await Given(page, 'I am on the page', 'http://localhost:3001');
  await When(page, 'enter', '#username-input', `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`);
  await When(page, 'enter', '#password-input', `123`);
  await When(page, 'click', '#login-button');
  await When(page, 'enter', '#task-title-input', `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`);
  await When(page, 'enter', '#task-description-input', `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`);
  await When(page, 'enter', '#task-priority-select', `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`);
  await When(page, 'enter', '#task-category-select', `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`);
  await When(page, 'enter', '#task-due-date-input', `2025-13-45`);
  await When(page, 'click', '#add-task-button');
  await Then(page, `I should see "invalid" or "format" error message`);
});

test('Add Task - Incomplete Form Failure', async ({ page }) => {
  await Given(page, 'I am on the page', 'http://localhost:3001');
  await When(page, 'enter', '#username-input', `cvb`);
  await When(page, 'enter', '#password-input', `cvb`);
  await When(page, 'click', '#login-button');
  await When(page, 'enter', '#task-title-input', `tazeazd`);
  await When(page, 'enter', '#task-description-input', `descrip`);
  await When(page, 'enter', '#task-priority-select', `medium`);
  await When(page, 'enter', '#task-category-select', `<hidden value>`);
  await When(page, 'click', '#add-task-button');
  await Then(page, `I should see "required field" error message`);
});

test('Delete', async ({ page }) => {
  await Given(page, 'I am on the page', 'http://localhost:3001');
  await When(page, 'enter', '#username-input', `cvb`);
  await When(page, 'enter', '#password-input', `cvb`);
  await When(page, 'click', '#login-button');
  await When(page, 'click', '#delete-task-689a87dbd954eff4b5f50b01-button');
  await Then(page, `element with selector "#task-689a87dbd954eff4b5f50b01" should be removed`);
});

test('Delete - Empty Fields Failure', async ({ page }) => {
  await Given(page, 'I am on the page', 'http://localhost:3001');
  await When(page, 'enter', '#username-input', ``);
  await When(page, 'enter', '#password-input', ``);
  await When(page, 'click', '#login-button');
  await When(page, 'click', '#delete-task-689a87dbd954eff4b5f50b01-button');
  await Then(page, `element with selector "#task-689a87dbd954eff4b5f50b01" should still be visible`);
});

test('Delete - Invalid Data Failure', async ({ page }) => {
  await Given(page, 'I am on the page', 'http://localhost:3001');
  await When(page, 'enter', '#username-input', `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`);
  await When(page, 'enter', '#password-input', `123`);
  await When(page, 'click', '#login-button');
  await When(page, 'click', '#delete-task-689a87dbd954eff4b5f50b01-button');
  await Then(page, `element with selector "#task-689a87dbd954eff4b5f50b01" should still be visible`);
});

test('Delete - Incomplete Form Failure', async ({ page }) => {
  await Given(page, 'I am on the page', 'http://localhost:3001');
  await When(page, 'enter', '#username-input', `cvb`);
  await When(page, 'click', '#login-button');
  await When(page, 'click', '#delete-task-689a87dbd954eff4b5f50b01-button');
  await Then(page, `element with selector "#task-689a87dbd954eff4b5f50b01" should still be visible`);
});

test('Logout', async ({ page }) => {
  await Given(page, 'I am on the page', 'http://localhost:3001');
  await When(page, 'enter', '#username-input', `cvb`);
  await When(page, 'enter', '#password-input', `cvb`);
  await When(page, 'click', '#login-button');
  await When(page, 'click', '#logout-button');
  await Then(page, `I should see "Login/RegisterLoginRegister"`);
});

test('Logout - Empty Fields Failure', async ({ page }) => {
  await Given(page, 'I am on the page', 'http://localhost:3001');
  await When(page, 'enter', '#username-input', ``);
  await When(page, 'enter', '#password-input', ``);
  await When(page, 'click', '#login-button');
  await When(page, 'click', '#logout-button');
  await Then(page, `I should see "required" or "empty" error message`);
});

test('Logout - Invalid Data Failure', async ({ page }) => {
  await Given(page, 'I am on the page', 'http://localhost:3001');
  await When(page, 'enter', '#username-input', `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`);
  await When(page, 'enter', '#password-input', `123`);
  await When(page, 'click', '#login-button');
  await When(page, 'click', '#logout-button');
  await Then(page, `I should see "invalid" or "format" error message`);
});

test('Logout - Incomplete Form Failure', async ({ page }) => {
  await Given(page, 'I am on the page', 'http://localhost:3001');
  await When(page, 'enter', '#username-input', `cvb`);
  await When(page, 'click', '#login-button');
  await When(page, 'click', '#logout-button');
  await Then(page, `I should see "required field" error message`);
});

