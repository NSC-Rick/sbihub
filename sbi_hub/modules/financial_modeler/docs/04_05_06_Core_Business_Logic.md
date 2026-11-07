# 04 Field Documentation + 05 Formula Library + 06 Business Rules

## Overview

This combined document covers field-level documentation, formula library, and business rules for the Operating Model application. It serves as the technical reference for understanding how the application calculates financial projections.

---

# PART 1: KEY FIELD DOCUMENTATION

## Revenue Fields

### Price per Unit
- **Location**: Revenue page → Revenue Streams → Price per Unit
- **Purpose**: Dollar amount charged per unit of product/service
- **Definition**: The selling price for one unit
- **Why It Matters**: Directly determines revenue; pricing power affects profitability
- **Expected Values**: $1 to $10,000+ depending on product/service
- **Validation**: Must be > 0
- **Formula Dependencies**: Revenue = Price × Volume
- **Reports Using**: Income Statement (Revenue), Cash Flow (via revenue)
- **Typical Range**: 
  - Retail products: $10-$500
  - Professional services: $50-$300/hour
  - SaaS: $10-$1000/month
- **Common Mistakes**: Setting price too low (undervaluing), too high (no market)
- **Business Coaching**: "Price should cover COGS + overhead + profit margin. Test market acceptance before finalizing."

### Volume (Initial)
- **Location**: Revenue page → Revenue Streams → Initial Volume
- **Purpose**: Number of units sold per period at start
- **Definition**: Baseline sales volume before growth
- **Why It Matters**: Combined with price, determines baseline revenue
- **Expected Values**: 1 to 10,000+ units depending on business
- **Validation**: Must be >= 0
- **Formula Dependencies**: Revenue = Price × Volume × Growth
- **Reports Using**: Income Statement (Revenue)
- **Typical Range**:
  - Retail store: 100-1000 transactions/month
  - Restaurant: 500-2000 covers/month
  - B2B service: 5-50 clients/month
- **Common Mistakes**: Overestimating initial volume, ignoring market size
- **Business Coaching**: "Start conservative. It's easier to exceed low expectations than explain missing high targets."

### Growth Rate (Annual)
- **Location**: Revenue page → Revenue Streams → Annual Growth Rate
- **Purpose**: Percentage increase in volume year-over-year
- **Definition**: Compound annual growth rate (CAGR) for volume
- **Why It Matters**: Determines revenue trajectory; affects all downstream projections
- **Expected Values**: -0.50 to 1.00 (-50% to 100%)
- **Validation**: Must be between -1.0 and 10.0
- **Formula Dependencies**: Volume[period] = Initial Volume × (1 + Growth)^period
- **Reports Using**: Income Statement (Revenue growth), KPIs
- **Typical Range**:
  - Mature business: 2-8%
  - Growth business: 15-30%
  - Startup: 30-100% (early years)
- **Common Mistakes**: Using unrealistic growth (>30% sustained), ignoring market saturation
- **Business Coaching**: "Lenders discount aggressive growth. Show conservative, moderate, and optimistic cases."

### COGS Percentage
- **Location**: Revenue page → Global COGS Settings → Default COGS Percentage
- **Purpose**: Cost of goods sold as percentage of revenue
- **Definition**: Direct costs to produce/deliver product or service
- **Why It Matters**: Determines gross profit margin; key profitability metric
- **Expected Values**: 0.0 to 1.0 (0% to 100%)
- **Validation**: Must be between 0.0 and 1.0; warning if > 0.90
- **Formula Dependencies**: COGS = Revenue × COGS %; Gross Profit = Revenue - COGS
- **Reports Using**: Income Statement (COGS, Gross Profit), KPIs (Gross Margin %)
- **Typical Range** (by industry):
  - Software/SaaS: 5-15%
  - Professional Services: 10-25%
  - Restaurants: 28-35%
  - Manufacturing: 40-60%
  - Retail: 50-70%
- **Common Mistakes**: Including overhead in COGS, using wrong industry benchmark
- **Business Coaching**: "COGS should only include DIRECT costs: materials, direct labor, shipping. Rent and marketing are NOT COGS."

## Payroll Fields

