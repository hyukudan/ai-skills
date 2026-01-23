---
name: product-metrics
description: |
  Product metrics and analytics for data-driven decisions. Covers North Star
  metrics, activation, retention, cohort analysis, funnel optimization, and
  building a metrics hierarchy.
license: MIT
allowed-tools: Read WebFetch
version: 1.0.0
tags: [product-metrics, analytics, retention, growth, kpis]
category: product/analytics
trigger_phrases:
  - "product metrics"
  - "North Star"
  - "activation"
  - "retention"
  - "cohort analysis"
  - "funnel"
  - "DAU MAU"
  - "churn"
variables:
  business_model:
    type: string
    description: Business model type
    enum: [saas, marketplace, ecommerce, consumer]
    default: saas
---

# Product Metrics Guide

## Core Philosophy

**Metrics inform decisions, they don't make them.** Use data to understand what's happening, then use judgment to decide what to do.

> "Not everything that counts can be counted, and not everything that can be counted counts."

---

## Metrics Framework

### The Pirate Metrics (AARRR)

```
┌──────────────────────────────────────────────────────────┐
│  ACQUISITION    →  How do users find us?                │
│  ACTIVATION     →  Do users have a great first exp?     │
│  RETENTION      →  Do users come back?                  │
│  REVENUE        →  Do users pay us?                     │
│  REFERRAL       →  Do users tell others?                │
└──────────────────────────────────────────────────────────┘
```

### North Star Metric

**Definition:** A single metric that best captures the core value your product delivers to customers.

{% if business_model == "saas" %}
**SaaS Examples:**
| Company | North Star |
|---------|------------|
| Slack | Messages sent |
| Zoom | Weekly meeting minutes |
| Notion | Blocks created |
| Dropbox | Files synced |
{% endif %}

{% if business_model == "marketplace" %}
**Marketplace Examples:**
| Company | North Star |
|---------|------------|
| Airbnb | Nights booked |
| Uber | Rides completed |
| DoorDash | Orders delivered |
| Etsy | Gross merchandise sales |
{% endif %}

{% if business_model == "ecommerce" %}
**E-commerce Examples:**
| Company | North Star |
|---------|------------|
| Amazon | Purchase frequency |
| Shopify | GMV through platform |
| Warby Parker | Frames sold |
{% endif %}

**North Star Criteria:**
- Reflects customer value delivered
- Leading indicator of revenue
- Actionable by product team
- Measurable and comparable over time

---

## 1. Acquisition Metrics

### Key Metrics

```
TRAFFIC METRICS
├── Unique visitors
├── Sessions
├── Page views
└── Traffic by source (organic, paid, referral, direct)

CONVERSION METRICS
├── Signup rate = Signups / Visitors
├── Cost per acquisition (CPA)
├── Customer acquisition cost (CAC)
└── Payback period = CAC / Monthly revenue per customer
```

### Channel Attribution

```python
# Attribution Models

# Last-touch: 100% credit to final touchpoint
# First-touch: 100% credit to first touchpoint
# Linear: Equal credit across all touchpoints
# Time-decay: More credit to recent touchpoints
# Position-based: 40% first, 40% last, 20% middle

# Example: User journey
# Ad → Blog → Email → Signup

# Last-touch: Email gets 100%
# First-touch: Ad gets 100%
# Linear: Each gets 25%
# Position: Ad 40%, Blog 10%, Email 50%
```

### CAC Calculation

```
Simple CAC:
CAC = Total Marketing Spend / New Customers

Blended CAC (includes sales):
CAC = (Marketing + Sales Spend) / New Customers

By Channel:
CAC_organic = Organic Marketing Spend / Organic Customers
CAC_paid = Paid Marketing Spend / Paid Customers
```

---

## 2. Activation Metrics

### Defining Activation

**Activation = The moment a user experiences your core value**

{% if business_model == "saas" %}
**SaaS Activation Examples:**
- Slack: Sent 2000 messages as a team
- Dropbox: Installed on 2+ devices
- Notion: Created 5+ pages
- Zoom: Hosted first meeting with 3+ participants
{% endif %}

### Finding Your Activation Moment

