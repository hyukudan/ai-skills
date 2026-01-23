---
name: pricing-strategy
description: |
  Master SaaS pricing from research to execution. This skill provides battle-tested
  frameworks for discovering willingness to pay, structuring tiers that sell, choosing
  value metrics that scale, and communicating price changes without losing customers.
license: MIT
allowed-tools: Read WebFetch
version: 1.0.0
tags: [pricing, monetization, saas, packaging, strategy, value-metric, revenue]
category: marketing/growth
scope:
  triggers:
    - pricing strategy
    - pricing tiers
    - freemium
    - free trial
    - packaging
    - price increase
    - value metric
    - Van Westendorp
    - willingness to pay
    - monetization
    - how to price
---

# The Complete Guide to SaaS Pricing

You are a pricing strategist who has helped hundreds of SaaS companies optimize their monetization. Your approach combines rigorous research methods with practical implementation experience.

## The Pricing Paradox

Most founders spend months perfecting their product and days deciding their price. This is backwards. Pricing is the fastest lever to improve revenue—a 1% improvement in price yields 11% improvement in profits on average, compared to 3.3% from volume and 7.8% from cutting costs.

Yet pricing terrifies people because it feels irreversible. It's not. Every successful company has changed their pricing multiple times.

---

## Discovery: Understanding What to Charge

Before setting numbers, you need data. Guessing based on competitors or gut feel leaves money on the table.

### The Pricing Research Stack

**Layer 1: Qualitative Discovery**

Talk to 15-20 customers and prospects with open-ended questions:

- "Walk me through how you decided to buy/not buy."
- "What would have to be true for this to be worth 2x the price?"
- "What's the alternative if our product didn't exist?"
- "How do you measure the value you get from this?"

Look for patterns in *how* they think about value, not specific numbers.

**Layer 2: Competitive Intelligence**

Build a pricing database of every competitor:
- What they charge
- How they charge (per seat, usage, flat)
- What's included at each tier
- How pricing has changed over time

Don't copy competitors—understand the market's price expectations.

**Layer 3: Quantitative Surveys**

Two methods that actually work:

**Van Westendorp (Price Sensitivity Meter)**

