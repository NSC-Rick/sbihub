# 03 Screen Documentation

## Overview

This document provides comprehensive documentation for every screen in the Operating Model application. Each screen is documented with its purpose, business objective, navigation path, inputs, outputs, calculations, dependencies, validation rules, and common user questions.

---

## 🏠 HOME PAGE

### Screen Name
**Home** (Model Management & Configuration)

### Purpose
Central hub for model management, scenario control, and time mode configuration. This is the starting point for all users and the place to save/load work.

### Business Objective
Enable users to:
- Save and restore their work
- Switch between different business scenarios
- Configure fundamental model parameters (time mode)
- Export models for external analysis
- Reset to defaults when starting fresh

### Navigation Path
**Sidebar → 🏠 Home** (First item in navigation)

### Information Displayed

#### Session Status Section
- **Session Recovery Status**: Indicates if a saved session exists
- **Last Saved Timestamp**: Shows when model was last saved (e.g., "5 min ago")
- **Restore Last Session Button**: Allows recovery of previous session

#### Model Management Section
- **Model Name Input**: Text field for naming the scenario
- **Save Model Button**: Downloads scenario as JSON file
- **Export to Excel Button**: Downloads model as Excel workbook (if openpyxl installed)
- **Upload Model**: File uploader for loading saved JSON scenarios
- **Reset to Defaults Button**: Clears all inputs and restores defaults

#### Time Mode Configuration
- **Time Mode Radio Buttons**: Monthly or Annual selection
- **Forecast Length Metric**: Displays "3 Years (36 periods)" or "3 Years (3 periods)"

#### Video Tutorial
- **Embedded YouTube Video**: 2-minute introduction to the Modeler

### Inputs Required

#### Model Name
- **Field**: Text input
- **Default**: "Business Scenario"
- **Purpose**: Identifies the scenario for save/load operations
- **Validation**: Any text allowed
- **Business Impact**: Used in filename when saving

#### Time Mode
- **Field**: Radio button (Monthly / Annual)
- **Default**: Monthly
- **Purpose**: Determines granularity of projections
- **Options**:
  - **Monthly**: 36 periods (3 years × 12 months)
  - **Annual**: 3 periods (3 years)
- **Business Impact**: Affects all calculations, growth rates, and cash flow timing

#### Scenario File Upload
- **Field**: File uploader
- **Accepted Format**: JSON only
- **Purpose**: Load previously saved scenario
- **Validation**: JSON structure validation, schema checking

### Calculations Performed
- **None** (This is a configuration page, not a calculation page)
- Time mode selection triggers period count update (36 or 3)
- Scenario validation occurs on file upload

### Reports Affected
- **All Reports**: Time mode affects all downstream calculations
- Changing time mode requires rebuilding model in Review page

### Dependencies

#### Upstream Dependencies
- **None** (This is the entry point)

#### Downstream Dependencies
- **All Pages**: Time mode setting affects all calculations
- **Revenue Page**: Growth rates converted to monthly if time_mode = 'monthly'
- **Payroll Page**: Raises calculated monthly if time_mode = 'monthly'
- **Operating Expenses Page**: Growth rates converted to monthly if time_mode = 'monthly'
- **Review Page**: Number of periods determines statement length

### Validation Rules

#### Model Name
- No validation (any text accepted)
- Used for filename generation (sanitized: spaces → underscores, special chars removed)

#### Scenario File Upload
- Must be valid JSON format
- Must contain required keys: time_mode, periods, revenue_streams, etc.
- Schema validation prevents loading incompatible files
- Error messages displayed for invalid files

#### Time Mode
- Must be 'monthly' or 'annual'
- Changing mode resets periods automatically

### Business Rationale

#### Why Save/Load Scenarios?
- **Scenario Comparison**: Test different business assumptions
- **Collaboration**: Share models with advisors, lenders, partners
- **Version Control**: Track model evolution over time
- **Safety Net**: Recover from mistakes or experiments

#### Why Time Mode Selection?
- **Monthly Mode**: Better for cash flow analysis, seasonal businesses, startups
- **Annual Mode**: Simpler for established businesses, long-term planning
- **Flexibility**: Users choose granularity that matches their needs