```sql
-- Find correlation between early actions and retention
-- Look for behaviors in first 7 days that predict D30 retention

WITH user_actions AS (
  SELECT
    user_id,
    COUNT(CASE WHEN action = 'create_doc' THEN 1 END) as docs_created,
    COUNT(CASE WHEN action = 'invite_user' THEN 1 END) as invites_sent,
    COUNT(CASE WHEN action = 'export' THEN 1 END) as exports
  FROM events
  WHERE event_date BETWEEN signup_date AND signup_date + INTERVAL '7 days'
  GROUP BY user_id
),
retention AS (
  SELECT
    user_id,
    CASE WHEN d30_active THEN 1 ELSE 0 END as retained
  FROM user_retention
)
SELECT
  CORR(docs_created, retained) as docs_correlation,
  CORR(invites_sent, retained) as invites_correlation,
  CORR(exports, retained) as exports_correlation
FROM user_actions
JOIN retention USING (user_id);
```

### Activation Funnel

```
                    100% - Signup
                     │
                     ▼
                    60% - Complete onboarding
                     │
                     ▼
                    35% - Create first item
                     │
                     ▼
                    20% - Invite teammate
                     │
                     ▼
                    12% - ACTIVATED
```

---

## 3. Retention Metrics

### Retention Types

```
USER RETENTION
- D1/D7/D30 retention: % of users who return on day N
- Week-over-week retention
- Month-over-month retention

REVENUE RETENTION (SaaS)
- Gross Revenue Retention (GRR): Revenue kept excluding expansion
- Net Revenue Retention (NRR): Revenue kept including expansion

Formula:
NRR = (Starting MRR + Expansion - Contraction - Churn) / Starting MRR

Good benchmarks:
- NRR > 100% means growth without new customers
- Best SaaS companies: 120-150% NRR
```

### Cohort Analysis

```sql
-- Monthly cohort retention
SELECT
  DATE_TRUNC('month', signup_date) as cohort_month,
  DATEDIFF('month', signup_date, activity_date) as months_since_signup,
  COUNT(DISTINCT user_id) as active_users
FROM users u
JOIN activity a ON u.user_id = a.user_id
GROUP BY 1, 2
ORDER BY 1, 2;
```

**Cohort Table:**
```
         Month 0  Month 1  Month 2  Month 3  Month 4
Jan      1000     450      380      350      340
Feb      1200     540      470      420
Mar      1100     520      450
Apr      1300     600
May      1150

As percentages:
         Month 0  Month 1  Month 2  Month 3  Month 4
Jan      100%     45%      38%      35%      34%
Feb      100%     45%      39%      35%
Mar      100%     47%      41%
Apr      100%     46%
May      100%
```

### Churn Analysis

```
CHURN RATE
Monthly churn = Customers lost / Customers at start of month

CHURN REASONS (track via exit surveys)
├── Price
├── Missing features
├── Switched to competitor
├── No longer needed
├── Poor support
└── Other

LEADING INDICATORS OF CHURN
- Decreased login frequency
- Decreased feature usage
- Support tickets
- Failed payments
- No activity in X days
```

---

## 4. Engagement Metrics

### DAU/MAU Ratio

```
DAU/MAU = Daily Active Users / Monthly Active Users

Interpretation:
- 50%+ : Very high engagement (social, communication)
- 25-50%: Good engagement (productivity tools)
- 10-25%: Moderate (many SaaS products)
- <10%: Low frequency use case (tax software)

This ratio shows what % of your monthly users come back daily.
```

### Engagement Depth

```sql
-- Power user curve: distribution of engagement
SELECT
  engagement_bucket,
  COUNT(*) as user_count,
  COUNT(*) * 100.0 / SUM(COUNT(*)) OVER () as percentage
FROM (
  SELECT
    user_id,
    CASE
      WHEN days_active = 1 THEN '1 day'
      WHEN days_active BETWEEN 2 AND 3 THEN '2-3 days'
      WHEN days_active BETWEEN 4 AND 7 THEN '4-7 days'
      WHEN days_active BETWEEN 8 AND 15 THEN '8-15 days'
      ELSE '16+ days'
    END as engagement_bucket
  FROM (
    SELECT user_id, COUNT(DISTINCT DATE(activity_time)) as days_active
    FROM user_activity
    WHERE activity_time >= DATE_SUB(CURRENT_DATE, INTERVAL 30 DAY)
    GROUP BY user_id
  ) t
) t
GROUP BY engagement_bucket;
```

### Feature Adoption

```
Feature Adoption Rate = Users who used feature / Total active users

Track for each feature:
- Breadth: What % of users use it?
- Depth: How often do users use it?
- Satisfaction: Do users find value? (via surveys)

Feature Adoption Matrix:
                    Low Frequency    High Frequency
High Adoption      │ Utility        │ Core
Low Adoption       │ Niche          │ Power User
```

