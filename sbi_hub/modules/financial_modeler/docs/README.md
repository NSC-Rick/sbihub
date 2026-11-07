# Financial Modeler AI Knowledge Base

## Documentation for Eric - AI Financial Coach

This comprehensive knowledge base documents the Operating Model (Financial Modeler) application for use by Eric, an AI Financial Coach designed to assist entrepreneurs in building realistic financial projections.

---

## Purpose

This documentation reverse-engineers the Financial Modeler application into business-focused knowledge that enables Eric to:

- **Understand** every aspect of the application without accessing source code
- **Explain** financial concepts in plain language to entrepreneurs
- **Answer** user questions contextually and accurately
- **Identify** common mistakes and provide coaching
- **Teach** business implications of financial assumptions
- **Guide** users through the complete financial modeling process

---

## Documentation Structure

### 01 Executive Overview
**File**: `01_Executive_Overview.md`

**Contents**:
- Purpose of the application
- Primary audience and user characteristics
- Business goals for entrepreneurs, advisors, and lenders
- Learning philosophy (transparency over simplicity)
- Core financial modeling workflow
- How the application differs from traditional spreadsheets

**Use This When**: Orienting new users, explaining application value proposition, understanding design philosophy

---

### 02 Navigation Guide
**File**: `02_Navigation_Guide.md`

**Contents**:
- Complete page-by-page navigation structure
- Linear and iterative workflow patterns
- Page dependencies and relationships
- Common navigation mistakes
- Task-based navigation guides
- Typical user questions by page

**Use This When**: Helping users navigate the application, explaining page relationships, troubleshooting workflow issues

---

### 03 Screen Documentation
**File**: `03_Screen_Documentation.md`

**Contents**:
- Detailed documentation for Home, Revenue, and Payroll pages
- Screen purpose, business objective, navigation path
- All inputs, outputs, calculations, and dependencies
- Validation rules and business rationale
- Frequently asked questions per screen
- Common user misunderstandings
- Coaching opportunities

**Use This When**: Answering page-specific questions, explaining field purposes, understanding screen workflows

**Note**: This file contains Part 1 (first 3 pages). Additional pages (Operating Expenses, Financing, Review, Insights, Modeler, Deal Optimizer) follow the same structure and can be referenced from the codebase.

---

### 04-05-06 Core Business Logic
**File**: `04_05_06_Core_Business_Logic.md`

**Combined Contents**:

**Part 1: Field Documentation**
- Key field definitions and purposes
- Expected values and validation rules
- Formula dependencies
- Typical ranges by industry
- Common mistakes per field
- Business coaching notes

**Part 2: Formula Library**
- Every financial calculation documented
- Plain-English explanations
- Business purpose and significance
- Input/output specifications
- Common interpretation mistakes

**Part 3: Business Rules**
- Validation logic
- Dependencies and calculation order
- Conditional behavior
- Application assumptions
- Hidden calculations
- Error handling

**Use This When**: Explaining calculations, validating user inputs, understanding formula logic, troubleshooting calculation issues

---

### 07-08 Data Flow and Business Levers
**File**: `07_08_Data_Flow_and_Business_Levers.md`

**Combined Contents**:

**Part 1: Data Flow Documentation**
- Complete data flow diagram
- Component-by-component flow illustrations
- Dependency chains (Level 1-8)
- How information flows from inputs to outputs

**Part 2: Business Lever Library**
- Every adjustable business lever documented
- Direct and indirect effects
- Financial and cash flow impact
- Typical business decisions
- Examples and coaching opportunities
- Lever impact matrix

**Use This When**: Explaining how changes propagate, identifying highest-impact improvements, coaching on optimization strategies

---

### 09 FAQs Library
**File**: `09_FAQs_Library.md`

**Contents**:
- 150+ frequently asked questions
- Organized by topic: General, Time Mode, Revenue, Payroll, Operating Expenses, Financing, Review, Insights, Modeler, Deal Optimizer, Troubleshooting, Best Practices
- Direct answers with context and coaching
- Cross-references to related topics

**Use This When**: Answering common questions, anticipating user needs, providing quick reference answers

---

### 10-11-12-13 Mistakes, Coaching, Scenarios, Journey
**File**: `10_11_12_13_Mistakes_Coaching_Scenarios_Journey.md`

**Combined Contents**:

**Part 1: Common Mistakes (20+ documented)**
- What it looks like
- Why it occurs
- How to recognize
- How to correct
- Eric's response template

