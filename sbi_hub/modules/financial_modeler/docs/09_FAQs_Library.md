# 09 Frequently Asked Questions

## Overview

This comprehensive FAQ library covers hundreds of likely user questions organized by topic. Use this to anticipate user needs and provide proactive guidance.

---

## GENERAL / GETTING STARTED

**Q: What is the Operating Model and who is it for?**  
A: The Operating Model is a financial planning tool for entrepreneurs, business buyers, and SBDC advisors. It helps you build transparent, realistic financial projections for small businesses.

**Q: Do I need financial experience to use this?**  
A: No. The application includes guidance, industry benchmarks, and plain-English explanations. However, working with an SBDC advisor is recommended for first-time entrepreneurs.

**Q: How is this different from a spreadsheet?**  
A: Unlike spreadsheets, the Operating Model has built-in validation, industry benchmarks, transparent calculations, and scenario management. All formulas are documented and testable.

**Q: Can I trust the calculations?**  
A: Yes. All calculations are deterministic (same inputs = same outputs), transparent (all formulas documented), and tested. The engine is separated from the UI for reliability.

**Q: How do I save my work?**  
A: Click "Save Model" on the Home page to download a JSON file. The app also auto-saves to your browser session, but JSON files are permanent.

**Q: Can I use this on my phone?**  
A: The app works on mobile but is optimized for desktop/tablet. Financial modeling requires detailed inputs best suited for larger screens.

**Q: Is my data secure?**  
A: Yes. All data stays on your computer. Nothing is sent to servers. Scenario files are saved locally as JSON files you control.

**Q: Can I share my model with my lender?**  
A: Yes. Save as JSON (for other Operating Model users) or export to Excel (for anyone). Excel export includes all financial statements.

---

## TIME MODE & CONFIGURATION

**Q: What's the difference between Monthly and Annual mode?**  
A: Monthly mode projects 36 months (3 years × 12 months) with monthly detail. Annual mode projects 3 years with annual totals. Monthly is better for cash flow analysis.

**Q: Can I switch between Monthly and Annual after entering data?**  
A: Yes, but the number of periods changes (36 → 3 or 3 → 36). All calculations adjust automatically, but review your assumptions.

**Q: Which mode should I use?**  
A: Use Monthly for: startups, seasonal businesses, cash flow analysis, lender presentations. Use Annual for: established businesses, long-term planning, simplicity.

**Q: Why does the app default to 3 years?**  
A: Three years is standard for small business projections. It's long enough to show viability but short enough to be realistic. Lenders typically require 3-5 year projections.

**Q: What is the Projection Start Date setting? (v1.1)**  
A: This lets you set the beginning month and year of your projection. Instead of seeing "Period 1, Period 2", you'll see "Jan 2026, Feb 2026", etc. This makes it easier to align your forecast with your actual business calendar. Find it on the Home page under Time Mode Configuration.

**Q: Does changing the Projection Start Date affect my calculations? (v1.1)**  
A: No. It only changes the labels on your reports and charts. All financial calculations remain exactly the same. It's purely for better context and readability.

**Q: What month should I start my projection? (v1.1)**  
A: Most businesses use January for calendar year planning. However, choose what makes sense for you: if you're opening in July, start there. If you have a fiscal year that starts in a different month, use that. The key is aligning with your actual business timeline.

**Q: Why do I see "Jan 2026" instead of "Period 1"? (v1.1)**  
A: Version 1.1 introduced calendar-based labels to make projections more meaningful. You can set your start month/year on the Home page. This helps you better understand when specific financial events occur in your business timeline.

**Q: Can I extend beyond 3 years?**  
A: Not currently. The app is designed for 3-year projections (36 months or 3 years). This matches lender requirements and realistic forecasting horizons.

---

## REVENUE QUESTIONS

**Q: How do I estimate my revenue if I'm a startup?**  
A: Start with market research: competitor pricing, target market size, realistic market share. Use conservative assumptions. Test with potential customers if possible.

**Q: What's a realistic growth rate?**  
A: Established businesses: 5-15% annually. Growth businesses: 15-30%. Startups: 30-100% in early years, declining to 10-20% as they mature. Be conservative—lenders discount aggressive projections.

