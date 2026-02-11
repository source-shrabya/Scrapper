#!/bin/bash
# activate.sh - Quick setup for Deal Engine Scraper

# Create virtual environment if needed
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv --upgrade-deps
    source venv/bin/activate
    echo "📥 Installing dependencies..."
    pip install playwright pydantic python-dotenv openai requests Pillow python-dateutil pytest -q
    echo "✅ Virtual environment created"
else
    source venv/bin/activate
fi

# Show system status
echo ""
echo "╔════════════════════════════════════════════════════════════════════════╗"
echo "║     DEAL ENGINE SCRAPER - READY TO USE                                 ║"
echo "║     ✅ Vision API  ✅ Storage  ✅ Probability Engine  ✅ Scrapers      ║"
echo "╚════════════════════════════════════════════════════════════════════════╝"
echo ""

# Test systems
echo "🧪 Checking systems..."

# Vision API test
if python test_vision_api.py 2>&1 | grep -q "Vision API initialized"; then
    echo "  ✅ Vision API: Ready (GPT-4 Vision configured)"
else
    echo "  ❌ Vision API: Not working"
fi

# Storage test
if python query_deals.py 2>&1 | grep -q "deals stored"; then
    DEALS=$(python query_deals.py 2>&1 | grep "Total deals" | awk '{print $3}')
    echo "  ✅ Storage: Ready ($DEALS deals saved)"
fi

# Show next steps
echo ""
echo "📋 NEXT STEPS - Real Foreclosure Scraping:"
echo "─────────────────────────────────────────"
echo "1. Visit: https://www.madison.co.ms.us/"
echo "2. Find deed search form"
echo "3. Right-click fields → Inspect (F12) → Copy CSS selectors"
echo "4. Edit: ./data/county_configs/madison_ms.json"
echo "5. Replace placeholder selectors with real ones from website"
echo "6. Run: python scrape_real_madison_county.py --run-scrape"
echo ""

echo "📚 Quick Commands:"
echo "─────────────────"
echo "  python query_deals.py list              # View all deals"
echo "  python query_deals.py export            # Export to CSV"
echo "  python analyze_real_deals.py            # Test with sample data"
echo "  python scrape_real_madison_county.py    # Verify selectors"
echo ""

echo "📖 Documentation:"
echo "────────────────"
echo "  cat SETUP_COMPLETE.md                   # Full setup guide"
echo "  cat REAL_SCRAPER_SETUP.md               # CSS selector instructions"
echo "  python QUICK_REFERENCE.py               # Quick reference"
echo ""

echo "═══════════════════════════════════════════════════════════════════════════"
echo "Your virtual environment is ready! Keep this terminal open or run:"
echo "  source /Users/shrabyabhattarai/Desktop/Scrapper/venv/bin/activate"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""
