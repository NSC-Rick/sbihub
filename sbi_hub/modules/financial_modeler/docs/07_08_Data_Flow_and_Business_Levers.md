# 07 Data Flow Documentation + 08 Business Lever Library

## Overview

This document illustrates how information flows through the Operating Model application and identifies every business lever that users can adjust to improve financial outcomes.

---

# PART 1: DATA FLOW DOCUMENTATION

## Complete Data Flow Diagram

```
USER INPUTS
    ↓
┌─────────────────────────────────────────────────────────────┐
│ REVENUE PLANNING                                            │
│ - Price per Unit                                            │
│ - Initial Volume                                            │
│ - Growth Rate                                               │
│ - Seasonality                                               │
│ - Startup Ramp                                              │
└─────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────┐
│ REVENUE CALCULATION                                         │
│ Revenue[period] = Price × Volume × Growth × Seasonality     │
└─────────────────────────────────────────────────────────────┘
    ↓
    ├──────────────────────────────────────────────────────────→ INCOME STATEMENT (Revenue)
    ├──────────────────────────────────────────────────────────→ WORKING CAPITAL (AR Balance)
    ↓
┌─────────────────────────────────────────────────────────────┐
│ COGS CALCULATION                                            │
│ COGS = Revenue × COGS %                                     │
└─────────────────────────────────────────────────────────────┘
    ↓
    ├──────────────────────────────────────────────────────────→ INCOME STATEMENT (COGS)
    ├──────────────────────────────────────────────────────────→ WORKING CAPITAL (AP, Inventory)
    ↓
┌─────────────────────────────────────────────────────────────┐
│ GROSS PROFIT CALCULATION                                    │
│ Gross Profit = Revenue - COGS                               │
│ Gross Margin % = Gross Profit / Revenue                     │
└─────────────────────────────────────────────────────────────┘
    ↓
    ├──────────────────────────────────────────────────────────→ INCOME STATEMENT (Gross Profit)
    ├──────────────────────────────────────────────────────────→ KPIs (Gross Margin %)
    ↓
┌─────────────────────────────────────────────────────────────┐
│ PAYROLL CALCULATION                                         │
│ - Direct Labor → COGS                                       │
│ - Indirect Labor → Operating Expenses                       │
│ Total = Wages + Taxes + Benefits                            │
└─────────────────────────────────────────────────────────────┘
    ↓
    ├──────────────────────────────────────────────────────────→ INCOME STATEMENT (Payroll)
    ├──────────────────────────────────────────────────────────→ CASH FLOW (Operating)
    ↓
┌─────────────────────────────────────────────────────────────┐
│ OPERATING EXPENSES CALCULATION                              │
│ - Fixed Expenses                                            │
│ - Variable % Revenue Expenses                               │
│ Total Opex = Sum of all categories                          │
└─────────────────────────────────────────────────────────────┘
    ↓
    ├──────────────────────────────────────────────────────────→ INCOME STATEMENT (Opex)
    ├──────────────────────────────────────────────────────────→ CASH FLOW (Operating)
    ↓
┌─────────────────────────────────────────────────────────────┐
│ EBITDA CALCULATION                                          │
│ EBITDA = Gross Profit - Payroll - Opex                      │
└─────────────────────────────────────────────────────────────┘
    ↓
    ├──────────────────────────────────────────────────────────→ INCOME STATEMENT (EBITDA)
    ├──────────────────────────────────────────────────────────→ KPIs (DSCR calculation)
    ↓
┌─────────────────────────────────────────────────────────────┐
│ LOAN CALCULATION                                            │
│ - Monthly Payment = PMT(rate, term, principal)             │
│ - Interest Expense                                          │
│ - Principal Payment                                         │
└─────────────────────────────────────────────────────────────┘
    ↓
    ├──────────────────────────────────────────────────────────→ INCOME STATEMENT (Interest)
    ├──────────────────────────────────────────────────────────→ CASH FLOW (Financing)
    ├──────────────────────────────────────────────────────────→ LOAN SCHEDULE
    ↓
┌─────────────────────────────────────────────────────────────┐
│ NET INCOME CALCULATION                                      │
│ Net Income = EBITDA - Interest - Depreciation - Taxes       │
└─────────────────────────────────────────────────────────────┘
    ↓
    ├──────────────────────────────────────────────────────────→ INCOME STATEMENT (Net Income)
    ├──────────────────────────────────────────────────────────→ CASH FLOW (Starting point)
    ↓
┌─────────────────────────────────────────────────────────────┐
│ WORKING CAPITAL CHANGES                                     │
│ - AR Change = AR[t] - AR[t-1]                              │
│ - AP Change = AP[t] - AP[t-1]                              │
│ - Inventory Change = Inv[t] - Inv[t-1]                     │
└─────────────────────────────────────────────────────────────┘
    ↓
    ├──────────────────────────────────────────────────────────→ CASH FLOW (Working Capital)
    ↓
┌─────────────────────────────────────────────────────────────┐
│ OPERATING CASH FLOW                                         │
│ OCF = Net Income - AR Δ + AP Δ - Inv Δ                     │
└─────────────────────────────────────────────────────────────┘
    ↓
    ├──────────────────────────────────────────────────────────→ CASH FLOW STATEMENT
    ├──────────────────────────────────────────────────────────→ KPIs
    ↓
┌─────────────────────────────────────────────────────────────┐
│ NET CASH FLOW                                               │
│ NCF = OCF - Loan Principal - Owner Distribution             │
└─────────────────────────────────────────────────────────────┘
    ↓
    ├──────────────────────────────────────────────────────────→ CASH FLOW STATEMENT
    ↓
┌─────────────────────────────────────────────────────────────┐
│ ENDING CASH BALANCE                                         │
│ Ending Cash = Beginning Cash + Cumulative NCF               │
└─────────────────────────────────────────────────────────────┘
    ↓
    ├──────────────────────────────────────────────────────────→ CASH FLOW STATEMENT
    ├──────────────────────────────────────────────────────────→ KPIs (Cash Balance)
    ├──────────────────────────────────────────────────────────→ INSIGHTS (Cash warnings)
    ↓
┌─────────────────────────────────────────────────────────────┐
│ KPI CALCULATIONS                                            │
│ - DSCR = EBITDA / Debt Service                             │
│ - Gross Margin % = Gross Profit / Revenue                  │
│ - EBITDA Margin % = EBITDA / Revenue                       │
│ - Net Margin % = Net Income / Revenue                      │
└─────────────────────────────────────────────────────────────┘
    ↓
    ├──────────────────────────────────────────────────────────→ REVIEW PAGE (KPIs Tab)
    ├──────────────────────────────────────────────────────────→ INSIGHTS PAGE (Flags)
    ├──────────────────────────────────────────────────────────→ CHARTS
    ↓
OUTPUT TO USER
```