**Q: Should I have multiple revenue streams?**  
A: Yes, if you have distinct products/services with different pricing or COGS. But don't over-complicate—2-3 main streams is usually enough. Group similar items together.

**Q: What is COGS and how do I calculate it?**  
A: COGS (Cost of Goods Sold) is the direct cost to produce your product or deliver your service. Includes: materials, direct labor, shipping. Excludes: rent, marketing, admin salaries. Check industry benchmarks or analyze competitor financials.

**Q: What COGS percentage should I use?**  
A: Depends on industry:
- Software/SaaS: 5-15%
- Professional Services: 10-25%
- Restaurants: 28-35%
- Manufacturing: 40-60%
- Retail: 50-70%

**Q: Should I include shipping in COGS?**  
A: Yes, if you pay for shipping to deliver products. No, if customer pays shipping separately.

**Q: Should I include marketing in COGS?**  
A: No. Marketing is an operating expense, not a direct cost. COGS should only include costs directly tied to producing/delivering each unit.

**Q: What is seasonality and should I use it?**  
A: Seasonality applies monthly revenue patterns (e.g., retail holiday spike). Use it if your business has predictable seasonal patterns. Skip it if revenue is relatively even year-round.

**Q: What is startup ramp?**  
A: Startup ramp models gradual revenue growth from 0% to 100% over X months. Use it for new businesses that won't reach full capacity immediately. Set to 0 for existing businesses.

**Q: How long should my startup ramp be?**  
A: Typical ranges:
- Retail: 3-6 months
- Restaurant: 6-12 months
- Service Business: 3-6 months
- Manufacturing: 12-24 months

**Q: Can I have different growth rates for different revenue streams?**  
A: Yes! Each revenue stream has its own growth rate. This lets you model different product lifecycles.

**Q: What if I don't know my exact pricing yet?**  
A: Use your best estimate based on competitor pricing and market research. You can always adjust later and save multiple scenarios.

---

## PAYROLL QUESTIONS

**Q: Should I include myself in payroll?**  
A: Depends on business structure. If you work in the business and take a salary (S-corp, C-corp), include yourself. If you take distributions (LLC, sole proprietor), use Owner Compensation in Financing page.

**Q: What's the difference between direct and indirect labor?**  
A: Direct labor produces the product/service (production workers, service delivery). Indirect labor supports operations (managers, admin, sales). Direct flows to COGS, indirect to operating expenses.

**Q: How do I classify my employees?**  
A: Ask: "Does this person directly produce our product/service?" If yes → Direct. If no → Indirect. Examples: Chef = Direct, Restaurant Manager = Indirect.

**Q: What should I set for payroll tax percentage?**  
A: Minimum 7.65% (FICA: Social Security + Medicare). Add 1-3% for state/federal unemployment and workers comp. Typical total: 8-12%.

**Q: What counts as benefits?**  
A: Health insurance, dental, vision, retirement contributions (401k match), paid time off, life insurance, disability insurance. Calculate as percentage of wages.

**Q: How do I estimate benefits percentage?**  
A: No benefits: 0%. Basic benefits: 10-15%. Comprehensive benefits: 20-30%. Check industry benchmarks or your current costs.

**Q: Should I plan for annual raises?**  
A: Yes. Employees expect annual increases, even if just cost-of-living (2-3%). Ignoring raises makes Year 2-3 projections unrealistic.

**Q: What's a reasonable raise percentage?**  
A: Cost-of-living: 2-3%. Performance: 3-5%. Promotion: 5-10%. Use 3% as default for planning purposes.

**Q: Can I have different raises for different roles?**  
A: Yes, create separate roles. Example: "Manager" with 5% raises, "Hourly Staff" with 3% raises.

**Q: How many employees do I need?**  
A: Check industry benchmarks for revenue per employee. Example: Retail typically $150k-$250k revenue per employee. Start lean and add staff as revenue justifies.

**Q: Should I include contract labor (1099 workers) here?**  
A: No. Contract labor goes in Operating Expenses as "Contract Labor" or "Professional Fees". No payroll taxes or benefits for contractors.

**Q: What if I have seasonal employees?**  
A: Use fractional headcount (e.g., 0.5 for half-year) or adjust hours per week to model part-time/seasonal patterns.

**Q: How do I handle hourly employees with variable hours?**  
A: Use average hours per week. Example: If employees work 30-50 hours, use 40 as average.