### Headcount
- **Location**: Payroll page → Payroll Roles → Headcount
- **Purpose**: Number of employees in this role
- **Definition**: FTE (full-time equivalent) count
- **Why It Matters**: Multiplies all labor costs; affects capacity and overhead
- **Expected Values**: 0 to 100 (typically 1-10 for small business)
- **Validation**: Must be >= 0; warning if > 50
- **Formula Dependencies**: Total Wages = Rate × Headcount × Hours
- **Reports Using**: Income Statement (Payroll), Cash Flow
- **Typical Range**:
  - Startup: 1-5 employees
  - Small business: 5-20 employees
  - Growing business: 20-50 employees
- **Common Mistakes**: Overstaffing early, not planning for growth
- **Business Coaching**: "Start lean. Add staff as revenue justifies. Check revenue-per-employee benchmarks for your industry."

### Annual Raise Percentage
- **Location**: Payroll page → Payroll Roles → Annual Raise %
- **Purpose**: Yearly salary increase percentage
- **Definition**: Compound annual increase in compensation
- **Why It Matters**: Affects multi-year labor costs; retention planning
- **Expected Values**: 0.0 to 0.10 (0% to 10%)
- **Validation**: Must be between 0.0 and 1.0; warning if > 0.10
- **Formula Dependencies**: Adjusted Rate = Base Rate × (1 + Raise %)^years
- **Reports Using**: Income Statement (Payroll), Cash Flow
- **Typical Range**:
  - Cost-of-living: 2-3%
  - Performance: 3-5%
  - Promotion: 5-10%
- **Common Mistakes**: Setting to 0% (unrealistic), using same % for all roles
- **Business Coaching**: "Employees expect annual increases. Plan for at least 2-3% to retain talent."

### Payroll Tax Percentage
- **Location**: Payroll page → Payroll Roles → Payroll Tax %
- **Purpose**: Employer portion of payroll taxes
- **Definition**: Mandatory employer taxes as % of wages
- **Why It Matters**: True cost of labor; required by law
- **Expected Values**: 0.0765 to 0.15 (7.65% to 15%)
- **Validation**: Must be >= 0.0765; warning if < 0.0765
- **Formula Dependencies**: Payroll Taxes = Wages × Tax %
- **Reports Using**: Income Statement (Payroll), Cash Flow
- **Typical Range**:
  - Minimum (FICA only): 7.65%
  - With unemployment: 8-10%
  - With workers comp: 10-15%
- **Common Mistakes**: Forgetting employer taxes, using employee withholding rate
- **Business Coaching**: "Employer must pay 7.65% minimum for FICA. Add state/federal unemployment and workers comp. Total typically 8-12%."

## Financing Fields

### Loan Principal
- **Location**: Financing page → Loan Amount
- **Purpose**: Total amount borrowed
- **Definition**: Initial loan balance
- **Why It Matters**: Determines monthly payment, interest expense, debt service
- **Expected Values**: $0 to $5,000,000+
- **Validation**: Must be >= 0
- **Formula Dependencies**: Monthly Payment = PMT(rate, term, principal)
- **Reports Using**: Cash Flow (Financing section), Loan Schedule, KPIs (DSCR)
- **Typical Range**:
  - Startup: $25,000-$100,000
  - Small business: $100,000-$500,000
  - Acquisition: $200,000-$2,000,000+
- **Common Mistakes**: Borrowing too much (DSCR < 1.25), too little (cash shortfall)
- **Business Coaching**: "Borrow enough to cover needs plus 10% buffer, but not so much that DSCR drops below 1.25."

### Loan Interest Rate
- **Location**: Financing page → Loan Annual Rate
- **Purpose**: Annual interest rate on loan
- **Definition**: APR (annual percentage rate)
- **Why It Matters**: Determines interest expense; affects cash flow and DSCR
- **Expected Values**: 0.03 to 0.15 (3% to 15%)
- **Validation**: Must be between 0.0 and 1.0
- **Formula Dependencies**: Monthly Interest = Principal × (Annual Rate / 12)
- **Reports Using**: Income Statement (Interest Expense), Loan Schedule
- **Typical Range** (2024):
  - SBA 7(a): 6-9%
  - Conventional: 5-8%
  - Alternative: 8-15%
