# REAL SCRAPER SETUP GUIDE

## ✅ Status Check

- ✅ **Vision API**: Configured and working with your API key
- ✅ **Storage System**: All deals save automatically
- ✅ **Test Data**: Working perfectly (3 deals analyzed)
- ⏳ **Real Scraper**: Ready to connect - needs manual setup

---

## Step-by-Step Setup

### STEP 1: Manual Website Inspection (5 minutes)

1. **Open Madison County website**:
   ```
   https://www.madison.co.ms.us/
   ```

2. **Find the deed search section** (look for tabs like):
   - "Deed Search"
   - "Records"
   - "Foreclosure Sales"
   - "Property Search"

3. **Right-click on a form field** → Select "Inspect" (or press F12)

4. **Copy the CSS selector** - You're looking for patterns like:
   ```
   input[name='borrowerName']
   input[id='search-field']
   button.search-btn
   #submitButton
   ```

5. **Update `madison_ms.json`** with the real selectors

---

### STEP 2: Update County Configuration

Edit `/data/county_configs/madison_ms.json`:

```json
{
  "county": "Madison",
  "state": "MS",
  "website_url": "https://www.madison.co.ms.us/",
  "deed_search_url": "https://www.madison.co.ms.us/",
  "search_fields": {
    "borrower_name_field": "[SELECTOR FROM WEBSITE]",
    "property_address_field": "[SELECTOR FROM WEBSITE]",
    "search_button": "[SELECTOR FROM WEBSITE]",
    "results_table": "[SELECTOR FROM WEBSITE]",
    "results_row": "[SELECTOR FROM WEBSITE]",
    "document_link": "[SELECTOR FROM WEBSITE]"
  }
}
```

**Example of real selectors** (from typical government sites):
```json
{
  "borrower_name_field": "input#borrowerName",
  "property_address_field": "input[name='propertyAddress']",
  "search_button": "button[type='submit']",
  "results_table": "table#resultsTable",
  "results_row": "tbody > tr",
  "document_link": "a.view-pdf"
}
```

---

### STEP 3: Test Selectors

Once you've updated the config, run:

```bash
python scrape_real_madison_county.py
```

This will:
1. ✅ Verify all selectors exist on the website
2. ✅ Show you which ones work and which don't
3. ✅ Take screenshots for verification

---

### STEP 4: Use Vision API for Document Extraction

Once the scraper finds documents, Vision API will:

1. **Capture document image** from the website
2. **Extract structured data** using GPT-4 Vision:
   - Borrower name
   - Property address
   - Loan amount
   - Auction date
   - etc.
3. **Populate CaseFile** object automatically
4. **Calculate probability** and store in database

**Example usage**:
```python
from src.extractors.vision_extractor import VisionExtractor
import os

api_key = os.getenv('OPENAI_API_KEY')
extractor = VisionExtractor(api_key)

# Extract from screenshot
case = await extractor.extract_from_screenshot('document.png')

print(f"Borrower: {case.owner.name}")
print(f"Address: {case.property.address.street}")
print(f"Equity: {case.numbers.equityPercent:.1f}%")
```

---

## Available Tools

### Run Test Mode (No Real Scraping Yet)
```bash
python test_vision_api.py
```

### Scrape Real Website (Once Selectors Verified)
```bash
python scrape_real_madison_county.py --run-scrape
```

### View Stored Deals
```bash
python query_deals.py list
python query_deals.py export
python query_deals.py county MADISON MS
```

### Analyze New Deals
```bash
python analyze_real_deals.py
```

---

## Timeline & Effort

| Step | Effort | Time |
|------|--------|------|
| 1. Inspect website | Manual | 5-10 min |
| 2. Update config | Edit JSON | 2-5 min |
| 3. Test selectors | Run script | 1-2 min |
| 4. Verify working | Check output | 2-5 min |
| **Total** | **Low** | **10-22 min** |

---

## Troubleshooting

### "Selector not found"
- Website structure changed
- Selector is incorrect CSS syntax
- Website uses JavaScript to load content (need to wait for load)

**Solution**: Right-click → Inspect again, verify selector is correct

### "Vision API returning null fields"
- Document image is unclear
- Field is handwritten (AI struggles)
- Document type not recognized

**Solution**: Ensure document is clear PDF/image with printed text

### "Can't connect to website"
- Website is down
- You need VPN
- IP is blocked

**Solution**: Try visiting https://www.madison.co.ms.us/ manually first

---

## Next Phase: Automated Daily Runs

Once real scraper is working, you can set up automated runs:

```bash
# Run at 3am every day
0 3 * * * cd /Users/shrabyabhattarai/Desktop/Scrapper && python scrape_real_madison_county.py --run-scrape
```

This will:
- Scrape Madison County deed records daily
- Extract with Vision API
- Calculate probabilities
- Store deals automatically
- Send you email alerts for 70%+ deals

---

## Summary

| Component | Status | What It Does |
|-----------|--------|-------------|
| **Vision API** | ✅ Ready | Extracts data from document images |
| **Storage** | ✅ Ready | Saves deals permanently |
| **Probability Engine** | ✅ Ready | Scores deals |
| **Test Data** | ✅ Working | 3 example deals |
| **CSS Selectors** | ⏳ Manual | Need you to verify website structure |
| **Real Scraper** | ⏳ Ready | Waiting for selectors |
| **Automation** | ⏳ Next Phase | After real scraper works |

---

## Questions?

1. **Can't find deed search on website?**
   - Try the website directly: https://www.madison.co.ms.us/
   - Look for any records, deeds, or property search section

2. **CSS selector syntax?**
   - By ID: `#elementId`
   - By name: `input[name='fieldName']`
   - By class: `.className`
   - By type: `button[type='submit']`
   - Copy from Inspector panel (right-click → Inspect)

3. **Need to test before full scrape?**
   - Run `python scrape_real_madison_county.py` (without --run-scrape)
   - It will verify selectors and show you screenshots

---

## You Are Here 🟢

```
Phase 1: Project Setup          ✅ Complete
Phase 2: Build Framework        ✅ Complete
Phase 3: Test with Sample Data  ✅ Complete (3 deals, 72-78% probability)
Phase 4: Storage System         ✅ Complete (auto-saves deals)
Phase 5: Vision API Setup       ✅ Complete (API key configured)
Phase 6: Real Website Scraping  ⏳ YOU ARE HERE - Need CSS selectors
Phase 7: Automated Daily Runs   ⏳ Next
Phase 8: Dashboard/UI           ⏳ Future
Phase 9: Multi-County Scaling   ⏳ Future
```

**Next Action**: Follow Step 1-2 above (10-20 minutes) to get real scraper working! 🚀
