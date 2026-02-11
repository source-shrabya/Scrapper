"""
Deal Probability Engine - Calculates deal close probability based on weighted factors
"""

from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from src.schemas.case_file import CaseFile


@dataclass
class ProbabilityFactor:
    """Represents a single factor in probability calculation"""
    name: str
    weight: float  # 0.0 to 1.0
    value: float  # 0.0 to 1.0
    explanation: str


class DealProbabilityEngine:
    """
    Calculates Deal Probability Score (0-100%)
    Based on weighted variables that provoke action
    """
    
    # Weight configuration - higher weight = more impact on final probability
    WEIGHTS = {
        'equity_percent': 0.25,          # Equity % (most important)
        'timeline_pressure': 0.20,       # Days until auction
        'debt_to_arv_ratio': 0.15,       # Profit spread (meat on the bone)
        'repair_magnitude': 0.12,        # Repair costs impact
        'probate_complexity': 0.10,      # Probate/heir indicators
        'senior_delinquency': 0.08,      # Senior exemption + taxes
        'title_complexity': 0.10,        # Multiple DOTs/liens/judgments
    }
    
    def __init__(self, case: CaseFile):
        self.case = case
        self.factors: List[ProbabilityFactor] = []
    
    def calculate_equity_factor(self) -> Tuple[float, str]:
        """
        Calculate equity percentage factor (15-20% weight)
        
        Rules:
        - Equity < 40%: bad deal = 0.2 probability
        - Equity 40-50%: poor deal = 0.4 probability
        - Equity 50-60%: decent deal = 0.6 probability
        - Equity 60%+: good deal = 0.8-1.0 probability
        """
        equity_pct = self.case.numbers.equityPercent or 0
        
        if equity_pct < 40:
            return (0.2, f"Low equity {equity_pct:.1f}% - bad deal")
        elif equity_pct < 50:
            return (0.4, f"Poor equity {equity_pct:.1f}%")
        elif equity_pct < 60:
            return (0.6, f"Decent equity {equity_pct:.1f}%")
        else:
            # Scale from 0.8 to 1.0 for 60%+ equity
            scaled = 0.8 + ((equity_pct - 60) / 40) * 0.2
            return (min(scaled, 1.0), f"Good equity {equity_pct:.1f}%")
    
    def calculate_timeline_pressure(self) -> Tuple[float, str]:
        """
        Calculate timeline pressure factor (days until auction)
        
        Rules:
        - 0-3 days: HIGH PRESSURE = 0.9 (urgent)
        - 3-7 days: MEDIUM PRESSURE = 0.7
        - 7-14 days: LOW PRESSURE = 0.5
        - 14+ days: NO PRESSURE = 0.3
        - No date or past date: = 0.1 (dead deal)
        """
        auction_date_str = self.case.foreclosure.auctionDate
        
        if not auction_date_str:
            return (0.1, "No auction date found")
        
        try:
            # Parse auction date
            auction_date = datetime.strptime(auction_date_str, "%Y-%m-%d").date()
            days_until = (auction_date - datetime.now().date()).days
            
            if days_until < 0:
                return (0.0, f"Auction already passed ({days_until} days ago)")
            elif days_until <= 3:
                return (0.9, f"HIGH PRESSURE: {days_until} days until auction")
            elif days_until <= 7:
                return (0.7, f"MEDIUM PRESSURE: {days_until} days until auction")
            elif days_until <= 14:
                return (0.5, f"LOW PRESSURE: {days_until} days until auction")
            else:
                return (0.3, f"NO PRESSURE: {days_until} days until auction")
        except:
            return (0.1, "Could not parse auction date")
    
    def calculate_debt_to_arv_ratio(self) -> Tuple[float, str]:
        """
        Calculate debt vs ARV ratio (profit spread)
        
        Rules:
        - Ratio > 0.95: minimal profit = 0.2
        - Ratio 0.85-0.95: tight margin = 0.4
        - Ratio 0.70-0.85: good spread = 0.7
        - Ratio < 0.70: excellent spread = 0.95
        """
        debt = self.case.numbers.estimatedDebt or 0
        arv = self.case.numbers.arvDollars or 0
        
        if arv == 0:
            return (0.1, "No ARV valuation found")
        
        ratio = debt / arv
        
        if ratio > 0.95:
            return (0.2, f"Minimal profit potential (ratio {ratio:.2f})")
        elif ratio > 0.85:
            return (0.4, f"Tight margin (ratio {ratio:.2f})")
        elif ratio > 0.70:
            return (0.7, f"Good profit spread (ratio {ratio:.2f})")
        else:
            return (0.95, f"Excellent profit margin (ratio {ratio:.2f})")
    
    def calculate_repair_magnitude(self) -> Tuple[float, str]:
        """
        Calculate repair cost impact
        
        Rules:
        - Est. repairs > 50% of ARV: HIGH = 0.3 (difficult to close)
        - Est. repairs 30-50% of ARV: MEDIUM = 0.6
        - Est. repairs 10-30% of ARV: LOW = 0.8
        - Est. repairs < 10% of ARV: MINIMAL = 0.95
        """
        repairs = self.case.repairs.estimatedRepairs or 0
        arv = self.case.numbers.arvDollars or 1
        
        repair_pct = (repairs / arv) * 100 if arv > 0 else 0
        
        if repair_pct > 50:
            return (0.3, f"HIGH repair needs ({repair_pct:.1f}% of ARV)")
        elif repair_pct > 30:
            return (0.6, f"MEDIUM repairs needed ({repair_pct:.1f}% of ARV)")
        elif repair_pct > 10:
            return (0.8, f"LOW repairs needed ({repair_pct:.1f}% of ARV)")
        else:
            return (0.95, f"Minimal repairs ({repair_pct:.1f}% of ARV)")
    
    def calculate_probate_complexity(self) -> Tuple[float, str]:
        """
        Calculate probate/estate complexity impact
        
        Rules:
        - No probate or deceased confirmed but simple: 0.9 (no issue)
        - Probate opened but no complications: 0.6
        - Multiple heirs or disputes: 0.3
        - Contested will or complex probate: 0.1
        """
        probate = self.case.probate
        
        if not probate.confirmedDeceased:
            return (0.9, "No probate complications")
        
        if not probate.probateOpened:
            return (0.7, "Estate situation but probate not opened")
        
        # Check for complications
        dispute_flags = probate.disputeFlags
        complications = sum([
            dispute_flags.heirConflict or False,
            dispute_flags.unknownHeirsPossible or False,
            dispute_flags.contestedWill or False,
            dispute_flags.occupantRefusingAccess or False,
            dispute_flags.squatterRisk or False,
        ])
        
        heirs_count = len(probate.heirs) if probate.heirs else 0
        
        if complications > 2 or heirs_count > 3:
            return (0.1, f"Complex probate with {complications} flags and {heirs_count} heirs")
        elif complications > 0 or heirs_count > 1:
            return (0.3, f"Probate complications: {complications} flags, {heirs_count} heirs")
        else:
            return (0.6, f"Simple probate case")
    
    def calculate_senior_delinquency(self) -> Tuple[float, str]:
        """
        Calculate senior exemption + delinquent tax impact
        
        Rules:
        - Senior exemption + delinquent taxes: HIGH PROBABILITY = 0.85
        - Just senior exemption: 0.7
        - Just delinquent taxes: 0.6
        - Senior but current on taxes: 0.5
        - No indicators: 0.3
        """
        has_senior_exemption = self.case.taxes.exemptionStatus and 'senior' in self.case.taxes.exemptionStatus.lower()
        has_tax_delinquency = self.case.taxes.currentTaxBalance and self.case.taxes.currentTaxBalance > 0
        
        if has_senior_exemption and has_tax_delinquency:
            return (0.85, "Senior + delinquent taxes (financial stress)")
        elif has_senior_exemption:
            return (0.7, "Senior exemption found")
        elif has_tax_delinquency:
            return (0.6, "Property tax delinquency")
        else:
            return (0.3, "No senior/tax delinquency indicators")
    
    def calculate_title_complexity(self) -> Tuple[float, str]:
        """
        Calculate title complexity (multiple liens, DOTs, judgments)
        
        Rules:
        - Multiple DOTs or complex liens: INCREASES probability = 0.8
        - Single DOT: moderate = 0.5
        - Unknown: 0.3
        """
        dot_count = len(self.case.loan.deedsOfTrust) if self.case.loan.deedsOfTrust else 0
        
        if dot_count > 2:
            return (0.8, f"Complex title with {dot_count} deeds of trust")
        elif dot_count == 1:
            return (0.5, f"Single deed of trust")
        elif dot_count == 0:
            return (0.3, "No deed of trust information found")
        else:
            return (0.5, f"{dot_count} deeds of trust")
    
    def calculate_probability(self) -> Tuple[float, Dict[str, ProbabilityFactor]]:
        """
        Calculate overall deal probability (0-100%)
        
        Returns:
            Tuple of (probability_percent, factors_dict)
        """
        factors = {}
        
        # Calculate all factors
        equity_factor, equity_explanation = self.calculate_equity_factor()
        timeline_factor, timeline_explanation = self.calculate_timeline_pressure()
        debt_factor, debt_explanation = self.calculate_debt_to_arv_ratio()
        repair_factor, repair_explanation = self.calculate_repair_magnitude()
        probate_factor, probate_explanation = self.calculate_probate_complexity()
        senior_factor, senior_explanation = self.calculate_senior_delinquency()
        title_factor, title_explanation = self.calculate_title_complexity()
        
        # Store factors
        factors['equity'] = ProbabilityFactor(
            'Equity Percentage', self.WEIGHTS['equity_percent'], equity_factor, equity_explanation
        )
        factors['timeline'] = ProbabilityFactor(
            'Timeline Pressure', self.WEIGHTS['timeline_pressure'], timeline_factor, timeline_explanation
        )
        factors['debt_to_arv'] = ProbabilityFactor(
            'Debt to ARV Ratio', self.WEIGHTS['debt_to_arv_ratio'], debt_factor, debt_explanation
        )
        factors['repairs'] = ProbabilityFactor(
            'Repair Magnitude', self.WEIGHTS['repair_magnitude'], repair_factor, repair_explanation
        )
        factors['probate'] = ProbabilityFactor(
            'Probate Complexity', self.WEIGHTS['probate_complexity'], probate_factor, probate_explanation
        )
        factors['senior'] = ProbabilityFactor(
            'Senior Delinquency', self.WEIGHTS['senior_delinquency'], senior_factor, senior_explanation
        )
        factors['title'] = ProbabilityFactor(
            'Title Complexity', self.WEIGHTS['title_complexity'], title_factor, title_explanation
        )
        
        # Calculate weighted probability
        total_probability = 0.0
        total_weight = 0.0
        
        for factor in factors.values():
            total_probability += factor.value * factor.weight
            total_weight += factor.weight
        
        # Normalize to 0-100%
        final_probability = (total_probability / total_weight * 100) if total_weight > 0 else 0
        
        return (final_probability, factors)
    
    def generate_summary(self) -> Dict:
        """Generate comprehensive probability summary"""
        probability, factors = self.calculate_probability()
        
        # Get top factors
        sorted_factors = sorted(
            factors.items(),
            key=lambda x: x[1].weight * x[1].value,
            reverse=True
        )
        
        return {
            'deal_probability_percent': round(probability, 1),
            'deal_quality': self._classify_deal(probability),
            'top_factors': [
                {
                    'name': factor.name,
                    'probability_contribution': round(factor.value * factor.weight * 100, 1),
                    'explanation': factor.explanation
                }
                for name, factor in sorted_factors[:3]
            ],
            'all_factors': {
                name: {
                    'value': round(factor.value * 100, 1),
                    'weight': factor.weight,
                    'explanation': factor.explanation
                }
                for name, factor in factors.items()
            }
        }
    
    def _classify_deal(self, probability: float) -> str:
        """Classify deal quality based on probability"""
        if probability >= 80:
            return "EXCELLENT - High Close Probability"
        elif probability >= 70:
            return "VERY GOOD - Strong Close Probability"
        elif probability >= 60:
            return "GOOD - Moderate Close Probability"
        elif probability >= 50:
            return "FAIR - Below Average Close Probability"
        elif probability >= 40:
            return "POOR - Low Close Probability"
        else:
            return "VERY POOR - Unlikely to Close"


# Utility function
def calculate_deal_probability(case: CaseFile) -> Dict:
    """
    Quick function to calculate deal probability for a case file
    """
    engine = DealProbabilityEngine(case)
    return engine.generate_summary()