## Detailed Flow by Component

### Revenue → COGS → Gross Profit Flow
```
Revenue Inputs (Revenue Page)
    ↓
Revenue Calculation Engine
    ↓
Revenue Series [Period 0...N]
    ↓
    ├─→ Income Statement (Revenue line)
    ├─→ AR Calculation (Revenue × AR Days / 30)
    └─→ COGS Calculation (Revenue × COGS %)
            ↓
        COGS Series [Period 0...N]
            ↓
            ├─→ Income Statement (COGS line)
            ├─→ AP Calculation (COGS × AP Days / 30)
            ├─→ Inventory Calculation (COGS × Inv Days / 30)
            └─→ Gross Profit Calculation (Revenue - COGS)
                    ↓
                Gross Profit Series [Period 0...N]
                    ↓
                    ├─→ Income Statement (Gross Profit line)
                    └─→ Gross Margin % (GP / Revenue × 100)
```

### Payroll → Operating Expenses → EBITDA Flow
```
Payroll Inputs (Payroll Page)
    ↓
Payroll Calculation Engine
    ↓
Payroll Series [Period 0...N]
    ├─→ Direct Labor → Added to COGS
    └─→ Indirect Labor → Operating Expenses
            ↓
Opex Inputs (Opex Page)
    ↓
Opex Calculation Engine
    ↓
Opex Series [Period 0...N]
    ↓
Total Operating Expenses = Indirect Payroll + Opex
    ↓
    ├─→ Income Statement (Operating Expenses line)
    └─→ EBITDA Calculation (Gross Profit - Operating Expenses)
            ↓
        EBITDA Series [Period 0...N]
            ↓
            ├─→ Income Statement (EBITDA line)
            └─→ DSCR Calculation (EBITDA / Debt Service)
```

