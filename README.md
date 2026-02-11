# Deal Engine Scraper

A comprehensive web scraping system for extracting real estate foreclosure data from county government records. Uses AI vision models to extract structured data and calculates deal probability scores for wholesale real estate opportunities.

## Overview

The Deal Engine Scraper identifies potential real estate wholesale deals by:

1. **Scraping** county government websites for foreclosure documents
2. **Extracting** structured data using GPT Vision API
3. **Calculating** deal probability based on equity, timeline, and other factors
4. **Scoring** properties to identify the highest-probability opportunities
5. **Outputting** clean JSON case files for downstream processing

## Key Features

- **Multi-County Support**: Extensible architecture for scraping multiple county jurisdictions
- **AI-Powered Extraction**: Uses GPT-4 Vision API to extract data from document screenshots
- **Anti-Bot Stealth**: Browserless.io/ScrapingBee integration for bypassing anti-bot detection
- **Deal Probability Engine**: Weighted scoring system based on equity %, timeline pressure, repair costs, and more
- **Comprehensive Case Files**: Normalized JSON schema containing all possible property/loan data points
- **Quality Validation**: Automated checks to ensure data integrity

## Project Structure

```
src/
  schemas/
    case_file.py          # Comprehensive Case File JSON schema
  scrapers/
    base_scraper.py       # Base scraper with Playwright + anti-bot
  extractors/
    vision_extractor.py   # GPT Vision API integration
  probability/
    engine.py             # Deal probability calculation engine
  counties/
    config_manager.py     # County-specific configuration management
  main.py                 # Main orchestration pipeline

data/
  county_configs/         # County configuration files (JSON)
  output/                 # Output case files and reports

tests/
  test_*.py               # Unit tests

requirements.txt          # Python dependencies
```

## Installation

### Prerequisites

- Python 3.10+
- OpenAI API key (for GPT-4 Vision)
- Optionally: Browserless.io or ScrapingBee account (for anti-bot)

### Setup

```bash
# Clone repository
cd Scrapper

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install

# Set up environment variables
export OPENAI_API_KEY="your-key-here"
```

## Configuration

### County Setup

Create a county configuration file in `data/county_configs/`:

```json
{
  "county_name": "Jackson",
  "state": "MS",
  "website_url": "https://www.co.jackson.ms.us/",
  "site_type": "recorder",
  "search_url": "https://www.co.jackson.ms.us/deed/search",
  "document_types": ["substitute_trustee", "deed_of_trust"],
  "search_fields": {
    "document_type": "#docType",
    "name": "#partyName",
    "date_from": "#startDate"
  },
  "is_active": true
}
```

### Environment Variables

```bash
OPENAI_API_KEY=sk-...              # OpenAI API key
BROWSERLESS_API_KEY=...            # Optional: Browserless.io key
SCRAPINGBEE_API_KEY=...            # Optional: ScrapingBee key
```

## Usage

### Run Full Pipeline

```bash
python -m src.main
```

This will:
1. Search for Substitute Trustee documents from the last 30 days
2. Extract data from document screenshots
3. Calculate deal probability scores
4. Filter to high-probability deals (60%+ probability)
5. Output JSON case files

### Process Specific County

```python
import asyncio
from src.main import DealEngineScraperPipeline

async def scrape_county():
    pipeline = DealEngineScraperPipeline(
        county_name='Jackson',
        state='MS',
        data_dir='./data'
    )
    summary = await pipeline.run()
    print(summary)

asyncio.run(scrape_county())
```

### Calculate Deal Probability

```python
from src.schemas.case_file import CaseFile
from src.probability.engine import calculate_deal_probability

# Create case file with data
case = CaseFile()
case.property.county = "Jackson"
case.property.address.street = "123 Main St"
# ... populate other fields

# Calculate probability
summary = calculate_deal_probability(case)
print(f"Deal Probability: {summary['deal_probability_percent']}%")
print(f"Quality: {summary['deal_quality']}")
```

## Scraper Workflow

### 1. Document Search (Last 30 Days)

The scraper searches for:
- **Document Type**: Substitute Trustee (Trust Book - NOT Deed Book)
- **Time Period**: Last 30 days
- **Result**: List of borrower names, property addresses, filing dates

### 2. Data Extraction

For each document:
1. **Navigate** to document via recorded button clicks
2. **Screenshot** all pages of the document
3. **Vision API** extracts:
   - Borrower name
   - Property address
   - Original loan date (CRITICAL for equity calc)
   - Legal description
   - Loan principal & interest rate
   - Deed of Trust references

### 3. Probability Calculation

