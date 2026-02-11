# Quick Start Guide

## 5-Minute Setup

### 1. Install Dependencies
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install
```

### 2. Set Up Environment
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### 3. Run Examples
```bash
python examples.py
```

## Running the Scraper

### Option A: Use Example Script
```python
python examples.py
```
Shows all features: case file creation, probability calculation, deal comparison, JSON export.

### Option B: Custom Python Script
```python
from src.schemas.case_file import CaseFile
from src.probability.engine import calculate_deal_probability

# Create case
case = CaseFile()
case.property.county = "Jackson"
case.owner.name = "John Smith"
case.numbers.arvDollars = 350000
case.numbers.estimatedEquity = 175000
case.numbers.equityPercent = 50.0

# Calculate probability
summary = calculate_deal_probability(case)
print(f"Deal Probability: {summary['deal_probability_percent']}%")
```

### Option C: Full Pipeline (Async)
```python
import asyncio
from src.main import DealEngineScraperPipeline

async def main():
    pipeline = DealEngineScraperPipeline(
        county_name='Jackson',
        state='MS'
    )
    summary = await pipeline.run()
    print(summary)

asyncio.run(main())
```

## Running Tests
```bash
pytest tests/
pytest -v  # Verbose
pytest --cov=src tests/  # With coverage
```

## File Structure

```
Scrapper/
├── src/
│   ├── schemas/          # Data models
│   │   └── case_file.py  # CaseFile schema
│   ├── scrapers/         # Web scraping
│   │   └── base_scraper.py
│   ├── extractors/       # Data extraction
│   │   └── vision_extractor.py
│   ├── probability/      # Deal probability
│   │   └── engine.py
│   ├── counties/         # County configs
│   │   └── config_manager.py
│   └── main.py           # Main pipeline
├── data/
│   ├── county_configs/   # County settings
│   └── output/           # Results (auto-created)
├── tests/
│   └── test_engine.py
├── examples.py           # Usage examples
├── requirements.txt      # Dependencies
└── README.md            # Full documentation
```

## Key Concepts

### Case File
A normalized JSON object containing ALL possible data about a property, even if some fields are null.

### Probability Engine
Calculates deal close probability (0-100%) based on:
- **Equity %** (most important - 50%+ is good)
- **Timeline pressure** (days until auction)
- **Profit margin** (debt vs property value)
- **Repair costs**
- **Probate complexity**
- And more...

### Extraction Pipeline
1. Scraper navigates to county website
2. Takes screenshots of documents
3. Sends to GPT Vision API
4. Extracts structured data
5. Populates CaseFile JSON

## Next Steps

1. **Add a County**: Create config in `data/county_configs/`
2. **Test Extraction**: Run examples.py to see probability calculation
3. **Explore API**: Check `src/extractors/vision_extractor.py` for vision model usage
4. **Build UI**: Use case file JSON to build map/dashboard
5. **Scale Out**: Add more counties, optimize scraper

## Troubleshooting

### ImportError: No module named 'src'
Make sure you're running from the Scrapper directory:
```bash
cd /path/to/Scrapper
python examples.py
```

### OpenAI API errors
Check your OPENAI_API_KEY:
```bash
echo $OPENAI_API_KEY
```

### Browser not opening
Make sure Playwright is installed:
```bash
playwright install
```

## Support & Next Steps

- Review `README.md` for full documentation
- Check `examples.py` for code samples
- Browse `tests/test_engine.py` for test patterns
- Look at `src/schemas/case_file.py` for all available fields

---

**Ready to scrape!** Start with `python examples.py` to see the system in action.
