# Automotive Sector Financial Analysis

A tool for generating comprehensive equity research memos by comparing financial data from automotive companies.

## Features

- Extract financial data from earnings decks/reports (PDF format)
- Generate detailed financial models with projections
- Perform comparative analysis between two companies
- Create investment recommendations with price targets

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up your API keys:
   - LLAMA_CLOUD_API_KEY
   - OPENAI_API_KEY

## Usage

```python
from financial_analysis import AutomotiveSectorAnalysisWorkflow, create_extract_agent

# Create the extraction agent
agent = create_extract_agent()

# Initialize the workflow
workflow = AutomotiveSectorAnalysisWorkflow(agent=agent)

# Run the workflow
result = workflow.run(
    deck_path_a="path/to/company_a_deck.pdf",
    deck_path_b="path/to/company_b_deck.pdf"
)

# Access the equity research memo
memo = result["memo"]
```

## Output

The workflow produces a comprehensive equity research memo containing:
- Detailed financial models for both companies
- Comparative analysis of financial performance
- Industry-specific metrics comparison
- Investment recommendation with price targets 