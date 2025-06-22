
from playwright.sync_api import Playwright, sync_playwright, expect

def test_google_com(page):
    # Test page loading and basic elements
    page.goto("https://www.google.com")
    expect(page).to_have_title("Google")
    expect(page.locator("img[alt='Google']")).to_be_visible()
    
    # Test search functionality
    search_box = page.locator("input[name='q']")
    expect(search_box).to_be_visible()
    search_box.fill("Playwright")
    search_box.press("Enter")
    expect(page).to_have_title("Playwright - Google Search")
    
    # Test navigation and links
    page.goto("https://www.google.com")
    expect(page.locator("text=Gmail")).to_be_visible()
    expect(page.locator("text=Images")).to_be_visible()
    
    # Test "I'm Feeling Lucky" button
    lucky_button = page.locator("input[name='btnI']")
    expect(lucky_button).to_be_visible()
    
    # Test language options
    language_link = page.locator("text=Google offered in:")
    expect(language_link).to_be_visible()
    
    # Test footer links
    expect(page.locator("text=About")).to_be_visible()
    expect(page.locator("text=Advertising")).to_be_visible()
    expect(page.locator("text=Business")).to_be_visible()
    expect(page.locator("text=How Search works")).to_be_visible()
    
    # Test responsive design
    page.set_viewport_size({"width": 1920, "height": 1080})
    expect(page.locator("input[name='q']")).to_be_visible()
    page.set_viewport_size({"width": 375, "height": 667})
    expect(page.locator("input[name='q']")).to_be_visible()
    
    # Test voice search button
    voice_search = page.locator("div[aria-label='Search by voice']")
    expect(voice_search).to_be_visible()
    
    # Test settings menu
    settings_button = page.locator("text=Settings")
    expect(settings_button).to_be_visible()
    settings_button.click()
    expect(page.locator("text=Search settings")).to_be_visible()
    expect(page.locator("text=Advanced search")).to_be_visible()
    
    # Test sign-in button
    sign_in_button = page.locator("text=Sign in")
    expect(sign_in_button).to_be_visible()

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        try:
            test_google_com(page)
            print("✅ All tests passed!")
        except Exception as e:
            print(f"❌ Test failed: {str(e)}")
        finally:
            browser.close()
