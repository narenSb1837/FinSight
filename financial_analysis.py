import os
from typing import Optional
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from pydantic import BaseModel, Field
from llama_cloud_services import LlamaExtract
from llama_cloud import ExtractConfig
from llama_cloud.core.api_error import ApiError

from llama_index.core.workflow import (
    Event,
    StartEvent,
    StopEvent,
    Context,
    Workflow,
    step,
)
from llama_index.llms.openai import OpenAI
from llama_index.core.llms.llm import LLM
from llama_index.core.prompts import ChatPromptTemplate
from llama_index.core.workflow import (
    Event,
    StartEvent,
    StopEvent,
    Context,
    Workflow,
    step,
)
from llama_index.llms.openai import OpenAI
from llama_index.core.llms.llm import LLM
from llama_index.core.prompts import ChatPromptTemplate


from models import (
    InitialFinancialDataOutput,
    FinancialModelOutput,
    ComparativeAnalysisOutput,
    FinalEquityResearchMemoOutput,
)

logger = logging.getLogger(__name__)


# Define custom events for each step

import os


from llama_cloud_services import LlamaExtract
from llama_cloud.core.api_error import ApiError
from llama_cloud import ExtractConfig


llama_extract = LlamaExtract()


try:
    existing_agent = llama_extract.get_agent(name="automotive-sector-analysis")
    if existing_agent:
        llama_extract.delete_agent(existing_agent.id)
except ApiError as e:
    if e.status_code == 404:
        pass
    else:
        raise

extract_config = ExtractConfig(
    extraction_mode="BALANCED"
    # extraction_mode="MULTIMODAL"
)


def create_extract_agent():
    try:
        # First try to get the existing agent
        agent = llama_extract.get_agent(name="automotive-sector-analysis")
        logger.info("Using existing extraction agent")
        return agent
    except ApiError as e:
        # If agent doesn't exist (404 error), create a new one
        if e.status_code == 404:
            logger.info("Creating new extraction agent")
            agent = llama_extract.create_agent(
                name="automotive-sector-analysis",
                data_schema=InitialFinancialDataOutput,
                config=extract_config,
            )
            return agent
        else:
            # For other errors, re-raise
            raise


# Define custom events for each step
class DeckAParseEvent(Event):
    deck_content: InitialFinancialDataOutput


class DeckBParseEvent(Event):
    deck_content: InitialFinancialDataOutput


class CompanyModelEvent(Event):
    model_output: FinancialModelOutput


class ComparableDataLoadEvent(Event):
    company_a_output: FinancialModelOutput
    company_b_output: FinancialModelOutput


class LogEvent(Event):
    msg: str
    delta: bool = False


