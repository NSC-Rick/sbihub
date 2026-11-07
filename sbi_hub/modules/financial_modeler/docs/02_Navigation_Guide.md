# 02 Navigation Guide

## Application Structure

The Operating Model uses a **sidebar navigation** pattern with 9 main pages organized in a logical workflow sequence. Users progress from inputs → calculations → analysis → optimization.

## Page Overview

### 🏠 Home
**Purpose**: Model management, scenario control, and time mode configuration  
**When to Use**: Starting a new model, saving/loading scenarios, or resetting inputs  
**Key Actions**: Save, Load, Reset, Configure time mode  
**Typical User Questions**: "How do I save my work?" "How do I start over?"

---

### 💵 Revenue
**Purpose**: Configure revenue streams, pricing, volume, and growth assumptions  
**When to Use**: First step in building a financial model  
**Key Actions**: Add revenue streams, set COGS, configure seasonality  
**Typical User Questions**: "How do I estimate my sales?" "What's a realistic growth rate?"

---

### 👥 Payroll
**Purpose**: Define staffing needs, compensation, and benefits  
**When to Use**: After revenue planning, when determining labor requirements  
**Key Actions**: Add roles, set pay rates, configure taxes and benefits  
**Typical User Questions**: "How many employees do I need?" "What should I pay them?"

---

### 📋 Operating Expenses
**Purpose**: Configure fixed and variable overhead costs  
**When to Use**: After payroll, to complete expense planning  
**Key Actions**: Set rent, utilities, insurance, marketing, and other overhead  
**Typical User Questions**: "What expenses am I forgetting?" "Is my rent too high?"

---

### 🏦 Financing
**Purpose**: Configure loans, working capital, and capital stack  
**When to Use**: After all operating assumptions are set  
**Key Actions**: Set loan terms, configure AR/AP/Inventory days, build capital stack  
**Typical User Questions**: "How much can I borrow?" "Do I have enough working capital?"

---

### 📊 Review
**Purpose**: View complete financial statements and analysis  
**When to Use**: After all inputs are configured, to see results  
**Key Actions**: Review Income Statement, Cash Flow, Loan Schedule, KPIs  
**Typical User Questions**: "Am I profitable?" "Will I run out of cash?"

---

### 💡 Insights
**Purpose**: Automated flag analysis based on financial metrics  
**When to Use**: After reviewing statements, to identify risks  
**Key Actions**: Review red/yellow/green flags  
**Typical User Questions**: "What are my biggest risks?" "Is my DSCR acceptable?"

---

### 🎯 Modeler
**Purpose**: Test revenue and expense sensitivities without changing base model  
**When to Use**: For quick "what-if" analysis  
**Key Actions**: Adjust revenue/expense sliders, compare to base case  
**Typical User Questions**: "What if sales are 10% lower?" "How sensitive is my cash flow?"

---

### 🎯 Deal Optimizer
**Purpose**: Find optimal capital structures for acquisitions  
**When to Use**: When buying a business and need to optimize financing  
**Key Actions**: Set constraints (DSCR, cash), run optimization  
**Typical User Questions**: "What's the best financing mix?" "How much equity do I need?"

---

## Navigation Patterns

### Linear Workflow (Recommended for New Users)
1. **Home** → Configure time mode
2. **Revenue** → Define revenue streams
3. **Payroll** → Add employees
4. **Operating Expenses** → Set overhead costs
5. **Financing** → Configure loans and working capital
6. **Review** → Build and review financial statements
7. **Insights** → Check for red flags
8. **Modeler** → Test sensitivities (optional)
9. **Deal Optimizer** → Optimize capital structure (optional, acquisition only)

### Iterative Workflow (Experienced Users)
Users often cycle between:
- **Revenue/Payroll/Opex** → Adjust assumptions
- **Review** → See impact
- **Insights** → Check flags
- **Modeler** → Test scenarios
- **Back to inputs** → Refine assumptions

