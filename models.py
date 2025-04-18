from pydantic import BaseModel, Field
from typing import Optional, List, Dict

# Define the structured output schema for initial financial data extraction
class RawFinancials(BaseModel):
    revenue: Optional[float] = Field(
        None, description="Extracted revenue (in million USD)"
    )
    operating_income: Optional[float] = Field(
        None, description="Extracted operating income (in million USD)"
    )
    eps: Optional[float] = Field(
        None, description="Extracted earnings per share"
    )
    # Add more metrics as needed

class InitialFinancialDataOutput(BaseModel):
    company_name: str = Field(
        ..., description="Company name as extracted from the earnings deck"
    )
    ticker: str = Field(
        ..., description="Stock ticker symbol"
    )
    report_date: str = Field(
        ..., description="Date of the earnings deck/report"
    )
    raw_financials: RawFinancials = Field(
        ..., description="Structured raw financial metrics"
    )
    narrative: Optional[str] = Field(
        None, description="Additional narrative content (if any)"
    )

# Define the structured output schema for each company's financial model
class FinancialModelOutput(BaseModel):
    revenue_projection: float = Field(
        ..., description="Projected revenue for next year (in million USD)"
    )
    operating_income_projection: float = Field(
        ..., description="Projected operating income for next year (in million USD)"
    )
    growth_rate: float = Field(
        ..., description="Expected revenue growth rate (%)"
    )
    discount_rate: float = Field(
        ..., description="Discount rate (%) used for valuation"
    )
    terminal_growth_rate: float = Field(
        ..., description="Terminal growth rate (%) used in the model"
    )
    valuation_estimate: float = Field(
        ..., description="Estimated enterprise value (in million USD)"
    )
    key_assumptions: str = Field(
        ..., description="Key assumptions such as tax rate, CAPEX ratio, etc."
    )
    summary: str = Field(
        ..., description="A brief summary of the preliminary financial model analysis."
    )

class ComparativeAnalysisOutput(BaseModel):
    comparative_analysis: str = Field(
        ..., description="Comparative analysis between Company A and Company B"
    )
    overall_recommendation: str = Field(
        ..., description="Overall investment recommendation with rationale"
    )

# Define the final equity research memo schema, which aggregates the outputs for both companies
class FinalEquityResearchMemoOutput(BaseModel):
    company_a_model: FinancialModelOutput = Field(
        ..., description="Financial model summary for Company A"
    )
    company_b_model: FinancialModelOutput = Field(
        ..., description="Financial model summary for Company B"
    )
    comparative_analysis: ComparativeAnalysisOutput = Field(
        ..., description="Comparative analysis between Company A and Company B"
    )
    # Additional fields for display purposes (not part of the original model)
    company_a_name: Optional[str] = None
    company_b_name: Optional[str] = None
