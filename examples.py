"""
Example usage of the Deal Engine Scraper system
Demonstrates key workflows and features
"""

import asyncio
import json
from datetime import datetime, timedelta

from src.schemas.case_file import CaseFile, DeedOfTrust
from src.probability.engine import DealProbabilityEngine, calculate_deal_probability
from src.counties.config_manager import CountyConfigManager, create_example_configs


def example_1_create_case_file():
    """Example 1: Create and populate a case file"""
    print("\n" + "="*60)
    print("EXAMPLE 1: Creating a Case File")
    print("="*60)
    
    # Create a new case file
    case = CaseFile()
    
    # Populate property information
    case.property.address.street = "123 Main Street"
    case.property.address.city = "Jackson"
    case.property.address.state = "MS"
    case.property.address.zip = "39201"
    case.property.county = "Jackson"
    case.property.legalDescription = "Lot 5, Block 2, Pleasantview Subdivision"
    case.property.beds = 3
    case.property.baths = 2
    case.property.squareFootage = 2000
    
    # Populate owner information
    case.owner.name = "John Smith"
    case.owner.phone = "(601) 555-1234"
    case.owner.email = "john@example.com"
    
    # Add loan information
    case.loan.deedsOfTrust = [
        DeedOfTrust(
            notePrincipal=250000,
            originalLender="First National Bank",
            originalDate="2010-01-15",
            interestRate=4.5,
            termMonths=360,
            maturityDate="2040-01-15"
        )
    ]
    
    # Add valuation
    case.valuation.arv = 350000
    case.valuation.arvSource = "Zillow Estimate"
    
    # Add repair estimates
    case.repairs.estimatedRepairs = 25000
    
    # Calculate financial numbers (would normally come from extraction)
    case.numbers.arvDollars = 350000
    case.numbers.estimatedDebt = 175000  # Roughly 70% paid down
    case.numbers.estimatedEquity = case.numbers.arvDollars - case.numbers.estimatedDebt
    case.numbers.equityPercent = (case.numbers.estimatedEquity / case.numbers.arvDollars) * 100
    
    # Add deal calculations
    assignment_fee = 10000
    case.deal.assignmentFee = assignment_fee
    case.deal.offerPriceToSeller = case.numbers.estimatedEquity - 10000
    case.deal.offerPricePlusAssignment = case.deal.offerPriceToSeller + assignment_fee
    case.deal.estimatedInvestorProfitHighEnd = (case.numbers.arvDollars - case.numbers.estimatedDebt - case.repairs.estimatedRepairs)
    
    # Print summary
    print(f"Created Case File:")
    print(f"  Owner: {case.owner.name}")
    print(f"  Property: {case.property.address.street}, {case.property.address.city}, {case.property.address.state}")
    print(f"  ARV: ${case.numbers.arvDollars:,.0f}")
    print(f"  Estimated Debt: ${case.numbers.estimatedDebt:,.0f}")
    print(f"  Equity: ${case.numbers.estimatedEquity:,.0f} ({case.numbers.equityPercent:.1f}%)")
    print(f"  Estimated Repairs: ${case.repairs.estimatedRepairs:,.0f}")
    
    return case


def example_2_calculate_probability(case: CaseFile):
    """Example 2: Calculate deal probability"""
    print("\n" + "="*60)
    print("EXAMPLE 2: Calculating Deal Probability")
    print("="*60)
    
    # Set auction date (creates timeline pressure)
    case.foreclosure.auctionDate = (datetime.now() + timedelta(days=10)).strftime('%Y-%m-%d')
    
    # Calculate probability
    summary = calculate_deal_probability(case)
    
    print(f"\nDeal Probability Analysis:")
    print(f"  Probability: {summary['deal_probability_percent']:.1f}%")
    print(f"  Quality: {summary['deal_quality']}")
    
    print(f"\nTop Factors:")
    for i, factor in enumerate(summary['top_factors'], 1):
        print(f"  {i}. {factor['name']}")
        print(f"     Contribution: {factor['probability_contribution']:.1f}%")
        print(f"     Details: {factor['explanation']}")
    
    print(f"\nAll Factors:")
    for name, data in summary['all_factors'].items():
        print(f"  {name.replace('_', ' ').title()}: {data['value']:.1f}% (weight: {data['weight']})")
    
    return summary


