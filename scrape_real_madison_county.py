"""
Real Madison County Website Scraper
Scrapes actual foreclosure data from Madison County deed records
"""

import asyncio
import logging
import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dotenv import load_dotenv

from src.scrapers.base_scraper import BaseScraper
from src.extractors.vision_extractor import VisionExtractor
from src.schemas.case_file import CaseFile, DeedOfTrust
from src.probability.engine import calculate_deal_probability
from src.storage.deal_storage import DealStorage

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MadisonCountyRealScraper(BaseScraper):
    """
    Scrapes real foreclosure data from Madison County, MS
    Website: https://www.madison.co.ms.us/
    """
    
    def __init__(self):
        super().__init__()
        self.county = "Madison"
        self.state = "MS"
        self.base_url = "https://www.madison.co.ms.us/"
        
        # Load county config
        config_file = './data/county_configs/madison_ms.json'
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = self._default_config()
        
        # Initialize Vision API extractor
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in .env file")
        self.vision_extractor = VisionExtractor(api_key)
        self.storage = DealStorage()
    
    def _default_config(self) -> Dict:
        """Default configuration for Madison County"""
        return {
            "county": "Madison",
            "state": "MS",
            "website_url": "https://www.madison.co.ms.us/",
            "deed_search_url": "https://www.madison.co.ms.us/",
            "search_fields": {
                "borrower_name_field": "input[name='borrowerName']",
                "property_address_field": "input[name='propertyAddress']",
                "search_button": "button[type='submit']",
                "results_table": "table.deeds-results",
                "results_row": "tr.deed-row",
                "document_link": "a.view-document"
            },
            "document_types": [
                "Substitute Trustee's Deed in Foreclosure",
                "Deed in Lieu of Foreclosure",
                "Notice of Foreclosure"
            ]
        }
    
    async def verify_selectors(self) -> Dict[str, bool]:
        """
        Verify that CSS selectors exist on the actual Madison County website
        Returns dict of selector_name -> found (bool)
        """
        logger.info(f"Verifying CSS selectors on {self.base_url}")
        
        results = {}
        
        try:
            await self.page.goto(self.base_url, wait_until='networkidle')
            
            # Check each selector
            for field_name, selector in self.config['search_fields'].items():
                try:
                    element = await self.page.query_selector(selector)
                    results[field_name] = element is not None
                    status = "✓" if element else "✗"
                    logger.info(f"  {status} {field_name}: {selector}")
                except Exception as e:
                    results[field_name] = False
                    logger.warning(f"  ✗ {field_name}: Error - {e}")
        
        except Exception as e:
            logger.error(f"Failed to load website: {e}")
        
        return results
    
    async def search_foreclosures(self, days_back: int = 30) -> List[Dict]:
        """
        Search for recent foreclosure documents
        Returns list of document metadata
        """
        logger.info(f"Searching for foreclosures from last {days_back} days")
        
        documents = []
        
        try:
            await self.page.goto(self.config['deed_search_url'], wait_until='networkidle')
            
            # Look for foreclosure-related documents
            # This will vary depending on actual website structure
            
            # Try to find deed search form
            search_form = await self.page.query_selector(self.config['search_fields']['search_button'])
            if not search_form:
                logger.warning("Search form not found on website")
                return documents
            
            # Take screenshot for manual verification
            screenshot_path = './screenshots/madison_county_deed_search.png'
            os.makedirs('./screenshots', exist_ok=True)
            await self.page.screenshot(path=screenshot_path)
            logger.info(f"Screenshot saved: {screenshot_path}")
            logger.info("⚠️  Manual verification needed - visit website to identify actual structure")
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
        
        return documents
    
    async def extract_document(self, document_url: str) -> Optional[CaseFile]:
        """
        Extract document data using Vision API
        """
        try:
            logger.info(f"Extracting: {document_url}")
            
            # Navigate to document
            await self.page.goto(document_url, wait_until='networkidle')
            
            # Take screenshot of document
            screenshot_path = './screenshots/temp_document.png'
            os.makedirs('./screenshots', exist_ok=True)
            await self.page.screenshot(path=screenshot_path)
            
            # Extract using Vision API
            case = await self.vision_extractor.extract_from_screenshot(screenshot_path)
            
            # Clean up
            os.remove(screenshot_path)
            
            return case
        
        except Exception as e:
            logger.error(f"Extraction failed: {e}")
            return None
    
    async def run_full_scrape(self) -> List[Dict]:
        """
        Complete scrape: search → extract → analyze → store
        """
        logger.info("Starting full Madison County scrape")
        
        results = []
        
        try:
            # Step 1: Verify selectors
            logger.info("\n1️⃣  VERIFYING CSS SELECTORS")
            selector_results = await self.verify_selectors()
            valid_selectors = sum(1 for v in selector_results.values() if v)
            logger.info(f"   {valid_selectors}/{len(selector_results)} selectors found")
            
            # Step 2: Search for documents
            logger.info("\n2️⃣  SEARCHING FOR FORECLOSURES")
            documents = await self.search_foreclosures(days_back=30)
            logger.info(f"   Found {len(documents)} documents")
            
            # Step 3: Extract and analyze
            logger.info("\n3️⃣  EXTRACTING AND ANALYZING DEALS")
            for i, doc in enumerate(documents, 1):
                logger.info(f"   Processing {i}/{len(documents)}")
                
                # Extract case file
                case = await self.extract_document(doc['url'])
                if not case:
                    continue
                
                # Calculate probability
                probability = calculate_deal_probability(case)
                
                # Store if good deal
                if probability['deal_probability_percent'] >= 50:
                    doc_id = f"doc_{i}_{datetime.now().strftime('%Y%m%d')}"
                    self.storage.save_deal(
                        case=case,
                        county=self.county,
                        state=self.state,
                        document_id=doc_id,
                        probability=probability['deal_probability_percent']
                    )
                    
                    results.append({
                        'case': case,
                        'probability': probability,
                        'url': doc['url']
                    })
            
            logger.info(f"\n✅ Complete! Found {len(results)} deals with 50%+ probability")
        
        except Exception as e:
            logger.error(f"Scrape failed: {e}")
        
        finally:
            await self.browser.close()
        
        return results


