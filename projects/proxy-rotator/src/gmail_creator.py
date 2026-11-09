"""Gmail account creation via anti-detect browser automation (Playwright + proxy)."""

from typing import Optional
from playwright.async_api import async_playwright

GMAIL_SIGNUP_URL = "https://accounts.google.com/signup"


async def create_gmail_account(email: str, password: str, proxy_url: Optional[str] = None) -> dict:
    """Launch Chromium (headless) with proxy and attempt Google signup flow.

    Anti-detect setup: browser context via proxy + clean profile.
    First name is derived from email local part (before digits), e.g.
    "Rumahdufan200@gmail.com" -> firstName "Rumah", lastName "dufan200".
    Tries to bypass phone-number gate by handling consent screen before fill.
    Returns dict: {email, ok, status, detail}
    """
    result = {"email": email, "ok": False, "status": 0, "detail": ""}
    local = email.split("@")[0] if "@" in email else email
    first_name = local[:len(local) // 2] if len(local) > 1 else local
    last_name = local[len(first_name):] if len(local) > 1 and local.lower().startswith(first_name.lower()) else first_name

    async with async_playwright() as p:
        launch_kwargs = {"headless": True}
        if proxy_url:
            launch_kwargs["proxy"] = {"server": proxy_url}
        browser = await p.firefox.launch(headless=True, proxy={"server": proxy_url} if proxy_url else None)
        # Android mobile emulation context (anti-detect fallback)
        context = await browser.new_context(
            viewport={"width": 412, "height": 823},
            is_mobile=True,
            has_touch=True,
            device_scale_factor=2.75,
            user_agent="Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
        )
        page = await context.new_page()
        try:
            await page.goto(GMAIL_SIGNUP_URL, wait_until="domcontentloaded", timeout=45000)

            try:
                consent = page.locator('text=I agree').first
                if await consent.count() > 0:
                    await consent.click(timeout=10000)
                    await page.wait_for_load_state("networkidle", timeout=15000)
            except Exception:
                pass

            await page.wait_for_selector('input[name="username"]', timeout=45000)
            await page.fill('input[name="firstName"]', first_name)
            await page.fill('input[name="lastName"]', last_name)
            await page.fill('input[name="username"]', email)
            await page.fill('input[name="passphrase"]', password)
            await page.click('button:has-text("Create account")')
            await page.wait_for_load_state("load", timeout=20000)
            result["ok"] = True
            result["status"] = 200
            result["detail"] = f"signup page reached: {page.url}"
        except Exception as e:
            result["ok"] = False
            result["status"] = 0
            result["detail"] = f"{type(e).__name__}: {e}"
        finally:
            try:
                await browser.close()
            except Exception:
                pass
    result["proxy"] = proxy_url
    return result