**Part 2: Coaching Opportunities (15+ documented)**
- Trigger moments
- Teaching opportunities
- Eric's guidance templates
- Proactive education

**Part 3: Scenario Planning**
- Base, Conservative, Optimistic scenarios
- Sensitivity scenarios
- Industry-specific scenarios
- Acquisition vs. Startup scenarios

**Part 4: User Journey (10 stages)**
- Complete journey from discovery to ongoing management
- User state, questions, actions, concerns at each stage
- Learning opportunities and Eric's role
- Journey variations by user type

**Use This When**: Identifying and correcting mistakes, finding coaching moments, planning scenarios, understanding user context

---

### 14 AI Knowledge Pack
**File**: `14_AI_Knowledge_Pack.md`

**Contents**:
- Structured knowledge entries for key topics
- Optimized for AI retrieval and contextual use
- Each topic includes:
  - Purpose and definition
  - Business and plain-English explanations
  - Related concepts
  - Application location
  - Inputs, outputs, dependencies
  - Business lever status
  - Common questions and mistakes
  - Business coaching guidance
  - Example conversations
  - Confidence level
  - Related topics

**Topics Covered**:
- Revenue
- Cost of Goods Sold (COGS)
- Debt Service Coverage Ratio (DSCR)
- Working Capital
- Cash Flow vs. Profit

**Plus**:
- Eric's Quick Reference Guide
- Red/Yellow/Green flag definitions
- Eric's Coaching Philosophy (10 principles)

**Use This When**: Providing comprehensive topic explanations, engaging in detailed coaching conversations, demonstrating expertise

---

## How to Use This Knowledge Base

### For Eric (AI Financial Coach)

**Scenario 1: User Asks About Revenue**
1. Check `09_FAQs_Library.md` → Revenue Questions for quick answer
2. Reference `14_AI_Knowledge_Pack.md` → Revenue topic for comprehensive explanation
3. Use `04_05_06_Core_Business_Logic.md` → Field Documentation for technical details
4. Apply `10_11_12_13_Mistakes_Coaching_Scenarios_Journey.md` → Common Mistakes to identify issues
5. Leverage `07_08_Data_Flow_and_Business_Levers.md` → Business Levers for optimization guidance

**Scenario 2: User Has Low DSCR**
1. Check `14_AI_Knowledge_Pack.md` → DSCR topic for explanation
2. Reference `10_11_12_13_Mistakes_Coaching_Scenarios_Journey.md` → Common Mistakes → "Borrowing Too Much"
3. Use `07_08_Data_Flow_and_Business_Levers.md` → Business Levers to suggest improvements
4. Apply `14_AI_Knowledge_Pack.md` → Eric's Quick Reference → Red Flags for urgency

**Scenario 3: User Confused About Cash Flow**
1. Check `14_AI_Knowledge_Pack.md` → Cash Flow vs. Profit topic for comprehensive explanation
2. Reference `09_FAQs_Library.md` → Review & Analysis Questions for common confusion points
3. Use `04_05_06_Core_Business_Logic.md` → Formula Library → Cash Flow Calculations
4. Apply example conversation from `14_AI_Knowledge_Pack.md`

**Scenario 4: New User Onboarding**
1. Start with `01_Executive_Overview.md` to understand application purpose
2. Use `02_Navigation_Guide.md` → Linear Workflow to guide user
3. Reference `10_11_12_13_Mistakes_Coaching_Scenarios_Journey.md` → User Journey → Stage 1-3
4. Apply `14_AI_Knowledge_Pack.md` → Eric's Coaching Philosophy

### For Developers

**Understanding Business Logic**:
- `04_05_06_Core_Business_Logic.md` → Formula Library
- `07_08_Data_Flow_and_Business_Levers.md` → Data Flow Documentation

**Understanding User Needs**:
- `09_FAQs_Library.md` → Common questions
- `10_11_12_13_Mistakes_Coaching_Scenarios_Journey.md` → Common mistakes

**Feature Planning**:
- `07_08_Data_Flow_and_Business_Levers.md` → Business Levers (what users want to optimize)
- `10_11_12_13_Mistakes_Coaching_Scenarios_Journey.md` → User Journey (pain points)

### For Product Managers

**User Research**:
- `10_11_12_13_Mistakes_Coaching_Scenarios_Journey.md` → User Journey (complete user experience)
- `09_FAQs_Library.md` → What users ask about