---

## OPERATING EXPENSES QUESTIONS

**Q: What should I include in operating expenses?**  
A: Rent, utilities, insurance, marketing, professional fees, office supplies, subscriptions, maintenance. Excludes: payroll (separate page), COGS (direct costs), loan payments (financing).

**Q: Is my rent too high?**  
A: Rent above 12% of revenue is a yellow flag. Ideal: 6-10% of revenue. If higher, consider negotiating, relocating, or growing revenue.

**Q: Should marketing be a percentage of revenue?**  
A: Can be. Use "Variable % Revenue" category if marketing scales with revenue. Or use fixed amount if you have set budget.

**Q: What's a typical marketing budget?**  
A: Varies widely: 2-5% of revenue for established businesses, 10-20% for startups/growth businesses. B2C typically higher than B2B.

**Q: What expenses am I probably forgetting?**  
A: Common forgotten expenses: insurance, licenses/permits, professional fees (accountant, lawyer), bank fees, credit card processing, software subscriptions, maintenance/repairs.

**Q: Should I include depreciation here?**  
A: No. Depreciation is configured separately in Financing page (Advanced mode). It's a non-cash expense for tax purposes.

**Q: What's the difference between fixed and variable expenses?**  
A: Fixed: Same amount each period (rent, insurance). Variable: Changes with revenue (credit card fees, commissions). Semi-fixed: Grows with inflation (utilities).

**Q: How do I handle one-time expenses?**  
A: The Operating Model is for ongoing operations. One-time expenses (equipment purchase, buildout) should be in Capital Stack (Advanced mode) or excluded from operating model.

**Q: Should I include owner's draw here?**  
A: No. Owner compensation is configured in Financing page (Advanced mode). Choose either salary (payroll) or distribution (owner comp), not both.

**Q: Why does my new expense start at $0? (v1.1)**  
A: This is intentional! Version 1.1 changed the default from $1,000 to $0 to ensure you enter the actual expense amount deliberately. This prevents errors from forgetting to update placeholder values. Just enter your real expense amount.

**Q: Can I change the default expense amount? (v1.1)**  
A: The default is always $0 for new expenses. This is by design to encourage intentional data entry. Simply update each expense to its actual value as you add it.

---

## FINANCING QUESTIONS

**Q: How much should I borrow?**  
A: Borrow enough to cover: startup costs, working capital, and 10% buffer. But not so much that DSCR drops below 1.25. Use Review page to check DSCR.

**Q: What's a good DSCR?**  
A: 1.25 or higher is healthy. 1.0-1.25 is marginal. Below 1.0 means you can't cover debt service—lenders won't approve.

**Q: What is DSCR?**  
A: Debt Service Coverage Ratio = EBITDA / Debt Service. Measures how many times you can cover your loan payment with operating profit. Lenders require 1.25+.

**Q: What interest rate should I use?**  
A: Check current rates: SBA 7(a) typically 6-9%, conventional 5-8%, alternative 8-15%. Use conservative (higher) rate for planning.

**Q: What loan term should I choose?**  
A: Longer term = lower payment but more total interest. Typical: 5-10 years for business loans, 15-25 years for real estate. Match term to asset life.

**Q: What are AR days?**  
A: Accounts Receivable days = average days to collect payment from customers. Also called DSO (Days Sales Outstanding). Cash business = 0, B2B typically 30-45.

**Q: What are AP days?**  
A: Accounts Payable days = average days to pay suppliers. Also called DPO (Days Payable Outstanding). Cash on delivery = 0, Net 30 terms = 30 days.

**Q: What are Inventory days?**  
A: Days inventory held before sale. Also called DIO (Days Inventory Outstanding). Service business = 0, retail typically 30-90, manufacturing 60-120.

**Q: Why do AR/AP/Inventory days matter?**  
A: They affect cash flow timing. Higher AR/Inventory = more cash tied up (bad for cash flow). Higher AP = more supplier financing (good for cash flow).

**Q: Should I set AR days to 0?**  
A: Only if you're a cash business (retail, restaurant). If you invoice customers (B2B), use realistic collection period (typically 30-45 days).

**Q: What is working capital?**  
A: Cash tied up in operations: (AR + Inventory) - AP. Growing businesses need more working capital. It's not an expense, but it consumes cash.