#### Why Session Auto-Save?
- **Prevent Data Loss**: Browser refresh doesn't lose work
- **Seamless Experience**: Users don't need to manually save constantly
- **Recovery**: Can restore session after accidental closure

### Frequently Asked Questions

**Q: What's the difference between Save Model and Session Auto-Save?**  
A: Session auto-save stores your work in browser memory (temporary). Save Model downloads a JSON file you can keep permanently and reload anytime.

**Q: Can I switch from Monthly to Annual mode after configuring inputs?**  
A: Yes, but it will change the number of periods from 36 to 3. All calculations adjust automatically, but you may want to review your assumptions.

**Q: What happens if I reset to defaults?**  
A: All inputs are cleared and replaced with default values. This action cannot be undone, so save your scenario first if you want to keep it.

**Q: Can I edit the JSON file manually?**  
A: Yes, advanced users can edit JSON files in a text editor. The file is human-readable and follows a documented schema.

**Q: Why can't I export to Excel?**  
A: Excel export requires the openpyxl Python library. If not installed, the button is disabled. This is an optional feature.

**Q: How do I compare two scenarios?**  
A: Save Scenario A, modify inputs, save Scenario B. Then load Scenario A, review results, load Scenario B, review results. Compare manually or in Excel.

**Q: What's included in the JSON file?**  
A: Everything: revenue streams, payroll roles, operating expenses, loan terms, working capital settings, capital stack, seasonality, and all configuration options.

**Q: Can I share my scenario with someone else?**  
A: Yes, send them the JSON file. They can load it in their own instance of the Operating Model.

### Common User Misunderstandings

**Misunderstanding 1**: "Session auto-save means my work is saved permanently"  
**Reality**: Session auto-save is browser-based and temporary. Always download JSON files for permanent storage.

**Misunderstanding 2**: "I can switch time modes without affecting my model"  
**Reality**: Switching from Monthly (36 periods) to Annual (3 periods) changes the projection length. Growth rates are recalculated automatically.

**Misunderstanding 3**: "Reset to Defaults will just clear my current page"  
**Reality**: Reset clears ALL inputs across ALL pages, not just the current page.

**Misunderstanding 4**: "The model name doesn't matter"  
**Reality**: Model name is used in filenames and helps you identify scenarios later. Use descriptive names like "Base_Case" or "High_Growth_Scenario".

### Coaching Opportunities

**Opportunity 1: Time Mode Selection**  
When user selects time mode, explain:
- "Monthly mode gives you 36 months of detail, which is great for cash flow analysis and seasonal businesses"
- "Annual mode simplifies to 3 years, which works well for established businesses with stable patterns"
- "Most lenders prefer monthly projections for the first year"

**Opportunity 2: Scenario Naming**  
When user names scenario, suggest:
- "Use descriptive names like 'Conservative_Case' or 'Optimistic_Growth'"
- "Include dates if you're tracking versions: 'Base_Case_Jan2024'"
- "Avoid generic names like 'Scenario1' that are hard to identify later"

**Opportunity 3: First Save**  
When user saves first scenario, celebrate:
- "Great! You've created your first financial model"
- "This JSON file contains all your assumptions and can be loaded anytime"
- "Consider saving multiple scenarios to compare different business strategies"

**Opportunity 4: Reset Warning**  
When user clicks Reset, emphasize:
- "This will erase all your work. Make sure you've saved your scenario first!"
- "Reset is useful when starting a completely new business model"
- "You can always reload your saved scenario if you change your mind"

---

## 💵 REVENUE PAGE

### Screen Name
**Revenue Streams** (Revenue Planning & Configuration)

### Purpose
Configure all revenue-generating activities including pricing, volume, growth, cost of goods sold (COGS), seasonality, and startup ramp assumptions.

### Business Objective
Enable users to:
- Define how the business makes money
- Set realistic pricing and volume assumptions
- Project revenue growth over time
- Configure cost of goods sold (COGS)
- Apply seasonal patterns to revenue
- Model startup ramp periods for new businesses

