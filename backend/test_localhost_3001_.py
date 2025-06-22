
import pytest
from playwright.sync_api import Page, expect

def test_localhost_3001(page: Page):
    # Test page loading and basic elements
    page.goto("http://localhost:3001/")
    expect(page).to_have_title("Vite + React")
    
    # Test navigation and links
    navbar = page.locator("nav")
    expect(navbar).to_be_visible()
    
    links = navbar.locator("a")
    expect(links).to_have_count(3)
    
    # Test forms and user interactions
    input_field = page.locator('input[type="text"]')
    expect(input_field).to_be_visible()
    
    input_field.fill("Test input")
    expect(input_field).to_have_value("Test input")
    
    submit_button = page.locator('button:has-text("Submit")')
    submit_button.click()
    
    # Test responsive design elements
    page.set_viewport_size({"width": 1200, "height": 800})
    expect(page.locator("main")).to_be_visible()
    
    page.set_viewport_size({"width": 375, "height": 667})
    expect(page.locator("main")).to_be_visible()
    
    # Test dynamic content loading
    load_more_button = page.locator('button:has-text("Load More")')
    
    if load_more_button.is_visible():
        initial_item_count = page.locator('.item').count()
        load_more_button.click()
        page.wait_for_selector('.item >> nth=' + str(initial_item_count))
        expect(page.locator('.item')).to_have_count(greater_than=initial_item_count)
    
    # Test error handling
    page.goto("http://localhost:3001/non-existent-page")
    expect(page.locator("text=404")).to_be_visible()
    
    # Test search functionality
    page.goto("http://localhost:3001/")
    search_input = page.locator('input[placeholder="Search..."]')
    
    if search_input.is_visible():
        search_input.fill("test search")
        search_input.press("Enter")
        page.wait_for_selector('.search-results')
        expect(page.locator('.search-results')).to_be_visible()
    
    # Test modal or popup if present
    modal_trigger = page.locator('button:has-text("Open Modal")')
    
    if modal_trigger.is_visible():
        modal_trigger.click()
        modal = page.locator('.modal')
        expect(modal).to_be_visible()
        
        close_button = modal.locator('button:has-text("Close")')
        close_button.click()
        expect(modal).to_be_hidden()
    
    # Test dark mode toggle if present
    dark_mode_toggle = page.locator('#dark-mode-toggle')
    
    if dark_mode_toggle.is_visible():
        initial_theme = page.evaluate('document.body.classList.contains("dark-theme")')
        dark_mode_toggle.click()
        new_theme = page.evaluate('document.body.classList.contains("dark-theme")')
        expect(new_theme).not_to_equal(initial_theme)

if __name__ == "__main__":
    pytest.main([__file__])
