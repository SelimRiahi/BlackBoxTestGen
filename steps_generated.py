import asyncio
from playwright.async_api import Playwright, Browser, Page

FEATURES = [
    "Feature: User Authentication",
    "  Scenario: Register a new user",
    "  Scenario: Log in an existing user",
    "Feature: Task Management",
    "  Scenario: Create a new task",
    "  Scenario: View tasks"
]

LOGIN_CREDENTIALS = {"username": "samer", "password": "123123"}

TASK_INPUT_DATA = [
    {"title": "Task 1", "description": "Description 1"},
    {"title": "Task 2", "description": "Description 2"},
    {"title": "Task 3", "description": "Description 3"}
]

async def register_user(browser, page):
    await page.goto("http://localhost:3001/register")
    await page.fill("#username", "new_user")
    await page.fill("#password", "new_pass")
    # Assuming no button for registering exists in the log, skip this action to avoid inventing or guessing selectors
    pass

async def login(browser, page):
    await page.goto("http://localhost:3001/login")
    await page.fill("#username", LOGIN_CREDENTIALS["username"])
    await page.fill("#password", LOGIN_CREDENTIALS["password"])
    await page.click("#submit-button")

async def create_task(browser, page):
    await page.goto("http://localhost:3001/tasks/create")
    await page.fill("#title", TASK_INPUT_DATA[0]["title"])
    await page.fill("#description", TASK_INPUT_DATA[0]["description"])
    await page.click("#submit-button")

async def view_tasks(browser, page):
    await page.goto("http://localhost:3010/your-tasks")

async def test_register_new_user():
    async with Playwright().start() as p:
        browser = p.chromium.launch(headless=False)
        page = await browser.newPage()
        await register_user(browser, page)

async def test_log_in_an_existing_user():
    async with Playwright().start() as p:
        browser = p.chromium.launch(headless=False)
        page = await browser.newPage()
        await login(browser, page)

async def test_create_a_new_task():
    async with Playwright().start() as p:
        browser = p.chromium.launch(headless=False)
        page = await browser.newPage()
        await login(browser, page)
        for data in TASK_INPUT_DATA:
            await create_task(browser, page)

async def test_view_tasks():
    async with Playwright().start() as p:
        browser = p.chromium.launch(headless=False)
        page = await browser.newPage()
        await login(browser, page)
        for _ in range(len(TASK_INPUT_DATA)):
            await view_tasks(browser, page)

async def main():
    async with Playwright().start() as p:
        browser = p.chromium.launch(headless=False)
        for feature in FEATURES:
            print(f"Running scenario: {feature}")
            if "Register a new user" in feature:
                await test_register_new_user()
            elif "Log in an existing user" in feature:
                await test_log_in_an_existing_user()
            else:
                await test_create_a_new_task()
                await test_view_tasks()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())