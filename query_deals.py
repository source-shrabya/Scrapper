#!/usr/bin/env python
"""
Deal Query & Export Utility
Query stored deals and export to various formats
"""

import json
import csv
from typing import List
from src.storage.deal_storage import DealStorage


def export_deals_to_csv(filename: str = './data/deals/export_all_deals.csv'):
    """Export all stored deals to CSV"""
    storage = DealStorage()
    
    # Get all high-probability deals
    deals = storage.get_high_probability_deals(min_probability=0)  # Get all
    
    if not deals:
        print("No deals found!")
        return
    
    # Prepare CSV headers
    headers = [
        'Borrower',
        'Address',
        'City',
        'State',
        'County',
        'Probability %',
        'Equity $',
        'Equity %',
        'ARV $',
        'Estimated Debt $',
        'Days to Auction',
        'Source'
    ]
    
    rows = []
    for deal in deals:
        case = deal['case']
        
        # Calculate days to auction
        from datetime import datetime
        try:
            days = (datetime.strptime(case['foreclosure']['auctionDate'], '%Y-%m-%d').date() - datetime.now().date()).days
        except:
            days = 'N/A'
        
        row = [
            case.get('owner', {}).get('name', 'Unknown'),
            case.get('property', {}).get('address', {}).get('street', ''),
            case.get('property', {}).get('address', {}).get('city', ''),
            case.get('property', {}).get('address', {}).get('state', ''),
            deal.get('source_file', '').replace('_index.json', ''),
            f"{deal['probability']:.1f}",
            f"{case.get('numbers', {}).get('estimatedEquity', 0):.0f}",
            f"{case.get('numbers', {}).get('equityPercent', 0):.1f}",
            f"{case.get('numbers', {}).get('arvDollars', 0):.0f}",
            f"{case.get('numbers', {}).get('estimatedDebt', 0):.0f}",
            str(days),
            deal['document_id'],
        ]
        rows.append(row)
    
    # Write CSV
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)
    
    print(f"✓ Exported {len(deals)} deals to {filename}")


def list_all_deals():
    """List all stored deals"""
    storage = DealStorage()
    deals = storage.get_high_probability_deals(min_probability=0)
    
    if not deals:
        print("No deals found!")
        return
    
    print("\n" + "="*100)
    print("ALL STORED DEALS")
    print("="*100)
    print(f"{'Prob':<6}{'Equity %':<10}{'Equity $':<15}{'Borrower':<25}{'Address':<35}{'County'}")
    print("-"*100)
    
    for deal in sorted(deals, key=lambda x: x['probability'], reverse=True):
        case = deal['case']
        borrower = case.get('owner', {}).get('name', 'Unknown')[:25]
        address = case.get('property', {}).get('address', {}).get('street', 'Unknown')[:35]
        county = deal.get('source_file', '').replace('_index.json', '')
        
        print(f"{deal['probability']:<6.1f}{case.get('numbers', {}).get('equityPercent', 0):<10.1f}"
              f"${case.get('numbers', {}).get('estimatedEquity', 0):<14,.0f}{borrower:<25}{address:<35}{county}")
    
    print("="*100 + "\n")


def list_county_deals(county: str, state: str):
    """List deals for a specific county"""
    storage = DealStorage()
    deals = storage.get_deals_by_county(county, state)
    
    if not deals:
        print(f"No deals found for {county}, {state}")
        return
    
    print(f"\n{county}, {state} - {len(deals)} deals stored")
    for deal in sorted(deals, key=lambda x: x['probability'], reverse=True):
        case = deal['case']
        borrower = case.get('owner', {}).get('name', 'Unknown')
        equity = case.get('numbers', {}).get('estimatedEquity', 0)
        prob = deal['probability']
        print(f"  • {borrower:<30} {prob:>6.1f}% prob  ${equity:>12,.0f} equity")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'export':
            export_deals_to_csv()
        elif sys.argv[1] == 'list':
            list_all_deals()
        elif sys.argv[1] == 'county' and len(sys.argv) >= 4:
            list_county_deals(sys.argv[2], sys.argv[3])
        else:
            print("Usage:")
            print("  python query_deals.py list                    # List all deals")
            print("  python query_deals.py county MADISON MS        # List county deals")
            print("  python query_deals.py export                  # Export to CSV")
    else:
        # Default: show stats
        storage = DealStorage()
        print("\nDeal Storage Status:")
        stats = storage.get_statistics()
        print(f"  Total deals stored: {stats['total_deals']}")
        print(f"  High probability (70%+): {stats['high_probability_deals']}")
        print(f"  Average probability: {stats['average_probability']:.1f}%")
        print(f"  Total equity: ${stats['total_equity']:,.0f}")
        print(f"\nRun 'python query_deals.py list' to see all deals")