### Financing → Interest → Net Income Flow
```
Loan Inputs (Financing Page)
    ↓
Loan Amortization Engine
    ↓
Loan Schedule [Period 0...N]
    ├─→ Interest Expense Series
    ├─→ Principal Payment Series
    └─→ Ending Balance Series
            ↓
Interest Expense Series
    ↓
    ├─→ Income Statement (Interest Expense line)
    └─→ Net Income Calculation
            ↓
        Net Income = EBITDA - Interest - Depreciation - Taxes
            ↓
        Net Income Series [Period 0...N]
            ↓
            ├─→ Income Statement (Net Income line)
            └─→ Cash Flow Statement (Starting point)
```

### Working Capital → Cash Flow Flow
```
Working Capital Inputs (Financing Page)
    ↓
Working Capital Calculation Engine
    ↓
AR Balance Series = Revenue × (AR Days / 30)
AP Balance Series = COGS × (AP Days / 30)
Inventory Balance Series = COGS × (Inv Days / 30)
    ↓
AR Change = AR[t] - AR[t-1]
AP Change = AP[t] - AP[t-1]
Inventory Change = Inv[t] - Inv[t-1]
    ↓
    └─→ Operating Cash Flow Calculation
            ↓
        OCF = Net Income - AR Change + AP Change - Inv Change
            ↓
            ├─→ Cash Flow Statement (Operating Cash Flow)
            └─→ Net Cash Flow Calculation
                    ↓
                NCF = OCF - Loan Principal - Owner Distribution
                    ↓
                    ├─→ Cash Flow Statement (Net Cash Flow)
                    └─→ Ending Cash Calculation
                            ↓
                        Ending Cash = Beginning Cash + Cumulative NCF
                            ↓
                            ├─→ Cash Flow Statement (Ending Cash)
                            ├─→ KPIs (Cash Balance)
                            └─→ Insights (Cash warnings)
```

## Dependency Chain

### Level 1 (No Dependencies)
- Revenue Inputs
- Payroll Inputs
- Operating Expense Inputs
- Loan Inputs
- Working Capital Assumptions

### Level 2 (Depends on Level 1)
- Revenue Calculation
- Payroll Calculation
- Opex Calculation
- Loan Amortization

### Level 3 (Depends on Level 2)
- COGS Calculation (depends on Revenue)
- Gross Profit (depends on Revenue, COGS)
- Operating Expenses Total (depends on Payroll, Opex)
- Interest Expense (depends on Loan)

### Level 4 (Depends on Level 3)
- EBITDA (depends on Gross Profit, Operating Expenses)
- Working Capital Balances (depend on Revenue, COGS)

### Level 5 (Depends on Level 4)
- Net Income (depends on EBITDA, Interest)
- Working Capital Changes (depend on WC Balances)

### Level 6 (Depends on Level 5)
- Operating Cash Flow (depends on Net Income, WC Changes)

### Level 7 (Depends on Level 6)
- Net Cash Flow (depends on Operating Cash Flow, Loan Principal)
- Ending Cash (depends on Net Cash Flow)

### Level 8 (Depends on Multiple Levels)
- DSCR (depends on EBITDA, Loan Payment)
- KPIs (depend on various calculations)
- Insights Flags (depend on KPIs)

---

# PART 2: BUSINESS LEVER LIBRARY

## Overview

Business levers are inputs that users can adjust to improve financial outcomes. Each lever has direct and indirect effects on profitability, cash flow, and viability.

---

## LEVER 1: PRICING

### Definition
Price charged per unit of product or service

### Inputs
- **Location**: Revenue Page → Revenue Streams → Price per Unit
- **Field Type**: Number input
- **Range**: $0.01 to unlimited

### Outputs Affected

#### Direct Effects
- **Revenue**: Increases proportionally with price
- **Gross Profit**: Increases (assuming COGS is percentage-based)
- **Gross Margin %**: Increases (more revenue per unit)

#### Indirect Effects
- **AR Balance**: Increases (higher revenue × AR days)
- **Operating Cash Flow**: Improves (higher profit)
- **Net Income**: Increases
- **DSCR**: Improves (higher EBITDA)

### Financial Impact

#### Cash Flow Impact
- **Immediate**: Higher revenue → higher AR → cash outflow (timing)
- **Ongoing**: Higher profit → better operating cash flow
- **Net Effect**: Positive (profit increase > AR timing impact)

