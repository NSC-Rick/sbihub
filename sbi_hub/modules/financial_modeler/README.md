# Operating Model - Financial Modeling Web App

A Streamlit-based financial modeling application for SBDC-style business planning with monthly/annual projections, multiple revenue streams, role-based payroll, and comprehensive financial statements.

## Features

- **Flexible Time Modes**: Toggle between monthly (60 periods) and annual (5 periods) projections
- **Multiple Revenue Streams**: Add/remove revenue streams with individual pricing, volume, and growth rates
- **Role-Based Payroll**: Configure multiple roles with hourly/salary compensation, raises, taxes, and benefits
- **Operating Expenses**: Track fixed expenses with inflation adjustments
- **Loan Amortization**: Full term loan schedule with interest/principal split
- **Working Capital**: AR/AP/Inventory days with cash flow impact
- **Profit & Loss Statement**: Complete P&L with depreciation and taxes
- **Financial Statements**: Complete 5-year Income Statement and Cash Flow Statement
- **KPI Dashboard**: DSCR, ending cash, net income, and other key metrics
- **Interactive Charts**: Revenue trends, cash flow, and DSCR visualizations
- **Scenario Management**: Save and load complete model scenarios as JSON files

## Installation

1. **Clone or download** this repository

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

From the `finlite_app` directory, run:

```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`

## Project Structure

```
finlite_app/
├── app.py                  # Main Streamlit application
├── engine/                 # Pure calculation engine (no UI)
│   ├── __init__.py
│   ├── model.py           # Main model builder
│   ├── revenue.py         # Revenue calculations
│   ├── payroll.py         # Payroll calculations
│   ├── opex.py            # Operating expense calculations
│   ├── loan.py            # Loan amortization
│   ├── statements.py      # Financial statements & KPIs
│   └── validation.py      # JSON scenario validation
├── ui/                    # Streamlit UI pages
│   ├── __init__.py
│   ├── home.py            # Home page with scenario management
│   ├── revenue_page.py    # Revenue stream configuration
│   ├── payroll_page.py    # Payroll role configuration
│   ├── opex_page.py       # Operating expense configuration
│   ├── financing_page.py  # Loan and working capital settings
│   └── review_page.py     # Financial statements and charts
├── tests/                 # Test suite
│   ├── __init__.py
│   ├── test_loan_amort.py # Loan amortization tests
│   ├── test_engine_smoke.py # Engine integration tests
│   ├── test_pnl.py        # P&L statement tests
│   └── test_scenario_json.py # Scenario save/load tests
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Usage Guide

### 1. Home Page

#### Scenario Management
- **Save Scenario**: Download your current model as a JSON file
  - Click "Download Scenario" to save all inputs
  - File is named `operating_model_scenario.json`
  - Can be loaded later to restore exact model state
  
- **Load Scenario**: Upload a previously saved scenario
  - Click "Upload Scenario" and select a JSON file
  - All inputs will be restored automatically
  - Invalid files will show an error message
  
- **Reset Model**: Restore all inputs to default values
  - Click "Reset to Defaults" to start fresh
  - All custom inputs will be cleared

#### Time Mode Configuration
- Select **Monthly** or **Annual** time mode
- This determines whether you're modeling 60 months or 5 years
- All inputs adjust automatically to the selected mode

### 2. Revenue Streams
- Add multiple revenue streams (products/services)
- Configure price per unit and initial volume
- Set annual growth rate (applies monthly if in monthly mode)
- Optionally override global COGS percentage per stream

### 3. Payroll & Personnel
- Add roles with headcount
- Choose hourly or salary compensation
- Configure annual raises, payroll taxes (e.g., 7.65% for FICA), and benefits
- All calculations compound over time

### 4. Operating Expenses
- Add fixed expenses (rent, utilities, insurance, etc.)
- Set growth rates for inflation
- Excludes payroll (handled separately)

### 5. Financing & Working Capital
- Configure term loan: principal, rate, term, start period
- Set working capital assumptions: AR days, AP days, Inventory days
- These affect cash flow timing

### 6. Review & Analysis
- View complete Income Statement and Cash Flow Statement
- Review loan amortization schedule
- Analyze KPIs including DSCR and ending cash
- Interactive charts for trends
- Download all tables as CSV

## Key Principles

### Deterministic & Transparent
- **No fabricated values**: All calculations derive from your inputs
- **Visible defaults**: All default values are shown and editable
- **Reproducible**: Same inputs always produce same outputs

### Separation of Concerns
- **Engine**: Pure Python functions with no UI dependencies
- **UI**: Streamlit pages that only read/write session state
- **Tests**: Validate core calculations independently

### Financial Accuracy
- Loan amortization uses standard formulas
- Monthly growth rates properly annualized
- Working capital changes affect cash flow
- DSCR calculated as EBITDA / Debt Service

## Running Tests

From the `finlite_app` directory:

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_loan_amort.py -v
pytest tests/test_engine_smoke.py -v
```

