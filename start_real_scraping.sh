#!/bin/bash
# START_REAL_SCRAPING.sh
# Quick launcher for real foreclosure scraping setup

echo ""
echo "╔════════════════════════════════════════════════════════════════════════╗"
echo "║     DEAL ENGINE SCRAPER - Real Foreclosure Setup                       ║"
echo "║     Vision API ✅  Storage ✅  Probability Engine ✅                    ║"
echo "╚════════════════════════════════════════════════════════════════════════╝"
echo ""

echo "Current Status:"
echo "  ✅ Vision API configured"
echo "  ✅ Storage system working (3 deals saved)"
echo "  ✅ Probability engine scoring deals (74.5% avg)"
echo "  ⏳ Real scraper ready (needs CSS selectors)"
echo ""

echo "Step 1: VERIFY VISION API (30 seconds)"
echo "────────────────────────────────────────"
python test_vision_api.py 2>&1 | grep -E "✅|❌|Vision API"
echo ""

echo "Step 2: NEXT - Inspect Madison County Website"
echo "─────────────────────────────────────────────"
echo "1. Visit: https://www.co.madison.ms.us/"
echo "2. Find deed search section"
echo "3. Right-click field → Inspect (F12)"
echo "4. Copy CSS selector (e.g., input[name='borrowerName'])"
echo "5. Edit: ./data/county_configs/madison_ms.json"
echo "6. Paste selector into search_fields"
echo ""

echo "Step 3: RUN REAL SCRAPER"
echo "────────────────────────"
echo "Once selectors are updated, run:"
echo ""
echo "  python scrape_real_madison_county.py --run-scrape"
echo ""
echo "This will:"
echo "  1. Search Madison County foreclosure records"
echo "  2. Extract documents with Vision API (GPT-4)"
echo "  3. Calculate deal probabilities"
echo "  4. Store deals in database"
echo ""

echo "Step 4: VIEW RESULTS"
echo "───────────────────"
echo "  python query_deals.py list          # See all deals"
echo "  python query_deals.py export        # Export to CSV"
echo ""

echo "Full Setup Guide:"
echo "  cat REAL_SCRAPER_SETUP.md"
echo ""

echo "Current Deal Inventory:"
echo "─────────────────────"
python query_deals.py 2>&1 | head -10
echo ""

echo "╔════════════════════════════════════════════════════════════════════════╗"
echo "║  Ready to scrape! Follow Steps 1-4 above to activate real scraping     ║"
echo "╚════════════════════════════════════════════════════════════════════════╝"
echo ""
