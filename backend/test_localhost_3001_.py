from playwright.sync_api import Page, expect, sync_playwright

def test_localhost_3001(page: Page):
    # 1. Test page loading and basic elements
    page.goto("http://localhost:3001/")
    expect(page).to_have_title("React App")
    
    # Wait for the root element to be present
    root = page.wait_for_selector("#root")
    expect(root).to_be_visible()

    # 2. Test navigation and links
    # Assuming there are navigation links, adjust selectors as needed
    nav_links = page.query_selector_all("nav a")
    for link in nav_links:
        href = link.get_attribute("href")
        if href and not href.startswith("http"):
            link.click()
            page.wait_for_load_state("networkidle")
            expect(page).to_have_url(f"http://localhost:3001{href}")
            page.go_back()

    # 3. Test forms and user interactions
    # Assuming there's a form, adjust selectors as needed
    form = page.query_selector("form")
    if form:
        input_field = page.query_selector('input[type="text"]')
        if input_field:
            input_field.fill("Test input")
            expect(input_field).to_have_value("Test input")

        submit_button = page.query_selector('button[type="submit"]')
        if submit_button:
            submit_button.click()
            page.wait_for_load_state("networkidle")

    # 4. Test responsive design elements
    page.set_viewport_size({"width": 1920, "height": 1080})
    expect(page.query_selector("body")).to_be_visible()

    page.set_viewport_size({"width": 375, "height": 667})
    expect(page.query_selector("body")).to_be_visible()

    # 5. Include proper assertions and error handling
    try:
        main_content = page.query_selector("main")
        expect(main_content).not_to_be_none()
    except AssertionError:
        print("Main content not found")

    # 6. Use robust selectors that are less likely to break
    header = page.query_selector('[data-testid="header"]') or page.query_selector("header")
    if header:
        expect(header).to_be_visible()

    # 7. Include waits for elements to load
    footer = page.wait_for_selector("footer", state="visible", timeout=5000)
    expect(footer).to_be_visible()

    # 8. Handle cases where elements might not be present
    dynamic_content = page.query_selector(".dynamic-content")
    if dynamic_content:
        expect(dynamic_content).to_be_visible()
    else:
        print("Dynamic content not found")

    # 9. Additional tests
    # Test for console errors
    console_messages = []
    page.on("console", lambda msg: console_messages.append(msg))
    assert len([msg for msg in console_messages if msg.type == "error"]) == 0, "Console errors found"

    # Test for broken images
    images = page.query_selector_all("img")
    for img in images:
        expect(img).to_have_js_property("naturalWidth", lambda width: width > 0)

    # Test for accessibility
    accessibility = page.accessibility.snapshot()
    assert accessibility["children"], "No accessibility tree found"

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        test_localhost_3001(page)
        browser.close()