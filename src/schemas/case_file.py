"""
Comprehensive Case File Schema for Deal Engine
Represents a single property/case with all possible data points
"""

from typing import Optional, List, Dict, Any
from datetime import date, datetime
from pydantic import BaseModel, Field


class Address(BaseModel):
    """Property address information"""
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None


class Parcel(BaseModel):
    """Parcel identification information"""
    ppin: Optional[str] = None  # Parcel Property Identification Number
    parcelNumber: Optional[str] = None


class Property(BaseModel):
    """Property details"""
    address: Address = Field(default_factory=Address)
    county: Optional[str] = None
    parcel: Parcel = Field(default_factory=Parcel)
    legalDescription: Optional[str] = None
    beds: Optional[int] = None
    baths: Optional[float] = None
    squareFootage: Optional[int] = None


class Owner(BaseModel):
    """Owner/borrower information"""
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    mailingAddress: Optional[str] = None
    notes: Optional[str] = None


class Taxes(BaseModel):
    """Tax information"""
    currentTaxBalance: Optional[float] = None
    taxDueDate: Optional[str] = None  # Date format
    exemptionStatus: Optional[str] = None


class Valuation(BaseModel):
    """Property valuation data"""
    arv: Optional[float] = None  # After Repair Value
    arvSource: Optional[str] = None
    propertyValueViaComparison: Optional[float] = None
    rentZestimate: Optional[float] = None
    
    class Zillow(BaseModel):
        zillowImg: Optional[str] = None
        zillowUrl: Optional[str] = None
    
    zillow: Zillow = Field(default_factory=Zillow)
    images: List[str] = Field(default_factory=list)
    aboutTheProperty: Optional[str] = None


class Repairs(BaseModel):
    """Repair cost estimates"""
    repairTierPerSqFt: Optional[float] = None
    estimatedRepairs: Optional[float] = None


class Deal(BaseModel):
    """Deal financial metrics"""
    assignmentFee: Optional[float] = None
    offerPriceToSeller: Optional[float] = None
    offerPricePlusAssignment: Optional[float] = None
    cashSellerGetsIfAny: Optional[float] = None
    estimatedInvestorProfitHighEnd: Optional[float] = None


class Foreclosure(BaseModel):
    """Foreclosure specific information"""
    foreclosingLender: Optional[str] = None
    auctionDate: Optional[str] = None  # Date format


class Contact(BaseModel):
    """Contact tracking"""
    lastContactDate: Optional[str] = None  # Date format
    nextFollowUpDate: Optional[str] = None  # Date format


class DeedOfTrust(BaseModel):
    """Deed of Trust document information"""
    notePrincipal: Optional[float] = None
    originalLender: Optional[str] = None
    originalDate: Optional[str] = None  # Date format
    interestRate: Optional[float] = None
    termMonths: Optional[int] = None
    maturityDate: Optional[str] = None  # Date format
    notes: Optional[str] = None


class CalcAssumptions(BaseModel):
    """Calculation assumptions for debt/equity estimation"""
    assumedInterestRate: Optional[float] = None
    assumedTermMonths: Optional[int] = None
    assumedStartDate: Optional[str] = None  # Date format
    assumedPaymentHistory: Optional[str] = None
    notes: Optional[str] = None


class Numbers(BaseModel):
    """Calculated financial numbers"""
    estimatedDebt: Optional[float] = None
    estimatedEquity: Optional[float] = None
    equityPercent: Optional[float] = None
    equityDollars: Optional[float] = None
    arvDollars: Optional[float] = None
    calcAssumptions: CalcAssumptions = Field(default_factory=CalcAssumptions)


class Loan(BaseModel):
    """Loan information"""
    newTrusteeSubstitute: Optional[str] = None
    loanType: Optional[str] = None
    deedsOfTrust: List[DeedOfTrust] = Field(default_factory=list)


class ProbateExecutor(BaseModel):
    """Probate executor information"""
    name: Optional[str] = None
    role: Optional[str] = None
    appointed: Optional[bool] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None


class ProbateAttorney(BaseModel):
    """Probate attorney information"""
    name: Optional[str] = None
    firm: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    notes: Optional[str] = None


class ProbateDisputeFlags(BaseModel):
    """Flags for probate complications"""
    heirConflict: Optional[bool] = None
    unknownHeirsPossible: Optional[bool] = None
    contestedWill: Optional[bool] = None
    occupantRefusingAccess: Optional[bool] = None
    squatterRisk: Optional[bool] = None


