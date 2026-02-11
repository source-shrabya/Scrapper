"""
County Configuration System
Stores button maps and site-specific settings for each county
"""

import json
import os
from typing import Dict, Optional, List
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class CountyConfig:
    """Configuration for a county scraper"""
    county_name: str
    state: str
    website_url: str
    site_type: str  # (e.g., "clerk", "recorder", "assessor")
    search_url: str
    
    # Button map for navigation
    button_map: Optional[Dict] = None
    
    # Search field selectors
    search_fields: Optional[Dict] = None  # Maps field names to CSS selectors
    
    # Document type patterns
    document_types: Optional[List[str]] = None  # (e.g., ["substitute_trustee", "deed_of_trust"])
    
    # Pagination handling
    pagination_selector: Optional[str] = None
    next_page_selector: Optional[str] = None
    
    # Field extraction hints
    field_hints: Optional[Dict] = None
    
    # Rate limiting
    delay_between_clicks: float = 0.5  # seconds
    delay_between_searches: float = 1.0
    
    # Status
    is_active: bool = True
    notes: Optional[str] = None


class CountyConfigManager:
    """Manages county configurations"""
    
    def __init__(self, config_dir: str = './data/county_configs'):
        self.config_dir = config_dir
        os.makedirs(config_dir, exist_ok=True)
        self.configs: Dict[str, CountyConfig] = {}
        self.load_all_configs()
    
    def load_config(self, county_name: str, state: str) -> Optional[CountyConfig]:
        """Load a county configuration"""
        config_file = os.path.join(
            self.config_dir,
            f"{county_name.lower().replace(' ', '_')}_{state.lower()}.json"
        )
        
        if not os.path.exists(config_file):
            logger.warning(f"Config file not found: {config_file}")
            return None
        
        try:
            with open(config_file, 'r') as f:
                data = json.load(f)
            
            config = CountyConfig(**data)
            key = f"{county_name}_{state}"
            self.configs[key] = config
            return config
        except Exception as e:
            logger.error(f"Failed to load config {config_file}: {e}")
            return None
    
    def load_all_configs(self):
        """Load all county configurations from directory"""
        if not os.path.exists(self.config_dir):
            logger.info(f"Config directory not found: {self.config_dir}")
            return
        
        for filename in os.listdir(self.config_dir):
            if filename.endswith('.json'):
                try:
                    with open(os.path.join(self.config_dir, filename), 'r') as f:
                        data = json.load(f)
                    config = CountyConfig(**data)
                    key = f"{config.county_name}_{config.state}"
                    self.configs[key] = config
                except Exception as e:
                    logger.warning(f"Failed to load config {filename}: {e}")
    
    def save_config(self, config: CountyConfig):
        """Save a county configuration"""
        config_file = os.path.join(
            self.config_dir,
            f"{config.county_name.lower().replace(' ', '_')}_{config.state.lower()}.json"
        )
        
        try:
            with open(config_file, 'w') as f:
                json.dump(asdict(config), f, indent=2)
            logger.info(f"Saved config: {config_file}")
        except Exception as e:
            logger.error(f"Failed to save config {config_file}: {e}")
    
    def get_config(self, county_name: str, state: str) -> Optional[CountyConfig]:
        """Get a county configuration"""
        key = f"{county_name}_{state}"
        return self.configs.get(key)
    
    def create_config(
        self,
        county_name: str,
        state: str,
        website_url: str,
        site_type: str,
        search_url: str,
        **kwargs
    ) -> CountyConfig:
        """Create a new county configuration"""
        config = CountyConfig(
            county_name=county_name,
            state=state,
            website_url=website_url,
            site_type=site_type,
            search_url=search_url,
            **kwargs
        )
        self.save_config(config)
        return config
    
    def list_counties(self) -> List[str]:
        """List all configured counties"""
        return list(self.configs.keys())
    
    def update_button_map(self, county_name: str, state: str, button_map: Dict):
        """Update button map for a county"""
        config = self.get_config(county_name, state)
        if config:
            config.button_map = button_map
            self.save_config(config)
            logger.info(f"Updated button map for {county_name}, {state}")


# Example configurations for common county sites
EXAMPLE_CONFIGS = {
    "jackson_ms": {
        "county_name": "Jackson",
        "state": "MS",
        "website_url": "https://www.co.jackson.ms.us/",
        "site_type": "recorder",
        "search_url": "https://www.co.jackson.ms.us/deed/search",
        "document_types": ["substitute_trustee", "deed_of_trust"],
        "search_fields": {
            "document_type": "#docType",
            "name": "#partyName",
            "date_from": "#startDate",
            "date_to": "#endDate",
            "book": "#bookNumber",
            "page": "#pageNumber",
        },
        "pagination_selector": ".pagination",
        "next_page_selector": "a.next",
        "field_hints": {
            "property_address_page": 2,
            "owner_name_indicators": ["Borrower", "Grantor"],
            "loan_date_indicators": ["original deed of trust date"],
        },
        "is_active": True,
    },
    "forrest_ms": {
        "county_name": "Forrest",
        "state": "MS",
        "website_url": "https://www.co.forrest.ms.us/",
        "site_type": "recorder",
        "search_url": "https://www.co.forrest.ms.us/land-records-search",
        "notes": "Site may have payment gate - needs investigation",
        "is_active": False,
    },
}


def create_example_configs(config_dir: str = './data/county_configs'):
    """Create example county configurations"""
    manager = CountyConfigManager(config_dir)
    
    for config_key, config_data in EXAMPLE_CONFIGS.items():
        manager.create_config(**config_data)
        logger.info(f"Created example config: {config_key}")
