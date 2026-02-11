"""
Deal Storage & Database
Saves deals to JSON files and provides query/retrieval functions
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional
import logging

from src.schemas.case_file import CaseFile

logger = logging.getLogger(__name__)


class DealStorage:
    """Store and retrieve deals"""
    
    def __init__(self, storage_dir: str = './data/deals'):
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
        
        # Create subdirectories
        self.deals_dir = os.path.join(storage_dir, 'cases')
        self.index_dir = os.path.join(storage_dir, 'index')
        
        os.makedirs(self.deals_dir, exist_ok=True)
        os.makedirs(self.index_dir, exist_ok=True)
        
        logger.info(f"DealStorage initialized: {storage_dir}")
    
    def save_deal(self, case: CaseFile, county: str, state: str, 
                  document_id: str, probability: float) -> str:
        """
        Save a deal case file
        
        Returns: path to saved file
        """
        # Create filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{county}_{document_id}_{timestamp}.json"
        filepath = os.path.join(self.deals_dir, filename)
        
        # Add probability to case
        case.conclusion = f"Deal Probability: {probability:.1f}%"
        
        # Save to file
        try:
            with open(filepath, 'w') as f:
                json.dump(case.to_json(), f, indent=2, default=str)
            
            logger.info(f"Saved deal: {filepath}")
            
            # Add to index
            self._add_to_index(county, state, document_id, filepath, probability)
            
            return filepath
        except Exception as e:
            logger.error(f"Failed to save deal: {e}")
            return None
    
    def _add_to_index(self, county: str, state: str, document_id: str, 
                      filepath: str, probability: float):
        """Add deal to searchable index"""
        index_file = os.path.join(self.index_dir, f'{county}_{state}_index.json')
        
        index = {}
        if os.path.exists(index_file):
            with open(index_file, 'r') as f:
                index = json.load(f)
        
        if 'deals' not in index:
            index['deals'] = []
        
        # Add entry
        index['deals'].append({
            'document_id': document_id,
            'filepath': filepath,
            'probability': probability,
            'saved_at': datetime.now().isoformat(),
        })
        
        # Save updated index
        with open(index_file, 'w') as f:
            json.dump(index, f, indent=2)
    
    def get_deals_by_county(self, county: str, state: str) -> List[Dict]:
        """Get all deals for a county"""
        index_file = os.path.join(self.index_dir, f'{county}_{state}_index.json')
        
        if not os.path.exists(index_file):
            logger.warning(f"No index found for {county}, {state}")
            return []
        
        try:
            with open(index_file, 'r') as f:
                index = json.load(f)
            
            deals = []
            for entry in index.get('deals', []):
                filepath = entry['filepath']
                if os.path.exists(filepath):
                    with open(filepath, 'r') as f:
                        case_data = json.load(f)
                    deals.append({
                        'document_id': entry['document_id'],
                        'probability': entry['probability'],
                        'case': case_data,
                    })
            
            return deals
        except Exception as e:
            logger.error(f"Failed to load deals: {e}")
            return []
    
    def get_high_probability_deals(self, min_probability: float = 70.0) -> List[Dict]:
        """Get all deals above probability threshold across all counties"""
        deals = []
        
        # Scan all index files
        for filename in os.listdir(self.index_dir):
            if filename.endswith('_index.json'):
                filepath = os.path.join(self.index_dir, filename)
                
                try:
                    with open(filepath, 'r') as f:
                        index = json.load(f)
                    
                    for entry in index.get('deals', []):
                        if entry['probability'] >= min_probability:
                            case_filepath = entry['filepath']
                            if os.path.exists(case_filepath):
                                with open(case_filepath, 'r') as f:
                                    case_data = json.load(f)
                                
                                deals.append({
                                    'document_id': entry['document_id'],
                                    'probability': entry['probability'],
                                    'case': case_data,
                                    'source_file': filename,
                                })
                except Exception as e:
                    logger.warning(f"Error reading {filepath}: {e}")
        
        # Sort by probability
        return sorted(deals, key=lambda x: x['probability'], reverse=True)
    
    def get_statistics(self) -> Dict:
        """Get statistics about stored deals"""
        stats = {
            'total_deals': 0,
            'high_probability_deals': 0,
            'total_equity': 0,
            'average_probability': 0,
            'counties': {},
        }
        
        all_deals = []
        
        # Scan all index files
        for filename in os.listdir(self.index_dir):
            if filename.endswith('_index.json'):
                filepath = os.path.join(self.index_dir, filename)
                
                try:
                    with open(filepath, 'r') as f:
                        index = json.load(f)
                    
                    county_key = filename.replace('_index.json', '')
                    stats['counties'][county_key] = {
                        'count': 0,
                        'high_prob_count': 0,
                        'total_equity': 0,
                    }
                    
                    for entry in index.get('deals', []):
                        stats['total_deals'] += 1
                        all_deals.append(entry['probability'])
                        stats['counties'][county_key]['count'] += 1
                        
                        if entry['probability'] >= 70:
                            stats['high_probability_deals'] += 1
                            stats['counties'][county_key]['high_prob_count'] += 1
                        
                        # Try to get equity from case file
                        if os.path.exists(entry['filepath']):
                            with open(entry['filepath'], 'r') as f:
                                case_data = json.load(f)
                                equity = case_data.get('numbers', {}).get('estimatedEquity')
                                if equity:
                                    stats['total_equity'] += equity
                                    stats['counties'][county_key]['total_equity'] += equity
                
                except Exception as e:
                    logger.warning(f"Error reading {filepath}: {e}")
        
        # Calculate average
        if all_deals:
            stats['average_probability'] = sum(all_deals) / len(all_deals)
        
        return stats


def store_analyzed_deals(deals: List[Dict], county: str, state: str):
    """
    Save analyzed deals to storage
    
    Args:
        deals: List of analyzed deal results from analyze_real_deals.py
        county: County name
        state: State code
    """
    storage = DealStorage()
    
    stored_count = 0
    for deal in deals:
        if 'case' in deal and 'probability' in deal:
            case = deal['case']
            # Create document ID from borrower name and timestamp
            doc_id = f"{deal['borrower'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}"
            
            filepath = storage.save_deal(
                case=case,
                county=county,
                state=state,
                document_id=doc_id,
                probability=deal['probability']['deal_probability_percent']
            )
            
            if filepath:
                stored_count += 1
    
    logger.info(f"Stored {stored_count} deals for {county}, {state}")


def print_storage_report():
    """Print storage statistics"""
    storage = DealStorage()
    stats = storage.get_statistics()
    
    print("\n" + "="*70)
    print("DEAL STORAGE STATISTICS")
    print("="*70)
    
    print(f"\nTotal Deals Stored: {stats['total_deals']}")
    print(f"High Probability (70%+): {stats['high_probability_deals']}")
    print(f"Average Probability: {stats['average_probability']:.1f}%")
    print(f"Total Equity: ${stats['total_equity']:,.0f}")
    
    print(f"\nBy County:")
    for county, info in stats['counties'].items():
        print(f"  {county}: {info['count']} deals "
              f"({info['high_prob_count']} high prob) "
              f"${info['total_equity']:,.0f} equity")
    
    # Show top 5 deals
    top_deals = storage.get_high_probability_deals(min_probability=0)
    
    if top_deals:
        print(f"\nTop 5 Deals (by probability):")
        for i, deal in enumerate(top_deals[:5], 1):
            borrower = deal['case'].get('owner', {}).get('name', 'Unknown')
            print(f"  {i}. {borrower}: {deal['probability']:.1f}% probability")
