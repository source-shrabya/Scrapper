"""
Unit tests for Deal Engine Scraper components
"""

import pytest
from datetime import datetime, timedelta
from src.schemas.case_file import CaseFile, DeedOfTrust
from src.probability.engine import DealProbabilityEngine


class TestCaseFile:
    """Test Case File schema"""
    
    def test_case_file_creation(self):
        """Test creating a case file"""
        case = CaseFile()
        assert case.property is not None
        assert case.owner is not None
        assert case.numbers is not None
    
    def test_case_file_population(self):
        """Test populating case file"""
        case = CaseFile()
        case.property.address.street = "123 Main St"
        case.property.address.city = "Jackson"
        case.property.address.state = "MS"
        case.owner.name = "John Smith"
        
        assert case.property.address.street == "123 Main St"
        assert case.owner.name == "John Smith"
    
    def test_case_file_to_json(self):
        """Test converting to JSON"""
        case = CaseFile()
        case.property.county = "Jackson"
        case.owner.name = "Test"
        
        json_data = case.to_json()
        assert isinstance(json_data, dict)
        assert json_data['property']['county'] == "Jackson"


class TestProbabilityEngine:
    """Test probability calculation"""
    
    def create_sample_case(self) -> CaseFile:
        """Create a sample case for testing"""
        case = CaseFile()
        case.property.county = "Jackson"
        case.property.address.street = "123 Main St"
        case.property.address.city = "Jackson"
        case.owner.name = "John Smith"
        
        # Add loan data
        case.loan.deedsOfTrust = [
            DeedOfTrust(
                notePrincipal=250000,
                originalDate="2010-01-15",
                interestRate=4.5,
                termMonths=360
            )
        ]
        
        # Add valuation
        case.numbers.arvDollars = 350000
        case.numbers.estimatedDebt = 175000
        case.numbers.estimatedEquity = 175000
        case.numbers.equityPercent = 50.0
        
        return case
    
    def test_equity_factor_low(self):
        """Test equity calculation with low equity"""
        case = self.create_sample_case()
        case.numbers.equityPercent = 30.0
        
        engine = DealProbabilityEngine(case)
        factor, explanation = engine.calculate_equity_factor()
        
        assert factor == 0.2
        assert "Low equity" in explanation
    
    def test_equity_factor_good(self):
        """Test equity calculation with good equity"""
        case = self.create_sample_case()
        case.numbers.equityPercent = 65.0
        
        engine = DealProbabilityEngine(case)
        factor, explanation = engine.calculate_equity_factor()
        
        assert factor > 0.8
        assert "Good equity" in explanation
    
    def test_timeline_pressure_high(self):
        """Test timeline pressure with urgent deadline"""
        case = self.create_sample_case()
        case.foreclosure.auctionDate = (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d')
        
        engine = DealProbabilityEngine(case)
        factor, explanation = engine.calculate_timeline_pressure()
        
        assert factor >= 0.9
        assert "HIGH PRESSURE" in explanation
    
    def test_debt_to_arv_ratio_good(self):
        """Test debt to ARV ratio with good spread"""
        case = self.create_sample_case()
        case.numbers.estimatedDebt = 200000
        case.numbers.arvDollars = 400000
        
        engine = DealProbabilityEngine(case)
        factor, explanation = engine.calculate_debt_to_arv_ratio()
        
        assert factor > 0.7
        assert "spread" in explanation.lower()
    
    def test_probability_calculation(self):
        """Test overall probability calculation"""
        case = self.create_sample_case()
        
        engine = DealProbabilityEngine(case)
        probability, factors = engine.calculate_probability()
        
        assert 0 <= probability <= 100
        assert 'equity' in factors
        assert 'timeline' in factors
    
    def test_probability_summary(self):
        """Test probability summary generation"""
        case = self.create_sample_case()
        
        engine = DealProbabilityEngine(case)
        summary = engine.generate_summary()
        
        assert 'deal_probability_percent' in summary
        assert 'deal_quality' in summary
        assert 'top_factors' in summary
        assert 'all_factors' in summary


class TestDealQualityClassification:
    """Test deal quality classification"""
    
    def test_excellent_deal(self):
        """Test excellent deal classification"""
        engine = DealProbabilityEngine(CaseFile())
        quality = engine._classify_deal(85.0)
        assert "EXCELLENT" in quality
    
    def test_good_deal(self):
        """Test good deal classification"""
        engine = DealProbabilityEngine(CaseFile())
        quality = engine._classify_deal(65.0)
        assert "GOOD" in quality
    
    def test_poor_deal(self):
        """Test poor deal classification"""
        engine = DealProbabilityEngine(CaseFile())
        quality = engine._classify_deal(35.0)
        assert "POOR" in quality


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