#### Profitability Impact
- **Gross Profit**: +$10 price increase on 100 units = +$1,000 gross profit/month
- **Net Income**: Flows through to bottom line (minus taxes)
- **Margin Improvement**: Higher price with fixed COGS = better margin

### Typical Business Decisions
- **Increase Price 10%**: Test market elasticity, improve margins
- **Premium Pricing**: Position as high-quality offering
- **Discount Pricing**: Gain market share, volume strategy
- **Value-Based Pricing**: Price based on customer value, not cost

### Examples

**Example 1: Restaurant Raising Menu Prices**
- Current: $15 average check, 1000 customers/month = $15,000 revenue
- New: $17 average check (+13%), 950 customers/month (-5% volume) = $16,150 revenue
- Result: +$1,150 revenue/month, +$805 gross profit (70% margin)

**Example 2: Service Business Premium Pricing**
- Current: $100/hour, 160 hours/month = $16,000 revenue
- New: $125/hour (+25%), 140 hours/month (-12.5% volume) = $17,500 revenue
- Result: +$1,500 revenue/month, +$1,350 gross profit (90% margin)

### Coaching Opportunities

**When User Increases Price**
- "Higher pricing improves margins, but watch for volume impact. Test with small increase first."
- "Premium pricing requires premium service. Make sure you can deliver the value."
- "Communicate value, not just price. Customers pay for benefits, not features."

**When User Decreases Price**
- "Lower pricing requires higher volume to maintain profit. Can you handle the volume?"
- "Discounting is easy, raising prices later is hard. Consider value-adds instead of discounts."
- "Race to the bottom on price rarely works. Compete on value, not price."

**When User Asks About Pricing Strategy**
- "Check competitor pricing, but don't just match. Differentiate on value."
- "Cost-plus pricing (COGS + margin) is a floor, not a ceiling. Price based on value."
- "Test pricing with small customer segment before rolling out broadly."

---

## LEVER 2: VOLUME

### Definition
Number of units sold per period

### Inputs
- **Location**: Revenue Page → Revenue Streams → Initial Volume
- **Field Type**: Number input
- **Range**: 0 to unlimited

### Outputs Affected

#### Direct Effects
- **Revenue**: Increases proportionally with volume
- **COGS**: Increases (more units = more direct costs)
- **Gross Profit**: Increases (assuming positive margin)

#### Indirect Effects
- **Working Capital**: Increases (more AR, AP, Inventory)
- **Operating Cash Flow**: Improves (if margin positive)
- **Capacity Needs**: May require more staff, space

### Financial Impact

#### Cash Flow Impact
- **Immediate**: Higher volume → higher working capital needs → cash outflow
- **Ongoing**: Higher profit → better operating cash flow
- **Net Effect**: Positive if margin > working capital impact

#### Profitability Impact
- **Gross Profit**: +10 units at $50 margin = +$500 gross profit/month
- **Operating Leverage**: Fixed costs spread over more units = better margin %
- **Scale Efficiency**: May reduce COGS % at higher volumes

### Typical Business Decisions
- **Increase Marketing**: Drive more customer traffic
- **Expand Capacity**: Add staff, space, equipment to handle volume
- **Improve Conversion**: Better sales process, customer experience
- **New Channels**: Online, wholesale, partnerships

### Examples

**Example 1: Retail Store Increasing Traffic**
- Current: 100 transactions/month, $50 average sale = $5,000 revenue
- New: 150 transactions/month (+50%), $50 average sale = $7,500 revenue
- Result: +$2,500 revenue/month, +$750 gross profit (30% margin)
- Requirement: May need additional staff for busy periods

**Example 2: Manufacturing Scaling Production**
- Current: 1,000 units/month, $100 price, 40% COGS = $60,000 gross profit
- New: 1,500 units/month (+50%), $100 price, 38% COGS (efficiency) = $93,000 gross profit
- Result: +$33,000 gross profit/month
- Requirement: More inventory, working capital

### Coaching Opportunities

**When User Increases Volume**
- "Higher volume is great, but make sure you have capacity. Can you deliver quality at scale?"
- "More volume means more working capital. Do you have cash to fund AR and inventory?"
- "Check if COGS improves at higher volume (economies of scale)."

**When User Sets Aggressive Volume**
- "Volume growth requires marketing investment. Have you budgeted for customer acquisition?"
- "Can your operations handle this volume? Consider staffing, space, equipment needs."
- "Test volume assumptions with market data. Is there enough demand?"