### Navigation Path
**Sidebar → 💵 Revenue** (Second item in navigation)

### Information Displayed

#### Global COGS Settings
- **Default COGS Percentage**: Slider (0% to 100%)
- **COGS Guidance Panel**: Industry benchmarks and recommendations
- **COGS Improvement per Year**: Annual efficiency improvement rate

#### Revenue Seasonality
- **Seasonality Mode**: OFF / Retail Preset / Custom
- **Monthly Weight Chart**: Visual bar chart showing seasonal distribution
- **Custom Weight Inputs**: 12 monthly weight fields (if Custom mode)

#### Revenue Input Method
- **Method Selector**: Monthly Revenue Target / Avg Sale × Monthly Transactions / Customers per Day × Days Open
- **Input Fields**: Vary based on selected method

#### Startup Revenue Ramp
- **Ramp Months**: Number of months to reach steady-state revenue

#### Revenue Streams
- **Stream List**: Expandable sections for each revenue stream
- **Add Revenue Stream Button**: Creates new stream

### Inputs Required

#### Global COGS Percentage
- **Field**: Number input (0.0 to 1.0)
- **Default**: 0.30 (30%)
- **Purpose**: Default cost of goods sold for all revenue streams
- **Business Impact**: Determines gross profit margin
- **Typical Values**:
  - Retail: 50-70%
  - Restaurants: 28-35%
  - Manufacturing: 40-60%
  - Services: 5-20%
  - Software: 0-15%

#### COGS Improvement per Year
- **Field**: Number input (0.0 to 10.0%)
- **Default**: 0.0%
- **Purpose**: Annual reduction in COGS as efficiency improves
- **Business Impact**: Gross margin increases over time
- **Example**: 2% improvement means COGS drops from 30% to 29.4% in Year 1, 28.8% in Year 2

#### Seasonality Mode
- **Field**: Radio button (OFF / Retail Preset / Custom)
- **Default**: OFF
- **Purpose**: Apply monthly revenue patterns
- **Business Impact**: Revenue distributed unevenly across months
- **Retail Preset**: Holiday-weighted (Nov: 11%, Dec: 17.5%)

#### Revenue Input Method
- **Field**: Radio button selector
- **Options**:
  1. **Monthly Revenue Target**: Direct revenue input
  2. **Avg Sale × Monthly Transactions**: Transaction-based calculation
  3. **Customers per Day × Days Open**: Behavioral model (Advanced mode only)
- **Purpose**: Different ways to estimate revenue
- **Business Impact**: Affects how revenue is calculated and displayed

#### Startup Ramp Months
- **Field**: Number input (0 to 24)
- **Default**: 0 (disabled)
- **Purpose**: Model gradual revenue growth from 0% to 100%
- **Business Impact**: Reduces early-period revenue, affects cash flow
- **Typical Values**:
  - Retail: 3-6 months
  - Restaurant: 6-12 months
  - Service: 3-6 months
  - Manufacturing: 12-24 months

#### Per-Stream Inputs
For each revenue stream:
- **Stream Name**: Text (e.g., "Product Sales", "Consulting Services")
- **Price per Unit**: Dollar amount
- **Initial Volume**: Units per period
- **Annual Growth Rate**: Percentage (e.g., 0.10 = 10%)
- **COGS Override**: Optional stream-specific COGS percentage

### Calculations Performed

#### Revenue Calculation
```
For each period:
  Base Revenue = Price × Volume × (1 + Growth Rate)^period
  
  If Seasonality Enabled:
    Seasonal Multiplier = Monthly Weight / (100/12)
    Base Revenue = Base Revenue × Seasonal Multiplier
  
  If Startup Ramp Enabled:
    Ramp Factor = min(1.0, (period + 1) / ramp_months)
    Base Revenue = Base Revenue × Ramp Factor
  
  Period Revenue = Base Revenue
```

#### COGS Calculation
```
For each period:
  If COGS Improvement > 0:
    Year Index = period / 12 (monthly) or period (annual)
    Adjusted COGS % = Base COGS % × (1 - Improvement Rate)^Year Index
  Else:
    Adjusted COGS % = Base COGS %
  
  Period COGS = Period Revenue × Adjusted COGS %
```