## Model Inputs Reference

### Revenue Stream
- `name`: Stream identifier
- `price`: Price per unit
- `volume`: Initial volume per period
- `growth_rate`: Annual growth rate (decimal, e.g., 0.10 = 10%)
- `cogs_override`: Optional COGS % override (None uses global)

### Payroll Role
- `role`: Role title
- `headcount`: Number of employees
- `pay_type`: 'salary' or 'hourly'
- `rate`: Annual salary or hourly wage
- `hours_per_week`: Hours per week (for hourly only)
- `annual_raise_pct`: Annual raise percentage
- `payroll_tax_pct`: Employer payroll tax rate (e.g., 0.0765)
- `benefits_pct`: Benefits as % of wages

### Operating Expense
- `name`: Expense identifier
- `amount`: Initial period amount
- `growth_rate`: Annual growth rate

### Loan
- `loan_principal`: Total loan amount
- `loan_annual_rate`: Annual interest rate (decimal)
- `loan_term_months`: Term in months
- `loan_start_period`: Period when loan starts (0-indexed)

### Working Capital
- `ar_days`: Days sales outstanding (accounts receivable)
- `ap_days`: Days payable outstanding (accounts payable)
- `inventory_days`: Days inventory held

## Output Reference

### Income Statement
- Revenue (by stream + total)
- COGS
- Gross Profit
- Payroll (wages + taxes + benefits)
- Operating Expenses
- EBITDA
- Interest Expense
- Net Income

### Cash Flow Statement
- Net Income
- AR/AP/Inventory Changes
- Operating Cash Flow
- Financing Cash Flow (loan principal)
- Net Cash Flow
- Ending Cash (cumulative)

### KPIs
- EBITDA
- Debt Service (loan payment)
- DSCR (Debt Service Coverage Ratio)
- Ending Cash

## JSON Scenario File Format

Scenario files are saved in JSON format with the following structure:

```json
{
  "time_mode": "monthly",
  "periods": 60,
  "revenue_streams": [
    {
      "name": "Product Sales",
      "price": 100.0,
      "volume": 100.0,
      "growth_rate": 0.10,
      "cogs_override": null
    }
  ],
  "global_cogs_pct": 0.30,
  "payroll_roles": [
    {
      "role": "Manager",
      "headcount": 1,
      "pay_type": "salary",
      "rate": 60000.0,
      "hours_per_week": 40,
      "annual_raise_pct": 0.03,
      "payroll_tax_pct": 0.0765,
      "benefits_pct": 0.15
    }
  ],
  "opex_items": [
    {
      "name": "Rent",
      "amount": 2000.0,
      "growth_rate": 0.03
    }
  ],
  "loan_principal": 50000.0,
  "loan_annual_rate": 0.06,
  "loan_term_months": 60,
  "loan_start_period": 0,
  "ar_days": 30,
  "ap_days": 30,
  "inventory_days": 30,
  "tax_rate": 0.25,
  "annual_depreciation": 0.0
}
```

### Scenario File Features

- **Client-Side Only**: No server storage, all data stays on your computer
- **Complete State**: All model inputs are preserved
- **Validation**: Files are validated before loading to prevent errors
- **Forward Compatible**: Extra keys in JSON files are ignored (for future features)
- **Human Readable**: JSON format is easy to read and edit manually if needed

### Sharing Scenarios

Scenario files can be:
- Emailed to colleagues
- Stored in version control (Git)
- Backed up to cloud storage
- Edited manually in a text editor (advanced users)

## Troubleshooting

### App won't start
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version (3.8+ recommended)

### Calculations seem wrong
- Verify time mode matches your expectations (monthly vs annual)
- Check growth rates are in decimal form (0.10 not 10)
- Review working capital days for reasonableness

### DSCR shows as 0
- DSCR only calculated when debt service > 0
- Check loan start period and term
- Verify loan principal > 0

## License

This project is provided as-is for educational and business planning purposes.

## Support

For issues or questions, please refer to the inline help text in the application or review the test files for usage examples.
