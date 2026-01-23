---
name: free-tool-strategy
description: |
  Build free tools that generate leads and SEO value. Covers tool types, ideation,
  lead capture strategies, MVP scoping, and ROI measurement for engineering as marketing.
license: MIT
allowed-tools: Read WebFetch
version: 1.2.0
tags: [free-tool, engineering-marketing, lead-gen, calculator, generator, seo]
category: marketing/growth
variables:
  tool_type:
    type: string
    description: Type of free tool to build
    enum: [calculator, generator, analyzer, tester, all]
    default: calculator
scope:
  triggers:
    - engineering as marketing
    - free tool
    - marketing tool
    - calculator
    - generator
    - interactive tool
    - lead gen tool
---

# Free Tools as Marketing

You help teams build free tools that attract and convert their target audience.

## When Free Tools Work

```
┌─────────────────────────────────────────────────────────────┐
│              FREE TOOL DECISION MATRIX                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   BUILD if:                    │  SKIP if:                  │
│   ─────────                    │  ────────                  │
│   ✓ Audience has tool-         │  ✗ Need immediate          │
│     solvable problem           │    revenue                 │
│   ✓ Natural connection to      │  ✗ Can't sustain           │
│     paid product               │    maintenance             │
│   ✓ Can build MVP in 2-4       │  ✗ Excellent tools         │
│     weeks                      │    already exist           │
│   ✓ Search volume for          │  ✗ No path from tool       │
│     problem space              │    to product interest     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Tool Categories

{% if tool_type == "calculator" or tool_type == "all" %}
### Calculators

Calculate something specific for the user.

**Examples:** ROI calculator, pricing estimator, cost comparison, time savings calculator

**Why they work:** Personalized output, high perceived value, bookmark-worthy

**Flow:**
```
[Input Fields] → [Validation] → [Calculation] → [Results] → [Email Gate] → [PDF Report]
```

**Key Pattern - Partial Gating:**
```javascript
// Show results immediately, gate the detailed report
const handleCalculate = () => {
  const results = calculate(inputs);
  setResults(results);        // Show basic results FREE
  setShowEmailGate(true);     // Gate the PDF/detailed report
};
```

{% endif %}

{% if tool_type == "generator" or tool_type == "all" %}
### Generators

Create something the user needs.

**Examples:** Policy generator, email subject lines, name generator, template creator

**Why they work:** Tangible output they can copy, saves time, shareable

**Flow:**
```
[Options] → [Input Context] → [Generate] → [Preview] → [Regenerate?] → [Copy/Download/Gate]
```

**Key Pattern - Regenerate Loop:**
```javascript
// Let users regenerate before asking for email
const handleGenerate = () => {
  const output = generate(options);
  setOutput(output);
  setRegenerateCount(prev => prev + 1);

  // Gate after 3 regenerations
  if (regenerateCount >= 3) {
    setShowEmailGate(true);
  }
};
```

{% endif %}

{% if tool_type == "analyzer" or tool_type == "all" %}
### Analyzers

Evaluate something the user has.

**Examples:** Website grader, SEO checker, headline analyzer, security audit

**Why they work:** Curiosity-driven, reveals problems you solve, creates urgency

**Flow:**
```
[URL/File Input] → [Fetch/Parse] → [Analyze] → [Score/Grade] → [Issues] → [Gate Full Report]
```

**Key Pattern - Score Reveal:**
```javascript
// Show score immediately, gate detailed recommendations
const handleAnalyze = async (url) => {
  const analysis = await analyze(url);

  setScore(analysis.score);           // Show: "Your score: 67/100"
  setTopIssues(analysis.issues.slice(0, 3));  // Show top 3 issues
  // Gate: Full report with all issues + how to fix
};
```

{% endif %}

{% if tool_type == "tester" or tool_type == "all" %}
### Testers

Check if something works correctly.

**Examples:** Meta tag preview, email rendering, mobile test, speed check

**Why they work:** Immediate utility, repeat usage, professional necessity

**Flow:**
```
[Input to Test] → [Execute Test] → [Pass/Fail] → [Fix Suggestions] → [Save/Share]
```

**Key Pattern - No Gate (SEO Play):**
```javascript
// Testers work best fully ungated for SEO and repeat usage
// Monetize through brand awareness and upsell to related paid product
```

{% endif %}

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    TOOL ARCHITECTURE                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  FRONTEND                                                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐          │
│  │  Input   │─►│ Results  │─►│  Lead Capture    │          │
│  │  Form    │  │ Display  │  │  (Email Gate)    │          │
│  └──────────┘  └──────────┘  └──────────────────┘          │
│                      │                                      │
│                      ▼                                      │
│  API                                                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐          │
│  │ Validate │─►│ Calculate│─►│  Store Lead      │          │
│  │  Input   │  │ / Process│  │  (CRM/Email)     │          │
│  └──────────┘  └──────────┘  └──────────────────┘          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Lead Capture Strategy

### Gating Spectrum

```
FULLY UNGATED          PARTIAL GATE           FULL GATE
─────────────          ────────────           ─────────