### Quick Analysis Workflow
For users with saved scenarios:
1. **Home** → Load scenario
2. **Review** → Build model
3. **Insights** → Check flags
4. **Modeler** → Test sensitivities

---

## Sidebar Information Panel

The sidebar displays **real-time model information**:

### Model Info Section
- **Model Name**: User-defined scenario name
- **Forecast Length**: Years and periods
- **Periods**: Total number of periods (36 for monthly, 3 for annual)
- **Revenue Streams**: Count of configured streams
- **Payroll Roles**: Count of configured roles
- **Opex Items**: Count of expense categories

### Save Status Indicator
- **🟢 Saved**: All changes saved to session
- **🟡 Unsaved Changes**: User has made edits since last save
- **Last Saved**: Timestamp of last save (e.g., "5 min ago")

### Navigation Behavior
- **Page Selection**: Radio button list
- **Auto-scroll**: Page scrolls to top on navigation
- **State Persistence**: All inputs preserved during navigation

---

## Page Dependencies

### No Dependencies
- **Home**: Can be accessed anytime
- **Revenue**: Can be configured independently
- **Payroll**: Can be configured independently
- **Operating Expenses**: Can be configured independently

### Soft Dependencies
- **Financing**: Works best after revenue/payroll/opex are configured
- **Review**: Requires at least one revenue stream for meaningful output
- **Insights**: Requires Review page to be built first
- **Modeler**: Requires Review page to be built first
- **Deal Optimizer**: Requires all inputs configured

### Data Flow Dependencies
```
Revenue → COGS → Gross Profit
Payroll → Operating Expenses
Opex → Operating Expenses
Operating Expenses + Gross Profit → EBITDA
EBITDA - Interest → Net Income
Net Income + Working Capital Changes → Cash Flow
Cash Flow + Loan Payments → Ending Cash
```

---

## Common Navigation Mistakes

### Mistake 1: Skipping Revenue Configuration
**Problem**: Users jump to Review without configuring revenue  
**Result**: Empty or default financial statements  
**Solution**: Always start with Revenue page

### Mistake 2: Not Building Model in Review
**Problem**: Users go to Insights or Modeler without building model first  
**Result**: Warning message "Please build model in Review tab first"  
**Solution**: Visit Review page and let model build before using Insights/Modeler

### Mistake 3: Forgetting to Save
**Problem**: Users make changes but don't save scenario  
**Result**: Work lost on browser refresh  
**Solution**: Watch for 🟡 Unsaved Changes indicator, save frequently

### Mistake 4: Editing in Wrong Mode
**Problem**: Users configure inputs in Basic mode, then switch to Advanced  
**Result**: Advanced features not configured, model incomplete  
**Solution**: Choose mode (Basic/Advanced) early in Financing page

### Mistake 5: Not Using Modeler for Testing
**Problem**: Users change base model inputs to test scenarios  
**Result**: Original assumptions lost  
**Solution**: Use Modeler page for temporary "what-if" analysis

---

## Related Pages by Task

### Task: "I want to increase profitability"
**Relevant Pages**:
1. Revenue → Increase pricing or volume
2. Revenue → Reduce COGS percentage
3. Payroll → Reduce headcount or compensation
4. Operating Expenses → Reduce overhead
5. Review → Verify impact on net income
6. Modeler → Test sensitivity

### Task: "I need to improve cash flow"
**Relevant Pages**:
1. Financing → Reduce AR days (collect faster)
2. Financing → Increase AP days (pay slower)
3. Financing → Reduce inventory days
4. Payroll → Reduce labor costs
5. Operating Expenses → Reduce overhead
6. Review → Check ending cash balance

### Task: "I need to qualify for a loan"
**Relevant Pages**:
1. Review → Check DSCR (must be > 1.25)
2. Insights → Review red/yellow flags
3. Revenue → Increase revenue to improve DSCR
4. Payroll/Opex → Reduce expenses to improve DSCR
5. Financing → Adjust loan amount/term to improve DSCR
6. Deal Optimizer → Find optimal capital structure