class AutomotiveSectorAnalysisWorkflow(Workflow):
    """
    Workflow to generate an equity research memo for automotive sector analysis.
    """

    def __init__(
        self,
        agent: LlamaExtract,
        llm: Optional[LLM] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.agent = agent
        self.llm = llm or OpenAI(model="o1")
        # Load financial modeling assumptions from file
        # with open(modeling_path, "r") as f:
        #     self.modeling_data = f.read()
        # Instead of loading comparable data from a text file, we load from a PDF

    async def _parse_deck(self, ctx: Context, deck_path) -> InitialFinancialDataOutput:
        extraction_result = await self.agent.aextract(deck_path)
        initial_output = extraction_result.data  # expected to be a string
        ctx.write_event_to_stream(LogEvent(msg="Transcript parsed successfully."))
        return initial_output

    @step
    async def parse_deck_a(self, ctx: Context, ev: StartEvent) -> DeckAParseEvent:
        initial_output = await self._parse_deck(ctx, ev.deck_path_a)
        await ctx.set("initial_output_a", initial_output)
        return DeckAParseEvent(deck_content=initial_output)

    @step
    async def parse_deck_b(self, ctx: Context, ev: StartEvent) -> DeckBParseEvent:
        initial_output = await self._parse_deck(ctx, ev.deck_path_b)
        await ctx.set("initial_output_b", initial_output)
        return DeckBParseEvent(deck_content=initial_output)

    async def _generate_financial_model(
        self, ctx: Context, financial_data: InitialFinancialDataOutput
    ) -> FinancialModelOutput:
        prompt_str = """
            You are a senior financial analyst with expertise in building financial models from earnings reports.

            TASK: Create a refined financial model based on earnings data and modeling assumptions.

            INPUT DATA:
            - Earnings deck raw financial data: {raw_data}

            INSTRUCTIONS:
            1. Extract and prioritize the most recent quarterly financial data
            2. Apply industry-standard financial modeling techniques
            3. Make intelligent adjustments to assumptions based on company context and sector trends
            4. Ensure all calculations are mathematically sound and internally consistent

            OUTPUT REQUIREMENTS:
            - Return a complete JSON object conforming to the FinancialModelOutput schema
            - All schema fields must be populated with calculated values (no null or placeholder values)
            - Include brief explanations for key assumption adjustments
            - Round financial figures appropriately (2 decimal places for percentages, nearest thousand for currency)

            FINANCIAL MODEL COMPONENTS TO INCLUDE:
            - Revenue projections (base, optimistic, conservative)
            - Operating expenses breakdown
            - Margin analysis (gross, operating, net)
            - Growth rate calculations (YoY, sequential)
            - Key valuation metrics (P/E, EV/EBITDA)
            - Cash flow projections
            - Balance sheet highlights
            - Risk factors quantification

            The goal is to produce an actionable financial model that could guide investment decisions.

    """
        prompt = ChatPromptTemplate.from_messages([("user", prompt_str)])
        refined_model = await self.llm.astructured_predict(
            FinancialModelOutput,
            prompt,
            raw_data=financial_data.model_dump_json(),
            # assumptions=self.modeling_data,
        )
        return refined_model

    @step
    async def refine_financial_model_company_a(
        self, ctx: Context, ev: DeckAParseEvent
    ) -> CompanyModelEvent:
        print("deck content A", ev.deck_content)
        refined_model = await self._generate_financial_model(ctx, ev.deck_content)
        print("refined_model A", refined_model)
        print(type(refined_model))
        await ctx.set("CompanyAModelEvent", refined_model)
        return CompanyModelEvent(model_output=refined_model)

    @step
    async def refine_financial_model_company_b(
        self, ctx: Context, ev: DeckBParseEvent
    ) -> CompanyModelEvent:
        print("deck content B", ev.deck_content)
        refined_model = await self._generate_financial_model(ctx, ev.deck_content)
        print("refined_model B", refined_model)
        print(type(refined_model))
        await ctx.set("CompanyBModelEvent", refined_model)
        return CompanyModelEvent(model_output=refined_model)

    @step
    async def cross_reference_models(
        self, ctx: Context, ev: CompanyModelEvent
    ) -> StopEvent:
        # Assume CompanyAModelEvent and CompanyBModelEvent are stored in the context
        company_a_model = await ctx.get("CompanyAModelEvent", default=None)
        company_b_model = await ctx.get("CompanyBModelEvent", default=None)
        if company_a_model is None or company_b_model is None:
            return

        prompt_str = """
You are a senior investment analyst with 15+ years of experience evaluating automotive companies.

TASK: Conduct a comparative analysis of two competing automotive companies and provide a specific investment recommendation on which company represents the better investment opportunity.

INPUT DATA:
- Company A financial model: {company_a_model}
- Company B financial model: {company_b_model}

ANALYSIS REQUIREMENTS:
1. Financial Performance Comparison
   - Revenue growth trajectories (historical and projected)
   - Margin evolution (gross, operating, net)
   - Production capacity and utilization metrics
   - R&D investment efficiency and product development pipelines

2. Industry-Specific Metrics
   - Vehicle delivery growth rates
   - Average selling price (ASP) trends
   - Manufacturing efficiency and cost structures
   - Market share trends in key segments
   - Technology leadership indicators

3. Valuation Analysis
   - Relative and absolute valuation metrics comparison
   - Discounted cash flow assumptions assessment
   - Price targets with detailed methodology explanation
   - Risk-adjusted expected returns

4. Investment Recommendation
   - Clear winner with specific rating (Strong Buy, Buy, Hold)
   - 12-month price target with bull/base/bear scenarios
   - Investment timeframe recommendation (short, medium, long-term)
   - Key catalysts and risk factors that could alter the thesis

FORMAT YOUR RESPONSE AS A PROFESSIONAL INVESTMENT REPORT WITH CLEAR SECTION HEADINGS AND CONCISE, DATA-DRIVEN ANALYSIS.
Don't mention just company A and B, use the actual names.
    """
        prompt = ChatPromptTemplate.from_messages([("user", prompt_str)])
        comp_analysis = await self.llm.astructured_predict(
            ComparativeAnalysisOutput,
            prompt,
            company_a_model=company_a_model.model_dump_json(),
            company_b_model=company_b_model.model_dump_json(),
        )
        final_memo = FinalEquityResearchMemoOutput(
            company_a_model=company_a_model,
            company_b_model=company_b_model,
            comparative_analysis=comp_analysis,
        )
        return StopEvent(result={"memo": final_memo})