#### Growth Rate Conversion
```
If Time Mode = Monthly:
  Monthly Growth = (1 + Annual Growth)^(1/12) - 1
  Volume[period] = Initial Volume × (1 + Monthly Growth)^period

If Time Mode = Annual:
  Volume[period] = Initial Volume × (1 + Annual Growth)^period
```

### Reports Affected
- **Income Statement**: Revenue (top line), COGS, Gross Profit
- **Cash Flow Statement**: Operating cash flow (via revenue)
- **KPIs**: Gross margin percentage, revenue growth
- **Charts**: Revenue trend chart
- **Working Capital**: AR balance (based on revenue × AR days)

### Dependencies

#### Upstream Dependencies
- **Home Page**: Time mode determines monthly vs. annual calculations
- **Financing Page**: Mode (Basic/Advanced) determines available input methods

#### Downstream Dependencies
- **Income Statement**: Revenue flows to top line
- **COGS**: Flows to income statement
- **Gross Profit**: Revenue - COGS
- **Working Capital**: AR = Revenue × (AR days / days in period)
- **Variable Expenses**: If opex uses "% of revenue" category

### Validation Rules

#### COGS Percentage
- Must be between 0.0 and 1.0 (0% to 100%)
- Warning if > 0.90 (90%) - unsustainable for most businesses
- Guidance panel shows industry benchmarks

#### Growth Rate
- Must be between -1.0 and 10.0 (-100% to 1000%)
- Warning if > 0.30 (30% annually) - very aggressive
- Typical range: 5-15% for established businesses, 20-50% for startups

#### Seasonality Weights
- Custom weights auto-normalize to 100%
- All weights must be >= 0
- At least one weight must be > 0

#### Startup Ramp
- Must be between 0 and 24 months
- 0 = disabled (no ramp)
- Warning if > 12 months for service businesses

#### Revenue Stream Name
- Must not be empty
- Duplicate names allowed but discouraged

### Business Rationale

#### Why Multiple Revenue Streams?
- **Diversification**: Reduce dependency on single product/service
- **Granularity**: Track performance by product line
- **Pricing Flexibility**: Different COGS for different offerings
- **Growth Modeling**: Different growth rates by stream

#### Why COGS Matters?
- **Gross Margin**: Determines profitability potential
- **Pricing Power**: Low COGS = more pricing flexibility
- **Scalability**: Lower COGS = better unit economics
- **Lender Analysis**: Lenders evaluate gross margin sustainability

#### Why Seasonality?
- **Cash Flow Accuracy**: Seasonal businesses have uneven cash needs
- **Working Capital**: Seasonal peaks require more inventory/AR
- **Realistic Planning**: Avoid assuming even monthly revenue
- **Lender Credibility**: Shows understanding of business patterns

#### Why Startup Ramp?
- **Realistic Expectations**: New businesses don't reach full capacity immediately
- **Cash Flow Planning**: Identifies early-period cash needs
- **Marketing Reality**: Customer acquisition takes time
- **Operational Reality**: Efficiency improves with experience

### Frequently Asked Questions

**Q: How many revenue streams should I have?**  
A: Start with 1-3 main streams. Too many streams create complexity without adding value. Group similar products/services together.

**Q: What's a realistic growth rate?**  
A: Established businesses: 5-15% annually. Startups: 20-50% in early years, declining to 10-20% as they mature. Be conservative - lenders discount aggressive projections.

**Q: What is COGS and how do I estimate it?**  
A: COGS (Cost of Goods Sold) is the direct cost to produce your product or deliver your service. Check industry benchmarks or analyze competitor financials. When in doubt, use 30% as a starting point.

**Q: Should I use seasonality?**  
A: Yes, if your business has predictable seasonal patterns (retail, tourism, landscaping). No, if revenue is relatively even throughout the year (most B2B services).

**Q: What's a startup ramp and do I need it?**  
A: Startup ramp models the time it takes to reach full revenue capacity. Use it for new businesses. Set to 0 for existing businesses or acquisitions.

