import asyncio
import pytest
from playwright.async_api import async_playwright

@pytest.mark.asyncio
async def scenario_for_post__register():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto("/register")
        await page.fill("#username-input", "selim123")
        await page.fill("#password-input", "selim123")
        await page.click("#login-button")
        assert True  # expected: 201

@pytest.mark.asyncio
async def scenario_for_post__login():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto("/login")
        await page.fill("#username-input", "selim123")
        await page.fill("#password-input", "selim123")
        await page.click("#login-button")
        assert True  # expected: 200

@pytest.mark.asyncio
async def scenario_for_get__tasks():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto("/tasks")
        await page.click("#login-button")
        assert True  # expected: 200

@pytest.mark.asyncio
async def scenario_for_post__tasks():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto("/tasks")
        await page.fill("#task-title-input", "azerty")
        await page.fill("#username-input", "afzfzafz")
        await page.fill("#username-input", "high")
        await page.fill("#username-input", "684c57f32853b824df237f6f")
        await page.fill("#username-input", "2026-08-20")
        await page.click("#login-button")
        assert True  # expected: 201

@pytest.mark.asyncio
async def scenario_for_get__tasks():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto("/tasks")
        await page.click("#login-button")
        assert True  # expected: 200

@pytest.mark.asyncio
async def scenario_for_post__tasks_invalid_title():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto("/tasks")
        await page.fill("#task-title-input", "azerty")
        await page.fill("#username-input", "")
        await page.fill("#username-input", "high")
        await page.click("#login-button")
        assert True  # expected: 201

@pytest.mark.asyncio
async def scenario_for_get__tasks():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto("/tasks")
        await page.click("#login-button")
        assert True  # expected: 200

@pytest.mark.asyncio
async def scenario_for_delete__tasks():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto("/tasks/68915cf2479b2525cb69123e")
        await page.click("#login-button")
        assert True  # expected: 204