Weighted factors:
- **Equity %** (25%) - Key driver: 50%+ equity = good deal
- **Timeline Pressure** (20%) - Days until auction
- **Debt to ARV Ratio** (15%) - Profit margin potential
- **Repair Magnitude** (12%) - Estimated repair costs
- **Probate Complexity** (10%) - Estate/heir issues
- **Senior Delinquency** (8%) - Senior + unpaid taxes
- **Title Complexity** (10%) - Multiple loans/liens

### 4. Output

```json
{
  "property": {
    "address": {
      "street": "123 Main St",
      "city": "Jackson",
      "state": "MS",
      "zip": "39201"
    },
    "county": "Jackson",
    "legalDescription": "..."
  },
  "owner": {
    "name": "John Smith",
    "phone": "(601) 555-1234",
    "email": "john@example.com"
  },
  "numbers": {
    "estimatedDebt": 175000,
    "estimatedEquity": 175000,
    "equityPercent": 50.0,
    "arvDollars": 350000
  },
  "deal": {
    "assignmentFee": 10000,
    "offerPriceToSeller": 280000,
    "estimatedInvestorProfitHighEnd": 35000
  }
}
```

## Data Extraction Rules (Golden Rules)

From briefing document Section 4.1:

1. **Search Last 30 Days** for Substitute Trustee in Trust Book (NOT Deed Book)
2. **Critical Data Point**: Original Deed of Trust date determines if property has equity
3. **Equity Filter**: Only pursue deals with 50%+ equity (40% = bad deal)
4. **Required Fields** (MVP):
   - Property address (street, city, state, zip)
   - Owner name & contact
   - Deed of Trust data (date, principal, rate, term)
   - Estimated debt & equity calculations

## Testing

```bash
# Run tests
pytest tests/

# Run with coverage
pytest --cov=src tests/
```

## API Integration

### OpenAI Vision API

The system uses GPT-4 Vision (`gpt-4o` model) for document analysis:

```python
from src.extractors.vision_extractor import VisionExtractor

extractor = VisionExtractor()
data = extractor.extract_from_screenshot(
    image=screenshot_bytes,
    document_type='substitute_trustee',
    field_hints={'county': 'Jackson'}
)
```

**Features**:
- Handles multiple page documents
- Cross-references data across pages
- 85%+ confidence threshold
- Type validation and format conversion

## Anti-Bot Detection

The scraper includes stealth measures:

- **User Agent Rotation**: Randomized realistic user agents
- **Request Headers**: Proper Accept, Referer, etc.
- **JavaScript Rendering**: Full DOM execution via Playwright
- **Proxy Support**: Browserless.io and ScrapingBee integration
- **Rate Limiting**: Configurable delays between requests
- **Session Management**: Persistent cookies and context

## Extending to New Counties

### 1. Research County Site

```bash
# Google search format: "[County Name] land records property search"
# Example: "Jackson county land records property search"
```

### 2. Check Site Capabilities

- Does it have searchable records?
- Is there a payment wall?
- What document types are available?

### 3. Create Configuration

```python
from src.counties.config_manager import CountyConfigManager

manager = CountyConfigManager()
manager.create_config(
    county_name='Forrest',
    state='MS',
    website_url='https://www.co.forrest.ms.us/',
    site_type='recorder',
    search_url='https://www.co.forrest.ms.us/land-records'
)
```

### 4. Record Button Map

```python
# Manual navigation with button recording
# Playwright codegen records all button clicks
```

## Performance & Scaling

- **Single County**: ~5-10 minutes per 30 documents
- **Multi-County**: Async processing for parallel scraping
- **Rate Limiting**: Configurable delays prevent blocking
- **Screenshot Size**: ~50KB per page (100+ documents = ~5MB)

## Known Limitations

1. Some county sites have payment gates (e.g., Forrest County, MS)
2. Older counties may not have digitized records
3. OCR accuracy depends on document quality
4. Some fields may require manual deed book lookup

## Future Enhancements

- [ ] UI Map rendering (Apple Maps style with probability pins)
- [ ] Route optimization for agent calling routes
- [ ] Daily call list generation with scripts
- [ ] Automated probability fine-tuning via ML
- [ ] Mobile app for field work
- [ ] Integration with CRM systems
- [ ] Automated lender contact database

## Contributing

Contributions welcome! Areas to help:

- Add new county configurations
- Improve vision API extraction prompts
- Add additional probability factors
- Build county-specific scrapers
- Create UI/mapping layer
- Optimize anti-bot detection

## License

[Your License]

## Support

For issues, questions, or feature requests, please open an issue or contact the team.

---

**Deal Engine Scraper v0.1** - Built to turn real estate uncertainty into statistically inevitable outcomes.
