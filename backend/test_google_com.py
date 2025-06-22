
import re
from playwright.sync_api import Page, expect

def test_google_homepage(page: Page):
    # Load the page
    page.goto("https://www.google.com")
    
    # Test page title
    expect(page).to_have_title(re.compile("Google"))
    
    # Test basic elements
    logo = page.locator('img[alt="Google"]')
    expect(logo).to_be_visible()
    
    search_box = page.locator('input[name="q"]')
    expect(search_box).to_be_visible()
    expect(search_box).to_be_editable()
    
    search_button = page.locator('input[name="btnK"]')
    expect(search_button).to_be_visible()
    
    # Test navigation and links
    page.locator('a:text("Gmail")').click()
    page.wait_for_load_state('networkidle')
    expect(page).to_have_url(re.compile("mail.google.com"))
    page.go_back()
    
    # Test forms and user interactions
    search_box.fill("Playwright")
    page.keyboard.press("Enter")
    page.wait_for_load_state('networkidle')
    expect(page).to_have_url(re.compile("search.*Playwright"))
    
    # Test search results
    results = page.locator('#search .g')
    expect(results).to_have_count(lambda count: count > 0)
    
    # Test responsive design
    page.set_viewport_size({"width": 1920, "height": 1080})
    expect(page.locator('#viewport')).to_have_css('width', '1920px')
    
    page.set_viewport_size({"width": 375, "height": 667})
    expect(page.locator('#viewport')).to_have_css('width', '375px')
    
    # Test footer elements
    footer = page.locator('#footer')
    expect(footer).to_be_visible()
    
    settings_link = footer.locator('a:text("Settings")')
    expect(settings_link).to_be_visible()
    
    # Test language selection
    if page.locator('#SIvCob').is_visible():
        language_links = page.locator('#SIvCob a')
        expect(language_links).to_have_count(lambda count: count > 0)
        
        # Click on a different language (if available)
        if language_links.count() > 0:
            language_links.first.click()
            page.wait_for_load_state('networkidle')
            expect(page).to_have_url(re.compile("google.com"))
    
    # Test "I'm Feeling Lucky" button
    lucky_button = page.locator('input[name="btnI"]')
    if lucky_button.is_visible():
        with page.expect_navigation():
            lucky_button.click(force=True)
        expect(page).not_to_have_url("https://www.google.com/")
    
    # Test image search
    page.goto("https://www.google.com")
    images_link = page.locator('a:text("Images")')
    if images_link.is_visible():
        images_link.click()
        page.wait_for_load_state('networkidle')
        expect(page).to_have_url(re.compile("google.com/imghp"))
        
        image_search_box = page.locator('input[name="q"]')
        expect(image_search_box).to_be_visible()
        
        image_search_box.fill("Playwright logo")
        page.keyboard.press("Enter")
        page.wait_for_load_state('networkidle')
        
        image_results = page.locator('#islrg img')
        expect(image_results).to_have_count(lambda count: count > 0)
    
    # Test Google apps menu
    apps_button = page.locator('a[aria-label="Google apps"]')
    if apps_button.is_visible():
        apps_button.click()
        apps_panel = page.locator('#gb div[aria-label="Google apps"]')
        expect(apps_panel).to_be_visible()
        
        app_icons = apps_panel.locator('li')
        expect(app_icons).to_have_count(lambda count: count > 0)
    
    # Test account sign-in button
    sign_in_button = page.locator('a:text("Sign in")')
    if sign_in_button.is_visible():
        expect(sign_in_button).to_have_attribute('href', re.compile("accounts.google.com"))
    
    # Error handling example
    non_existent = page.locator('#non-existent-element')
    expect(non_existent).not_to_be_visible()

if __name__ == "__main__":
    from playwright.sync_api import sync_playwright
    
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        test_google_homepage(page)
        browser.close()