**Q: Can I have different COGS for different revenue streams?**  
A: Yes! Use the "Override COGS %" checkbox. Example: Product sales might be 60% COGS while consulting services are 10% COGS.

**Q: What if I don't know my exact pricing yet?**  
A: Use your best estimate based on market research and competitor pricing. You can always adjust later and save multiple scenarios.

**Q: Should marketing be included in COGS?**  
A: No. COGS is only DIRECT costs (materials, direct labor, shipping). Marketing is an operating expense, configured on the Operating Expenses page.

**Q: What's the difference between the three revenue input methods?**  
A: 
- **Monthly Revenue Target**: Simple - just enter total revenue
- **Avg Sale × Transactions**: Better for transaction-based businesses (retail, restaurants)
- **Customers per Day**: Most detailed - models daily traffic patterns (Advanced mode only)

**Q: How does COGS improvement work?**  
A: If you set 2% annual improvement, your COGS percentage decreases each year as you gain efficiency. Example: Year 1 = 30%, Year 2 = 29.4%, Year 3 = 28.8%.

### Common User Misunderstandings

**Misunderstanding 1**: "COGS includes all my expenses"  
**Reality**: COGS is only DIRECT costs to produce/deliver. Rent, marketing, salaries are operating expenses, not COGS.

**Misunderstanding 2**: "Growth rate is monthly"  
**Reality**: Growth rate is ANNUAL, even in monthly mode. The system converts it to monthly growth automatically.

**Misunderstanding 3**: "I should set aggressive growth to impress lenders"  
**Reality**: Lenders discount unrealistic projections. Conservative, well-supported assumptions are more credible.

**Misunderstanding 4**: "Seasonality is only for retail"  
**Reality**: Many businesses have seasonality: landscaping (weather), accounting (tax season), tourism (summer), construction (weather).

**Misunderstanding 5**: "Startup ramp means revenue starts at zero"  
**Reality**: Startup ramp means revenue gradually increases from 0% to 100% of your target. If ramp = 6 months, Month 1 is 16.7% of target, Month 6 is 100%.

**Misunderstanding 6**: "I need a separate revenue stream for every product"  
**Reality**: Group similar products together. "Widget Sales" can represent 10 different widgets. Too much detail creates complexity.

### Coaching Opportunities

**Opportunity 1: COGS Estimation**  
When user sets COGS, explain:
- "COGS of 30% means for every $100 in sales, $30 goes to direct costs, leaving $70 gross profit"
- "Your industry benchmark is [X]%. You're at [Y]%, which is [higher/lower]. This affects your pricing power."
- "Lower COGS = higher gross margin = more money to cover overhead and generate profit"

**Opportunity 2: Growth Rate Reality Check**  
When user sets growth > 25%, caution:
- "Growth above 25% annually is very aggressive. Can you support this with market data?"
- "High growth requires marketing investment, working capital, and operational capacity"
- "Consider modeling a conservative case (10%) and optimistic case (25%) separately"

**Opportunity 3: Seasonality Impact**  
When user enables seasonality, explain:
- "Seasonal businesses need more working capital during peak months"
- "Your cash flow will be uneven - expect low cash in slow months"
- "Plan for seasonal hiring and inventory buildup before peak season"

**Opportunity 4: Startup Ramp Planning**  
When user sets startup ramp, discuss:
- "Ramp of 6 months means you'll reach full revenue in Month 6"
- "This creates a cash flow gap in early months - make sure you have enough startup capital"
- "Marketing, word-of-mouth, and operational efficiency all improve during ramp period"

**Opportunity 5: Multiple Revenue Streams**  
When user adds streams, guide:
- "Multiple streams reduce risk - if one declines, others can compensate"
- "But don't over-complicate - 2-3 main streams is usually enough"
- "Consider grouping similar products/services into one stream"

---

## 👥 PAYROLL PAGE

### Screen Name
**Payroll & Personnel** (Staffing & Compensation Planning)

### Purpose
Configure all employee-related costs including wages, payroll taxes, benefits, and raises. Classify labor as direct (production) or indirect (overhead).