**Q: What is a capital stack?**  
A: (Advanced mode) The complete financing structure for an acquisition: how much from buyer equity, bank loan, seller note, etc. Shows uses (purchase price, working capital) and sources (where money comes from).

**Q: When should I use Advanced mode?**  
A: Use Advanced mode if you're: buying a business, need dual loan structure (business + real estate), want capital stack planning, or need detailed working capital controls.

---

## REVIEW & ANALYSIS QUESTIONS

**Q: Am I profitable?**  
A: Check Income Statement → Net Income. Positive = profitable. But also check Cash Flow Statement → Ending Cash. You can be profitable but run out of cash.

**Q: Will I run out of cash?**  
A: Check Cash Flow Statement → Ending Cash. If it goes negative, you need more startup capital. Look at "Cash Requirement Summary" for recommended starting cash.

**Q: What's the difference between profit and cash flow?**  
A: Profit (Net Income) is accounting measure. Cash flow is actual cash in/out. Differences: timing (AR/AP), non-cash expenses (depreciation), financing (loan principal).

**Q: When do I break even?**  
A: Check Cash Flow Statement → Break-Even Period. This is when Ending Cash becomes positive. Different from profitability break-even (when Net Income > 0).

**Q: How much startup capital do I need?**  
A: Check Cash Flow Statement → "Cash Requirement Summary" → "Recommended Starting Cash". This includes 10% buffer above minimum requirement.

**Q: What is EBITDA?**  
A: Earnings Before Interest, Taxes, Depreciation, Amortization. Operating profit before financing costs. Used for DSCR calculation and business valuation.

**Q: Why is my cash flow negative when I'm profitable?**  
A: Common reasons: working capital growth (AR/Inventory increasing), loan principal payments (not an expense but cash outflow), owner distributions.

**Q: Can I download my financial statements?**  
A: Yes. Each tab in Review page has "Download CSV" button. Or use "Export to Excel" on Home page for complete workbook.

**Q: How do I print my financial statements?**  
A: Click "Generate Print Report" in Review page. This creates printer-friendly view. Use browser print function (Ctrl+P or Cmd+P).

---

## INSIGHTS & FLAGS QUESTIONS

**Q: What do the red/yellow/green flags mean?**  
A: Red = serious risk requiring action. Yellow = caution, monitor closely. Green = healthy metrics. All flags are rule-based and transparent.

**Q: What does "DSCR below 1.0" mean?**  
A: You can't cover your debt service with operating profit. This is unsustainable—lenders won't approve, or you'll default. Reduce loan amount, increase revenue, or reduce expenses.

**Q: What does "Negative cash after debt and owner" mean?**  
A: After paying debt service and owner compensation, you have negative cash. Business can't cover obligations. Reduce debt, reduce owner comp, or improve profitability.

**Q: What does "Rent exceeds 12% of revenue" mean?**  
A: Your rent is high relative to revenue. This limits profitability. Consider negotiating lower rent, relocating, or growing revenue.

**Q: What does "Gross margin below 30%" mean?**  
A: Your gross profit margin is low, leaving little room for overhead and profit. Consider raising prices, reducing COGS, or both.

**Q: How do I fix red flags?**  
A: Depends on flag:
- Low DSCR: Reduce loan, increase revenue, reduce expenses
- Negative cash: Improve profitability, reduce debt service
- High rent: Negotiate, relocate, grow revenue
- Low margin: Raise prices, reduce COGS

**Q: Are yellow flags bad?**  
A: Yellow flags are caution signs, not deal-breakers. Monitor them and have a plan to improve. Lenders may ask about yellow flags.

**Q: Can I ignore green signals?**  
A: Green signals show strengths. Highlight them in lender presentations. But don't get complacent—maintain healthy metrics.

---

## MODELER QUESTIONS

**Q: What is the Modeler?**  
A: Non-destructive simulation tool. Test revenue/expense changes without modifying your base model. Great for "what-if" analysis.

**Q: How is Modeler different from changing inputs?**  
A: Modeler is temporary—changes reset when you reload. Changing inputs on other pages is permanent (until you reset or reload scenario).

