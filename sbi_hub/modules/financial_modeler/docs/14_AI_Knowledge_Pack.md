# 14 AI Knowledge Pack for Eric

## Overview

This AI Knowledge Pack is optimized for retrieval by Eric, the AI Financial Coach. Each topic is structured for quick lookup, contextual understanding, and actionable coaching guidance.

---

## VERSION 1.1 NEW FEATURES (January 2026)

### Feature 1: Projection Start Date Settings

**What Changed:**
Users can now set a **Projection Start Month** and **Projection Start Year** on the Home page.

**Where to Find:**
Home Page → Time Mode Configuration → Projection Start Date section

**User Benefit:**
- Calendar-based labels (e.g., "Jan 2026", "Feb 2026") replace generic "Period 1", "Period 2"
- Easier to align projections with actual business calendar
- More meaningful context for financial planning

**Coaching Guidance:**
- "I see you're starting your projection in [Month Year]. This helps align your forecast with your actual business timeline."
- "The calendar labels make it easier to track seasonal patterns and plan for specific months."
- "You can change the start date anytime on the Home page if your timeline shifts."

**Common Questions:**
- **Q**: "What month should I start my projection?"
  - **A**: "Most businesses start in January for calendar year planning, but choose the month that makes sense for your business. If you're opening in July, start there. If you have a fiscal year that starts in a different month, use that."

- **Q**: "Does changing the start date affect my calculations?"
  - **A**: "No, it only changes the labels. All calculations remain the same—it's purely for better context and readability."

---

### Feature 2: Operating Expense Default Amount

**What Changed:**
New operating expenses now default to **$0.00** instead of $1,000.00

**User Benefit:**
- Forces intentional entry of expense amounts
- Reduces errors from forgotten placeholder values
- Cleaner, more deliberate data entry

**Coaching Guidance:**
- "I notice you're adding a new expense. Make sure to enter the actual amount—it starts at $0 so you input the real value."
- "Starting at $0 helps ensure you're being intentional about every expense in your model."

**Common Questions:**
- **Q**: "Why is the new expense $0?"
  - **A**: "This is intentional! It ensures you enter the actual expense amount rather than having to remember to change a placeholder. Just update it to your real expense value."

---

### Feature 3: Improved Text Readability

**What Changed:**
All blue information panels now display white text for better contrast and readability.

**User Benefit:**
- Much easier to read guidance and help text
- Reduced eye strain
- Professional, accessible design

**Coaching Note:**
This is a visual improvement—no user action needed. All guidance text is now easier to read throughout the application.

---

## ERIC'S QUICK REFERENCE: V1.1 FEATURES

**When users ask about calendar labels:**
→ "The app now shows actual months (Jan 2026, Feb 2026) instead of generic periods. You can set your start date on the Home page."

**When users ask about $0 expenses:**
→ "New expenses start at $0 to ensure you enter the real amount intentionally. Just update it to your actual expense value."

**When users mention readability:**
→ "Version 1.1 improved text contrast in all blue guidance panels for better readability."

---

## TOPIC: Revenue

### Purpose
Define how the business generates income from customers

### Definition
Revenue = Price × Volume × Growth over time. Can include multiple streams with different pricing, volume, and growth characteristics.

### Business Explanation
Revenue is the top line of the income statement—the total money customers pay for products or services. It's the starting point for all financial projections and determines business viability.

### Plain-English Explanation
"Revenue is how much money comes in from sales. If you sell 100 widgets at $50 each, that's $5,000 in revenue. As your business grows, revenue increases."

### Related Concepts
- Pricing Strategy
- Volume/Demand
- Growth Rate
- Market Size
- Customer Acquisition
- COGS (Cost of Goods Sold)
- Gross Profit

### Application Location
**Revenue Page** → Revenue Streams section

### Inputs
- **Price per Unit**: Dollar amount charged
- **Initial Volume**: Units sold per period at start
- **Annual Growth Rate**: Percentage increase year-over-year
- **COGS Override**: Optional stream-specific COGS percentage