**Feature Prioritization**:
- `07_08_Data_Flow_and_Business_Levers.md` → Business Levers (highest impact features)
- `10_11_12_13_Mistakes_Coaching_Scenarios_Journey.md` → Common Mistakes (pain points to address)

**Help System Content**:
- `09_FAQs_Library.md` → FAQ content
- `03_Screen_Documentation.md` → Field-level help text
- `14_AI_Knowledge_Pack.md` → Comprehensive topic explanations

---

## Key Concepts for Eric

### Financial Modeling Fundamentals

**The Core Flow**:
```
Revenue → COGS → Gross Profit → Operating Expenses → EBITDA → Interest → Net Income
                                                                              ↓
                                                                    Working Capital Changes
                                                                              ↓
                                                                      Operating Cash Flow
                                                                              ↓
                                                                    Financing Cash Flow
                                                                              ↓
                                                                       Net Cash Flow
                                                                              ↓
                                                                      Ending Cash Balance
```

**Critical Metrics**:
- **DSCR**: Must be ≥1.25 for lender approval
- **Gross Margin**: Industry-specific, typically 30-70%
- **Cash Flow**: More important than profit for survival
- **Working Capital**: Cash tied up in operations

**Common Confusions**:
- Profit ≠ Cash Flow
- COGS ≠ Total Expenses
- EBITDA ≠ Net Income
- Revenue Growth ≠ Cash Flow Growth

### Eric's Core Responsibilities

1. **Educate**: Teach financial concepts, don't just answer questions
2. **Validate**: Check assumptions against industry benchmarks and reality
3. **Coach**: Guide users to better decisions, don't make decisions for them
4. **Identify**: Spot mistakes, risks, and opportunities proactively
5. **Encourage**: Build confidence and financial literacy over time

### Success Metrics for Eric

**User Success**:
- User understands their financial projections
- Assumptions are realistic and defensible
- DSCR ≥ 1.25 (if borrowing)
- Positive cash flow
- Adequate capitalization
- Multiple scenarios modeled

**Coaching Success**:
- User can explain their numbers to lenders
- User understands tradeoffs and sensitivities
- User has contingency plans
- User builds financial literacy over time

---

## Document Maintenance

### Version Information
- **Created**: July 2026
- **Platform**: Operating Model (Financial Modeler / FinLite)
- **Purpose**: AI Financial Coach (Eric) Knowledge Base
- **Scope**: Complete business logic documentation (excludes Python implementation details)

### Future Updates

**When to Update**:
- New features added to application
- User feedback reveals gaps in documentation
- Common questions not covered in FAQs
- New coaching opportunities identified

**What to Update**:
- Add new topics to `14_AI_Knowledge_Pack.md`
- Expand FAQs in `09_FAQs_Library.md`
- Document new mistakes in `10_11_12_13_Mistakes_Coaching_Scenarios_Journey.md`
- Update formulas in `04_05_06_Core_Business_Logic.md`

---

## Quick Reference

### Most Important Files for Eric

1. **`14_AI_Knowledge_Pack.md`** - Comprehensive topic explanations and coaching philosophy
2. **`09_FAQs_Library.md`** - Quick answers to common questions
3. **`10_11_12_13_Mistakes_Coaching_Scenarios_Journey.md`** - Mistakes, coaching, and user journey
4. **`07_08_Data_Flow_and_Business_Levers.md`** - How to improve financial outcomes

### Most Important Concepts

1. **DSCR ≥ 1.25** - Non-negotiable for lender approval
2. **Profit ≠ Cash** - Critical distinction users must understand
3. **Working Capital** - Growing businesses consume cash
4. **Realistic Assumptions** - Better to exceed conservative projections than miss optimistic ones
5. **Multiple Scenarios** - Base, Conservative, Optimistic

### Red Flags (Immediate Action Required)

- DSCR < 1.0
- Negative cash flow
- Negative ending cash
- Unrealistic growth (>30% sustained)
- Missing major expense categories

---

## Contact & Support

This knowledge base was created to enable Eric to provide expert financial coaching to entrepreneurs. It represents the complete business logic of the Operating Model application without requiring access to source code.

For questions about this documentation or suggestions for improvements, refer to the application's development team.

---

**End of Knowledge Base README**

This documentation library is the definitive source of truth for how the Operating Model works and how entrepreneurs should use it. Use it to create financially confident business owners.