### Business Objective
Enable users to:
- Plan staffing needs by role
- Set competitive compensation
- Include employer costs (taxes, benefits)
- Project salary increases over time
- Classify labor costs correctly (COGS vs. Operating Expenses)

### Navigation Path
**Sidebar → 👥 Payroll** (Third item in navigation)

### Information Displayed

#### Payroll Roles Section
- **Role List**: Expandable sections for each role
- **Add Payroll Role Button**: Creates new role

#### Per-Role Display
- **Role Title**: Name of position
- **Headcount**: Number of employees
- **Pay Type**: Salary or Hourly
- **Compensation**: Annual salary or hourly rate
- **Hours per Week**: For hourly employees
- **Annual Raise %**: Yearly increase
- **Payroll Tax %**: Employer taxes (FICA, etc.)
- **Benefits %**: Benefits as percentage of wages
- **Role Type**: Direct (COGS) or Indirect (Opex)

### Inputs Required

#### Role Title
- **Field**: Text input
- **Default**: "Role 1", "Role 2", etc.
- **Purpose**: Identify the position
- **Examples**: "Manager", "Sales Associate", "Production Worker", "Bookkeeper"

#### Headcount
- **Field**: Integer input (0+)
- **Default**: 1
- **Purpose**: Number of employees in this role
- **Business Impact**: Multiplies all costs by headcount

#### Pay Type
- **Field**: Dropdown (Salary / Hourly)
- **Default**: Salary
- **Purpose**: Determines how compensation is calculated
- **Salary**: Annual amount, paid evenly
- **Hourly**: Rate × hours worked

#### Rate
- **Field**: Number input
- **For Salary**: Annual salary (e.g., $60,000)
- **For Hourly**: Hourly wage (e.g., $15.00)
- **Purpose**: Base compensation before taxes and benefits

#### Hours per Week
- **Field**: Number input (0 to 168)
- **Default**: 40
- **Purpose**: For hourly employees, determines annual hours
- **Calculation**: Annual hours = Hours per Week × 52

#### Annual Raise %
- **Field**: Number input (0.0 to 1.0)
- **Default**: 0.03 (3%)
- **Purpose**: Yearly salary increase
- **Business Impact**: Compounds over time
- **Typical Values**: 2-5% for cost-of-living, 5-10% for performance/promotion

#### Payroll Tax %
- **Field**: Number input (0.0 to 1.0)
- **Default**: 0.0765 (7.65%)
- **Purpose**: Employer portion of payroll taxes
- **Minimum**: 7.65% (FICA: 6.2% Social Security + 1.45% Medicare)
- **May Include**: State unemployment, federal unemployment, workers comp

#### Benefits %
- **Field**: Number input (0.0 to 1.0)
- **Default**: 0.15 (15%)
- **Purpose**: Benefits as percentage of wages
- **Includes**: Health insurance, retirement contributions, paid time off
- **Typical Values**: 10-30% depending on benefits package

#### Role Type
- **Field**: Dropdown (Direct / Indirect)
- **Default**: Indirect
- **Purpose**: Determines where cost flows in financial statements
- **Direct**: Production labor → flows to COGS
- **Indirect**: Administrative/overhead → flows to Operating Expenses

### Calculations Performed

#### Salary Employee (Monthly Mode)
```
For each period:
  Years Elapsed = period / 12
  Raise Multiplier = (1 + Annual Raise %)^Years Elapsed
  
  Monthly Wages = (Annual Salary / 12) × Headcount × Raise Multiplier
  Monthly Taxes = Monthly Wages × Payroll Tax %
  Monthly Benefits = Monthly Wages × Benefits %
  
  Total Monthly Cost = Monthly Wages + Monthly Taxes + Monthly Benefits
```

#### Hourly Employee (Monthly Mode)
```
For each period:
  Years Elapsed = period / 12
  Raise Multiplier = (1 + Annual Raise %)^Years Elapsed
  
  Monthly Hours = (Hours per Week × 52) / 12
  Monthly Wages = Hourly Rate × Monthly Hours × Headcount × Raise Multiplier
  Monthly Taxes = Monthly Wages × Payroll Tax %
  Monthly Benefits = Monthly Wages × Benefits %
  
  Total Monthly Cost = Monthly Wages + Monthly Taxes + Monthly Benefits
```