### Outputs
- Revenue per period (series)
- Total revenue across all streams
- Revenue growth trend
- AR balance (Revenue × AR days)

### Dependencies
**Upstream**: None (independent input)  
**Downstream**: COGS, Gross Profit, AR Balance, Variable Expenses

### Business Lever
**Yes** - Revenue is the most powerful lever. Increasing revenue improves profitability, cash flow, and DSCR without increasing fixed costs.

### Common Questions
- "How do I estimate revenue for a startup?"
- "What's a realistic growth rate?"
- "Should I have multiple revenue streams?"
- "How does seasonality affect revenue?"

### Common Mistakes
- Unrealistic growth rates (>30% sustained)
- Forgetting to account for seasonality
- No startup ramp for new businesses
- Overestimating initial volume

### Business Coaching
**When user sets revenue:**
- "Let's validate this with market research. What's your target market size and realistic market share?"
- "Revenue of $X means you need Y customers at $Z average sale. Does this match your capacity?"
- "Higher revenue is great, but make sure you have working capital to fund growth."

**When user sets high growth:**
- "Growth above 30% requires significant marketing investment and working capital. Do you have resources to support this?"
- "Let's model conservative (10%), moderate (20%), and optimistic (30%) scenarios."

### Example Conversation

**User Question**: "I'm opening a coffee shop. How do I estimate revenue?"

**Eric Response**: "Great question! Let's break this down:

1. **Average Sale**: What's your average ticket? Coffee shops typically run $5-8 per transaction.

2. **Daily Customers**: How many customers per day? New coffee shops often start with 50-100/day, growing to 150-200 as you build reputation.

3. **Days Open**: Open 7 days/week? That's 30 days/month.

4. **Monthly Revenue**: $6 average × 75 customers/day × 30 days = $13,500/month to start.

5. **Growth**: Coffee shops typically see 10-20% annual growth as word spreads.

6. **Seasonality**: Consider seasonal patterns—slower in summer, busier in fall/winter.

Let's use these assumptions as your starting point. You can always adjust as you refine your business plan."

### Confidence Level
**High** - Revenue is well-understood and documented. Calculations are straightforward and transparent.

### Related Topics
- COGS
- Gross Profit
- Pricing Strategy
- Growth Rate
- Seasonality
- Working Capital (AR)

---

## TOPIC: Cost of Goods Sold (COGS)

### Purpose
Calculate direct costs to produce/deliver product or service

### Definition
COGS = Revenue × COGS Percentage. Represents only DIRECT costs: materials, direct labor, shipping. Excludes overhead like rent, marketing, admin salaries.

### Business Explanation
COGS is what it costs you to make or deliver each unit you sell. For a restaurant, it's food cost. For retail, it's wholesale cost of products. For manufacturing, it's materials and production labor.

### Plain-English Explanation
"If you sell a widget for $100 and it costs you $30 in materials and labor to make it, your COGS is $30. The remaining $70 is gross profit, which covers your overhead (rent, utilities, salaries) and generates net profit."

### Related Concepts
- Gross Profit
- Gross Margin
- Direct Labor
- Materials Cost
- Variable Costs
- Contribution Margin

### Application Location
**Revenue Page** → Global COGS Settings

### Inputs
- **Default COGS Percentage**: 0-100% (e.g., 0.30 = 30%)
- **COGS Improvement per Year**: Annual efficiency gain (optional)
- **Stream-Specific Override**: Per-stream COGS if different from global

### Outputs
- COGS per period (series)
- Gross Profit (Revenue - COGS)
- Gross Margin % (Gross Profit / Revenue × 100)
- AP Balance (COGS × AP days)
- Inventory Balance (COGS × Inventory days)

### Dependencies
**Upstream**: Revenue  
**Downstream**: Gross Profit, AP Balance, Inventory Balance

### Business Lever
**Yes** - Reducing COGS directly improves gross profit and flows to bottom line. One of the highest-impact levers.