---

## LEVER 3: GROWTH RATE

### Definition
Annual percentage increase in volume

### Inputs
- **Location**: Revenue Page → Revenue Streams → Annual Growth Rate
- **Field Type**: Number input (percentage)
- **Range**: -100% to 1000%

### Outputs Affected

#### Direct Effects
- **Revenue**: Compounds over time
- **COGS**: Increases with revenue
- **Gross Profit**: Grows with revenue

#### Indirect Effects
- **Working Capital**: Increases (growing revenue → growing AR)
- **Capacity Needs**: May require scaling staff, space
- **Cash Flow**: Growth consumes cash (working capital)

### Financial Impact

#### Cash Flow Impact
- **Immediate**: Growth increases working capital needs → cash outflow
- **Ongoing**: Higher profit → better operating cash flow
- **Net Effect**: Growth consumes cash in early years, generates cash later

#### Profitability Impact
- **Year 1**: Base profit
- **Year 2**: Base × (1 + Growth Rate)
- **Year 3**: Base × (1 + Growth Rate)²
- **Compounding**: Dramatic impact over 3-5 years

### Typical Business Decisions
- **Conservative Growth (5-10%)**: Established business, steady expansion
- **Moderate Growth (15-25%)**: Growth business, proven model
- **Aggressive Growth (30-50%+)**: Startup, land grab, market opportunity

### Examples

**Example 1: Conservative Growth**
- Year 1: $100,000 revenue
- Year 2: $105,000 (+5%)
- Year 3: $110,250 (+5%)
- 3-Year Total: $315,250
- Cash Flow: Stable, modest working capital needs

**Example 2: Aggressive Growth**
- Year 1: $100,000 revenue
- Year 2: $150,000 (+50%)
- Year 3: $225,000 (+50%)
- 3-Year Total: $475,000
- Cash Flow: Consumes cash, requires capital injection

### Coaching Opportunities

**When User Sets High Growth (>30%)**
- "Growth above 30% is very aggressive. Can you support this with market data?"
- "High growth consumes cash for working capital. Make sure you have adequate funding."
- "Consider modeling conservative (10%), moderate (20%), and aggressive (30%) scenarios."

**When User Sets Low/Negative Growth**
- "Negative growth is concerning. Is this a declining industry or temporary issue?"
- "Even mature businesses typically grow 2-5% with inflation. 0% growth may be unrealistic."
- "If market is declining, consider diversification or pivoting."

---

## LEVER 4: COST OF GOODS SOLD (COGS)

### Definition
Direct costs to produce/deliver product or service as percentage of revenue

### Inputs
- **Location**: Revenue Page → Global COGS Settings → Default COGS Percentage
- **Field Type**: Number input (percentage)
- **Range**: 0% to 100%

### Outputs Affected

#### Direct Effects
- **COGS**: Decreases with lower percentage
- **Gross Profit**: Increases with lower COGS
- **Gross Margin %**: Improves with lower COGS

#### Indirect Effects
- **AP Balance**: Decreases (lower COGS × AP days)
- **Inventory Balance**: Decreases (lower COGS × Inv days)
- **Operating Cash Flow**: Improves (higher profit)
- **DSCR**: Improves (higher EBITDA)

### Financial Impact

#### Cash Flow Impact
- **Immediate**: Lower COGS → lower AP/Inventory → cash outflow (timing)
- **Ongoing**: Higher profit → better operating cash flow
- **Net Effect**: Strongly positive (profit increase > working capital impact)

#### Profitability Impact
- **Gross Profit**: -5% COGS on $100k revenue = +$5,000 gross profit
- **Margin Improvement**: 30% → 25% COGS = 70% → 75% gross margin
- **Bottom Line**: Flows through to net income

### Typical Business Decisions
- **Negotiate Supplier Pricing**: Volume discounts, better terms
- **Improve Efficiency**: Reduce waste, optimize processes
- **Vertical Integration**: Bring production in-house
- **Substitute Materials**: Lower-cost alternatives without quality loss

### Examples

**Example 1: Restaurant Reducing Food Costs**
- Current: 32% COGS, $30,000 revenue = $9,600 COGS, $20,400 gross profit
- New: 28% COGS (-4%), $30,000 revenue = $8,400 COGS, $21,600 gross profit
- Result: +$1,200 gross profit/month (+6%)
- Method: Better supplier contracts, reduce waste, optimize menu

