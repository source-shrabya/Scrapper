"""
Vision API Extraction Demo
Shows how to extract deal data from real foreclosure documents
"""

import os
import logging
from dotenv import load_dotenv

from src.extractors.vision_extractor import VisionExtractor
from src.probability.engine import calculate_deal_probability
from src.storage.deal_storage import DealStorage

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_vision_api():
    """Test that Vision API is properly configured"""
    
    print("\n" + "="*80)
    print("VISION API CONFIGURATION TEST")
    print("="*80)
    
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("\n❌ OPENAI_API_KEY not found in .env file")
        print("\nTo fix:")
        print("  1. Add this to .env:")
        print("     OPENAI_API_KEY=sk-proj-xxxxx")
        print("  2. Save the file")
        print("  3. Run this script again")
        return False
    
    if api_key.startswith('sk-proj-'):
        print("\n✅ API Key format looks correct (sk-proj-...)")
    else:
        print("\n⚠️  API Key might be invalid - should start with 'sk-proj-'")
        return False
    
    # Try to initialize Vision Extractor
    try:
        print("\n🔍 Testing Vision API connection...")
        extractor = VisionExtractor(api_key)
        print("✅ Vision API initialized successfully!")
        print(f"   - Using OpenAI GPT-4 Vision")
        print(f"   - Ready to extract documents")
        return True
    
    except Exception as e:
        print(f"\n❌ Vision API initialization failed: {e}")
        return False


def show_extraction_workflow():
    """Show how to extract real foreclosure documents"""
    
    print("\n" + "="*80)
    print("DOCUMENT EXTRACTION WORKFLOW")
    print("="*80)
    
    print("""
STEP 1: Capture Document Image
────────────────────────────────
- Visit Madison County deed records website
- Find substitute trustee foreclosure notices
- Take screenshot of the document (use Playwright/Selenium)
- Save as PNG: ./screenshots/foreclosure_document.png

Example code:
    from src.scrapers.base_scraper import BaseScraper
    scraper = BaseScraper()
    await scraper.page.goto('https://deed.co.madison.ms.us/')
    await scraper.page.screenshot(path='./screenshots/doc.png')

STEP 2: Extract with Vision API
────────────────────────────────
Example code:
    from src.extractors.vision_extractor import VisionExtractor
    import os
    
    api_key = os.getenv('OPENAI_API_KEY')
    extractor = VisionExtractor(api_key)
    
    case = await extractor.extract_from_screenshot(
        './screenshots/foreclosure_document.png'
    )
    
    print(f"Borrower: {case.owner.name}")
    print(f"Address: {case.property.address.street}")

STEP 3: Calculate Deal Probability
───────────────────────────────────
Example code:
    from src.probability.engine import calculate_deal_probability
    
    prob = calculate_deal_probability(case)
    print(f"Deal Probability: {prob['deal_probability_percent']:.1f}%")
    print(f"Quality: {prob['deal_quality']}")

STEP 4: Store Deal
──────────────────
Example code:
    from src.storage.deal_storage import DealStorage
    
    storage = DealStorage()
    storage.save_deal(
        case=case,
        county='Madison',
        state='MS',
        document_id='DOC_12345',
        probability=prob['deal_probability_percent']
    )
    
    print("✅ Deal saved to storage")

STEP 5: Query & Export
──────────────────────
Command line:
    python query_deals.py list          # View all deals
    python query_deals.py export        # Export to CSV
    python query_deals.py county MADISON MS  # County-specific
    """)


def show_complete_example():
    """Show a complete working example"""
    
    print("\n" + "="*80)
    print("COMPLETE EXAMPLE: Real Document Extraction")
    print("="*80)
    
    print("""
#!/usr/bin/env python
import asyncio
import os
from dotenv import load_dotenv
from src.scrapers.base_scraper import BaseScraper
from src.extractors.vision_extractor import VisionExtractor
from src.probability.engine import calculate_deal_probability
from src.storage.deal_storage import DealStorage

load_dotenv()

async def extract_real_foreclosure():
    # 1. Scrape document from website
    scraper = BaseScraper()
    await scraper.page.goto(
        'https://www.co.madison.ms.us/deed-search',
        wait_until='networkidle'
    )
    
    # Take screenshot of foreclosure notice
    await scraper.page.screenshot(path='./screenshots/foreclosure.png')
    await scraper.browser.close()
    
    # 2. Extract with Vision API
    api_key = os.getenv('OPENAI_API_KEY')
    extractor = VisionExtractor(api_key)
    
    case = await extractor.extract_from_screenshot(
        './screenshots/foreclosure.png'
    )
    
    # 3. Calculate probability
    prob = calculate_deal_probability(case)
    
    # 4. Store if it's a good deal
    if prob['deal_probability_percent'] >= 60:
        storage = DealStorage()
        storage.save_deal(
            case=case,
            county='Madison',
            state='MS',
            document_id='REAL_DOC_001',
            probability=prob['deal_probability_percent']
        )
        print(f"✅ Stored deal: {case.owner.name} - {prob['deal_probability_percent']:.1f}%")
    
    return case, prob

# Run it
if __name__ == '__main__':
    case, prob = asyncio.run(extract_real_foreclosure())
    print(f"Borrower: {case.owner.name}")
    print(f"Probability: {prob['deal_probability_percent']:.1f}%")
    """)


def main():
    """Main execution"""
    
    # Test API
    api_ok = test_vision_api()
    
    if not api_ok:
        print("\n⚠️  Cannot proceed without Vision API key")
        print("\nSet up instructions:")
        print("1. Get API key from https://platform.openai.com/account/api-keys")
        print("2. Add to .env file: OPENAI_API_KEY=sk-proj-xxxxx")
        print("3. Run this script again")
        return
    
    # Show workflow
    show_extraction_workflow()
    
    # Show example
    show_complete_example()
    
    print("\n" + "="*80)
    print("NEXT STEPS")
    print("="*80)
    print("""
1. ✅ Vision API configured
2. 📝 Update madison_ms.json with real CSS selectors from website
3. 🌐 Visit https://www.co.madison.ms.us/ and verify form fields
4. 🔍 Run real scraper once selectors are verified:
   python scrape_real_madison_county.py

5. 📊 View extracted deals:
   python query_deals.py list

6. 📤 Export to spreadsheet:
   python query_deals.py export
    """)
    print("="*80 + "\n")


if __name__ == '__main__':
    main()
