"""Playwright browser integration test verifying full gameplay in index.html."""

from pathlib import Path
from playwright.sync_api import sync_playwright

def test_full_browser_playthrough():
    html_path = Path(__file__).resolve().parent.parent / "index.html"
    assert html_path.exists(), "index.html must exist"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(html_path.resolve().as_uri())

        # 1. Start Modal
        page.wait_for_selector("#kc-modal-overlay")
        page.click("button:has-text('Start Planning Mission')")
        page.wait_for_selector("#kc-map")

        # 2. Check initial status
        assert "Round 1 of 3" in page.inner_text("#kc-round-badge")
        assert "2 AP" in page.inner_text("#kc-ap-badge")

        # 3. Round 1 Actions
        # Action 1: Speak with counselor
        page.locator(".kc-action-card", has_text="Speak with a Counselor").locator("button.kc-btn-primary").click()
        assert "1 AP" in page.inner_text("#kc-ap-badge")

        # Action 2: Investigate Health Start
        page.locator(".kc-action-card", has_text="Investigate Health Start").locator("button.kc-btn-primary").click()
        assert "0 AP" in page.inner_text("#kc-ap-badge")

        # Advance to Round 2
        page.click("#kc-advance-btn")
        assert "Round 2 of 3" in page.inner_text("#kc-round-badge")
        assert "2 AP" in page.inner_text("#kc-ap-badge")

        # 4. Round 2 Actions
        # Prepare Health Start inquiry (costs 2 AP)
        page.locator(".kc-action-card", has_text="Prepare Health Start Inquiry").locator("button.kc-btn-primary").click()
        assert "0 AP" in page.inner_text("#kc-ap-badge")

        # Advance to Round 3
        page.click("#kc-advance-btn")
        assert "Round 3 of 3" in page.inner_text("#kc-round-badge")

        # 5. Finish Mission
        page.click("#kc-advance-btn")
        page.wait_for_selector("#kc-modal-overlay")

        # Verify ending screen
        title = page.inner_text("#kc-modal-box h2")
        assert "Health Start Inquiry Plan Completed" in title

        # Verify Replay button exists and resets
        page.click("button:has-text('Replay')")
        page.wait_for_selector("#kc-modal-overlay")
        assert "A Future in Healthcare" in page.inner_text("#kc-modal-box h2")

        browser.close()
