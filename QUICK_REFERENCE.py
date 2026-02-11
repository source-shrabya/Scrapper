#!/usr/bin/env python
"""
QUICK REFERENCE: Vision API + Real Scraper Setup
Shows exact code and steps needed
"""

def show_vision_api_example():
    """Show Vision API usage"""
    
    code = """
# Vision API Usage - Extract Data from Document Images
from src.extractors.vision_extractor import VisionExtractor
import os

api_key = os.getenv('OPENAI_API_KEY')  # sk-proj-...
extractor = VisionExtractor(api_key)

# Extract from a document screenshot
case = await extractor.extract_from_screenshot('foreclosure_notice.png')

# Access extracted data
print(f"Borrower: {case.owner.name}")
print(f"Address: {case.property.address.street}")
print(f"Loan Amount: ${case.loan.deedsOfTrust[0].notePrincipal:,.0f}")
print(f"Interest Rate: {case.loan.deedsOfTrust[0].interestRate}%")
print(f"Property Value: ${case.numbers.arvDollars:,.0f}")
print(f"Estimated Equity: ${case.numbers.estimatedEquity:,.0f}")
    """
    
    print("\n" + "="*80)
    print("VISION API - Extract Data from Documents")
    print("="*80)
    print(code)


def show_selector_examples():
    """Show CSS selector examples"""
    
    examples = """
COMMON CSS SELECTORS (Copy from right-click → Inspect):

Input Fields:
  input[name='borrowerName']
  input[id='searchField']
  input[placeholder='Enter name']
  input[type='text']

Buttons:
  button[type='submit']
  button.search-btn
  input[type='submit']
  #submitButton

Tables:
  table#resultsTable
  table.deeds-list
  tbody > tr

Links:
  a.view-document
  a[href*='pdf']
  button.download

How to find real selectors:
  1. Visit website
  2. Right-click on field → Inspect (F12)
  3. Look at HTML: <input name="borrowerName" ...>
  4. Use that to build selector: input[name='borrowerName']
  5. Update madison_ms.json with real selectors
    """
    
    print("\n" + "="*80)
    print("CSS SELECTOR EXAMPLES")
    print("="*80)
    print(examples)


def show_workflow():
    """Show the complete workflow"""
    
    workflow = """
COMPLETE REAL DEAL SCRAPING WORKFLOW:

Step 1: INSPECT WEBSITE (Manual, 5 min)
├─ Visit: https://www.madison.co.ms.us/
├─ Find deed search section
├─ Right-click fields → Inspect
└─ Copy CSS selectors

Step 2: UPDATE CONFIG (Edit JSON, 2 min)
├─ Edit: ./data/county_configs/madison_ms.json
├─ Replace placeholder selectors
├─ Save file
└─ Run: python scrape_real_madison_county.py

Step 3: VERIFY SELECTORS (Automated, 1 min)
├─ Script tests all selectors
├─ Shows which ones work
├─ Takes screenshots
└─ Confirms website structure

Step 4: RUN SCRAPER (Automated, 5-30 min depending on docs)
├─ python scrape_real_madison_county.py --run-scrape
├─ Scraper finds documents
├─ Vision API extracts data
├─ Automatically saves deals
└─ Shows summary report

Step 5: VIEW RESULTS
├─ python query_deals.py list
├─ python query_deals.py export
├─ python query_deals.py county MADISON MS
└─ CSV ready for email/CRM

TOTAL TIME: 20-45 minutes to get real deals flowing
    """
    
    print("\n" + "="*80)
    print("COMPLETE WORKFLOW")
    print("="*80)
    print(workflow)


def show_commands():
    """Show all useful commands"""
    
    commands = """
COMMAND REFERENCE:

Test Vision API (verify it works):
  python test_vision_api.py

Inspect website for selectors:
  python inspect_website.py

Test selectors without scraping:
  python scrape_real_madison_county.py

Run full scraper (after selectors verified):
  python scrape_real_madison_county.py --run-scrape

View stored deals:
  python query_deals.py                    # Stats
  python query_deals.py list               # All deals
  python query_deals.py county MADISON MS  # County specific
  python query_deals.py export             # CSV export

Analyze deals:
  python analyze_real_deals.py             # Test with sample data

View deal details:
  cat ./data/deals/cases/Madison_*.json    # Raw JSON
  
View storage statistics:
  python query_deals.py                    # Full stats
    """
    
    print("\n" + "="*80)
    print("COMMAND REFERENCE")
    print("="*80)
    print(commands)


def show_files():
    """Show created files"""
    
    files = """
NEW FILES CREATED:

Core Implementation:
  ✅ src/storage/deal_storage.py          - Store/retrieve deals
  ✅ scrape_real_madison_county.py        - Real website scraper
  ✅ test_vision_api.py                   - Vision API tester
  ✅ query_deals.py                       - Query tool
  ✅ inspect_website.py                   - Website inspector

Documentation:
  ✅ REAL_SCRAPER_SETUP.md                - Setup guide
  ✅ STORAGE_GUIDE.md                     - Storage system docs
  ✅ test_vision_api.py (this file)       - Quick reference

Deal Storage:
  ✅ ./data/deals/cases/                  - Individual deal JSON files
  ✅ ./data/deals/index/                  - County indexes
  ✅ ./data/deals/export_all_deals.csv    - CSV export

Configuration:
  ✅ ./data/county_configs/madison_ms.json - County selectors (NEEDS UPDATE)
  ✅ .env                                 - API key (✅ already set)
    """
    
    print("\n" + "="*80)
    print("FILES CREATED")
    print("="*80)
    print(files)


def show_status():
    """Show current status"""
    
    status = """
🟢 READY TO USE:
  ✅ Vision API configured and working
  ✅ Storage system working (3 deals stored)
  ✅ Test data shows system is functional (72-78% probability)
  ✅ API key in .env file

🟡 IN PROGRESS:
  ⏳ CSS selector verification (manual, 5 min)
  ⏳ Real website scraping (waiting for selectors)

🔴 NOT YET:
  ❌ Automated daily runs
  ❌ Dashboard/UI
  ❌ Multi-county expansion

NEXT ACTION:
  1. Visit https://www.madison.co.ms.us/
  2. Find deed search section
  3. Right-click → Inspect → Copy CSS selectors
  4. Update madison_ms.json with real selectors
  5. Run: python scrape_real_madison_county.py
    """
    
    print("\n" + "="*80)
    print("CURRENT STATUS")
    print("="*80)
    print(status)


if __name__ == '__main__':
    show_status()
    show_vision_api_example()
    show_selector_examples()
    show_workflow()
    show_commands()
    show_files()
    
    print("\n" + "="*80)
    print("START HERE: REAL_SCRAPER_SETUP.md")
    print("="*80)
    print("""
Full step-by-step guide:
  cat REAL_SCRAPER_SETUP.md

Then:
  1. Inspect website (5 min)
  2. Update madison_ms.json (2 min)
  3. Run scraper (5-30 min)
  4. View results

That's it! You'll have real deals from Madison County.
    """)
