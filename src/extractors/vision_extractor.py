"""
LLM-based Data Extractor using GPT Vision API
Extracts structured data from document screenshots using vision model
"""

import os
import json
import base64
from typing import Dict, Optional, List, Any
import logging

try:
    from openai import OpenAI
except ImportError:
    raise ImportError("Please install openai: pip install openai")

from src.schemas.case_file import CaseFile

logger = logging.getLogger(__name__)


class VisionExtractor:
    """
    Extracts data from document images using GPT Vision API
    
    Strategy:
    1. Take screenshots of document pages
    2. Send to vision model with extraction schema
    3. Get structured JSON output
    4. Validate and merge with probabilities
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = "gpt-4o"  # Using GPT-4 Omni for vision capabilities
    
    def _encode_image(self, image_path_or_bytes) -> str:
        """Encode image to base64"""
        if isinstance(image_path_or_bytes, bytes):
            return base64.standard_b64encode(image_path_or_bytes).decode('utf-8')
        else:
            with open(image_path_or_bytes, 'rb') as f:
                return base64.standard_b64encode(f.read()).decode('utf-8')
    
    def extract_from_screenshot(
        self,
        image: bytes,
        document_type: str = "substitute_trustee",
        field_hints: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Extract data from a document screenshot
        
        Args:
            image: Image bytes
            document_type: Type of document (substitute_trustee, deed_of_trust, etc)
            field_hints: Optional hints about where to find fields
        
        Returns:
            Dictionary of extracted fields
        """
        
        image_base64 = self._encode_image(image)
        
        # Build extraction prompt based on document type and schema
        prompt = self._build_extraction_prompt(document_type, field_hints)
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/png",
                                    "data": image_base64,
                                },
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ],
                    }
                ],
            )
            
            # Parse response
            response_text = response.content[0].text
            
            # Extract JSON from response
            extracted_data = self._parse_extraction_response(response_text)
            
            return extracted_data
        
        except Exception as e:
            logger.error(f"Vision extraction failed: {e}")
            return {}
    
    def extract_from_screenshots(
        self,
        images: List[bytes],
        document_type: str = "substitute_trustee"
    ) -> Dict[str, Any]:
        """
        Extract data from multiple document pages
        Combines results from all pages
        """
        all_extracted = {}
        
        for idx, image in enumerate(images):
            logger.info(f"Extracting from page {idx + 1}/{len(images)}")
            extracted = self.extract_from_screenshot(
                image,
                document_type=document_type,
                field_hints=all_extracted  # Use previous results as hints
            )
            
            # Merge results, preferring non-null values
            for key, value in extracted.items():
                if value and key not in all_extracted:
                    all_extracted[key] = value
        
        return all_extracted
    
    def _build_extraction_prompt(self, document_type: str, field_hints: Optional[Dict]) -> str:
        """Build detailed extraction prompt for vision model"""
        
        base_prompt = f"""
You are an expert document analyst extracting data from {document_type.replace('_', ' ')} documents.

CRITICAL EXTRACTION RULES:
1. Only extract data you can clearly see in the document
2. If a field is not visible or unclear, return null for that field
3. Be precise with formatting (dates as YYYY-MM-DD, phone as (XXX) XXX-XXXX, etc)
4. Cross-reference information when possible (e.g., match name with address)
5. Watch for different address types (property address vs mailing address vs trustee address)

FIELD IDENTIFICATION RULES:
- Property Address: Usually appears in uppercase, after "legal description" section, often on pages 2-3
- Owner Name: Typically labeled as "Borrower" or "Owner" near the top of document
- Deed of Trust Date: Look for "original deed of trust date" or similar - this is CRITICAL for equity calculation
- Legal Description: Multi-line description starting with "Being" or similar, usually page 1-2
- Loan Principal: Original note principal amount in deed of trust section
- Interest Rate: Usually expressed as percentage (e.g., 5.25%)

CONFIDENCE THRESHOLD:
- Only include fields where you are at least 85% confident
- If uncertain, return null rather than guessing
- Note any ambiguities in the "extraction_confidence" field

DOCUMENT-SPECIFIC HINTS:
{self._get_document_specific_hints(document_type)}

{"Previous page extractions (use to avoid duplicates): " + json.dumps(field_hints) if field_hints else ""}

Return ONLY a valid JSON object with these fields:
{{
    "owner_name": "string or null",
    "owner_phone": "string or null",
    "owner_email": "string or null",
    "property_address_street": "string or null",
    "property_address_city": "string or null",
    "property_address_state": "string or null",
    "property_address_zip": "string or null",
    "property_county": "string or null",
    "legal_description": "string or null",
    "original_loan_date": "YYYY-MM-DD or null",
    "original_loan_principal": "number or null",
    "interest_rate": "number (as percentage) or null",
    "loan_term_months": "number or null",
    "property_beds": "number or null",
    "property_baths": "number or null",
    "property_sqft": "number or null",
    "mailing_address": "string or null",
    "trustee_name": "string or null",
    "trustee_address": "string or null",
    "lender_name": "string or null",
    "auction_date": "YYYY-MM-DD or null",
    "extraction_confidence": "high|medium|low",
    "notes": "string with any observations or uncertainties"
}}
"""
        return base_prompt
    
    def _get_document_specific_hints(self, document_type: str) -> str:
        """Get document-type specific extraction guidance"""
        
        hints = {
            'substitute_trustee': """
For Substitute Trustee documents:
- Look for "Substitution of Trustee" in Trust Book
- Borrower name is critical (also called "Grantor")
- Property address often appears in formatted block, usually page 2-3
- Trustee information identifies who is handling the foreclosure
- Document date shows when substitution was filed (NOT the original loan date)
- Cross-reference "related documents" to find original Deed of Trust for loan details
            """,
            'deed_of_trust': """
For Deed of Trust documents:
- This document contains original loan details
- Look for "Grantor" (borrower), "Trustee", and "Beneficiary" (lender)
- Original loan date, principal amount, and interest rate are in this document
- "Legal description" is detailed property description
- "Secured property" section shows the address
- Term (years or months) is important for debt calculation
            """,
            'notice_of_sale': """
For Notice of Sale documents:
- Auction/sale date is critical
- Property address should match other documents
- Trustee information for auction attendance
- Trust book recording references
- Loan account information may be present
            """,
        }
        
        return hints.get(document_type, "Standard document extraction rules apply.")
    
    def _parse_extraction_response(self, response_text: str) -> Dict[str, Any]:
        """Parse vision model response and extract JSON"""
        
        # Find JSON in response
        try:
            # Try to find JSON block
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON from response: {e}")
        
        return {}
    
    def populate_case_file(
        self,
        case: CaseFile,
        extracted_data: Dict[str, Any],
        source_document: str = "unknown"
    ) -> CaseFile:
        """
        Populate CaseFile object with extracted data
        Handles field mapping and type conversion
        """
        
        # Map extracted fields to CaseFile structure
        field_mapping = {
            'owner_name': ('owner', 'name'),
            'owner_phone': ('owner', 'phone'),
            'owner_email': ('owner', 'email'),
            'property_address_street': ('property', 'address', 'street'),
            'property_address_city': ('property', 'address', 'city'),
            'property_address_state': ('property', 'address', 'state'),
            'property_address_zip': ('property', 'address', 'zip'),
            'property_county': ('property', 'county'),
            'legal_description': ('property', 'legalDescription'),
            'original_loan_date': ('loan', 'deedsOfTrust[0]', 'originalDate'),
            'original_loan_principal': ('loan', 'deedsOfTrust[0]', 'notePrincipal'),
            'interest_rate': ('loan', 'deedsOfTrust[0]', 'interestRate'),
            'loan_term_months': ('loan', 'deedsOfTrust[0]', 'termMonths'),
            'property_beds': ('property', 'beds'),
            'property_baths': ('property', 'baths'),
            'property_sqft': ('property', 'squareFootage'),
            'mailing_address': ('owner', 'mailingAddress'),
            'trustee_name': ('loan', 'newTrusteeSubstitute'),
            'lender_name': ('loan', 'deedsOfTrust[0]', 'originalLender'),
            'auction_date': ('foreclosure', 'auctionDate'),
        }
        
        # Apply extracted data to case file
        for extracted_key, case_path in field_mapping.items():
            if extracted_key in extracted_data and extracted_data[extracted_key]:
                self._set_nested_attr(case, case_path, extracted_data[extracted_key])
        
        # Add note about extraction
        if case.notes is None:
            case.notes = []
        case.notes.append(f"Data extracted from {source_document} via Vision API")
        
        return case
    
    @staticmethod
    def _set_nested_attr(obj, path_tuple, value):
        """Set attribute on nested object using path tuple"""
        if not isinstance(path_tuple, tuple):
            path_tuple = (path_tuple,)
        
        # Navigate to parent
        current = obj
        for key in path_tuple[:-1]:
            if '[' in key:  # Handle array notation like 'deedsOfTrust[0]'
                base_key = key[:key.index('[')]
                index = int(key[key.index('[') + 1:key.index(']')])
                attr = getattr(current, base_key)
                if not attr:
                    setattr(current, base_key, [{}])
                if len(attr) <= index:
                    attr.extend([{} for _ in range(index + 1 - len(attr))])
                current = attr[index]
            else:
                current = getattr(current, key, None)
                if current is None:
                    return
        
        # Set final attribute
        final_key = path_tuple[-1]
        if '[' in final_key:
            base_key = final_key[:final_key.index('[')]
            index = int(final_key[final_key.index('[') + 1:final_key.index(']')])
            attr = getattr(current, base_key, None)
            if not attr:
                setattr(current, base_key, [{}])
            if len(attr) <= index:
                attr.extend([{} for _ in range(index + 1 - len(attr))])
            attr[index] = value
        else:
            setattr(current, final_key, value)