def example_3_compare_deals():
    """Example 3: Compare multiple deals"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Comparing Multiple Deals")
    print("="*60)
    
    deals = []
    
    # Deal 1: Good deal with high equity
    case1 = CaseFile()
    case1.property.address.street = "101 Oak Ave"
    case1.property.county = "Jackson"
    case1.owner.name = "Alice Johnson"
    case1.numbers.arvDollars = 300000
    case1.numbers.estimatedDebt = 120000
    case1.numbers.estimatedEquity = 180000
    case1.numbers.equityPercent = 60.0
    case1.foreclosure.auctionDate = (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d')
    
    # Deal 2: Moderate deal with medium equity
    case2 = CaseFile()
    case2.property.address.street = "202 Pine St"
    case2.property.county = "Jackson"
    case2.owner.name = "Bob Williams"
    case2.numbers.arvDollars = 250000
    case2.numbers.estimatedDebt = 150000
    case2.numbers.estimatedEquity = 100000
    case2.numbers.equityPercent = 40.0
    case2.foreclosure.auctionDate = (datetime.now() + timedelta(days=20)).strftime('%Y-%m-%d')
    
    # Deal 3: High equity but urgent timeline
    case3 = CaseFile()
    case3.property.address.street = "303 Elm Lane"
    case3.property.county = "Jackson"
    case3.owner.name = "Carol Davis"
    case3.numbers.arvDollars = 400000
    case3.numbers.estimatedDebt = 200000
    case3.numbers.estimatedEquity = 200000
    case3.numbers.equityPercent = 50.0
    case3.foreclosure.auctionDate = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    # Calculate probabilities
    for case in [case1, case2, case3]:
        summary = calculate_deal_probability(case)
        deals.append({
            'owner': case.owner.name,
            'address': case.property.address.street,
            'equity_percent': case.numbers.equityPercent,
            'probability': summary['deal_probability_percent'],
            'quality': summary['deal_quality']
        })
    
    # Sort by probability
    deals_sorted = sorted(deals, key=lambda x: x['probability'], reverse=True)
    
    print(f"\nRanked Deal Comparison:")
    print(f"{'Rank':<6} {'Probability':<15} {'Equity %':<12} {'Owner':<20} {'Quality'}")
    print("-" * 80)
    for i, deal in enumerate(deals_sorted, 1):
        print(f"{i:<6} {deal['probability']:.1f}%{'':<9} {deal['equity_percent']:.1f}%{'':<7} {deal['owner']:<20} {deal['quality']}")


def example_4_county_configuration():
    """Example 4: County configuration management"""
    print("\n" + "="*60)
    print("EXAMPLE 4: County Configuration Management")
    print("="*60)
    
    # Create example configurations
    create_example_configs('./data/county_configs')
    
    # Load configurations
    manager = CountyConfigManager('./data/county_configs')
    
    # List all counties
    counties = manager.list_counties()
    print(f"\nConfigured Counties: {len(counties)}")
    for county in counties:
        config = manager.get_config(county.split('_')[0], county.split('_')[1])
        print(f"  - {config.county_name}, {config.state}: {config.website_url}")
        print(f"    Site Type: {config.site_type}")
        print(f"    Active: {config.is_active}")


def example_5_export_to_json():
    """Example 5: Export case file to JSON"""
    print("\n" + "="*60)
    print("EXAMPLE 5: Exporting to JSON")
    print("="*60)
    
    # Create a case file
    case = example_1_create_case_file()
    
    # Export to JSON
    json_data = case.to_json()
    
    # Print (abbreviated for demo)
    print("\nCase File as JSON (sample):")
    sample = {
        'property': json_data['property'],
        'owner': json_data['owner'],
        'numbers': json_data['numbers'],
        'deal': json_data['deal'],
    }
    print(json.dumps(sample, indent=2, default=str))


def main():
    """Run all examples"""
    print("\n" + "="*70)
    print("DEAL ENGINE SCRAPER - USAGE EXAMPLES")
    print("="*70)
    
    # Example 1: Create case file
    case = example_1_create_case_file()
    
    # Example 2: Calculate probability
    example_2_calculate_probability(case)
    
    # Example 3: Compare deals
    example_3_compare_deals()
    
    # Example 4: County configuration
    example_4_county_configuration()
    
    # Example 5: Export to JSON
    example_5_export_to_json()
    
    print("\n" + "="*70)
    print("Examples completed!")
    print("="*70 + "\n")


if __name__ == '__main__':
    main()