**Example 2: Manufacturer Improving Efficiency**
- Current: 50% COGS, $100,000 revenue = $50,000 COGS, $50,000 gross profit
- New: 45% COGS (-5%), $100,000 revenue = $45,000 COGS, $55,000 gross profit
- Result: +$5,000 gross profit/month (+10%)
- Method: Process improvements, automation, better sourcing

### Coaching Opportunities

**When User Sets High COGS (>70%)**
- "COGS above 70% leaves little room for overhead and profit. Can you reduce costs or increase pricing?"
- "High COGS businesses need high volume to succeed. Make sure you can scale."
- "Look for efficiency opportunities: waste reduction, better suppliers, process improvements."

**When User Reduces COGS**
- "Lower COGS is great, but don't sacrifice quality. Customers notice."
- "COGS reduction compounds with revenue growth. Small improvements have big impact."
- "Track COGS monthly. It should improve over time as you gain efficiency."

---

## LEVER 5: PAYROLL

### Definition
Total employee compensation including wages, taxes, and benefits

### Inputs
- **Location**: Payroll Page → Multiple roles
- **Components**: Headcount, Rate, Taxes, Benefits, Raises

### Outputs Affected

#### Direct Effects
- **Operating Expenses**: Increases with more/higher-paid staff
- **EBITDA**: Decreases with higher payroll
- **COGS**: Increases if direct labor

#### Indirect Effects
- **Capacity**: More staff = more capacity
- **Quality**: Better staff = better service
- **DSCR**: Decreases (lower EBITDA)

### Financial Impact

#### Cash Flow Impact
- **Immediate**: Payroll is cash outflow every period
- **Ongoing**: Fixed cost regardless of revenue
- **Net Effect**: Negative on cash, positive on capacity

#### Profitability Impact
- **Operating Leverage**: Fixed cost, so margin improves as revenue grows
- **Labor %**: Target 20-40% of revenue depending on industry
- **Efficiency**: Revenue per employee is key metric

### Typical Business Decisions
- **Hire More Staff**: Increase capacity, improve service
- **Reduce Headcount**: Cut costs, improve efficiency
- **Increase Wages**: Attract/retain talent, improve quality
- **Automate**: Replace labor with technology

### Examples

**Example 1: Adding Sales Staff**
- Current: 2 salespeople, $50k each = $100k payroll
- New: 3 salespeople (+1), $50k each = $150k payroll
- Cost: +$50k payroll/year (+$4,167/month)
- Benefit: +$200k revenue/year if each generates $100k
- Net: +$150k revenue - $50k payroll = +$100k gross profit (assuming 50% margin)

**Example 2: Reducing Overhead Staff**
- Current: 5 admin staff, $40k each = $200k payroll
- New: 4 admin staff (-1), $40k each = $160k payroll
- Savings: -$40k payroll/year (-$3,333/month)
- Impact: +$3,333 cash flow/month, +$40k net income/year

### Coaching Opportunities

**When User Adds Staff**
- "More staff increases capacity, but also fixed costs. Make sure revenue justifies the hire."
- "Calculate revenue per employee. Industry benchmarks help determine if you're overstaffed."
- "Don't forget taxes (7.65%+) and benefits (10-30%). True cost is 20-40% above wages."

**When User Reduces Staff**
- "Cutting staff saves money but reduces capacity. Can you maintain service quality?"
- "Consider attrition, automation, or outsourcing before layoffs."
- "Labor cuts flow straight to bottom line, but may hurt growth."

---

## LEVER 6: OPERATING EXPENSES

### Definition
Fixed and variable overhead costs (rent, utilities, marketing, etc.)

### Inputs
- **Location**: Operating Expenses Page → Multiple categories
- **Types**: Fixed, Semi-Fixed, Variable % Revenue

### Outputs Affected

#### Direct Effects
- **Operating Expenses**: Increases with higher costs
- **EBITDA**: Decreases with higher expenses
- **Net Income**: Decreases with higher expenses

#### Indirect Effects
- **DSCR**: Decreases (lower EBITDA)
- **Cash Flow**: Decreases (more cash outflow)
- **Break-Even**: Increases (need more revenue to cover costs)

### Financial Impact