- **Common Mistakes**: Using monthly rate instead of annual, ignoring rate changes
- **Business Coaching**: "SBA loans typically offer best rates for small businesses. Shop around and compare total cost, not just rate."

### AR Days (Accounts Receivable Days)
- **Location**: Financing page → Working Capital → AR Days
- **Purpose**: Average days to collect payment from customers
- **Definition**: Days sales outstanding (DSO)
- **Why It Matters**: Affects cash flow timing; longer AR = more cash tied up
- **Expected Values**: 0 to 90 days
- **Validation**: Must be >= 0; warning if > 60
- **Formula Dependencies**: AR Balance = Revenue × (AR Days / Days in Period)
- **Reports Using**: Cash Flow (Working Capital Changes), Balance Sheet
- **Typical Range**:
  - Cash business: 0 days
  - Retail with credit: 5-15 days
  - B2B: 30-45 days
  - Government contracts: 60-90 days
- **Common Mistakes**: Setting to 0 for B2B business, ignoring collection issues
- **Business Coaching**: "Longer AR days mean you're financing your customers. Negotiate shorter terms or require deposits."

### AP Days (Accounts Payable Days)
- **Location**: Financing page → Working Capital → AP Days
- **Purpose**: Average days to pay suppliers
- **Definition**: Days payable outstanding (DPO)
- **Why It Matters**: Affects cash flow timing; longer AP = more supplier financing
- **Expected Values**: 0 to 60 days
- **Validation**: Must be >= 0
- **Formula Dependencies**: AP Balance = COGS × (AP Days / Days in Period)
- **Reports Using**: Cash Flow (Working Capital Changes), Balance Sheet
- **Typical Range**:
  - Cash on delivery: 0 days
  - Net 30 terms: 30 days
  - Extended terms: 45-60 days
