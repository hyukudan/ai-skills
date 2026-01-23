---
name: paywall-upgrade-cro
description: |
  Optimize in-app paywalls, upgrade screens, and feature gates. Convert free users
  to paid at moments of experienced value with feature locks, usage limits, and trial flows.
license: MIT
allowed-tools: Read WebFetch
version: 1.0.0
tags: [paywall, upgrade, monetization, freemium, conversion, saas]
category: marketing/cro
scope:
  triggers:
    - paywall
    - upgrade screen
    - upsell
    - feature gate
    - freemium conversion
    - trial expiration
    - plan upgrade
---

# Paywall & Upgrade Optimization

You convert free users to paid at moments of experienced value.

## Fundamental Rules

**1. Value before ask**
- User must have experienced real value
- Upgrade feels like natural next step
- After aha moment, not before

**2. Demonstrate, don't just list**
- Preview what they're missing
- Show the feature in action
- Make upgrade tangible

**3. Friction-free path**
- Easy to upgrade when ready
- Don't hide pricing
- Remove conversion barriers

**4. Respect the decline**
- Don't trap or pressure
- Easy to continue free
- Trust enables future conversion

---

## Trigger Points

### Feature Gates
When clicking paid feature:
- Explain why it's paid
- Show what it does
- Quick unlock path
- Option to continue without

### Usage Limits
When hitting limit:
- Clear indication of limit reached
- Show what upgrading provides
- Option to buy more without full upgrade
- Don't block abruptly

### Trial Expiration
As trial ends:
- Early warnings (7, 3, 1 day)
- Clear "what happens" at expiration
- Summarize value received
- Easy restart if expired

### Context-Triggered
When behavior indicates fit:
- Power users who'd benefit
- Heavy usage near limits
- Team features for solo users
- Inviting teammates

---

## Paywall Components

**1. Headline** — What they get, not what they pay
- "Unlock [Feature] to [Benefit]"
- Not: "Upgrade to Pro for $X/month"

**2. Value Demonstration**
- Preview feature in action
- Before/after comparison
- "With Pro, you could..." examples

**3. Feature Comparison** (if showing tiers)
- Key differences highlighted
- Current plan marked
- Recommended plan emphasized

**4. Pricing**
- Clear, simple
- Annual vs. monthly
- Per-seat clarity
- Trial/guarantee info

**5. CTA**
- Specific: "Upgrade to Pro"
- Value-oriented: "Start Getting [Benefit]"
- If trial: "Start Free Trial"

**6. Escape Hatch**
- "Continue with Free" clearly visible
- Don't guilt-trip

---

## Paywall Templates

### Feature Lock
```
[Lock Icon]
This feature is available on Pro

[Feature preview]

[Feature] helps you [benefit]:
• [Capability 1]
• [Capability 2]

[Upgrade to Pro - $X/mo]
[Maybe Later]
```

### Usage Limit
```
You've reached your free limit

[Progress bar at 100%]

Free: 3 projects | Pro: Unlimited

[Upgrade to Pro]  [Delete a project]
```

### Trial Ending
```
Your trial ends in 3 days

What you'll lose:
• [Feature used]
• [Work created]

What you've done:
• Created X projects

[Continue with Pro]
[Remind me later]  [Downgrade]
```

---

## Timing & Frequency

**When to show:**
- After value moment, before frustration
- After activation/aha moment
- When hitting genuine limits

**When NOT to show:**
- During onboarding (too early)
- Mid-flow
- Repeatedly after dismissal

**Rules:**
- Limit per session
- Cool-down after dismiss (days, not hours)
- Escalate appropriately for trial end

---

## Upgrade Flow

**From paywall to payment:**
- Minimize steps
- Keep in-context if possible
- Pre-fill known info
- Show security signals

**Plan selection:**
- Default to recommended
- Clear annual vs. monthly trade-off
- FAQ nearby

**Post-upgrade:**
- Immediate feature access
- Guide to new features
- Celebration

---

## Anti-Patterns

**Dark patterns:** Hidden close, confusing selection, buried downgrade, guilt-trip copy

**Conversion killers:** Asking before value, too frequent, blocking critical flows

**Trust destroyers:** Surprise charges, hard cancellation, data hostage

---

## By Business Model

**Freemium SaaS:**
- Generous free tier
- Feature gates for power features
- Usage limits for volume
- Soft prompts for heavy users

**Free Trial:**
- Countdown prominent
- Value summary at expiration
- Grace period or easy restart

**Usage-Based:**
- Clear usage tracking
- Alerts at thresholds (75%, 100%)
- Easy to add more

**Per-Seat:**
- Friction at invitation
- Team feature highlights
- Volume pricing clear

---

## Psychology

**Loss aversion:** "Don't lose your 50 projects" > "Get unlimited projects"

**Endowment:** "Your 3 projects are safe" — reference their investment

**Sunk cost:** "You've created 20 designs—don't stop now"

**Social proof:** "Teams your size choose Pro"

---

## Testing Ideas

**Triggers:** Earlier vs. later, hard gate vs. soft prompt

**Presentation:** Feature list vs. benefits, show loss vs. gain

**Pricing:** Monthly vs. annual default, include price in CTA or not

**Trial:** 7 vs. 14 days, credit card required vs. not

---

## Related Skills

- **@include skill:page-cro**: Public pricing page
- **@include skill:onboarding-cro**: Driving to aha moment
- **@include skill:pricing-strategy**: Pricing model decisions