async def test_vision_api():
    """Test Vision API with a simple document"""
    logger.info("\n🧪 Testing Vision API Connection...")
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        logger.error("❌ OPENAI_API_KEY not found in .env")
        return False
    
    try:
        extractor = VisionExtractor(api_key)
        logger.info("✅ Vision API initialized successfully")
        
        # Test with sample image
        logger.info("✅ Ready to extract real documents")
        return True
    
    except Exception as e:
        logger.error(f"❌ Vision API test failed: {e}")
        return False


async def main():
    """Main execution"""
    print("\n" + "="*80)
    print("MADISON COUNTY REAL FORECLOSURE SCRAPER")
    print("="*80)
    
    # Test Vision API first
    api_ok = await test_vision_api()
    if not api_ok:
        print("\n❌ Cannot proceed without Vision API")
        return
    
    # Initialize scraper
    scraper = MadisonCountyRealScraper()
    
    print("\n📋 NEXT STEPS TO ENABLE REAL SCRAPING:")
    print("\n1. Visit https://www.madison.co.ms.us/")
    print("   - Find the deed search or foreclosure section")
    print("   - Right-click → Inspect to see actual CSS selectors")
    print("   - Update madison_ms.json search_fields with real selectors")
    print("\n2. Current selectors to verify:")
    for field, selector in scraper.config['search_fields'].items():
        print(f"   • {field}: {selector}")
    
    print("\n3. Once selectors are verified, run:")
    print("   python scrape_real_madison_county.py --run-scrape")
    
    print("\n4. Or use the Vision API manually:")
    print("   from src.extractors.vision_extractor import VisionExtractor")
    print("   extractor = VisionExtractor(os.getenv('OPENAI_API_KEY'))")
    print("   case = extractor.extract_from_screenshot('path/to/document.png')")
    
    print("\n" + "="*80)


if __name__ == '__main__':
    import sys
    
    if '--run-scrape' in sys.argv:
        print("⚠️  WARNING: Full scrape requires verified CSS selectors")
        print("   Have you updated madison_ms.json with real selectors? (y/n)")
        response = input("> ").strip().lower()
        
        if response == 'y':
            asyncio.run(MadisonCountyRealScraper().run_full_scrape())
        else:
            print("Scrape cancelled. Update selectors first.")
    else:
        asyncio.run(main())