#### Direct vs. Indirect Classification
```
If Role Type = Direct:
  Cost flows to COGS (reduces Gross Profit)
Else:
  Cost flows to Operating Expenses (reduces EBITDA)
```

### Reports Affected
- **Income Statement**: 
  - Direct labor → COGS
  - Indirect labor → Operating Expenses (Payroll line)
- **Cash Flow Statement**: Payroll affects operating cash flow
- **KPIs**: Labor cost as % of revenue

### Dependencies

#### Upstream Dependencies
- **Home Page**: Time mode determines monthly vs. annual calculations

#### Downstream Dependencies
- **Income Statement**: Payroll flows to COGS (direct) or Opex (indirect)
- **Cash Flow**: Payroll is cash outflow
- **Working Capital**: Payroll may affect AP if accrued

### Validation Rules

#### Headcount
- Must be >= 0
- Warning if > 50 for small business model

#### Rate
- Must be > 0 if headcount > 0
- Warning if salary < $20,000 (below minimum wage equivalent)
- Warning if hourly rate < $7.25 (federal minimum wage)

#### Hours per Week
- Must be between 0 and 168 (hours in a week)
- Warning if > 60 (overtime concerns)
- Typical: 40 for full-time, 20-30 for part-time

#### Annual Raise %
- Must be between 0.0 and 1.0
- Warning if > 0.10 (10% is very high)
- Typical: 0.02-0.05 (2-5%)

#### Payroll Tax %
- Must be >= 0.0765 (minimum FICA)
- Warning if < 0.0765 (missing required taxes)
- Typical: 0.08-0.12 (includes state/federal unemployment)

#### Benefits %
- Must be >= 0.0
- Warning if > 0.50 (50% is very high)
- Typical: 0.10-0.30 (10-30%)

### Business Rationale

#### Why Separate Payroll from Operating Expenses?
- **Visibility**: Payroll is often the largest expense
- **Classification**: Direct vs. indirect labor affects gross margin
- **Benchmarking**: Labor cost % is key metric
- **Planning**: Headcount planning is strategic decision

#### Why Include Payroll Taxes?
- **True Cost**: Employer pays 7.65% minimum on top of wages
- **Legal Requirement**: FICA, unemployment insurance are mandatory
- **Cash Flow**: Taxes are cash outflow, must be budgeted
- **Lender Expectation**: Lenders expect fully-loaded labor costs

#### Why Include Benefits?
- **Competitive Hiring**: Benefits are part of total compensation
- **True Cost**: Health insurance, retirement add 10-30% to wages
- **Employee Retention**: Benefits affect turnover
- **Cash Flow**: Benefits are real cash outflows

#### Why Model Raises?
- **Retention**: Employees expect annual increases
- **Inflation**: Cost of living increases 2-3% annually
- **Realistic Planning**: Ignoring raises understates future costs
- **Multi-Year Accuracy**: Raises compound over time

#### Why Direct vs. Indirect Classification?
- **Gross Margin Accuracy**: Direct labor is part of COGS
- **Benchmarking**: Industry compares gross margins
- **Pricing Decisions**: Gross margin informs pricing strategy
- **Scalability**: Direct labor scales with revenue, indirect doesn't

### Frequently Asked Questions

**Q: What's the difference between direct and indirect labor?**  
A: Direct labor produces the product/service (production workers, service delivery). Indirect labor supports operations (managers, admin, sales). Direct flows to COGS, indirect to operating expenses.

**Q: Should I include the owner's salary?**  
A: Depends on business structure. If owner works in the business, include their salary here. If owner takes distributions (profit share), configure in Financing page under Owner Compensation.

**Q: What should I set for payroll tax percentage?**  
A: Minimum 7.65% (FICA). Add 1-3% for state/federal unemployment and workers comp. Typical total: 8-12%.

**Q: What counts as benefits?**  
A: Health insurance, dental, vision, retirement contributions (401k match), paid time off, life insurance, disability insurance.