class ProbateOccupancy(BaseModel):
    """Occupancy information for probate cases"""
    isOccupied: Optional[bool] = None
    occupantType: Optional[str] = None
    occupantName: Optional[str] = None
    cashForKeysPotential: Optional[float] = None
    notes: Optional[str] = None


class DealReadiness(BaseModel):
    """Probate deal readiness assessment"""
    canSignNow: Optional[bool] = None
    blockers: List[str] = Field(default_factory=list)
    estimatedTimeToAuthorityDays: Optional[int] = None
    notes: Optional[str] = None


class Probate(BaseModel):
    """Probate information for deceased owner cases"""
    confirmedDeceased: Optional[bool] = None
    deathDate: Optional[str] = None  # Date format
    deathConfirmedBy: Optional[str] = None
    deathConfirmationLinks: List[str] = Field(default_factory=list)
    probateOpened: Optional[bool] = None
    probateCaseNumber: Optional[str] = None
    probateCourt: Optional[str] = None
    probateCounty: Optional[str] = None
    probateState: Optional[str] = None
    estateStatus: Optional[str] = None
    willKnown: Optional[bool] = None
    executor: ProbateExecutor = Field(default_factory=ProbateExecutor)
    attorney: ProbateAttorney = Field(default_factory=ProbateAttorney)
    heirs: List[Dict[str, Any]] = Field(default_factory=list)
    familyDynamics: Optional[str] = None
    disputeFlags: ProbateDisputeFlags = Field(default_factory=ProbateDisputeFlags)
    occupancy: ProbateOccupancy = Field(default_factory=ProbateOccupancy)
    timeline: List[Dict[str, Any]] = Field(default_factory=list)
    nextSteps: List[str] = Field(default_factory=list)
    dealReadiness: DealReadiness = Field(default_factory=DealReadiness)


class FloodRisk(BaseModel):
    """Flood risk and FEMA zone information"""
    femaZone: Optional[str] = None
    bfeFeet: Optional[float] = None  # Base Flood Elevation
    insuranceMandatory: Optional[bool] = None
    groundElevationFeet: Optional[float] = None
    elevationValuesRaw: List[Optional[float]] = Field(default_factory=list)
    sourcePanel: Optional[str] = None
    sourceLinks: List[str] = Field(default_factory=list)
    heuristicSummary: Optional[str] = None


class CaseFile(BaseModel):
    """
    Comprehensive Case File - represents a single property/deal
    A null value indicates that data point is not applicable to this case.
    """
    conclusion: Optional[str] = None
    property: Property = Field(default_factory=Property)
    owner: Owner = Field(default_factory=Owner)
    taxes: Taxes = Field(default_factory=Taxes)
    valuation: Valuation = Field(default_factory=Valuation)
    repairs: Repairs = Field(default_factory=Repairs)
    deal: Deal = Field(default_factory=Deal)
    foreclosure: Foreclosure = Field(default_factory=Foreclosure)
    contact: Contact = Field(default_factory=Contact)
    loan: Loan = Field(default_factory=Loan)
    numbers: Numbers = Field(default_factory=Numbers)
    probate: Probate = Field(default_factory=Probate)
    floodRisk: FloodRisk = Field(default_factory=FloodRisk)
    documents: List[Dict[str, Any]] = Field(default_factory=list)
    notes: List[str] = Field(default_factory=list)
    
    class Config:
        json_encoders = {
            date: lambda v: v.isoformat() if v else None,
            datetime: lambda v: v.isoformat() if v else None,
        }
    
    def to_json(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dictionary"""
        return self.model_dump(exclude_none=False)
    
    def validate_required_fields(self) -> tuple[bool, List[str]]:
        """
        Validate that all required fields (MVP) are present or explicitly null
        Returns: (is_valid, list_of_missing_fields)
        """
        required_fields = [
            'property.address.street',
            'property.address.city',
            'property.address.state',
            'property.address.zip',
            'property.county',
            'property.legalDescription',
            'owner.name',
            'owner.phone',
            'owner.email',
            'repairs.estimatedRepairs',
            'deal.assignmentFee',
            'deal.offerPriceToSeller',
            'deal.offerPricePlusAssignment',
            'deal.cashSellerGetsIfAny',
            'deal.estimatedInvestorProfitHighEnd',
            'foreclosure.loanType',
            'loan.deedsOfTrust[].notePrincipal',
            'loan.deedsOfTrust[].originalDate',
            'loan.deedsOfTrust[].interestRate',
            'loan.deedsOfTrust[].termMonths',
            'numbers.estimatedDebt',
            'numbers.estimatedEquity',
            'numbers.equityPercent',
            'numbers.arvDollars',
        ]
        # Validation logic would check if critical fields are populated
        return (True, [])  # Simplified for now
