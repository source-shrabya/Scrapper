"""
Real Madison County, MS Data Analysis
Demonstrates how to work with real county data
"""

import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict

from src.schemas.case_file import CaseFile, DeedOfTrust
from src.probability.engine import calculate_deal_probability
from src.storage.deal_storage import DealStorage, print_storage_report

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def analyze_real_deal(borrower_name: str, address: str, original_loan_date: str, 
                      original_principal: float, interest_rate: float, 
                      property_value: float, filing_date: str) -> Dict:
    """
    Analyze a single real deal from Madison County
    """
    
    case = CaseFile()
    
    # Property info
    case.property.county = 'Madison'
    case.property.address.state = 'MS'
    
    # Parse address
    parts = address.split(',')
    if len(parts) >= 2:
        case.property.address.street = parts[0].strip()
        case.property.address.city = 'Madison'
        case.property.address.zip = parts[1].strip()
    
    # Owner
    case.owner.name = borrower_name
    
    # Loan data
    case.loan.deedsOfTrust = [
        DeedOfTrust(
            notePrincipal=original_principal,
            originalDate=original_loan_date,
            interestRate=interest_rate,
            termMonths=360  # 30-year mortgage
        )
    ]
    
    # Valuation
    case.numbers.arvDollars = property_value
    
    # Calculate remaining debt
    try:
        loan_date = datetime.strptime(original_loan_date, '%Y-%m-%d').date()
        years_elapsed = (datetime.now().date() - loan_date).days / 365.25
        
        # Estimate principal paydown (roughly 3% per year, capped at 70%)
        paydown_ratio = min(0.70, max(0.05, 0.03 * years_elapsed))
        case.numbers.estimatedDebt = original_principal * (1 - paydown_ratio)
    except:
        case.numbers.estimatedDebt = original_principal * 0.6
    
    case.numbers.estimatedEquity = case.numbers.arvDollars - case.numbers.estimatedDebt
    case.numbers.equityPercent = (case.numbers.estimatedEquity / case.numbers.arvDollars) * 100
    
    # Auction date (estimate: 10-25 days from filing)
    try:
        filing = datetime.strptime(filing_date, '%Y-%m-%d').date()
        auction_days = 15  # Typical timeline
        case.foreclosure.auctionDate = (filing + timedelta(days=auction_days)).strftime('%Y-%m-%d')
    except:
        case.foreclosure.auctionDate = (datetime.now() + timedelta(days=15)).strftime('%Y-%m-%d')
    
    # Calculate probability
    summary = calculate_deal_probability(case)
    
    return {
        'borrower': borrower_name,
        'address': address,
        'case': case,
        'probability': summary,
    }


