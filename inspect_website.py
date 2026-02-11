"""
Madison County Website Inspector
Opens the website and helps you identify real CSS selectors
"""

import asyncio
import json
import logging
from playwright.async_api import async_playwright

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def inspect_madison_county_website():
    """
    Opens Madison County website and takes screenshots for manual inspection
    """
    
    print("\n" + "="*80)
    print("MADISON COUNTY WEBSITE INSPECTOR")
    print("="*80)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
    
    try:
        print("\n🌐 Loading Madison County website...")
        await page.goto(
            'https://www.madison.co.ms.us/',
            wait_until='networkidle',
            timeout=30000
        )
        
        # Take screenshot of homepage
        screenshot1 = './screenshots/madison_homepage.png'
        await page.screenshot(path=screenshot1, full_page=True)
        print(f"✓ Homepage screenshot: {screenshot1}")
        
        # Try to find deed/foreclosure search
        print("\n🔍 Looking for deed search section...")
        
        # Check for common foreclosure-related links
        links = await page.evaluate("""
            () => {
                const links = [];
                document.querySelectorAll('a').forEach(link => {
                    const text = link.textContent.toLowerCase();
                    if (text.includes('deed') || text.includes('foreclosure') || 
                        text.includes('search') || text.includes('records')) {
                        links.push({
                            text: link.textContent.trim(),
                            href: link.href
                        });
                    }
                });
                return links;
            }
        """)
        
        if links:
            print(f"\n Found {len(links)} relevant links:")
            for i, link in enumerate(links, 1):
                print(f"  {i}. {link['text'][:50]}")
                print(f"     → {link['href']}")
        else:
            print("  No deed/foreclosure links found on homepage")
        
        # Try common deed search URLs
        print("\n🔎 Trying common deed search URLs...")
        
        potential_urls = [
            'https://www.madison.co.ms.us/deed-search',
            'https://www.madison.co.ms.us/records',
            'https://www.madison.co.ms.us/clerk',
            'https://records.madison.co.ms.us/',
            'https://deeds.madison.co.ms.us/',
        ]
        
        for url in potential_urls:
            try:
                await page.goto(url, wait_until='networkidle', timeout=10000)
                print(f"  ✓ Found: {url}")
                
                # Take screenshot
                screenshot = f"./screenshots/madison_{url.split('/')[-1] or 'homepage'}.png"
                await page.screenshot(path=screenshot, full_page=True)
                print(f"    Screenshot: {screenshot}")
                
                # Check for form fields
                form_fields = await page.evaluate("""
                    () => {
                        const fields = [];
                        document.querySelectorAll('input, textarea, select, button').forEach(el => {
                            if (el.name || el.id || el.placeholder) {
                                fields.push({
                                    type: el.tagName,
                                    name: el.name || el.id || el.placeholder,
                                    selector: el.name ? `input[name='${el.name}']` : 
                                             el.id ? `#${el.id}` : 
                                             `input[placeholder='${el.placeholder}']`
                                });
                            }
                        });
                        return fields;
                    }
                """)
                
                if form_fields:
                    print(f"    Found {len(form_fields)} form fields:")
                    for field in form_fields[:5]:
                        print(f"      • {field['name']}: {field['selector']}")
                
                break  # Found it, stop trying others
            
            except Exception as e:
                pass  # URL not found, try next
        
        print("\n" + "="*80)
        print("INSTRUCTIONS FOR MANUAL VERIFICATION")
        print("="*80)
        print("""
1. Open this URL in your browser:
   https://www.madison.co.ms.us/

2. Find the deed search or records section

3. Right-click on form fields → Select "Inspect" (or press F12)

4. Look for CSS selectors like:
   • input[name='borrowerName']
   • input[id='searchButton']
   • button.search-btn
   • etc.

5. Update madison_ms.json with the actual selectors:
   "search_fields": {
       "borrower_name_field": "[ACTUAL SELECTOR HERE]",
       "property_address_field": "[ACTUAL SELECTOR HERE]",
       ...
   }

6. Common selector patterns:
   • By name:    input[name='fieldName']
   • By ID:      #elementId or input#fieldId
   • By class:   .className or button.submit-btn
   • By type:    button[type='submit']
        """)
        
        print("\n📋 Current selectors in madison_ms.json:")
        print("-" * 80)
        
        try:
            with open('./data/county_configs/madison_ms.json', 'r') as f:
                config = json.load(f)
                for field, selector in config.get('search_fields', {}).items():
                    print(f"  {field:30} {selector}")
        except:
            print("  (Could not load madison_ms.json)")
        
        print("\n" + "="*80)
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure:")
        print("  1. You have internet connection")
        print("  2. Madison County website is accessible")
        print("  3. Playwright browsers are installed (playwright install chromium)")
    
    finally:
        try:
            await browser.close()
        except:
            pass


async def main():
    print("\n⚠️  This will open your browser and visit Madison County website")
    print("   Looking for deed search/foreclosure records...")
    
    await inspect_madison_county_website()


if __name__ == '__main__':
    asyncio.run(main())