#### Cash Flow Impact
- **Immediate**: Operating expenses are cash outflow
- **Ongoing**: Fixed costs regardless of revenue
- **Net Effect**: Negative on cash and profit

#### Profitability Impact
- **Operating Leverage**: Fixed costs, so margin improves as revenue grows
- **Opex %**: Target 20-40% of revenue depending on industry
- **Efficiency**: Revenue per dollar of opex

### Typical Business Decisions
- **Reduce Rent**: Relocate, negotiate, downsize
- **Cut Marketing**: Reduce customer acquisition costs
- **Renegotiate Contracts**: Insurance, utilities, services
- **Eliminate Waste**: Subscriptions, unused services

### Examples

**Example 1: Relocating to Lower Rent**
- Current: $5,000/month rent (15% of $33k revenue)
- New: $3,000/month rent (-$2,000)
- Savings: -$24,000/year
- Impact: +$24,000 net income, +$24,000 cash flow
- Consideration: Location impact on revenue

**Example 2: Increasing Marketing**
- Current: $1,000/month marketing
- New: $3,000/month marketing (+$2,000)
- Cost: +$24,000/year
- Benefit: +$100,000 revenue (5:1 ROI)
- Net: +$100k revenue × 50% margin - $24k marketing = +$26k net income

### Coaching Opportunities

**When User Has High Rent (>12% of revenue)**
- "Rent above 12% of revenue is a yellow flag. Can you negotiate, relocate, or grow revenue?"
- "High rent is fixed cost. Make sure you have volume to support it."
- "Consider revenue per square foot. Are you using space efficiently?"

**When User Cuts Marketing**
- "Cutting marketing saves money short-term but may hurt revenue long-term."
- "Track customer acquisition cost (CAC) and lifetime value (LTV). Marketing is investment, not expense."
- "Test marketing channels. Cut what doesn't work, invest in what does."

---

## LEVER 7: LOAN AMOUNT

### Definition
Total amount borrowed to finance business

### Inputs
- **Location**: Financing Page → Loan Amount
- **Related**: Interest Rate, Term

### Outputs Affected

#### Direct Effects
- **Interest Expense**: Increases with higher principal
- **Debt Service**: Increases (higher payment)
- **DSCR**: Decreases (higher debt service)

#### Indirect Effects
- **Cash Flow**: Decreases (higher payment)
- **Beginning Cash**: Increases (loan proceeds)
- **Risk**: Increases (more debt = more risk)

### Financial Impact

#### Cash Flow Impact
- **Period 0**: +Loan proceeds (cash inflow)
- **Ongoing**: -Monthly payment (cash outflow)
- **Net Effect**: Provides liquidity but costs interest

#### Profitability Impact
- **Interest Expense**: Reduces net income
- **Leverage**: Can amplify returns if ROIC > interest rate
- **Risk**: Higher debt = higher risk of default

### Typical Business Decisions
- **Borrow More**: Fund growth, working capital, equipment
- **Borrow Less**: Reduce risk, lower payments
- **Refinance**: Lower rate, extend term
- **Pay Down Early**: Reduce interest, improve DSCR

### Examples

**Example 1: Increasing Loan for Working Capital**
- Current: $100k loan, 6%, 10 years = $1,110/month payment
- New: $150k loan (+$50k), 6%, 10 years = $1,665/month payment
- Cost: +$555/month payment, +$250/month interest (avg)
- Benefit: +$50k cash for working capital
- Net: Better liquidity, higher debt service

**Example 2: Reducing Loan to Improve DSCR**
- Current: $200k loan, DSCR = 1.15 (risky)
- New: $150k loan (-$50k), DSCR = 1.45 (healthy)
- Trade-off: Less cash, better debt coverage
- Decision: Depends on cash needs vs. lender requirements

### Coaching Opportunities

**When User Borrows Too Much (DSCR < 1.25)**
- "DSCR below 1.25 is risky. Lenders may not approve, or you may struggle to make payments."
- "Consider borrowing less, improving EBITDA, or extending loan term."
- "Run scenarios: What if revenue is 10% lower? Can you still make payments?"

**When User Borrows Too Little**
- "You may run out of cash in Month X. Consider borrowing more or reducing expenses."
- "Undercapitalization is a top reason businesses fail. Better to have buffer."
- "Lenders prefer to lend more than you need than have you come back for more later."

---

