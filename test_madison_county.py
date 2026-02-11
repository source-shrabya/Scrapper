"""
Madison County, MS Scraper Test
Demonstrates scraping and probability calculation for Madison County deals
"""

import asyncio
import json
from datetime import datetime, timedelta

from src.schemas.case_file import CaseFile, DeedOfTrust
from src.probability.engine import calculate_deal_probability
from src.counties.config_manager import CountyConfigManager


async def test_madison_county():
    """Test Madison County scraper with sample data"""
    
    print("\n" + "="*70)
    print("MADISON COUNTY, MS - DEAL FINDER TEST")
    print("="*70)
    
    # Create Madison County configuration
    manager = CountyConfigManager('./data/county_configs')
    
    config = manager.create_config(
        county_name='Madison',
        state='MS',
        website_url='https://www.co.madison.ms.us/',
        site_type='recorder',
        search_url='https://www.co.madison.ms.us/deed-search',
        document_types=['substitute_trustee', 'deed_of_trust'],
        search_fields={
            'document_type': '#doc-type-select',
            'book': '#book-select',
            'date_from': '#date-from',
            'date_to': '#date-to',
        },
        pagination_selector='.pagination',
        next_page_selector='.next-page',
        is_active=True,
        notes='Madison County property records - active configuration'
    )
    
    print(f"\n✓ Created configuration for Madison County, MS")
    print(f"  Website: {config.website_url}")
    print(f"  Search URL: {config.search_url}")
    
    # Create sample deals found in Madison County
    sample_deals = [
        {
            'document_id': 'MC-2026-0001',
            'borrower': 'James Patterson',
            'address': '456 Ridgetop Road, Madison, MS 39110',
            'loan_date': '2008-06-15',
            'loan_principal': 320000,
            'interest_rate': 5.2,
            'term_months': 360,
            'property_value': 450000,
            'filing_date': '2026-02-05',
        },
        {
            'document_id': 'MC-2026-0002',
            'borrower': 'Sarah Mitchell',
            'address': '789 Meadowbrook Lane, Madison, MS 39110',
            'loan_date': '2009-03-22',
            'loan_principal': 280000,
            'interest_rate': 4.8,
            'term_months': 360,
            'property_value': 400000,
            'filing_date': '2026-02-08',
        },
        {
            'document_id': 'MC-2026-0003',
            'borrower': 'Michael Johnson',
            'address': '321 Oakwood Drive, Madison, MS 39110',
            'loan_date': '2007-11-10',
            'loan_principal': 250000,
            'interest_rate': 6.5,
            'term_months': 360,
            'property_value': 380000,
            'filing_date': '2026-02-10',
        },
    ]
    
    print(f"\n✓ Found {len(sample_deals)} Substitute Trustee documents from last 30 days")
    
    # Process each deal
    results = []
    
    for deal in sample_deals:
        print(f"\n{'-'*70}")
        print(f"Processing: {deal['document_id']} - {deal['borrower']}")
        print(f"Address: {deal['address']}")
        
        # Create case file
        case = CaseFile()
        
        # Property info
        case.property.county = 'Madison'
        case.property.address.state = 'MS'
        address_parts = deal['address'].split(',')
        case.property.address.street = address_parts[0].strip()
        case.property.address.city = address_parts[1].strip() if len(address_parts) > 1 else 'Madison'
        case.property.address.zip = address_parts[2].strip() if len(address_parts) > 2 else '39110'
        
        # Owner info
        case.owner.name = deal['borrower']
        
        # Loan data
        case.loan.deedsOfTrust = [
            DeedOfTrust(
                notePrincipal=deal['loan_principal'],
                originalDate=deal['loan_date'],
                interestRate=deal['interest_rate'],
                termMonths=deal['term_months']
            )
        ]
        
        # Valuation
        case.numbers.arvDollars = deal['property_value']
        
        # Calculate debt (roughly 60% paid down after ~15-18 years)
        years_elapsed = (datetime.now().date() - datetime.strptime(deal['loan_date'], '%Y-%m-%d').date()).days / 365.25
        payment_ratio = min(0.7, 0.03 * years_elapsed)  # ~3% per year, max 70%
        case.numbers.estimatedDebt = deal['loan_principal'] * (1 - payment_ratio)
        case.numbers.estimatedEquity = case.numbers.arvDollars - case.numbers.estimatedDebt
        case.numbers.equityPercent = (case.numbers.estimatedEquity / case.numbers.arvDollars) * 100
        
        # Auction date (10-30 days from filing)
        auction_days = 15 + (hash(deal['document_id']) % 15)
        filing_date = datetime.strptime(deal['filing_date'], '%Y-%m-%d')
        case.foreclosure.auctionDate = (filing_date + timedelta(days=auction_days)).strftime('%Y-%m-%d')
        
        # Calculate deal probability
        summary = calculate_deal_probability(case)
        
        # Display results
        print(f"\n  Financial Metrics:")
        print(f"    Property Value (ARV): ${case.numbers.arvDollars:,.0f}")
        print(f"    Original Loan: ${deal['loan_principal']:,.0f}")
        print(f"    Estimated Debt: ${case.numbers.estimatedDebt:,.0f}")
        print(f"    Owner Equity: ${case.numbers.estimatedEquity:,.0f} ({case.numbers.equityPercent:.1f}%)")
        print(f"    Days to Auction: {(datetime.strptime(case.foreclosure.auctionDate, '%Y-%m-%d').date() - datetime.now().date()).days}")
        
        print(f"\n  Deal Probability: {summary['deal_probability_percent']:.1f}%")
        print(f"  Quality: {summary['deal_quality']}")
        
        print(f"\n  Top Factors:")
        for i, factor in enumerate(summary['top_factors'], 1):
            print(f"    {i}. {factor['name']}: {factor['explanation']}")
        
        results.append({
            'document_id': deal['document_id'],
            'borrower': deal['borrower'],
            'address': deal['address'],
            'probability': summary['deal_probability_percent'],
            'equity_percent': case.numbers.equityPercent,
            'equity_dollars': case.numbers.estimatedEquity,
            'quality': summary['deal_quality'],
        })
    
    # Summary report
    print(f"\n\n" + "="*70)
    print("MADISON COUNTY SUMMARY REPORT")
    print("="*70)
    
    # Sort by probability
    sorted_results = sorted(results, key=lambda x: x['probability'], reverse=True)
    
    print(f"\n{'Rank':<6} {'Probability':<15} {'Equity %':<12} {'Borrower':<20} {'Quality'}")
    print("-"*80)
    
    for i, deal in enumerate(sorted_results, 1):
        print(f"{i:<6} {deal['probability']:.1f}%{'':<9} {deal['equity_percent']:.1f}%{'':<7} {deal['borrower']:<20} {deal['quality']}")
    
    # Summary stats
    high_prob = len([r for r in results if r['probability'] >= 70])
    medium_prob = len([r for r in results if 50 <= r['probability'] < 70])
    low_prob = len([r for r in results if r['probability'] < 50])
    
    print(f"\nResults Summary:")
    print(f"  Total Documents Found: {len(results)}")
    print(f"  High Probability (70%+): {high_prob}")
    print(f"  Medium Probability (50-70%): {medium_prob}")
    print(f"  Low Probability (<50%): {low_prob}")
    
    total_equity = sum([r['equity_dollars'] for r in results])
    print(f"  Total Equity in All Properties: ${total_equity:,.0f}")
    
    print(f"\n✓ Test Complete!")
    print(f"  Configuration saved to: data/county_configs/madison_ms.json")
    
    return results


if __name__ == '__main__':
    results = asyncio.run(test_madison_county())
