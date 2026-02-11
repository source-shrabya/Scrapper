"""
Main Orchestration Script - Deal Engine Scraper Pipeline
Coordinates all components: scraping, extraction, probability calculation, output
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import os

from src.schemas.case_file import CaseFile
from src.probability.engine import DealProbabilityEngine
from src.extractors.vision_extractor import VisionExtractor
from src.counties.config_manager import CountyConfigManager
from src.scrapers.base_scraper import CountyScraperFactory

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DealEngineScraperPipeline:
    """
    Main pipeline for scraping, extracting, and scoring deals
    
    Workflow:
    1. Load county configuration
    2. Search for relevant documents (Substitute Trustee, last 30 days)
    3. Capture screenshots of documents
    4. Extract data using Vision API
    5. Calculate equity and deal probability
    6. Filter by deal quality
    7. Output JSON case files
    """
    
    def __init__(
        self,
        county_name: str,
        state: str,
        data_dir: str = './data',
        use_proxy: bool = False,
        proxy_url: Optional[str] = None,
    ):
        self.county_name = county_name
        self.state = state
        self.data_dir = data_dir
        self.use_proxy = use_proxy
        self.proxy_url = proxy_url
        
        # Initialize components
        self.config_manager = CountyConfigManager(f'{data_dir}/county_configs')
        self.vision_extractor = VisionExtractor()
        self.county_config = self.config_manager.get_config(county_name, state)
        
        # Output directories
        self.output_dir = os.path.join(data_dir, 'output', f'{county_name}_{state}')
        self.screenshots_dir = os.path.join(self.output_dir, 'screenshots')
        self.cases_dir = os.path.join(self.output_dir, 'cases')
        
        os.makedirs(self.screenshots_dir, exist_ok=True)
        os.makedirs(self.cases_dir, exist_ok=True)
        
        self.scraper = None
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    async def initialize(self):
        """Initialize scraper"""
        if not self.county_config:
            raise ValueError(f"No configuration found for {self.county_name}, {self.state}")
        
        # Create county-specific scraper (simplified for demo)
        # In production, would have specialized scrapers for each county site
        logger.info(f"Initializing scraper for {self.county_name}, {self.state}")
        logger.info(f"Target URL: {self.county_config.website_url}")
    
    async def search_documents(self) -> List[Dict]:
        """
        Search for Substitute Trustee documents from last 30 days
        
        Returns:
            List of document references
        """
        logger.info("Searching for documents...")
        
        # Search parameters - from briefing doc Section 4.1
        search_params = {
            'document_type': 'Substitute Trustee',
            'book': 'Trust Book',
            'date_from': (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
            'date_to': datetime.now().strftime('%Y-%m-%d'),
        }
        
        # In production, would execute actual search via scraper
        # For now, return mock results
        logger.info(f"Search parameters: {search_params}")
        
        documents = [
            {
                'document_id': 'DOC_001',
                'title': 'Substitute Trustee - Trust Book',
                'filing_date': datetime.now().strftime('%Y-%m-%d'),
                'borrower': 'John Smith',
                'property_address': '123 Main St, Jackson, MS 39201',
                'url': self.county_config.search_url,
            },
            # More documents would be found in production
        ]
        
        logger.info(f"Found {len(documents)} potential documents")
        return documents
    
    async def extract_and_score(self, documents: List[Dict]) -> List[Dict]:
        """
        Extract data from documents and calculate deal scores
        
        Args:
            documents: List of document references
        
        Returns:
            List of case files with scores
        """
        results = []
        
        for doc in documents:
            logger.info(f"Processing document: {doc['document_id']}")
            
            try:
                # Create case file
                case = CaseFile()
                
                # Set property county
                case.property.county = self.county_name
                
                # In production, would:
                # 1. Navigate to document via scraper
                # 2. Capture screenshots
                # 3. Extract data from images
                # For demo, we'll create a mock case with some data
                
                # Mock extracted data
                case.owner.name = doc.get('borrower')
                case.property.address.street = doc.get('property_address', '').split(',')[0]
                case.property.address.city = self.county_name
                case.property.address.state = self.state
                case.property.county = self.county_name
                
                # Mock loan data for probability calculation
                case.loan.deedsOfTrust = [{
                    'notePrincipal': 250000,
                    'originalDate': '2010-01-15',
                    'interestRate': 4.5,
                    'termMonths': 360,
                }]
                
                # Mock valuation
                case.numbers.arvDollars = 350000
                
                # Calculate estimated debt (simplified)
                if case.loan.deedsOfTrust:
                    dot = case.loan.deedsOfTrust[0]
                    case.numbers.estimatedDebt = dot.notePrincipal * 0.7  # Roughly 70% paid down
                    case.numbers.estimatedEquity = case.numbers.arvDollars - case.numbers.estimatedDebt
                    case.numbers.equityPercent = (case.numbers.estimatedEquity / case.numbers.arvDollars) * 100
                
                # Calculate deal probability
                engine = DealProbabilityEngine(case)
                probability_summary = engine.generate_summary()
                
                # Store probability in case notes
                case.notes.append(f"Deal Probability: {probability_summary['deal_probability_percent']}%")
                case.notes.append(f"Quality: {probability_summary['deal_quality']}")
                
                # Save case file
                case_filename = os.path.join(
                    self.cases_dir,
                    f"{doc['document_id']}_case.json"
                )
                
                with open(case_filename, 'w') as f:
                    json.dump(case.to_json(), f, indent=2, default=str)
                
                logger.info(f"Saved case file: {case_filename}")
                
                results.append({
                    'document': doc,
                    'case': case,
                    'probability': probability_summary,
                })
            
            except Exception as e:
                logger.error(f"Error processing document {doc['document_id']}: {e}")
        
        return results
    
    async def filter_deals(self, results: List[Dict], min_probability: float = 60.0) -> List[Dict]:
        """
        Filter results to high-probability deals
        
        Args:
            results: List of case results
            min_probability: Minimum deal probability percentage
        
        Returns:
            Filtered list of good deals
        """
        good_deals = [
            r for r in results
            if r['probability']['deal_probability_percent'] >= min_probability
        ]
        
        logger.info(f"Filtered {len(results)} deals down to {len(good_deals)} "
                   f"with {min_probability}%+ probability")
        
        return good_deals
    
    def generate_summary_report(self, results: List[Dict]) -> Dict:
        """
        Generate summary report of scraping run
        
        Returns:
            Summary statistics and top deals
        """
        if not results:
            return {
                'county': f"{self.county_name}, {self.state}",
                'run_date': datetime.now().isoformat(),
                'total_documents_found': 0,
                'high_probability_deals': 0,
                'deals': [],
            }
        
        # Sort by probability
        sorted_results = sorted(
            results,
            key=lambda x: x['probability']['deal_probability_percent'],
            reverse=True
        )
        
        return {
            'county': f"{self.county_name}, {self.state}",
            'run_date': datetime.now().isoformat(),
            'total_documents_found': len(results),
            'high_probability_deals': len(sorted_results),
            'deals': [
                {
                    'document_id': r['document']['document_id'],
                    'borrower': r['case'].owner.name,
                    'address': f"{r['case'].property.address.street}, {r['case'].property.address.city}",
                    'probability_percent': r['probability']['deal_probability_percent'],
                    'quality': r['probability']['deal_quality'],
                    'estimated_equity': r['case'].numbers.estimatedEquity,
                    'equity_percent': r['case'].numbers.equityPercent,
                    'top_factors': r['probability']['top_factors'],
                }
                for r in sorted_results[:10]  # Top 10 deals
            ],
        }
    
    async def run(self) -> Dict:
        """
        Execute the full scraping and analysis pipeline
        
        Returns:
            Summary report
        """
        try:
            logger.info(f"Starting pipeline for {self.county_name}, {self.state}")
            
            await self.initialize()
            
            # Step 1: Search for documents
            documents = await self.search_documents()
            
            if not documents:
                logger.warning("No documents found")
                return {'status': 'no_documents', 'county': self.county_name}
            
            # Step 2: Extract and score
            results = await self.extract_and_score(documents)
            
            # Step 3: Filter by quality
            good_deals = await self.filter_deals(results, min_probability=60.0)
            
            # Step 4: Generate report
            summary = self.generate_summary_report(good_deals)
            
            # Save summary
            summary_file = os.path.join(self.output_dir, f'summary_{self.session_id}.json')
            with open(summary_file, 'w') as f:
                json.dump(summary, f, indent=2, default=str)
            
            logger.info(f"Pipeline completed. Summary saved to {summary_file}")
            
            return summary
        
        except Exception as e:
            logger.error(f"Pipeline failed: {e}", exc_info=True)
            return {'status': 'error', 'error': str(e)}


async def main():
    """
    Demo execution of the pipeline
    """
    # Initialize pipeline for Jackson County, MS
    pipeline = DealEngineScraperPipeline(
        county_name='Jackson',
        state='MS',
        data_dir='./data',
    )
    
    # Run pipeline
    summary = await pipeline.run()
    
    # Print results
    print("\n" + "="*60)
    print("DEAL ENGINE SCRAPER - SUMMARY REPORT")
    print("="*60)
    print(json.dumps(summary, indent=2, default=str))


if __name__ == '__main__':
    asyncio.run(main())
