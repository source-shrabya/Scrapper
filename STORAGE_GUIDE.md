# Deal Storage System - Complete Implementation

## Overview

Yes! Your deals are now **automatically stored** whenever you run analysis. Here's what was added:

## Storage Architecture

```
/data/deals/
├── cases/                          # Individual deal JSON files
│   ├── Madison_Robert_Williams_*.json
│   ├── Madison_Judith_Anderson_*.json
│   └── Madison_Kenneth_Brown_*.json
└── index/                          # Searchable index files
    └── Madison_MS_index.json       # Fast lookup by county
```

## Features

### 1. **Automatic Deal Persistence**
When you run `analyze_real_deals.py`:
- Deals are automatically saved to `./data/deals/cases/` as JSON files
- County index updated automatically in `./data/deals/index/`
- Timestamp included in filename for versioning

### 2. **Query Tools**
```bash
# Show storage statistics
python query_deals.py

# List all deals in table format
python query_deals.py list

# List deals for specific county
python query_deals.py county MADISON MS

# Export all deals to CSV
python query_deals.py export
```

### 3. **Programmatic Access**
```python
from src.storage.deal_storage import DealStorage

storage = DealStorage()

# Get all deals for a county
deals = storage.get_deals_by_county('Madison', 'MS')

# Get only high-probability deals
high_prob = storage.get_high_probability_deals(min_probability=70)

# Get statistics
stats = storage.get_statistics()
print(f"Total equity: ${stats['total_equity']:,}")
```

## Current Storage Status

✓ **3 Deals Stored** from Madison County, MS
- Robert Williams: 77.6% probability, $305,166 equity
- Judith Anderson: 73.0% probability, $325,573 equity  
- Kenneth Brown: 72.8% probability, $225,004 equity

**Total Equity Identified: $855,743**

## File Locations

| Type | Location |
|------|----------|
| **Raw Case Files** | `./data/deals/cases/*.json` |
| **County Index** | `./data/deals/index/*_index.json` |
| **CSV Export** | `./data/deals/export_all_deals.csv` |
| **Storage Module** | `./src/storage/deal_storage.py` |
| **Query Tool** | `./query_deals.py` |

## What Gets Stored in Each Deal File

Each JSON file contains the complete `CaseFile` object:

```json
{
  "conclusion": "Deal Probability: 77.6%",
  "property": {
    "address": { "street", "city", "state", "zip" },
    "county": "Madison",
    "beds": null,
    "baths": null,
    ...
  },
  "owner": { "name", "phone", "email", ... },
  "loan": { "deedsOfTrust": [...] },
  "numbers": {
    "estimatedEquity": 305166,
    "equityPercent": 72.7,
    "estimatedDebt": 114834,
    "arvDollars": 420000
  },
  "foreclosure": {
    "auctionDate": "2026-02-16",
    ...
  },
  ... (60+ more fields)
}
```

## How to Use the Storage System

### Scenario 1: Run Analysis & Auto-Save
```bash
python analyze_real_deals.py
# Deals automatically saved to ./data/deals/
```

### Scenario 2: Query Saved Deals
```bash
# See all stored deals
python query_deals.py list

# Get stats
python query_deals.py

# Export for email/spreadsheet
python query_deals.py export
# Creates ./data/deals/export_all_deals.csv
```

### Scenario 3: Access Deals in Python
```python
from src.storage.deal_storage import DealStorage

storage = DealStorage()

# Get all Madison County deals
deals = storage.get_deals_by_county('Madison', 'MS')

for deal in deals:
    print(f"{deal['case']['owner']['name']}: {deal['probability']:.1f}%")
```

### Scenario 4: Automated Daily Runs
```python
from src.storage.deal_storage import DealStorage, store_analyzed_deals

# After scraping new deals
results = [list of analyzed deals]
store_analyzed_deals(results, county='Madison', state='MS')

# Check what was stored
storage = DealStorage()
stats = storage.get_statistics()
print(f"Total deals: {stats['total_deals']}")
```

## What Happens When You Run analyze_real_deals.py?

1. ✓ Analyzes 3 Madison County deals
2. ✓ Calculates probabilities and equity
3. ✓ **Saves each deal as JSON file**
4. ✓ **Updates county index**
5. ✓ Prints summary report
6. ✓ Prints storage statistics

## Next Steps

1. **Expand to More Counties**: Create scrapers for Hinds, Rankin, DeSoto counties
2. **Integrate Vision API**: Extract real documents → auto-populate case files
3. **Set Up Automation**: Daily 3am runs to scrape new foreclosures
4. **Build Dashboard**: Query storage and display deals on map
5. **Export Integration**: Email agent lists, sync to CRM, etc.

## Key Files Added/Modified

```
✓ src/storage/deal_storage.py  - Storage engine with query methods
✓ query_deals.py               - CLI tool for querying deals
✓ analyze_real_deals.py        - Updated to auto-save deals
```

## Database Schema (Index File)

Each county has an index file that tracks all deals:

```json
{
  "deals": [
    {
      "document_id": "Robert_Williams_20260210",
      "filepath": "./data/deals/cases/Madison_Robert_Williams_*.json",
      "probability": 77.6,
      "saved_at": "2026-02-10T19:49:02.123456"
    },
    ...
  ]
}
```

This enables fast queries without loading all JSON files.
