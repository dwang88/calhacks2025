
import pytest
from playwright.sync_api import Page, expect

def test_page_load_and_basic_elements(page: Page):
    page.goto("http://localhost:3002/")
    expect(page).to_have_title("React App")
    expect(page.locator("header")).to_be_visible()
    expect(page.locator("main")).to_be_visible()
    expect(page.locator("footer")).to_be_visible()

def test_navigation_and_links(page: Page):
    page.goto("http://localhost:3002/")
    
    # Test navigation menu items
    nav_items = page.locator("nav a")
    expect(nav_items).to_have_count(4)
    
    for item in ["Home", "About", "Services", "Contact"]:
        expect(nav_items.get_by_text(item)).to_be_visible()
    
    # Test footer links
    footer_links = page.locator("footer a")
    expect(footer_links).to_have_count(3)
    
    for link in ["Privacy Policy", "Terms of Service", "Contact Us"]:
        expect(footer_links.get_by_text(link)).to_be_visible()

def test_forms_and_user_interactions(page: Page):
    page.goto("http://localhost:3002/")
    
    # Test contact form
    name_input = page.locator("#name")
    email_input = page.locator("#email")
    message_input = page.locator("#message")
    submit_button = page.locator("button[type='submit']")
    
    name_input.fill("Test User")
    email_input.fill("test@example.com")
    message_input.fill("This is a test message")
    submit_button.click()
    
    # Check for success message (assuming one exists)
    success_message = page.locator(".success-message")
    expect(success_message).to_be_visible()
    expect(success_message).to_contain_text("Message sent successfully")

def test_responsive_design(page: Page):
    page.goto("http://localhost:3002/")
    
    # Test desktop view
    page.set_viewport_size({"width": 1280, "height": 720})
    expect(page.locator("nav")).to_be_visible()
    
    # Test mobile view
    page.set_viewport_size({"width": 375, "height": 667})
    expect(page.locator("nav")).to_be_hidden()
    
    # Check for hamburger menu in mobile view
    hamburger_menu = page.locator(".hamburger-menu")
    expect(hamburger_menu).to_be_visible()
    
    # Test hamburger menu functionality
    hamburger_menu.click()
    mobile_nav = page.locator(".mobile-nav")
    expect(mobile_nav).to_be_visible()

def test_error_handling(page: Page):
    page.goto("http://localhost:3002/non-existent-page")
    error_message = page.locator(".error-message")
    expect(error_message).to_be_visible()
    expect(error_message).to_contain_text("404")

def test_dynamic_content_loading(page: Page):
    page.goto("http://localhost:3002/")
    
    # Assuming there's a "Load More" button for dynamic content
    load_more_button = page.locator("#load-more")
    
    if load_more_button.is_visible():
        initial_content_count = page.locator(".content-item").count()
        load_more_button.click()
        page.wait_for_load_state("networkidle")
        
        new_content_count = page.locator(".content-item").count()
        assert new_content_count > initial_content_count, "Content was not loaded dynamically"

def test_image_loading(page: Page):
    page.goto("http://localhost:3002/")
    
    images = page.locator("img")
    for i in range(images.count()):
        img = images.nth(i)
        expect(img).to_be_visible()
        src = img.get_attribute("src")
        assert src and src != "", f"Image {i} has no source"

def test_accessibility(page: Page):
    page.goto("http://localhost:3002/")
    
    # Check for alt text on images
    images = page.locator("img")
    for i in range(images.count()):
        img = images.nth(i)
        alt_text = img.get_attribute("alt")
        assert alt_text and alt_text != "", f"Image {i} is missing alt text"
    
    # Check for proper heading structure
    headings = page.locator("h1, h2, h3, h4, h5, h6")
    previous_level = 0
    for i in range(headings.count()):
        heading = headings.nth(i)
        level = int(heading.evaluate("el => el.tagName.charAt(1)"))
        assert level <= previous_level + 1, f"Heading structure is not sequential at heading {i+1}"
        previous_level = level

if __name__ == "__main__":
    pytest.main([__file__])