**Q: How do I estimate benefits percentage?**  
A: No benefits: 0%. Basic benefits: 10-15%. Comprehensive benefits: 20-30%. Check industry benchmarks or your current costs.

**Q: Should annual raises be 3% every year?**  
A: 3% is typical for cost-of-living adjustments. Performance raises may be 5-10%. Conservative models use 2-3%.

**Q: Can I have employees with different raise percentages?**  
A: Yes, create separate roles. Example: "Manager" with 5% raises, "Hourly Staff" with 3% raises.

**Q: What if I'm not sure how many employees I need?**  
A: Start with minimum staffing, then test scenarios. Use industry benchmarks (revenue per employee) as guide.

**Q: Should I include contract labor here?**  
A: No. Contract labor (1099 workers) should go in Operating Expenses as "Contract Labor" or "Professional Fees". No payroll taxes or benefits for contractors.

**Q: How do I handle seasonal employees?**  
A: Create a role with fractional headcount (e.g., 0.5 for half-year) or use hours per week to model part-time/seasonal patterns.

### Common User Misunderstandings

**Misunderstanding 1**: "Payroll tax is what employees pay"  
**Reality**: Payroll tax here is the EMPLOYER portion (7.65% minimum). Employee withholding is separate and not modeled here.

**Misunderstanding 2**: "Benefits percentage is what employees contribute"  
**Reality**: Benefits % is what the EMPLOYER pays. If health insurance costs $500/month and employer pays 80%, that's $400/month or ~10% of a $50k salary.

**Misunderstanding 3**: "I don't need to include raises"  
**Reality**: Employees expect annual increases. Ignoring raises makes Year 2-3 projections unrealistic.

**Misunderstanding 4**: "All labor is indirect"  
**Reality**: Production workers, delivery drivers, service technicians are DIRECT labor (flows to COGS). Only admin/overhead is indirect.

**Misunderstanding 5**: "Hourly employees work exactly 40 hours every week"  
**Reality**: Part-time employees work less. Adjust hours per week accordingly (20 for half-time, 30 for three-quarter time).

**Misunderstanding 6**: "I should include owner's salary and distributions"  
**Reality**: Choose one. Salary = payroll role. Distributions = owner compensation in Financing page. Don't double-count.

### Coaching Opportunities

**Opportunity 1: Payroll Tax Education**  
When user sets payroll tax < 7.65%, explain:
- "Employer must pay at least 7.65% for FICA (Social Security + Medicare)"
- "You'll also owe state unemployment, federal unemployment, and possibly workers comp"
- "Total employer taxes typically run 8-12% of wages"

**Opportunity 2: Benefits Reality**  
When user sets benefits = 0%, discuss:
- "No benefits makes it hard to attract quality employees"
- "Even basic health insurance adds 10-15% to labor costs"
- "Consider starting with 10% for a basic benefits package"

**Opportunity 3: Direct Labor Classification**  
When user classifies production workers as indirect, correct:
- "Production workers should be 'Direct' because they're part of COGS"
- "This affects your gross margin, which lenders use to evaluate your business"
- "Direct labor scales with revenue; indirect labor is fixed overhead"

**Opportunity 4: Raise Planning**  
When user sets raises = 0%, caution:
- "Employees expect annual raises, even if just cost-of-living (2-3%)"
- "Ignoring raises makes your Year 2-3 projections unrealistically low"
- "Plan for at least 2-3% annually to retain employees"

**Opportunity 5: Headcount Planning**  
When user adds many roles, guide:
- "Labor is often the biggest expense - make sure you need all these roles"
- "Can you start lean and add staff as revenue grows?"
- "Check industry benchmarks for revenue per employee"

**Opportunity 6: Owner Compensation**  
When user asks about owner salary, clarify:
- "If you work in the business, include your salary here"
- "If you're an investor/owner taking distributions, use Owner Compensation in Financing page"
- "Don't include both - that's double-counting"

---

*[Document continues with Operating Expenses, Financing, Review, Insights, Modeler, and Deal Optimizer pages...]*

**Note**: This is Part 1 of the Screen Documentation. The file is being created in sections due to length. Additional pages will be documented in subsequent sections.