**Q: When should I use Modeler?**  
A: Use for quick sensitivity testing: "What if revenue is 10% lower?" "What if expenses increase 5%?" Don't use for permanent scenario changes.

**Q: Why do I need to build model in Review first?**  
A: Modeler uses pre-computed metrics from Review page. Build model there first, then return to Modeler.

**Q: Can I save Modeler scenarios?**  
A: No. Modeler is for temporary testing only. If you want to save a scenario, make changes on input pages and save from Home page.

**Q: What does "Year 1 Only" vs "Entire Forecast" mean?**  
A: Currently both show Year 1 metrics. This is a display option for future functionality.

---

## DEAL OPTIMIZER QUESTIONS

**Q: What is the Deal Optimizer?**  
A: (Advanced mode) Automated tool that searches thousands of capital structure combinations to find optimal financing mix for acquisitions.

**Q: When should I use Deal Optimizer?**  
A: Use when buying a business and want to: minimize buyer equity, maximize purchase price, optimize DSCR, or maximize owner income.

**Q: How does it work?**  
A: You set constraints (minimum DSCR, minimum cash) and objective (what to optimize). It tests thousands of combinations and returns the best options.

**Q: How long does optimization take?**  
A: Typically 30-60 seconds. It tests up to 5,000 scenarios.

**Q: What if no valid scenarios are found?**  
A: Your constraints are too tight. Try: lowering minimum DSCR, lowering minimum cash, increasing search ranges, or adjusting purchase price.

**Q: Can I trust the optimizer results?**  
A: Yes, but verify. The optimizer finds mathematically optimal solutions based on your constraints. Review the top scenarios and choose what makes business sense.

---

## TROUBLESHOOTING

**Q: Why won't my scenario file load?**  
A: Common issues: corrupted JSON, incompatible version, missing required fields. Try: re-downloading file, checking file extension (.json), validating JSON syntax.

**Q: Why did my inputs disappear?**  
A: Browser session was cleared. Always save scenarios as JSON files for permanent storage. Session auto-save is temporary.

**Q: Why is my DSCR showing as 0?**  
A: DSCR only calculated when debt service > 0. If loan amount = 0, you're debt-free and DSCR doesn't apply.

**Q: Why is my ending cash negative?**  
A: You're spending more than you're making. Common causes: insufficient revenue, too much debt service, high expenses, working capital growth. Increase revenue, reduce expenses, or inject more capital.

**Q: Why don't my changes show in Review page?**  
A: Click "Build Model" button in Review page. Changes don't auto-update—you must rebuild model.

**Q: Can I undo changes?**  
A: No undo function. Save scenarios frequently so you can reload previous versions.

**Q: Why can't I export to Excel?**  
A: Excel export requires openpyxl Python library. If not installed, button is disabled. This is optional feature.

---

## BEST PRACTICES

**Q: How often should I update my model?**  
A: Update monthly with actual results. Compare projections to actuals and adjust assumptions. This improves accuracy over time.

**Q: Should I create multiple scenarios?**  
A: Yes! Create conservative, moderate, and optimistic scenarios. Show lenders you've thought through different outcomes.

**Q: How do I present this to a lender?**  
A: Export to Excel, print financial statements, prepare narrative explaining assumptions. Highlight: realistic assumptions, healthy DSCR (1.25+), adequate cash reserves.

**Q: What assumptions should I document?**  
A: Document everything: pricing research, market size, competitor analysis, industry benchmarks, growth justification. Lenders want to see your thinking.

**Q: How conservative should I be?**  
A: Very. Lenders discount aggressive projections. Better to exceed conservative projections than miss optimistic ones.

**Q: Should I round numbers?**  
A: For presentation, yes. Round to nearest $100 or $1,000. But keep detailed numbers in your working model for accuracy.

**Q: How do I handle uncertainty?**  
A: Create scenarios, use conservative assumptions, include buffers (10% extra cash), test sensitivities (what if revenue is 10% lower?).

**Q: What if my projections show I'll fail?**  
A: Better to know now than after investing. Options: improve business model, reduce costs, increase pricing, find more capital, or reconsider the opportunity.

---

**Total Questions**: 150+

**Coaching Note for Eric**: Use these FAQs to anticipate user needs. When users ask questions, provide direct answers plus context and coaching. Link related FAQs to help users discover connected concepts.