def main():
    """Analyze example Madison County deals"""
    
    print("\n" + "="*80)
    print("MADISON COUNTY, MS - REAL DEAL ANALYSIS")
    print("="*80)
    
    # Example deals (you would get these from actual county records)
    deals_to_analyze = [
        {
            'borrower': 'Robert Williams',
            'address': '1850 County Road 37, Madison, MS 39110',
            'loan_date': '2006-09-12',
            'principal': 275000,
            'rate': 6.75,
            'value': 420000,
            'filing_date': '2026-02-01',
        },
        {
            'borrower': 'Judith Anderson',
            'address': '2100 Ridgeway Drive, Madison, MS 39110',
            'loan_date': '2009-05-20',
            'principal': 310000,
            'rate': 5.25,
            'value': 480000,
            'filing_date': '2026-02-05',
        },
        {
            'borrower': 'Kenneth Brown',
            'address': '850 Jackson Avenue, Madison, MS 39110',
            'loan_date': '2010-03-15',
            'principal': 220000,
            'rate': 4.95,
            'value': 340000,
            'filing_date': '2026-02-08',
        },
    ]
    
    results = []
    
    print(f"\nAnalyzing {len(deals_to_analyze)} deals from Madison County...\n")
    
    for deal in deals_to_analyze:
        result = analyze_real_deal(
            borrower_name=deal['borrower'],
            address=deal['address'],
            original_loan_date=deal['loan_date'],
            original_principal=deal['principal'],
            interest_rate=deal['rate'],
            property_value=deal['value'],
            filing_date=deal['filing_date']
        )
        
        results.append(result)
        
        # Display deal analysis
        case = result['case']
        prob = result['probability']
        
        print(f"\n{'-'*80}")
        print(f"DEAL: {result['borrower']}")
        print(f"{'-'*80}")
        print(f"Address: {result['address']}")
        print(f"\nFinancial Details:")
        print(f"  Original Loan:        ${deal['principal']:>12,}  ({deal['rate']}% interest, {deal['loan_date']})")
        print(f"  Estimated Debt Today: ${case.numbers.estimatedDebt:>12,.0f}")
        print(f"  Property Value (ARV): ${case.numbers.arvDollars:>12,.0f}")
        print(f"  Owner's Equity:       ${case.numbers.estimatedEquity:>12,.0f} ({case.numbers.equityPercent:>5.1f}%)")
        print(f"  Days to Auction:      {(datetime.strptime(case.foreclosure.auctionDate, '%Y-%m-%d').date() - datetime.now().date()).days:>12}")
        
        print(f"\nProbability Analysis:")
        print(f"  Deal Probability:     {prob['deal_probability_percent']:>12.1f}%")
        print(f"  Quality Rating:       {prob['deal_quality']}")
        
        print(f"\n  Top 3 Factors:")
        for i, factor in enumerate(prob['top_factors'], 1):
            print(f"    {i}. {factor['name']:<30} {factor['probability_contribution']:>6.1f}% impact")
            print(f"       → {factor['explanation']}")
    
    # Summary Report
    print(f"\n\n" + "="*80)
    print("MADISON COUNTY SUMMARY")
    print("="*80)
    
    sorted_results = sorted(
        results,
        key=lambda x: x['probability']['deal_probability_percent'],
        reverse=True
    )
    
    print(f"\n{'Rank':<6}{'Probability':<15}{'Equity %':<12}{'Borrower':<25}{'Quality'}")
    print("-"*80)
    
    for i, result in enumerate(sorted_results, 1):
        case = result['case']
        prob = result['probability']
        print(f"{i:<6}{prob['deal_probability_percent']:.1f}%{'':<9}{case.numbers.equityPercent:.1f}%{'':<7}{result['borrower']:<25}{prob['deal_quality'][:40]}")
    
    # Statistics
    total_equity = sum([r['case'].numbers.estimatedEquity for r in results])
    avg_probability = sum([r['probability']['deal_probability_percent'] for r in results]) / len(results)
    high_prob = len([r for r in results if r['probability']['deal_probability_percent'] >= 70])
    
    # Save deals to storage
    storage = DealStorage()
    stored_count = 0
    for result in results:
        case = result['case']
        doc_id = f"{result['borrower'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}"
        filepath = storage.save_deal(
            case=case,
            county='Madison',
            state='MS',
            document_id=doc_id,
            probability=result['probability']['deal_probability_percent']
        )
        if filepath:
            stored_count += 1
    
    logger.info(f"Saved {stored_count} deals to storage")
    
    print(f"\nStatistics:")
    print(f"  Total Deals Analyzed:    {len(results)}")
    print(f"  Deals Saved to Storage:  {stored_count}")
    print(f"  High Probability (70%+): {high_prob}")
    print(f"  Average Probability:     {avg_probability:.1f}%")
    print(f"  Total Equity:            ${total_equity:,.0f}")
    
    # Recommendations
    print(f"\nRecommendations:")
    if high_prob > 0:
        print(f"  ✓ {high_prob} deal(s) with 70%+ probability - ready to contact borrowers")
    else:
        print(f"  → Most deals need auction timeline for closing pressure")
    
    print(f"  → Focus on deals with 50%+ equity")
    print(f"  → Prioritize deals within 2 weeks of auction date")
    
    # Next steps
    print(f"\nNext Steps:")
    print(f"  1. Verify these deals exist in actual Madison County records")
    print(f"  2. Update county website selectors in madison_ms.json")
    print(f"  3. Implement full scraper with Vision API extraction")
    print(f"  4. Set up automated daily runs")
    print(f"  5. Create agent contact list with top deals")
    
    # Show storage report
    print(f"\n" + "="*80)
    print_storage_report()
    
    print(f"\n" + "="*80)


if __name__ == '__main__':
    main()