### Task: "I'm buying a business"
**Relevant Pages**:
1. Financing → Switch to Advanced mode
2. Financing → Configure capital stack
3. Financing → Set business stage to "Acquisition"
4. Financing → Set working capital source
5. Review → Verify cash requirements
6. Deal Optimizer → Optimize financing mix

### Task: "I want to compare scenarios"
**Relevant Pages**:
1. Home → Save current scenario (Scenario A)
2. Revenue/Payroll/Opex → Modify assumptions
3. Review → Build new model
4. Home → Save modified scenario (Scenario B)
5. Home → Load Scenario A
6. Review → Compare results
7. Repeat as needed

---

## Typical User Questions by Page

### Home Page
- "How do I save my work?"
- "Can I come back to this later?"
- "How do I start over?"
- "What's the difference between monthly and annual mode?"
- "Can I export to Excel?"

### Revenue Page
- "How many revenue streams should I have?"
- "What's a realistic growth rate?"
- "What is COGS and how do I estimate it?"
- "Should I use seasonality?"
- "What's a startup ramp?"

### Payroll Page
- "How many employees do I need?"
- "Should I use salary or hourly?"
- "What's the difference between direct and indirect labor?"
- "What should I include in benefits?"
- "What's a reasonable raise percentage?"

### Operating Expenses Page
- "What expenses am I forgetting?"
- "Is my rent too high?"
- "Should marketing be a percentage of revenue?"
- "What's the difference between fixed and variable expenses?"

### Financing Page
- "How much can I borrow?"
- "What's a good loan term?"
- "What are AR/AP/Inventory days?"
- "Do I need working capital?"
- "What's a capital stack?"

### Review Page
- "Am I profitable?"
- "Will I run out of cash?"
- "What's my DSCR?"
- "When do I break even?"
- "How much startup capital do I need?"

### Insights Page
- "What are my biggest risks?"
- "Is my DSCR acceptable?"
- "What do these flags mean?"
- "How do I fix red flags?"

### Modeler Page
- "What if sales are lower than expected?"
- "How sensitive is my cash flow to expenses?"
- "Will I still be profitable if revenue drops 10%?"

### Deal Optimizer Page
- "What's the best financing mix?"
- "How much equity do I need?"
- "Can I minimize my down payment?"
- "What's the maximum I can pay for this business?"

---

## Common Mistakes by Page

### Home Page
- Not saving scenarios before making major changes
- Switching time mode after configuring inputs (causes confusion)
- Not naming scenarios descriptively

### Revenue Page
- Setting unrealistic growth rates (>30% annually)
- Forgetting to set COGS percentage
- Not using seasonality for retail businesses
- Ignoring startup ramp for new businesses

### Payroll Page
- Forgetting payroll taxes (7.65% minimum for FICA)
- Not including benefits
- Classifying all labor as indirect (should use direct for production)
- Not planning for raises

### Operating Expenses Page
- Forgetting major categories (insurance, utilities)
- Setting rent too high (>12% of revenue is yellow flag)
- Not accounting for inflation

### Financing Page
- Setting AR/AP/Inventory days to zero (unrealistic for most businesses)
- Not configuring working capital for acquisition scenarios
- Borrowing too much (DSCR < 1.25)

### Review Page
- Not building model before checking results
- Ignoring negative cash balances
- Not understanding DSCR

### Insights Page
- Ignoring red flags
- Not understanding what flags mean
- Not taking action on yellow flags

### Modeler Page
- Confusing Modeler adjustments with base model changes
- Not resetting to base case before new simulation

### Deal Optimizer Page
- Setting unrealistic constraints (DSCR > 2.0)
- Not understanding optimization objectives
- Running optimizer without configuring base model first

---

**Next Steps**: Proceed to Screen Documentation for detailed page-by-page analysis.