- **Common Mistakes**: Setting too high (suppliers won't allow), ignoring early payment discounts
- **Business Coaching**: "Longer AP helps cash flow but may cost early payment discounts. Balance cash needs with supplier relationships."

### Inventory Days
- **Location**: Financing page → Working Capital → Inventory Days
- **Purpose**: Average days inventory held before sale
- **Definition**: Days inventory outstanding (DIO)
- **Why It Matters**: Affects cash tied up in inventory; storage costs
- **Expected Values**: 0 to 180 days
- **Validation**: Must be >= 0
- **Formula Dependencies**: Inventory Balance = COGS × (Inventory Days / Days in Period)
- **Reports Using**: Cash Flow (Working Capital Changes), Balance Sheet
- **Typical Range**:
  - Service business: 0 days
  - Restaurant: 3-7 days
  - Retail: 30-90 days
  - Manufacturing: 60-120 days
- **Common Mistakes**: Setting to 0 for product business, not accounting for seasonal buildup
- **Business Coaching**: "Less inventory = less cash tied up, but risk stockouts. Find balance between cash flow and customer service."

---

# PART 2: FORMULA LIBRARY

## Revenue Calculations

### Base Revenue Formula
```
Revenue[period] = Price × Volume[period]

Where:
  Volume[period] = Initial Volume × (1 + Growth Rate)^period
  
  If Time Mode = Monthly:
    Growth Rate = (1 + Annual Growth)^(1/12) - 1
  Else:
    Growth Rate = Annual Growth
```

**Business Purpose**: Calculate total sales revenue for each period  
**Inputs**: Price, Initial Volume, Growth Rate, Time Mode  
**Outputs**: Revenue per period  
**Plain-English**: "Revenue grows each period based on your growth rate. In monthly mode, annual growth is converted to monthly growth."  
**Financial Significance**: Top line of income statement; drives all other metrics  
**Common Mistakes**: Using monthly growth rate in annual mode, forgetting to compound growth

### Revenue with Seasonality
```
Base Revenue = Price × Volume[period]

If Seasonality Enabled:
  Month Index = period % 12
  Seasonal Multiplier = Monthly Weight[Month Index] / (100/12)
  Adjusted Revenue = Base Revenue × Seasonal Multiplier
Else:
  Adjusted Revenue = Base Revenue
```

**Business Purpose**: Apply monthly revenue patterns (e.g., retail holiday spike)  
**Inputs**: Base Revenue, Seasonality Mode, Monthly Weights  
**Outputs**: Seasonally-adjusted revenue  
**Plain-English**: "Seasonal businesses make more in some months. This spreads annual revenue unevenly across months."  
**Financial Significance**: Affects cash flow timing, working capital needs  
**Common Mistakes**: Forgetting to normalize weights to 100%, applying to annual mode

### Revenue with Startup Ramp
```
Base Revenue = Price × Volume[period]

If Startup Ramp Enabled:
  Ramp Factor = min(1.0, (period + 1) / Ramp Months)
  Adjusted Revenue = Base Revenue × Ramp Factor
Else:
  Adjusted Revenue = Base Revenue
```

**Business Purpose**: Model gradual revenue growth from 0% to 100% for new businesses  
**Inputs**: Base Revenue, Ramp Months  
**Outputs**: Ramped revenue  
**Plain-English**: "New businesses don't reach full capacity immediately. This models gradual growth over X months."  
**Financial Significance**: Reduces early revenue, increases cash needs  
**Common Mistakes**: Using ramp for existing business, setting ramp too long

## COGS Calculations

### Basic COGS Formula
```
COGS[period] = Revenue[period] × COGS Percentage

Where:
  COGS Percentage = Stream COGS Override OR Global COGS %
```

**Business Purpose**: Calculate direct costs to produce/deliver product or service  
**Inputs**: Revenue, COGS Percentage  
**Outputs**: COGS per period  
**Plain-English**: "For every dollar of revenue, X cents goes to direct costs (materials, direct labor, shipping)."  
**Financial Significance**: Determines gross profit; key profitability metric  
**Common Mistakes**: Including overhead in COGS, using wrong industry benchmark

### COGS with Efficiency Improvement
```
For each period:
  Year Index = period / 12 (monthly) OR period (annual)
  Improvement Rate = COGS Improvement % / 100
  Adjusted COGS % = Base COGS % × (1 - Improvement Rate)^Year Index
  COGS[period] = Revenue[period] × Adjusted COGS %
```

**Business Purpose**: Model operational efficiency gains over time  
**Inputs**: Base COGS %, Improvement Rate, Period  
**Outputs**: Declining COGS percentage  
**Plain-English**: "As you gain experience, you become more efficient. COGS drops X% per year."  
**Financial Significance**: Gross margin improves over time  
**Common Mistakes**: Setting improvement too high (>5%), forgetting diminishing returns

## Payroll Calculations

### Salary Employee (Monthly Mode)
```
Years Elapsed = period / 12
Raise Multiplier = (1 + Annual Raise %)^Years Elapsed

Monthly Wages = (Annual Salary / 12) × Headcount × Raise Multiplier
Monthly Taxes = Monthly Wages × Payroll Tax %
Monthly Benefits = Monthly Wages × Benefits %

Total Payroll = Monthly Wages + Monthly Taxes + Monthly Benefits
```

**Business Purpose**: Calculate fully-loaded labor cost for salaried employees  
**Inputs**: Annual Salary, Headcount, Raise %, Tax %, Benefits %  
**Outputs**: Total monthly payroll cost  
**Plain-English**: "Salary is divided by 12 for monthly cost. Add employer taxes and benefits. Raises compound over time."  
**Financial Significance**: Often largest operating expense  
**Common Mistakes**: Forgetting taxes/benefits, not modeling raises

### Hourly Employee (Monthly Mode)
```
Years Elapsed = period / 12
Raise Multiplier = (1 + Annual Raise %)^Years Elapsed

Monthly Hours = (Hours per Week × 52) / 12
Monthly Wages = Hourly Rate × Monthly Hours × Headcount × Raise Multiplier
Monthly Taxes = Monthly Wages × Payroll Tax %
Monthly Benefits = Monthly Wages × Benefits %

Total Payroll = Monthly Wages + Monthly Taxes + Monthly Benefits
```

**Business Purpose**: Calculate fully-loaded labor cost for hourly employees  
**Inputs**: Hourly Rate, Hours per Week, Headcount, Raise %, Tax %, Benefits %  
**Outputs**: Total monthly payroll cost  
**Plain-English**: "Hourly rate × hours worked × headcount. Add employer taxes and benefits. Raises compound over time."  
**Financial Significance**: Variable labor cost scales with hours  
**Common Mistakes**: Using 40 hours for part-time, forgetting overtime

## Loan Calculations

### Loan Payment (PMT Function)
```
Monthly Rate = Annual Rate / 12
Number of Payments = Loan Term (months)

Monthly Payment = Principal × [Monthly Rate × (1 + Monthly Rate)^N] / [(1 + Monthly Rate)^N - 1]

Where N = Number of Payments
```

**Business Purpose**: Calculate fixed monthly loan payment  
**Inputs**: Principal, Annual Rate, Term (months)  
**Outputs**: Monthly payment amount  
**Plain-English**: "Standard amortizing loan formula. Payment stays same each month, but interest/principal split changes."  
**Financial Significance**: Determines debt service, affects DSCR  
**Common Mistakes**: Using annual rate instead of monthly, forgetting to convert term to months

### Interest vs. Principal Split
```
For each period:
  Beginning Balance = Previous Ending Balance (or Principal for period 0)
  Interest Payment = Beginning Balance × (Annual Rate / 12)
  Principal Payment = Monthly Payment - Interest Payment
  Ending Balance = Beginning Balance - Principal Payment
```

**Business Purpose**: Track loan balance and interest expense over time  
**Inputs**: Beginning Balance, Monthly Payment, Annual Rate  
**Outputs**: Interest, Principal, Ending Balance  
**Plain-English**: "Early payments are mostly interest. Later payments are mostly principal. Balance decreases over time."  
**Financial Significance**: Interest is expense (reduces profit), principal is cash outflow (not expense)  
**Common Mistakes**: Treating principal as expense, not tracking balance

## Working Capital Calculations

### Accounts Receivable Balance
```
Days in Period = 30 (monthly) OR 365 (annual)
AR Balance[period] = Revenue[period] × (AR Days / Days in Period)
AR Change[period] = AR Balance[period] - AR Balance[period-1]
```

**Business Purpose**: Calculate cash tied up in customer receivables  
**Inputs**: Revenue, AR Days, Time Mode  
**Outputs**: AR Balance, AR Change  
**Plain-English**: "If customers pay in 30 days, you have 30 days of revenue tied up in AR. Increase in AR is cash outflow."  
**Financial Significance**: AR increase reduces cash flow  
**Common Mistakes**: Setting AR days to 0 for B2B, not understanding cash impact

### Accounts Payable Balance
```
Days in Period = 30 (monthly) OR 365 (annual)
AP Balance[period] = COGS[period] × (AP Days / Days in Period)
AP Change[period] = AP Balance[period] - AP Balance[period-1]
```

**Business Purpose**: Calculate supplier financing (cash you owe)  
**Inputs**: COGS, AP Days, Time Mode  
**Outputs**: AP Balance, AP Change  
**Plain-English**: "If you pay suppliers in 30 days, you owe 30 days of COGS. Increase in AP is cash inflow (supplier financing)."  
**Financial Significance**: AP increase improves cash flow  
**Common Mistakes**: Setting AP too high (suppliers won't allow), forgetting Period 0 special handling

### Inventory Balance
```
Days in Period = 30 (monthly) OR 365 (annual)
Inventory Balance[period] = COGS[period] × (Inventory Days / Days in Period)
Inventory Change[period] = Inventory Balance[period] - Inventory Balance[period-1]
```

**Business Purpose**: Calculate cash tied up in inventory  
**Inputs**: COGS, Inventory Days, Time Mode  
**Outputs**: Inventory Balance, Inventory Change  
**Plain-English**: "If you hold 30 days of inventory, you have 30 days of COGS tied up in stock. Increase in inventory is cash outflow."  
**Financial Significance**: Inventory increase reduces cash flow  
**Common Mistakes**: Setting to 0 for product business, not planning for seasonal buildup

## Income Statement Calculations

### Gross Profit
```
Gross Profit = Revenue - COGS
Gross Margin % = (Gross Profit / Revenue) × 100
```

**Business Purpose**: Measure profitability after direct costs  
**Inputs**: Revenue, COGS  
**Outputs**: Gross Profit, Gross Margin %  
**Plain-English**: "Money left after paying for direct costs. This covers overhead and generates profit."  
**Financial Significance**: Key profitability metric; lenders evaluate sustainability  
**Common Mistakes**: Confusing with net profit, including overhead in COGS

### EBITDA
```
Operating Expenses = Payroll (indirect) + Operating Expenses
EBITDA = Gross Profit - Operating Expenses
EBITDA Margin % = (EBITDA / Revenue) × 100
```

**Business Purpose**: Earnings before interest, taxes, depreciation, amortization  
**Inputs**: Gross Profit, Operating Expenses  
**Outputs**: EBITDA, EBITDA Margin %  
**Plain-English**: "Operating profit before financing costs. Shows business performance independent of capital structure."  
**Financial Significance**: Used for DSCR calculation, valuation  
**Common Mistakes**: Confusing with net income, forgetting it excludes interest

### Net Income
```
EBT = EBITDA - Interest Expense - Depreciation
Taxes = EBT × Tax Rate
Net Income = EBT - Taxes
```

**Business Purpose**: Bottom-line profit after all expenses  
**Inputs**: EBITDA, Interest, Depreciation, Tax Rate  
**Outputs**: Net Income  
**Plain-English**: "Actual profit after everything. This is what's available for owner distributions or reinvestment."  
**Financial Significance**: Key profitability metric  
**Common Mistakes**: Confusing with cash flow, forgetting taxes

## Cash Flow Calculations

### Operating Cash Flow
```
Operating Cash Flow = Net Income - AR Change + AP Change - Inventory Change
```

**Business Purpose**: Cash generated from operations  
**Inputs**: Net Income, Working Capital Changes  
**Outputs**: Operating Cash Flow  
**Plain-English**: "Start with profit, adjust for timing differences. AR increase uses cash, AP increase provides cash."  
**Financial Significance**: Core cash generation ability  
**Common Mistakes**: Confusing with net income, forgetting working capital

### Ending Cash Balance
```
Net Cash Flow = Operating Cash Flow - Loan Principal Payment - Owner Distribution
Ending Cash = Beginning Cash + Net Cash Flow
```

**Business Purpose**: Track cumulative cash position  
**Inputs**: Operating Cash Flow, Financing Cash Flow, Beginning Cash  
**Outputs**: Ending Cash Balance  
**Plain-English**: "Cash in bank at end of period. Cumulative sum of all cash flows."  
**Financial Significance**: Liquidity metric; negative = need capital injection  
**Common Mistakes**: Forgetting beginning cash, not tracking cumulative

## KPI Calculations

### Debt Service Coverage Ratio (DSCR)
```
Debt Service = Loan Payment (principal + interest)
DSCR = EBITDA / Debt Service

If Debt Service = 0:
  DSCR = N/A (debt-free)
```

**Business Purpose**: Measure ability to service debt  
**Inputs**: EBITDA, Debt Service  
**Outputs**: DSCR ratio  
**Plain-English**: "How many times can you cover your loan payment with operating profit. 1.25+ is healthy."  
**Financial Significance**: Lender requirement; <1.25 is risky  
**Common Mistakes**: Using net income instead of EBITDA, including principal in numerator

### Break-Even Period
```
For each period:
  If Ending Cash >= 0:
    Break-Even Period = current period
    Break
```

**Business Purpose**: Identify when business becomes cash-positive  
**Inputs**: Ending Cash series  
**Outputs**: Period number  
**Plain-English**: "First period where you have positive cash. Before this, you need capital injection."  
**Financial Significance**: Determines startup capital needs  
**Common Mistakes**: Confusing with profitability break-even

---

# PART 3: BUSINESS RULES

## Validation Logic

### Revenue Validation
1. **Price > 0**: Cannot have free products (use $0.01 if truly free)
2. **Volume >= 0**: Cannot have negative sales
3. **Growth Rate between -100% and 1000%**: Prevents unrealistic projections
4. **COGS between 0% and 100%**: Cannot exceed 100% of revenue
5. **Warning if Growth > 30%**: Aggressive growth requires justification

### Payroll Validation
1. **Headcount >= 0**: Cannot have negative employees
2. **Rate > 0 if Headcount > 0**: Must pay employees
3. **Hours per Week between 0 and 168**: Cannot exceed hours in week
4. **Payroll Tax >= 7.65%**: Minimum FICA requirement
5. **Benefits >= 0%**: Cannot be negative
6. **Annual Raise between 0% and 100%**: Prevents unrealistic increases

### Financing Validation
1. **Loan Principal >= 0**: Cannot have negative loan
2. **Interest Rate between 0% and 100%**: Reasonable range
3. **Loan Term > 0**: Must have term if principal > 0
4. **AR Days >= 0**: Cannot collect before sale
5. **AP Days >= 0**: Cannot pay before purchase
6. **Inventory Days >= 0**: Cannot have negative inventory
7. **Warning if AR Days > 60**: Slow collection risk
8. **Warning if DSCR < 1.25**: Debt service risk

## Dependencies

### Calculation Order
1. **Revenue** → Calculated first (independent)
2. **COGS** → Depends on Revenue
3. **Gross Profit** → Depends on Revenue, COGS
4. **Payroll** → Calculated independently
5. **Operating Expenses** → Calculated independently (may depend on Revenue if variable)
6. **EBITDA** → Depends on Gross Profit, Payroll, Opex
7. **Interest Expense** → Depends on Loan Balance
8. **Net Income** → Depends on EBITDA, Interest
9. **Working Capital Changes** → Depend on Revenue, COGS
10. **Cash Flow** → Depends on Net Income, Working Capital
11. **Ending Cash** → Depends on Cash Flow, Beginning Cash

### Circular Dependencies (None)
The model is designed to avoid circular dependencies. All calculations flow in one direction.

## Conditional Behavior

### Time Mode Conditional
```
If Time Mode = Monthly:
  - Periods = 36
  - Growth rates converted to monthly
  - Days in period = 30
Else (Annual):
  - Periods = 3
  - Growth rates used as-is
  - Days in period = 365
```

### Mode Conditional (Basic vs. Advanced)
```
If Mode = Basic:
  - Single loan only
  - No capital stack
  - No working capital source options
  - Revenue input methods: 2 options
Else (Advanced):
  - Dual loan structure
  - Capital stack enabled
  - Working capital source options
  - Revenue input methods: 3 options
```

### Business Stage Conditional
```
If Business Stage = Startup OR Acquisition:
  - Period 0 AP = 0 (prevents phantom supplier credit)
Else (Existing):
  - Period 0 AP calculated from AP days
```

### Model Mode Conditional
```
If Model Mode = Startup:
  - Opening AR, AP, Inventory = 0
Else (Acquisition):
  - Opening balances calculated from operating assumptions
```

## Application Assumptions

### Default Values
- **Time Mode**: Monthly (36 periods)
- **Global COGS**: 30%
- **Payroll Tax**: 7.65% (FICA minimum)
- **Benefits**: 15%
- **Annual Raise**: 3%
- **Tax Rate**: 25%
- **AR Days**: 0 (cash business)
- **AP Days**: 0 (cash on delivery)
- **Inventory Days**: 0 (service business)

### Hidden Calculations
- **Monthly growth conversion**: (1 + Annual)^(1/12) - 1
- **Compound raises**: Applied exponentially, not linearly
- **Working capital opening balances**: Calculated based on model mode
- **DSCR calculation**: Uses EBITDA, not Net Income

### Automatic Updates
- **Period count**: Updates when time mode changes
- **Growth rates**: Convert when switching time modes
- **Session state**: Auto-saves every 30 seconds
- **Model rebuild**: Required when inputs change

### State Management
- **Session persistence**: Browser-based, temporary
- **Scenario files**: JSON format, permanent
- **Unsaved changes tracking**: Flags modifications
- **Page navigation**: Preserves all inputs

### Error Handling
- **Invalid JSON**: Error message, no load
- **Missing fields**: Use defaults
- **Out-of-range values**: Validation warnings
- **Division by zero**: Safe divide returns 0
- **Negative cash**: Warning, not error

---

**Coaching Note for Eric**: This document provides the technical foundation for understanding how the Operating Model works. Use it to explain calculations, validate user assumptions, and identify when inputs don't make business sense.