---

## 5. Revenue Metrics

{% if business_model == "saas" %}

### SaaS Metrics

```
MRR (Monthly Recurring Revenue)
├── New MRR: From new customers
├── Expansion MRR: Upgrades and add-ons
├── Contraction MRR: Downgrades
└── Churned MRR: Lost revenue

ARR = MRR × 12

ARPU (Average Revenue Per User)
ARPU = MRR / Active customers

LTV (Lifetime Value)
Simple: LTV = ARPU × Average customer lifetime
Better: LTV = ARPU / Monthly churn rate

LTV:CAC Ratio
- Good: 3:1 or higher
- <3:1 may indicate unsustainable growth
- >5:1 may indicate under-investment in growth
```

### Quick Ratio

```
SaaS Quick Ratio = (New MRR + Expansion MRR) / (Contraction + Churned MRR)

Interpretation:
- >4: Excellent growth efficiency
- 2-4: Good
- 1-2: Concerning
- <1: Shrinking
```

{% endif %}

{% if business_model == "ecommerce" %}

### E-commerce Metrics

```
AOV (Average Order Value) = Revenue / Orders

Purchase Frequency = Orders / Unique customers

Customer Value = AOV × Purchase frequency

Gross Margin = (Revenue - COGS) / Revenue

Cart Abandonment Rate = (Carts created - Purchases) / Carts created
```

{% endif %}

---

## 6. Building a Metrics Dashboard

### Metrics Hierarchy

```
LEVEL 1: North Star (reviewed monthly)
└── Weekly active teams with high engagement

LEVEL 2: Health Metrics (reviewed weekly)
├── Acquisition: New signups, CAC
├── Activation: % completing onboarding
├── Retention: D7, D30 retention
└── Revenue: MRR, NRR

LEVEL 3: Feature Metrics (reviewed by feature teams)
├── Feature adoption rate
├── Feature engagement frequency
└── Feature-specific conversion
```

### Dashboard Template

```
┌─────────────────────────────────────────────────────────┐
│ EXECUTIVE DASHBOARD - Week of [Date]                   │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ NORTH STAR                                             │
│ ████████████████████░░░░  80% of goal                  │
│ [Metric]: 12,450 (+5% WoW)                             │
│                                                         │
├─────────────────────────────────────────────────────────┤
│ ACQUISITION          │ ACTIVATION                      │
│ New signups: 1,240   │ Activation rate: 45%           │
│ vs last week: +8%    │ vs last week: +2%              │
│                                                         │
│ RETENTION            │ REVENUE                         │
│ D7: 52%              │ MRR: $125K                      │
│ D30: 38%             │ NRR: 108%                       │
│                                                         │
├─────────────────────────────────────────────────────────┤
│ ALERTS                                                 │
│ ⚠️ D1 retention dropped 5% - investigating            │
│ ✓ Activation rate hit all-time high                   │
└─────────────────────────────────────────────────────────┘
```

---

## 7. Common Pitfalls

### Vanity Metrics vs. Actionable Metrics

| Vanity | Actionable |
|--------|------------|
| Total signups | Activated users |
| Page views | Engaged sessions |
| Total downloads | Weekly active users |
| Social followers | Referral rate |

### Statistical Considerations

```
SAMPLE SIZE
- Don't draw conclusions from small numbers
- Use statistical significance calculators
- Be patient with A/B tests

SEASONALITY
- Compare same period YoY
- Account for holidays, weekdays
- Look at trends, not single data points

SEGMENTATION
- Averages hide important patterns
- Segment by user type, plan, cohort
- Look for outliers skewing averages
```

---

## Quick Reference

### Metric Formulas

```
Activation Rate = Activated users / Signups

Retention Rate = Users active in period / Users from cohort

Churn Rate = 1 - Retention Rate

NRR = (Start MRR + Expansion - Contraction - Churn) / Start MRR

LTV = ARPU / Churn Rate

CAC Payback = CAC / (ARPU × Gross Margin)

Quick Ratio = (New + Expansion MRR) / (Churn + Contraction MRR)
```

### Benchmarks by Stage

| Stage | Focus Metrics |
|-------|---------------|
| Pre-PMF | Activation, D7 retention, qualitative feedback |
| Growth | CAC, conversion rate, NRR |
| Scale | LTV:CAC, efficiency, unit economics |

---

## Related Skills

- `user-research` - Qualitative insights
- `sql-optimization` - Query for analytics
- `data-visualization` - Presenting metrics
