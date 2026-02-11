"""
Madison County, MS Property Records Scraper
Scrapes substitute trustee documents from Madison County land records website
"""

import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta

from src.scrapers.base_scraper import BaseScraper
from src.schemas.case_file import CaseFile

logger = logging.getLogger(__name__)


class MadisonCountyMSScraper(BaseScraper):
    """
    Scraper for Madison County, MS property records
    Website: https://www.co.madison.ms.us/
    
    Search path:
    1. Navigate to Property Records/Deed Search
    2. Search for Substitute Trustee documents (Trust Book)
    3. Filter by last 30 days
    4. Extract borrower name, address, loan details
    """
    
    def __init__(self, **kwargs):
        super().__init__(
            county_name='Madison',
            **kwargs
        )
        self.county_website = 'https://www.co.madison.ms.us/'
        self.search_base_url = 'https://www.co.madison.ms.us/deed-search'
    
    async def search_documents(self, search_params: Dict) -> List[Dict]:
        """
        Search for Substitute Trustee documents in Madison County
        
        Search parameters:
        - document_type: 'Substitute Trustee'
        - book: 'Trust Book'
        - date_from: last 30 days
        - date_to: today
        """
        logger.info(f"Searching Madison County for {search_params.get('document_type')} documents")
        
        try:
            # Navigate to search page
            await self.navigate_to(self.search_base_url)
            
            # Wait for search form to load
            if not await self.wait_for_element('#search-form'):
                logger.warning("Search form not found")
                return []
            
            # Fill in search parameters
            # Document type dropdown
            await self.click_element('#doc-type-select')
            await asyncio.sleep(0.3)
            await self.click_element('option[value="substitute_trustee"]')
            
            # Book selection (Trust Book)
            await self.click_element('#book-select')
            await asyncio.sleep(0.3)
            await self.click_element('option[value="trust_book"]')
            
            # Date range
            date_from = search_params.get('date_from', 
                (datetime.now() - timedelta(days=30)).strftime('%m/%d/%Y'))
            date_to = search_params.get('date_to', 
                datetime.now().strftime('%m/%d/%Y'))
            
            await self.fill_input('#date-from', date_from)
            await self.fill_input('#date-to', date_to)
            
            # Submit search
            await self.click_element('#search-button')
            
            # Wait for results
            await asyncio.sleep(2)
            
            # Extract results from page
            documents = await self._extract_search_results()
            
            logger.info(f"Found {len(documents)} documents in Madison County")
            return documents
        
        except Exception as e:
            logger.error(f"Search failed for Madison County: {e}")
            return []
    
    async def _extract_search_results(self) -> List[Dict]:
        """Extract document references from search results page"""
        try:
            # Get all result rows
            results_html = await self.page.evaluate('''
                () => {
                    const rows = document.querySelectorAll('.result-row');
                    return Array.from(rows).map(row => ({
                        documentId: row.querySelector('.doc-id')?.textContent?.trim(),
                        borrower: row.querySelector('.borrower-name')?.textContent?.trim(),
                        propertyAddress: row.querySelector('.property-address')?.textContent?.trim(),
                        filingDate: row.querySelector('.filing-date')?.textContent?.trim(),
                        bookPage: row.querySelector('.book-page')?.textContent?.trim(),
                        url: row.querySelector('a')?.href
                    }));
                }
            ''')
            
            documents = []
            for result in results_html:
                if result['documentId']:
                    documents.append({
                        'document_id': result['documentId'],
                        'title': f"Substitute Trustee - {result['borrower']}",
                        'borrower': result['borrower'],
                        'property_address': result['propertyAddress'],
                        'filing_date': result['filingDate'],
                        'book_page': result['bookPage'],
                        'url': result['url'],
                        'county': 'Madison',
                        'state': 'MS'
                    })
            
            return documents
        except Exception as e:
            logger.warning(f"Could not extract results: {e}")
            return []
    
    async def extract_data(self, document_ref: Dict) -> CaseFile:
        """
        Extract data from a Substitute Trustee document
        """
        logger.info(f"Extracting data from document {document_ref['document_id']}")
        
        case = CaseFile()
        
        try:
            # Navigate to document
            if document_ref.get('url'):
                await self.navigate_to(document_ref['url'])
            
            # Wait for document to load
            await asyncio.sleep(1)
            
            # Capture screenshots of all pages
            screenshots = []
            page_count = 1
            max_pages = 10
            
            while page_count <= max_pages:
                screenshot = await self.get_screenshot(page_count)
                if screenshot:
                    screenshots.append(screenshot)
                    page_count += 1
                    
                    # Try to go to next page
                    next_btn = await self.page.query_selector('.next-page')
                    if not next_btn:
                        break
                    
                    await self.click_element('.next-page')
                    await asyncio.sleep(0.5)
                else:
                    break
            
            logger.info(f"Captured {len(screenshots)} pages for document {document_ref['document_id']}")
            
            # Populate basic info from search results
            case.property.county = 'Madison'
            case.property.address.state = 'MS'
            case.owner.name = document_ref.get('borrower')
            
            # Parse address if available
            if document_ref.get('property_address'):
                address_parts = document_ref['property_address'].split(',')
                if len(address_parts) >= 3:
                    case.property.address.street = address_parts[0].strip()
                    case.property.address.city = address_parts[1].strip()
                    case.property.address.zip = address_parts[2].strip()
            
            # Note: In production, would send screenshots to Vision API for extraction
            case.notes.append(f"Document ID: {document_ref['document_id']}")
            case.notes.append(f"Filing Date: {document_ref.get('filing_date')}")
            case.notes.append(f"Book/Page: {document_ref.get('book_page')}")
            
            return case
        
        except Exception as e:
            logger.error(f"Data extraction failed for {document_ref['document_id']}: {e}")
            return case