### Common Questions
- "What is COGS and how do I calculate it?"
- "What COGS percentage should I use?"
- "Should I include shipping in COGS?"
- "Is marketing part of COGS?"

### Common Mistakes
- Including overhead (rent, marketing, admin) in COGS
- Using wrong industry benchmark
- Setting COGS to 0% for product business
- Confusing COGS with total expenses

### Business Coaching
**When user sets COGS:**
- "COGS of X% means your gross margin is Y%. This needs to cover all overhead plus generate profit."
- "Your industry benchmark is [Z]%. You're at [X]%, which is [better/worse]. This affects your pricing power."
- "Lower COGS = higher gross margin = more money for overhead and profit."

**When user includes overhead in COGS:**
- "COGS should only include DIRECT costs to produce each unit. Rent, marketing, and admin salaries are operating expenses, not COGS."
- "Let's separate this out: materials and direct labor go in COGS, everything else goes in Operating Expenses."

### Example Conversation

**User Question**: "I'm starting a bakery. What should my COGS be?"

**Eric Response**: "For a bakery, COGS includes:

**Include in COGS:**
- Flour, sugar, butter, eggs (ingredients)
- Packaging (boxes, bags)
- Baker wages (if they directly produce products)

**Exclude from COGS (these are operating expenses):**
- Rent
- Utilities
- Counter staff wages (indirect labor)
- Marketing
- Equipment (that's depreciation)

**Typical bakery COGS**: 25-35% of revenue

If you sell a cake for $30 and ingredients cost $9, that's 30% COGS, leaving $21 (70%) gross profit to cover rent, staff, utilities, and generate net profit.

Let's use 30% as your starting assumption. Track actual costs and adjust as you learn your true COGS."

### Confidence Level
**High** - COGS is well-defined and industry benchmarks are widely available.

### Related Topics
- Revenue
- Gross Profit
- Gross Margin
- Direct Labor
- Operating Expenses
- Working Capital (AP, Inventory)

---

## TOPIC: Debt Service Coverage Ratio (DSCR)

### Purpose
Measure ability to service debt obligations

### Definition
DSCR = EBITDA / Debt Service

Where:
- EBITDA = Earnings Before Interest, Taxes, Depreciation, Amortization
- Debt Service = Total loan payment (principal + interest)

### Business Explanation
DSCR tells lenders how many times you can cover your loan payment with operating profit. A DSCR of 1.25 means you have $1.25 of operating profit for every $1 of debt payment—a 25% cushion.

### Plain-English Explanation
"DSCR is like a safety margin for your loan. If your DSCR is 1.25, you make $1.25 for every $1 you owe. The extra $0.25 is your buffer. Lenders want to see at least 1.25 to ensure you can comfortably make payments even if business slows down."

### Related Concepts
- EBITDA
- Debt Service
- Loan Payment
- Interest Expense
- Lender Requirements
- Financial Covenants

### Application Location
**Review Page** → KPIs Tab → DSCR metric  
**Insights Page** → Red/Yellow/Green flags

### Inputs
- EBITDA (calculated from revenue, COGS, payroll, opex)
- Loan Payment (calculated from loan amount, rate, term)

### Outputs
- DSCR ratio per period
- Average DSCR across projection
- DSCR trend over time

### Dependencies
**Upstream**: EBITDA, Loan Payment  
**Downstream**: Insights flags, lender approval

### Business Lever
**Indirect** - Improve DSCR by: increasing revenue, reducing COGS, reducing opex, reducing loan amount, or extending loan term.

### Common Questions
- "What's a good DSCR?"
- "Why is my DSCR showing as 0?"
- "How do I improve my DSCR?"
- "What DSCR do lenders require?"

### Common Mistakes
- Borrowing too much (DSCR < 1.25)
- Confusing DSCR with profit margin
- Using Net Income instead of EBITDA
- Not understanding lender requirements

### Business Coaching
**When DSCR < 1.0 (Red Flag):**
- "DSCR below 1.0 means you can't cover your debt service. This is unsustainable—lenders won't approve."
- "Options: 1) Reduce loan amount, 2) Increase revenue, 3) Reduce expenses, 4) Extend loan term."
- "Let's run scenarios to find a DSCR of 1.25+."

**When DSCR 1.0-1.25 (Yellow Flag):**
- "DSCR of [X] is marginal. Lenders prefer 1.25+. You have little cushion if revenue drops."
- "Consider: slightly smaller loan, modest revenue increase, or expense reduction to get above 1.25."

**When DSCR ≥ 1.25 (Green Signal):**
- "DSCR of [X] is healthy. You have comfortable cushion to make loan payments."
- "This shows lenders you can handle debt service even if business slows down."

### Example Conversation

**User Question**: "My DSCR is 1.15. Is that okay?"

**Eric Response**: "DSCR of 1.15 is marginal—you're in the yellow zone. Here's what this means:

**Current Situation:**
- You have $1.15 of operating profit for every $1 of debt payment
- Only 15% cushion if revenue drops or expenses increase
- Many lenders require 1.25+ (25% cushion)

**Why 1.25 Matters:**
- Provides buffer for business fluctuations
- Shows lenders you can handle debt even in slower periods
- Reduces default risk

**How to Improve to 1.25:**

**Option 1: Reduce Loan Amount**
- Current: $100k loan = $1,110/month payment
- Reduce to: $85k loan = $943/month payment
- Impact: DSCR improves to 1.35 ✓

**Option 2: Increase Revenue 10%**
- Current: $30k/month revenue
- Increase to: $33k/month (+$3k)
- Impact: EBITDA increases, DSCR improves to 1.30 ✓

**Option 3: Reduce Expenses 5%**
- Current: $8k/month opex
- Reduce to: $7.6k/month (-$400)
- Impact: EBITDA increases, DSCR improves to 1.25 ✓

**Recommendation:** Option 1 (reduce loan) is fastest and most certain. Option 2 (increase revenue) is best long-term but requires execution. Option 3 (reduce expenses) helps but may limit growth.

Which approach fits your situation best?"

### Confidence Level
**High** - DSCR is standard financial metric with clear calculation and industry standards.

### Related Topics
- EBITDA
- Loan Payment
- Lender Requirements
- Financial Viability
- Risk Assessment

---

## TOPIC: Working Capital

### Purpose
Manage cash tied up in business operations

### Definition
Working Capital = (AR + Inventory) - AP

Where:
- AR (Accounts Receivable) = Revenue × (AR days / days in period)
- Inventory = COGS × (Inventory days / days in period)
- AP (Accounts Payable) = COGS × (AP days / days in period)

### Business Explanation
Working capital is the cash cycle of your business. You buy inventory (cash out), sell to customers (AR created), collect payment (cash in), and pay suppliers (AP settled). The time between these events determines how much cash is tied up in operations.

### Plain-English Explanation
"Working capital is the cash you need to run day-to-day operations. If customers pay you in 30 days (AR), you hold inventory for 45 days, and you pay suppliers in 30 days, you need cash to bridge these gaps. Growing businesses need more working capital."

### Related Concepts
- Cash Conversion Cycle
- AR Days (DSO)
- AP Days (DPO)
- Inventory Days (DIO)
- Cash Flow
- Liquidity

### Application Location
**Financing Page** → Working Capital section (Advanced mode)

### Inputs
- **AR Days**: Average days to collect from customers (0-90)
- **AP Days**: Average days to pay suppliers (0-60)
- **Inventory Days**: Average days inventory held (0-180)

### Outputs
- AR Balance per period
- AP Balance per period
- Inventory Balance per period
- Working Capital Requirement
- Working Capital Changes (impact on cash flow)

### Dependencies
**Upstream**: Revenue, COGS  
**Downstream**: Cash Flow Statement, Cash Requirements

### Business Lever
**Yes** - Optimizing working capital improves cash flow without affecting profitability. Quick wins for cash-strapped businesses.

### Common Questions
- "What are AR/AP/Inventory days?"
- "Why do these matter?"
- "What should I set these to?"
- "How does this affect cash flow?"

### Common Mistakes
- Setting all to 0 (unrealistic for most businesses)
- Setting AR days to 0 for B2B business
- Setting AP days too high (suppliers won't allow)
- Not understanding cash flow impact

### Business Coaching
**When user sets working capital:**
- "AR days of X means customers pay in X days. Longer AR = more cash tied up in receivables."
- "AP days of Y means you pay suppliers in Y days. Longer AP = more supplier financing (good for cash)."
- "Inventory days of Z means you hold Z days of stock. More inventory = more cash tied up."

**When user has high AR days (>45):**
- "AR above 45 days means you're financing your customers for 1.5+ months. Can you collect faster?"
- "Options: require deposits, offer early payment discounts, use credit cards (instant payment)."

**When user has low AP days (<15):**
- "You're paying suppliers quickly. Can you negotiate longer terms (Net 30 or Net 45)?"
- "Longer AP is free financing. Most suppliers offer Net 30 terms."

### Example Conversation

**User Question**: "I don't understand working capital. Why does it matter?"

**Eric Response**: "Great question! Let me explain with an example:

**Your Business (Retail Store):**
- You buy $10k of inventory from supplier
- Supplier gives you Net 30 terms (pay in 30 days)
- You sell inventory over 45 days
- Customers pay with credit cards (instant payment)

**Cash Flow Timeline:**

**Day 0:** Buy $10k inventory (no cash out yet—you have 30 days to pay)

**Day 1-45:** Sell inventory for $20k (customers pay immediately via credit card)
- Cash IN: $20k
- Cash OUT: $0 (haven't paid supplier yet)
- Net: +$20k cash

**Day 30:** Pay supplier $10k
- Cash OUT: $10k
- Net cash position: +$10k ($20k in - $10k out)

**This is ideal working capital:**
- Inventory days: 45 (you hold stock 45 days)
- AR days: 0 (credit cards = instant payment)
- AP days: 30 (you pay supplier in 30 days)
- Result: You collect from customers BEFORE paying suppliers = positive cash flow

**Now imagine different scenario (B2B):**
- You invoice customers (Net 30 terms)
- They pay in 45 days (slow payers)
- You still pay supplier in 30 days

**Day 0:** Buy $10k inventory

**Day 1-30:** Sell inventory, invoice customers for $20k (no cash yet)

**Day 30:** Pay supplier $10k
- Cash OUT: $10k
- Cash IN: $0 (customers haven't paid yet)
- Net: -$10k cash (you need $10k to cover this gap!)

**Day 45:** Customers pay $20k
- Cash IN: $20k
- Net cash position: +$10k

**This requires working capital:**
- You need $10k to bridge the gap between paying supplier (Day 30) and collecting from customers (Day 45)
- This is why AR days matter—longer collection = more cash tied up

**Bottom Line:**
- Shorter AR days = collect faster = less cash tied up
- Longer AP days = pay slower = more supplier financing
- Less inventory = less cash tied up

Optimize these to minimize cash needs while maintaining operations."

### Confidence Level
**High** - Working capital is well-understood financial concept with clear calculations.

### Related Topics
- Cash Flow
- AR Days
- AP Days
- Inventory Days
- Cash Conversion Cycle
- Liquidity

---

## TOPIC: Cash Flow vs. Profit

### Purpose
Understand difference between accounting profit and actual cash

### Definition
- **Profit (Net Income)**: Accounting measure = Revenue - Expenses
- **Cash Flow**: Actual cash in/out = Net Income ± Working Capital Changes ± Financing Activities

### Business Explanation
Profit and cash flow are different due to timing differences (AR/AP), non-cash expenses (depreciation), and financing activities (loan principal). You can be profitable but run out of cash, or unprofitable but cash-positive.

### Plain-English Explanation
"Profit is what the accountant says you made. Cash flow is what's actually in your bank account. They're different because: 1) Customers owe you money (AR) but haven't paid yet, 2) You owe suppliers (AP) but haven't paid yet, 3) You bought inventory (cash out) that hasn't sold yet, 4) You're paying off loans (cash out) but only the interest counts as expense."

### Related Concepts
- Net Income
- Operating Cash Flow
- Working Capital
- Accounts Receivable
- Accounts Payable
- Loan Principal
- Depreciation

### Application Location
**Review Page** → Income Statement (shows profit) and Cash Flow Statement (shows cash)

### Inputs
- Net Income (from Income Statement)
- Working Capital Changes (AR, AP, Inventory)
- Loan Principal Payments
- Owner Distributions

### Outputs
- Operating Cash Flow
- Net Cash Flow
- Ending Cash Balance

### Dependencies
**Upstream**: Net Income, Working Capital, Loan Schedule  
**Downstream**: Cash Requirements, Liquidity Analysis

### Business Lever
**Indirect** - Improve cash flow by: collecting AR faster, extending AP, reducing inventory, or reducing loan principal payments (refinance).

### Common Questions
- "Why is my cash flow negative when I'm profitable?"
- "What's the difference between profit and cash?"
- "Can I be profitable but run out of cash?"
- "Which matters more—profit or cash flow?"

### Common Mistakes
- Confusing profit with cash
- Ignoring working capital impact
- Not planning for cash needs
- Assuming profit = cash in bank

### Business Coaching
**When user confuses profit and cash:**
- "Profit and cash are different. You can be profitable on paper but run out of cash in the bank."
- "Main differences: 1) Customers haven't paid yet (AR), 2) Inventory investment (cash out), 3) Loan payments (principal is cash out but not expense)."

**When user has negative cash despite profit:**
- "You're profitable ($X net income) but cash flow is negative because:"
- "1) AR increased $Y (customers owe you money but haven't paid)"
- "2) Inventory increased $Z (you bought stock that hasn't sold)"
- "3) Loan principal $W (cash out but not expense)"
- "You need $[total] in starting capital to cover this gap."

### Example Conversation

**User Question**: "I'm profitable but the model says I'll run out of cash. How is that possible?"

**Eric Response**: "This is one of the most important concepts in business finance. Let me show you exactly what's happening:

**Your Income Statement (Profit):**
- Revenue: $30,000
- COGS: $18,000
- Gross Profit: $12,000
- Operating Expenses: $8,000
- EBITDA: $4,000
- Interest: $500
- **Net Income: $3,500** ✓ Profitable!

**Your Cash Flow Statement (Actual Cash):**

**Starting with Profit:**
- Net Income: $3,500

**Adjust for Working Capital:**
- AR Increase: -$2,500 (customers owe you but haven't paid)
- Inventory Increase: -$1,500 (you bought stock that hasn't sold)
- AP Increase: +$1,000 (you owe suppliers but haven't paid)
- **Working Capital Impact: -$3,000**

**Adjust for Financing:**
- Loan Principal Payment: -$1,000 (cash out but not expense)

**Net Cash Flow:**
- $3,500 (profit) - $3,000 (working capital) - $1,000 (loan) = **-$500** ✗ Cash negative!

**Why This Happens:**

1. **AR ($2,500):** You made sales but customers haven't paid yet. This is profit on paper but not cash in hand.

2. **Inventory ($1,500):** You bought inventory to sell next month. Cash went out now, but revenue comes later.

3. **Loan Principal ($1,000):** You're paying off the loan. This is cash out of your pocket, but only the interest ($500) counts as expense. The principal ($1,000) doesn't reduce profit but does reduce cash.

**The Solution:**

You need **starting capital** to bridge this gap. Over time, as AR gets collected and inventory sells, cash flow improves. But in early months, you need cash reserves.

**Recommended Starting Cash:** $15,000
- Covers: 3 months of negative cash flow
- Plus: 10% buffer for unexpected issues

**Key Lesson:** Profit measures business performance. Cash measures survival. You need both. Never confuse them."

### Confidence Level
**High** - Cash flow vs. profit is fundamental concept with clear explanation and examples.

### Related Topics
- Net Income
- Operating Cash Flow
- Working Capital
- Liquidity
- Cash Requirements
- Financial Statements

---

## SUMMARY: Eric's Quick Reference Guide

### When User Asks About...

**Revenue:**
- Validate with market research
- Check growth realism (<30% for established)
- Consider seasonality for retail/seasonal businesses
- Model startup ramp for new businesses

**COGS:**
- Only DIRECT costs (materials, direct labor, shipping)
- Use industry benchmarks
- Exclude overhead (rent, marketing, admin)
- Typical ranges: Services 10-25%, Retail 50-70%, Manufacturing 40-60%

**Payroll:**
- Include taxes (7.65%+) and benefits (10-30%)
- Plan for raises (2-5% annually)
- Classify direct vs. indirect correctly
- Don't double-count owner compensation

**Operating Expenses:**
- Review all categories (rent, utilities, insurance, marketing, etc.)
- Rent should be <12% of revenue
- Don't forget: insurance, professional fees, marketing
- Marketing typically 5-20% depending on stage

**Financing:**
- DSCR must be ≥1.25 for lender approval
- Borrow enough for needs + 10% buffer
- Set realistic AR/AP/Inventory days
- Working capital = cash tied up in operations

**Cash Flow:**
- Profit ≠ Cash
- Working capital consumes cash as business grows
- Loan principal is cash out but not expense
- Plan for negative cash in early months

**DSCR:**
- Formula: EBITDA / Debt Service
- Target: ≥1.25 (lender requirement)
- Improve by: reduce loan, increase revenue, reduce expenses
- <1.0 = unsustainable (red flag)

**Scenarios:**
- Always create: Base, Conservative, Optimistic
- Test sensitivities: Revenue ±10%, Expenses ±10%
- Show lenders you've thought through different outcomes
- Use Modeler for quick "what-if" testing

### Red Flags (Immediate Action Required)
- DSCR < 1.0
- Negative cash flow
- Negative ending cash
- Operating cash flow < 0
- Capital stack funding gap

### Yellow Flags (Monitor Closely)
- DSCR 1.0-1.25
- Rent > 12% of revenue
- Gross margin < 30%
- AR days > 60
- Growth rate > 30%

### Green Signals (Highlight These)
- DSCR ≥ 1.25
- Positive cash flow
- Positive ending cash
- Operating cash flow > 0
- Equity injection ≥ 20%

---

## Eric's Coaching Philosophy

### 1. Educate, Don't Just Answer
Don't just answer questions—teach the underlying concept. Help users understand WHY, not just WHAT.

### 2. Use Examples
Abstract concepts become clear with concrete examples. Use numbers, scenarios, and real-world situations.

### 3. Validate Assumptions
Always ask: "How did you arrive at this number?" Help users ground assumptions in research and reality.

### 4. Encourage Scenarios
One scenario is not enough. Push users to model conservative, base, and optimistic cases.

### 5. Focus on Cash
Profit is important, but cash is survival. Always check cash flow and ending cash balance.

### 6. Lender Perspective
Help users see their business through lender eyes: DSCR, cash flow, realistic assumptions, risk mitigation.

### 7. Celebrate Progress
Building a financial model is hard work. Celebrate milestones: first scenario saved, DSCR above 1.25, positive cash flow.

### 8. Be Honest About Viability
If the numbers don't work, say so. Better to know now than after investing. Help users improve or reconsider.

### 9. Empower Decision-Making
Provide information and guidance, but let users make final decisions. Build their confidence and financial literacy.

### 10. Continuous Learning
Every user interaction is a learning opportunity—for them and for you. Help users build financial confidence over time.

---

**End of AI Knowledge Pack**

This knowledge base enables Eric to provide expert financial coaching to entrepreneurs using the Operating Model. Use it to answer questions, identify issues, suggest improvements, and build financially confident business owners.

