"""
Real Madison County, MS Data Scraper
Attempts to scrape actual property records from Madison County website
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("Error: Playwright not installed. Run: pip install playwright && playwright install")
    exit(1)

from src.schemas.case_file import CaseFile, DeedOfTrust
from src.probability.engine import calculate_deal_probability

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RealMadisonCountyScraper:
    """Scrape real data from Madison County, MS website"""
    
    def __init__(self):
        self.county = "Madison"
        self.state = "MS"
        self.website = "https://www.co.madison.ms.us/"
        self.browser = None
        self.page = None
    
    async def initialize(self):
        """Start browser"""
        async with async_playwright() as p:
            self.browser = await p.chromium.launch(headless=False)  # Show browser
            self.page = await self.browser.new_page()
            self.page.set_default_timeout(30000)
            logger.info("Browser initialized")
    
    async def find_search_page(self) -> bool:
        """Navigate to property search page"""
        try:
            logger.info(f"Navigating to {self.website}")
            await self.page.goto(self.website, wait_until='networkidle')
            
            # Look for deed search or property records link
            logger.info("Looking for property records search link...")
            
            # Try common patterns
            search_links = [
                "text='Deed Search'",
                "text='Property Search'",
                "text='Land Records'",
                "text='Property Records'",
                "a:has-text('Deed')",
                "a:has-text('Property')",
            ]
            
            for link_selector in search_links:
                try:
                    link = await self.page.query_selector(link_selector)
                    if link:
                        logger.info(f"Found link: {link_selector}")
                        await link.click()
                        await asyncio.sleep(2)
                        return True
                except:
                    continue
            
            logger.warning("Could not find deed search link - showing page content")
            content = await self.page.content()
            
            # Print page title and links for debugging
            title = await self.page.title()
            logger.info(f"Page title: {title}")
            
            links = await self.page.evaluate('''
                () => {
                    return Array.from(document.querySelectorAll('a'))
                        .map(a => ({text: a.textContent, href: a.href}))
                        .filter(link => link.text.toLowerCase().includes('deed') || 
                                       link.text.toLowerCase().includes('property') ||
                                       link.text.toLowerCase().includes('record'));
                }
            ''')
            
            if links:
                logger.info(f"Found relevant links: {json.dumps(links, indent=2)}")
            
            return False
        
        except Exception as e:
            logger.error(f"Navigation error: {e}")
            return False
    
    async def search_documents(self) -> List[Dict]:
        """Search for Substitute Trustee documents"""
        try:
            logger.info("Searching for Substitute Trustee documents...")
            
            # Try to find search form
            search_form = await self.page.query_selector('form')
            if not search_form:
                logger.warning("No search form found on page")
                return []
            
            # Get current URL to understand site structure
            current_url = self.page.url
            logger.info(f"Current URL: {current_url}")
            
            # Print all form fields
            form_fields = await self.page.evaluate('''
                () => {
                    return Array.from(document.querySelectorAll('input, select, textarea'))
                        .map(field => ({
                            name: field.name || field.id || 'unknown',
                            type: field.type || 'select',
                            options: field.tagName === 'SELECT' ? 
                                Array.from(field.options).map(o => o.text) : []
                        }));
                }
            ''')
            
            logger.info(f"Found form fields: {json.dumps(form_fields, indent=2)}")
            
            return []
        
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []
    
    async def run(self):
        """Run the scraper"""
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=False)
                page = await browser.new_page()
                
                try:
                    logger.info("="*70)
                    logger.info("REAL MADISON COUNTY DATA SCRAPER")
                    logger.info("="*70)
                    
                    # Step 1: Go to county website
                    logger.info("\n[Step 1] Navigating to Madison County website...")
                    await page.goto(self.website, wait_until='networkidle')
                    
                    page_title = await page.title()
                    logger.info(f"Landed on: {page_title}")
                    
                    # Step 2: Find and click deed search
                    logger.info("\n[Step 2] Looking for property records search...")
                    
                    # Get all links on page
                    all_links = await page.evaluate('''
                        () => Array.from(document.querySelectorAll('a'))
                            .slice(0, 20)
                            .map(a => ({text: a.textContent.trim(), href: a.href}))
                    ''')
                    
                    logger.info("First 20 links on page:")
                    for i, link in enumerate(all_links, 1):
                        logger.info(f"  {i}. {link['text']} → {link['href']}")
                    
                    # Manual instruction
                    logger.info("\n⚠️  MANUAL ACTION REQUIRED:")
                    logger.info("1. Browser window opened showing Madison County website")
                    logger.info("2. Find and click the 'Deed Search' or 'Property Records' link")
                    logger.info("3. Once on search page, look for form fields")
                    logger.info("4. Close the browser when done (script will continue)")
                    
                    # Keep browser open for manual interaction
                    await asyncio.sleep(30)
                    
                    # After manual interaction
                    current_url = page.url
                    logger.info(f"\nCurrent URL after manual navigation: {current_url}")
                    
                    # Try to detect if we're on a search page
                    search_forms = await page.query_selector_all('form')
                    if search_forms:
                        logger.info(f"Found {len(search_forms)} form(s) on page")
                        
                        # Inspect first form
                        form_info = await page.evaluate('''
                            () => {
                                const form = document.querySelector('form');
                                if (!form) return null;
                                
                                return {
                                    id: form.id,
                                    action: form.action,
                                    fields: Array.from(form.querySelectorAll('input, select, textarea'))
                                        .map(f => ({
                                            name: f.name,
                                            id: f.id,
                                            type: f.type || f.tagName,
                                            placeholder: f.placeholder,
                                            options: f.tagName === 'SELECT' ? 
                                                Array.from(f.options).map(o => ({value: o.value, text: o.text})) : []
                                        }))
                                };
                            }
                        ''')
                        
                        logger.info(f"Form structure: {json.dumps(form_info, indent=2)}")
                    
                    logger.info("\n✓ Scraper ready for real data extraction")
                    logger.info("Next steps:")
                    logger.info("1. Update selectors in madison_ms.json based on actual form fields")
                    logger.info("2. Implement actual document search")
                    logger.info("3. Extract Substitute Trustee documents")
                    
                finally:
                    await browser.close()
        
        except Exception as e:
            logger.error(f"Fatal error: {e}", exc_info=True)


async def main():
    """Main entry point"""
    scraper = RealMadisonCountyScraper()
    await scraper.run()


if __name__ == '__main__':
    print("\n" + "="*70)
    print("MADISON COUNTY REAL DATA SCRAPER")
    print("="*70)
    print("\nThis script will:")
    print("1. Open Madison County website in a browser")
    print("2. Let you manually navigate to property records")
    print("3. Inspect the search form structure")
    print("4. Guide you to update the configuration")
    print("\nPress Enter to start...")
    input()
    
    asyncio.run(main())