Ask four questions about price:
1. Too cheap (quality concerns)
2. Good deal (would definitely buy)
3. Getting expensive (but would consider)
4. Too expensive (wouldn't consider)

Plot cumulative distributions to find the acceptable range and optimal point.

**MaxDiff (Feature Prioritization)**

Show sets of 4-5 features, ask which is most and least important. After 10-15 rounds, you'll know exactly which features drive willingness to pay.

Run with 150+ respondents for statistical significance. Segment by persona—different customers have wildly different willingness to pay.

---

## The Value Architecture Framework

Pricing isn't a number—it's a system with three interconnected parts.

### 1. Value Metric (What You Charge For)

The value metric is the unit of exchange. It should:
- Scale with value received
- Be easy to predict and understand
- Grow naturally as customers succeed
- Be hard to game

**Metric Selection Matrix:**

| Product Type | Strong Metrics | Weak Metrics |
|-------------|----------------|--------------|
| Collaboration tools | Users, guests | Storage |
| Developer tools | API calls, compute | Seats |
| Marketing tools | Contacts, campaigns | Features |
| Data platforms | Records, queries | Users |
| Design tools | Projects, exports | Storage |

**The 10x Test**: If a customer's usage increases 10x, would your revenue from them also increase proportionally? If not, you'll hit ceiling where largest customers pay the same as small ones.

### 2. Packaging (What's In Each Tier)

Group features into bundles that match distinct customer segments.

**The Feature Sorting Method:**

1. List all features
2. Score each 1-5 on:
   - Value differentiation (does it make sales?)
   - Cost to serve (infrastructure, support)
   - Strategic importance (moat-building)
3. Sort into buckets:
   - **Must-haves**: All tiers (table stakes)
   - **Differentiators**: Separate tiers (make the sale)
   - **Add-ons**: Optional purchases (expansion revenue)

**The Goldilocks Principle:**
- Too few tiers (2): Miss segments, leave revenue on table
- Too many tiers (5+): Paralyze buyers, complicate operations
- Just right (3-4): Clear progression, obvious choice

### 3. Price Points (The Actual Numbers)

Numbers aren't arbitrary—they communicate positioning.

**Psychological Pricing Rules:**
- $49 says "value" (charm pricing)
- $50 says "premium" (round pricing)
- $99 is a barrier; $79 feels dramatically different
- Annual discounts should be 15-20% (more feels desperate)

**The 3x Rule:**
Each tier should be roughly 3x the previous tier's price for the jump to feel proportional to the value increase.

Example progression: $29 → $99 → $299

---

## Freemium vs. Free Trial: A Decision Framework

This choice fundamentally shapes your business model.

### When Freemium Works

Freemium requires all five conditions:
1. Very large market (millions of potential users)
2. Low marginal cost per user
3. Product has viral or network effects
4. Clear, natural upgrade triggers
5. Free users provide value (data, content, referrals)

**Freemium Math:**
If 3% of free users convert and CAC is $100, you need LTV > $3,333 to justify freemium. Most products don't qualify.

### When Free Trial Works

Free trials work when:
- Product value is clear within days
- Onboarding investment creates switching costs
- Price point justifies evaluation period
- Sales cycle benefits from hands-on experience

**Trial Design:**
- 7 days for simple products
- 14 days for most SaaS
- 30 days for complex, team-based products

**Credit Card Upfront:**
- With CC: 40-60% trial-to-paid conversion, lower volume
- Without CC: 15-25% conversion, higher volume

Choose based on whether you're optimizing for quality or quantity of trials.

### The Reverse Trial Model

New approach: Give full access, then downgrade to free tier if they don't pay.

Users experience premium value first, making the free tier feel like loss. Slack, Notion, and many others use this successfully.

---

## Enterprise Pricing: A Separate Game

Enterprise deals require completely different thinking.

### When to Go Enterprise

Add "Contact Sales" when any apply:
- Deal sizes regularly exceed $15K ARR
- Procurement processes are involved
- Custom contracts are expected
- Implementation services needed
- Security/compliance reviews required

### Enterprise Packaging Elements

**Security & Compliance:**
- SSO/SAML
- SCIM provisioning
- Audit logs
- Data residency
- SOC 2 / HIPAA compliance

**Administration:**
- Advanced permissions
- Team management
- Usage analytics
- API rate limits

**Support:**
- Dedicated CSM
- Priority support
- Implementation services
- Training sessions
- Executive business reviews

### Enterprise Pricing Models

**Per-seat with volume discounts:**
Standard pricing for users 1-100, then negotiate discounts for larger deployments.

**Platform fee + usage:**
$10K/year platform access + usage-based pricing. Guarantees minimum revenue while allowing growth.

**Value-based contracts:**
Price tied to outcomes—revenue generated, costs saved, etc. Risky but highest upside.

---

## Changing Prices: The Playbook

Every company changes pricing. Here's how to do it without damage.

### Price Increase Signals

It's time when you see:
- Conversion rates > 30% (you're too cheap)
- Competitors have raised prices
- Customers say "this is a steal"
- Feature set has grown substantially
- Unit economics need improvement

### Implementation Strategies

**Strategy 1: New Customers Only**
Raise prices for new signups. Existing customers keep current pricing indefinitely.
- Pro: Zero churn risk
- Con: Creates technical debt, leaves money on table

**Strategy 2: Grandfathering with Sunset**
New price for new customers. Existing customers have 12-24 months at old rate, then migrate.
- Pro: Smooth transition
- Con: Requires good communication

**Strategy 3: Value-Justified Increase**
Launch new tier or major feature. Position price increase as investment in new capabilities.
- Pro: Feels fair
- Con: Requires actual new value

### Communication Template

For existing customers:

```
Subject: Upcoming changes to [Product] pricing

Hi [Name],

We're reaching out about updates to [Product] pricing, effective [Date].

Over the past [time], we've [added features/improvements]. To continue investing in [Product], we're adjusting our pricing.

What this means for you:
- Your current plan: [Current price]
- New pricing: [New price]
- Your rate until: [Date or "grandfathered indefinitely"]

[If action needed]: You can lock in current pricing for [term] by [action] before [deadline].

Thank you for being a [Product] customer. We're committed to [value prop].

Questions? Reply to this email.

[Name]
```

---

## Pricing Page Optimization

Your pricing page is often the highest-intent page on your site.

### Above-the-Fold Must-Haves

- All tiers visible without scrolling
- Monthly/annual toggle (annual selected by default)
- Recommended tier clearly marked
- One primary CTA per tier

### Anchoring Techniques

**Price Anchoring:**
Show the highest tier first (left position) to anchor expectations high.

**Feature Anchoring:**
List the most impressive features at the top of each tier's list.

**Social Anchoring:**
"Most popular" badges create FOMO and social validation.

### Reducing Friction

- Show price per month even for annual plans
- Calculator for usage-based pricing
- FAQ section addressing objections
- Trust signals (logos, security badges, guarantees)
- Chat widget for questions

---

## Pricing Metrics That Matter

### Health Metrics

**ARPU (Average Revenue Per User):**
Total MRR / Total customers. Track trends over time.

**Revenue Per Customer Segment:**
Are enterprise customers paying proportionally more? They should be.

**Price Realization:**
Actual revenue / List price. Shows discounting effectiveness.

### Warning Signs

- ARPU flat while features grow (you're under-monetizing)
- High discount rates (pricing doesn't match perceived value)
- Tier concentration (80%+ on one tier means bad packaging)
- Price objections increasing (market conditions shifted)

---

## Common Pricing Mistakes

**Mistake 1: Pricing on Cost**
Your costs are irrelevant to customers. Price on value delivered.

**Mistake 2: Copying Competitors**
Competitor pricing reflects their costs, positioning, and mistakes—not yours.

**Mistake 3: One Price Forever**
Pricing should evolve with your product and market.

**Mistake 4: Too Many Options**
Paradox of choice is real. 3-4 tiers maximum.

**Mistake 5: Identical Tiers**
If tiers differ only by limits, you're not capturing different willingness to pay.

---

## Putting It Together

### Pricing Sprint (2 Weeks)

**Week 1:**
- Day 1-2: Customer interviews (10 calls)
- Day 3-4: Competitive analysis
- Day 5-7: Quantitative survey design and launch

**Week 2:**
- Day 8-10: Survey analysis
- Day 11-12: Tier structure design
- Day 13-14: Pricing page mockup and review

### Decision Questions

When you're stuck, ask:
1. If we charged 2x, would customers still see value?
2. What would they use instead of us?
3. What outcome are they really buying?
4. Who would pay 10x for premium treatment?
5. What's the simplest version that captures value?

---

## Related Skills

- **@include skill:page-cro**: Optimize your pricing page for conversion
- **@include skill:marketing-psychology**: Apply pricing psychology principles
- **@include skill:ab-test-setup**: Test pricing variations safely
- **@include skill:copywriting**: Write compelling tier descriptions
