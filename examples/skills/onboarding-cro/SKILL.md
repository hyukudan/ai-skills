---
name: onboarding-cro
description: |
  Optimize user activation and first-run experience. Help users reach value quickly
  through onboarding flows, checklists, empty states, and engagement loops.
license: MIT
allowed-tools: Read WebFetch
version: 1.0.0
tags: [onboarding, activation, retention, ux, product, cro]
category: marketing/cro
scope:
  triggers:
    - onboarding flow
    - activation rate
    - user activation
    - first-run experience
    - empty states
    - aha moment
    - time to value
---

# User Activation Optimization

You optimize the journey from signup to value realization.

## Activation Fundamentals

**Find your aha moment:** The action that predicts retention
- What do retained users do that churned users don't?
- What's the earliest indicator of engagement?

**Examples by product:**
- Project tool: Create project + add teammate
- Analytics: Install tracking + see first report
- Design app: Create + export/share design
- Marketplace: Complete first transaction

**Key metrics:**
- % signups reaching activation
- Time to activation
- Steps to activation

---

## Core Principles

**1. Compress time-to-value**
- Remove every step between signup and value
- Consider: Can they experience value BEFORE signup?

**2. One goal per session**
- Don't teach everything at once
- Focus first session on one win

**3. Action over explanation**
- Interactive > Tutorial
- Doing > Watching

**4. Progress creates momentum**
- Show advancement
- Celebrate completions

---

## Onboarding Patterns

### Immediate Post-Signup

**Product-first:** Drop directly in
- Best for: Simple products, B2C, mobile
- Risk: Empty state overwhelm

**Guided setup:** Short wizard
- Best for: Products needing personalization
- Risk: Friction before value

**Value-first:** Show outcome immediately
- Best for: Products with demo data
- Risk: May feel artificial

### Checklist Pattern

Best for multi-step setup or feature discovery.

**Structure:**
- 3-7 items (not overwhelming)
- Order by value delivered
- Start with quick wins
- Progress bar visible
- Dismissable (don't trap)

```
☐ Connect data source (2 min)
  Get real-time insights from your tools
  [Connect Now]
```

### Empty States

Transform dead ends into activation moments.

**Include:**
1. What this area does
2. Preview with data
3. Primary CTA to add first item
4. Secondary: Import or template

### Tooltips and Tours

**Use when:** Complex UI, non-obvious features
**Avoid when:** Simple interface, mobile apps

**Rules:**
- Max 3-5 steps
- Point to actual UI
- Dismissable anytime
- Don't repeat for returning users

---

## Multi-Channel Coordination

**Email triggers:**
- Welcome (immediate)
- Incomplete onboarding (24h, 72h)
- Activation achieved (celebrate + next step)
- Feature discovery (days 3, 7, 14)

**Email should:**
- Reinforce, not duplicate in-app
- Drive back with specific CTA
- Personalize based on actions taken

---

## Engagement Loops

**Building habits:**
```
Trigger → Action → Variable Reward → Investment
```

- Trigger: Email digest, notification
- Action: Log in to respond
- Reward: Progress, achievement, social
- Investment: More data, connections, content

**Milestones:** Acknowledge achievements, suggest next one, make shareable

---

## Re-engaging Stalled Users

**Detection:** X days inactive, incomplete setup

**Tactics:**
1. **Email:** Value reminder, address blockers, offer help
2. **In-app:** Welcome back, simplified path
3. **Human touch:** For high-value accounts

---

## Psychology Principles

**IKEA Effect:** Users value what they build. Let them create something.

**Endowed Progress:** Start at 20%, not 0%. People complete what's started.

**Zeigarnik Effect:** Incomplete tasks persist in memory. Leave clear next action.

---

## By Product Type

**B2B SaaS:** Setup wizard → First value action → Team invite → Deeper setup

**Marketplace:** Profile → First search → First transaction → Repeat loop

**Mobile App:** Permissions (strategic timing) → Quick win → Push setup → Habit loop

**Content Platform:** Customize feed → Consume → Create → Engage

---

## Related Skills

- **@include skill:signup-flow-cro**: Pre-onboarding optimization
- **@include skill:email-sequence**: Onboarding email series
- **@include skill:paywall-upgrade-cro**: Converting to paid post-activation
