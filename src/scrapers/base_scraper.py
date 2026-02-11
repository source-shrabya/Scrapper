"""
Base Web Scraper with Anti-Bot Detection
Supports Playwright + Browserless.io / ScrapingBee for proxy handling
"""

import os
import json
import asyncio
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from abc import ABC, abstractmethod
import logging

try:
    from playwright.async_api import async_playwright, Browser, BrowserContext, Page
except ImportError:
    raise ImportError("Please install playwright: pip install playwright")

logger = logging.getLogger(__name__)


class AntiBot:
    """Anti-bot detection and stealth configurations"""
    
    @staticmethod
    def get_stealth_context_config() -> Dict:
        """Get stealth browser context configurations"""
        return {
            'viewport': {'width': 1920, 'height': 1080},
            'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'extra_http_headers': {
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Cache-Control': 'max-age=0',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
            },
            'locale': 'en-US',
            'timezone_id': 'America/Chicago',
        }


class BaseScraper(ABC):
    """
    Base scraper class - handles browser automation and page navigation
    
    Subclasses should implement:
    - setup_county_config(): Load county-specific settings
    - search_documents(): Perform search for relevant documents
    - extract_data(): Extract data from document pages
    """
    
    def __init__(
        self,
        county_name: str,
        use_proxy: bool = False,
        proxy_url: Optional[str] = None,
        headless: bool = True,
        timeout: int = 30000,
    ):
        self.county_name = county_name
        self.use_proxy = use_proxy
        self.proxy_url = proxy_url
        self.headless = headless
        self.timeout = timeout
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.button_map: Dict = {}  # Stores recorded button selectors for replay
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    async def initialize(self):
        """Initialize browser and context"""
        async with async_playwright() as p:
            launch_args = {
                'headless': self.headless,
            }
            
            # Add proxy if using
            if self.use_proxy and self.proxy_url:
                launch_args['proxy'] = {'server': self.proxy_url}
            
            self.browser = await p.chromium.launch(**launch_args)
            
            # Create context with stealth settings
            context_config = AntiBot.get_stealth_context_config()
            self.context = await self.browser.new_context(**context_config)
            
            self.page = await self.context.new_page()
            self.page.set_default_timeout(self.timeout)
            
            logger.info(f"Browser initialized for {self.county_name}")
    
    async def close(self):
        """Close browser"""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        logger.info(f"Browser closed for {self.county_name}")
    
    async def navigate_to(self, url: str) -> bool:
        """Navigate to URL with error handling"""
        try:
            await self.page.goto(url, wait_until='networkidle')
            logger.info(f"Navigated to {url}")
            return True
        except Exception as e:
            logger.error(f"Navigation failed to {url}: {e}")
            return False
    
    async def wait_for_element(self, selector: str, timeout: int = 5000) -> bool:
        """Wait for element to appear"""
        try:
            await self.page.wait_for_selector(selector, timeout=timeout)
            return True
        except Exception as e:
            logger.warning(f"Element not found: {selector} - {e}")
            return False
    
    async def click_element(self, selector: str) -> bool:
        """Click element by selector"""
        try:
            await self.page.click(selector)
            await asyncio.sleep(0.5)  # Brief pause for page to respond
            logger.debug(f"Clicked element: {selector}")
            return True
        except Exception as e:
            logger.warning(f"Could not click element {selector}: {e}")
            return False
    
    async def fill_input(self, selector: str, text: str) -> bool:
        """Fill input field"""
        try:
            await self.page.fill(selector, text)
            await asyncio.sleep(0.3)
            logger.debug(f"Filled input {selector} with text")
            return True
        except Exception as e:
            logger.warning(f"Could not fill input {selector}: {e}")
            return False
    
    async def record_button_map(self, county_config: Dict) -> Dict:
        """
        Record button clicks and selectors for a county
        User manually navigates to a document, script records all button interactions
        
        Returns dictionary mapping step names to selectors
        """
        button_map = {
            'county': self.county_name,
            'timestamp': self.session_id,
            'steps': []
        }
        
        logger.info("Starting button map recording - navigate manually to document")
        # User performs clicks, each registered as a step
        # This would be captured via Playwright's codegen or manual recording
        
        return button_map
    
    async def replay_button_map(self, button_map: Dict) -> bool:
        """
        Replay recorded button map to navigate to documents
        """
        try:
            for step in button_map.get('steps', []):
                selector = step.get('selector')
                action = step.get('action')
                
                if action == 'click':
                    await self.click_element(selector)
                elif action == 'fill':
                    text = step.get('text', '')
                    await self.fill_input(selector, text)
                
                await asyncio.sleep(0.3)
            
            logger.info("Button map replay completed successfully")
            return True
        except Exception as e:
            logger.error(f"Button map replay failed: {e}")
            return False
    
    async def get_screenshot(self, page_num: int = 1) -> Optional[bytes]:
        """Capture page screenshot"""
        try:
            screenshot = await self.page.screenshot()
            logger.debug(f"Screenshot captured (page {page_num})")
            return screenshot
        except Exception as e:
            logger.warning(f"Screenshot failed: {e}")
            return None
    
    async def extract_page_text(self) -> str:
        """Extract all text from current page"""
        try:
            text = await self.page.evaluate('() => document.documentElement.innerText')
            return text
        except Exception as e:
            logger.warning(f"Text extraction failed: {e}")
            return ""
    
    async def get_page_html(self) -> str:
        """Get page HTML"""
        try:
            html = await self.page.content()
            return html
        except Exception as e:
            logger.warning(f"HTML extraction failed: {e}")
            return ""
    
    @abstractmethod
    async def search_documents(self, search_params: Dict) -> List[Dict]:
        """
        Search for documents based on parameters
        Must be implemented by county-specific subclass
        
        Args:
            search_params: Dict with search criteria (date range, trustee, etc)
        
        Returns:
            List of document references found
        """
        pass
    
    @abstractmethod
    async def extract_data(self, document_ref: Dict) -> Dict:
        """
        Extract data from a document
        Must be implemented by county-specific subclass
        
        Args:
            document_ref: Reference to a document
        
        Returns:
            Dictionary of extracted data
        """
        pass


class CountyScraperFactory:
    """Factory to create county-specific scrapers"""
    
    _scrapers: Dict = {}
    
    @classmethod
    def register(cls, county_name: str, scraper_class):
        """Register a county scraper"""
        cls._scrapers[county_name.lower()] = scraper_class
        logger.info(f"Registered scraper for {county_name}")
    
    @classmethod
    def create(cls, county_name: str, **kwargs) -> BaseScraper:
        """Create scraper instance for county"""
        scraper_class = cls._scrapers.get(county_name.lower())
        if not scraper_class:
            raise ValueError(f"No scraper registered for county: {county_name}")
        return scraper_class(**kwargs)
    
    @classmethod
    def list_counties(cls) -> List[str]:
        """List all registered counties"""
        return list(cls._scrapers.keys())