Max usage              Balance                Max leads
Brand only             Usage + Leads          Min usage

Best for:              Best for:              Best for:
• SEO plays            • PDF reports          • Unique tools
• Testers              • Saved results        • High-value output
• Viral tools          • Email courses

Example:               Example:               Example:
Speed test free,       Calculator free,       Requires email
no signup              PDF needs email        to start
```

### Email Capture Best Practices

- **Value exchange must be clear:** "Get detailed report with recommendations"
- **Ask for email only:** Name optional, company skip
- **Show preview first:** Let them see it works before asking
- **Deliver immediately:** Don't make them wait

---

## Ideation Process

### Find the Problem

1. **What does your audience Google?** → "how to calculate X", "X generator"
2. **What do they solve with spreadsheets?** → Any manual calculation = opportunity
3. **What questions before buying?** → Pre-purchase uncertainty = calculator
4. **What data helps decisions?** → Budget justification, comparison tools

### Validation Checklist

| Check | How to Validate | Minimum |
|-------|-----------------|---------|
| Search demand | Google Keyword Planner | 500+ monthly |
| Competition | Google the concept | Can be 3x better |
| Audience fit | Match buyer persona | 70%+ overlap |
| Build feasibility | Scope requirements | MVP in 2-4 weeks |

---

## SEO for Tools

### Technical Requirements

- Clean URL: `/tools/[tool-name]` or `/[tool-name]-calculator`
- Dedicated landing page (not buried in app)
- Mobile responsive (Google mobile-first)
- Core Web Vitals passing

### Schema Markup

```json
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "ROI Calculator",
  "applicationCategory": "BusinessApplication",
  "operatingSystem": "Web",
  "offers": { "@type": "Offer", "price": "0" }
}
```

### Content Around the Tool

- H1 with primary keyword
- Explanatory content above fold
- FAQ section (featured snippets)
- Related tools/resources links

---

## Analytics

### Events to Track

```javascript
// Essential events
trackEvent('tool_start');           // First input interaction
trackEvent('tool_complete', { result });  // Saw results
trackEvent('email_captured', { result }); // Provided email
trackEvent('report_downloaded');    // Downloaded PDF
```

### Conversion Funnel Benchmarks

```
Page Views ─────────────────── 100%
Tool Starts ───────────────── 60-80%  (filled first input)
Tool Completes ────────────── 40-60%  (saw results)
Email Captured ────────────── 15-30%  (provided email)
MQL ───────────────────────── 5-15%   (qualified lead)
Customer ──────────────────── 1-5%
```

### Key Metrics

| Metric | Target |
|--------|--------|
| Completion Rate (Completes/Starts) | > 60% |
| Capture Rate (Emails/Completes) | > 25% |
| Lead Quality (MQLs/Leads) | > 30% |
| Tool ROI (Customers × LTV / Build Cost) | > 5x year 1 |

---

## MVP Scope

### Build First
- [ ] Core functionality only (one calculation/generation)
- [ ] Clear input → output flow
- [ ] Mobile responsive
- [ ] Basic email capture (one field)
- [ ] Single CTA after results

### Skip for V1
- Account creation / login
- Saving results history
- Advanced options
- Perfect design (functional > pretty)
- PDF generation (V2)

---

## Checklist

### Pre-Development
- [ ] Validated 500+ monthly searches
- [ ] Mapped tool users to buyer persona
- [ ] Defined value exchange for email
- [ ] Scoped MVP (2-4 weeks)
- [ ] Chosen gating strategy

### Development
- [ ] Responsive input form
- [ ] Calculation/generation logic
- [ ] Results display
- [ ] Email capture form
- [ ] Lead storage (CRM/database)
- [ ] Analytics tracking
- [ ] Mobile tested

### Launch
- [ ] SEO: Clean URL, meta, schema
- [ ] Soft launch to beta users
- [ ] Bug fixes from feedback
- [ ] Promoted on social
- [ ] Added to site navigation

### Post-Launch
- [ ] Weekly analytics review
- [ ] A/B test email capture copy
- [ ] Monitor lead quality
- [ ] Plan V2 based on data

---

## Related Skills

- **@include skill:page-cro**: Optimize tool landing page
- **@include skill:form-cro**: Optimize email capture form
- **@include skill:email-sequence**: Nurture tool leads