## LEVER 8: WORKING CAPITAL (AR/AP/Inventory Days)

### Definition
Cash tied up in operations (receivables, payables, inventory)

### Inputs
- **Location**: Financing Page → Working Capital
- **Components**: AR Days, AP Days, Inventory Days

### Outputs Affected

#### Direct Effects
- **AR Balance**: Increases with more AR days
- **AP Balance**: Increases with more AP days
- **Inventory Balance**: Increases with more inventory days

#### Indirect Effects
- **Operating Cash Flow**: Decreases with higher working capital
- **Cash Needs**: Increases (more cash tied up)
- **Liquidity**: Decreases (less available cash)

### Financial Impact

#### Cash Flow Impact
- **AR Days**: +10 days = -$X cash (financing customers)
- **AP Days**: +10 days = +$X cash (supplier financing)
- **Inventory Days**: +10 days = -$X cash (stock on hand)
- **Net Effect**: Optimize balance between cash and operations

#### Profitability Impact
- **No Direct Impact**: Working capital doesn't affect profit
- **Indirect Impact**: Better terms may improve supplier pricing

### Typical Business Decisions
- **Reduce AR Days**: Faster collection, deposits, credit cards
- **Increase AP Days**: Negotiate longer terms with suppliers
- **Reduce Inventory Days**: Just-in-time, better forecasting
- **Increase Inventory Days**: Avoid stockouts, seasonal buildup

### Examples

**Example 1: Reducing AR Days**
- Current: 45 days AR, $100k revenue/month = $150k AR balance
- New: 30 days AR (-15 days), $100k revenue/month = $100k AR balance
- Cash Impact: +$50k cash freed up (one-time)
- Method: Require deposits, offer early payment discounts, use credit cards

**Example 2: Negotiating Longer AP Terms**
- Current: 30 days AP, $50k COGS/month = $50k AP balance
- New: 45 days AP (+15 days), $50k COGS/month = $75k AP balance
- Cash Impact: +$25k cash (supplier financing, one-time)
- Method: Negotiate with suppliers, commit to volume, pay reliably

### Coaching Opportunities

**When User Has High AR Days (>45)**
- "AR above 45 days means you're financing customers. Can you collect faster?"
- "Consider deposits, progress payments, or credit card processing."
- "Slow collection increases bad debt risk. Track aging and follow up promptly."

**When User Has Low AP Days (<15)**
- "You're paying suppliers quickly. Can you negotiate longer terms to improve cash flow?"
- "Longer AP is free financing. Most suppliers offer Net 30, some offer Net 45-60."
- "Balance early payment discounts (2/10 Net 30) vs. cash flow needs."

---

## Summary: Lever Impact Matrix

| Lever | Profitability | Cash Flow | DSCR | Difficulty | Impact Speed |
|-------|--------------|-----------|------|------------|--------------|
| **Increase Price** | ↑↑↑ High | ↑↑ Medium | ↑↑ High | Medium | Immediate |
| **Increase Volume** | ↑↑ Medium | ↑ Low | ↑ Medium | High | Slow |
| **Increase Growth** | ↑↑↑ High | ↓ Negative | ↑ Medium | High | Slow |
| **Reduce COGS** | ↑↑↑ High | ↑↑ Medium | ↑↑ High | Medium | Medium |
| **Reduce Payroll** | ↑↑ Medium | ↑↑ Medium | ↑↑ High | High | Medium |
| **Reduce Opex** | ↑↑ Medium | ↑↑ Medium | ↑↑ High | Medium | Fast |
| **Reduce Loan** | ↓ Negative | ↑↑ Medium | ↑↑↑ High | Low | Immediate |
| **Reduce AR Days** | — None | ↑↑ Medium | — None | Medium | Fast |
| **Increase AP Days** | — None | ↑↑ Medium | — None | Easy | Fast |
| **Reduce Inv Days** | — None | ↑ Low | — None | Medium | Medium |

**Legend:**
- ↑↑↑ = Very Positive Impact
- ↑↑ = Positive Impact
- ↑ = Small Positive Impact
- ↓ = Negative Impact
- — = No Impact

---

**Coaching Note for Eric**: Use this lever library to guide entrepreneurs toward the highest-impact changes. Focus on levers that improve both profitability AND cash flow (pricing, COGS reduction, opex reduction). Working capital levers improve cash without hurting profit—quick wins for cash-strapped businesses.

