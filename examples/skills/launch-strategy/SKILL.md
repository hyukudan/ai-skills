---
name: launch-strategy
description: |
  Plan and execute product launches with decision frameworks for timing,
  channels, and tactics based on product type and audience.
version: 2.0.0
tags: [launch, product-hunt, go-to-market, release, announcement, marketing]
category: marketing/growth
variables:
  launch_type:
    type: string
    description: Scale of the launch
    enum: [major, feature, update]
    default: feature
  product_type:
    type: string
    description: Type of product
    enum: [b2b-saas, b2c-app, devtool, marketplace, content]
    default: b2b-saas
  audience_size:
    type: string
    description: Existing audience
    enum: [none, small, medium, large]
    default: small
scope:
  triggers:
    - launch strategy
    - product launch
    - Product Hunt
    - go-to-market
    - feature release
---

# Launch Strategy

You plan launches that maximize impact for the context.

## Decision Framework

```
LAUNCH TYPE → TIMELINE → CHANNELS → TACTICS

major   → 4-8 weeks prep → all channels → full campaign
feature → 1-2 weeks prep → owned + 1-2 rented → focused push
update  → 1-3 days prep  → changelog + social → momentum signal
```

---

## Launch Type Selection

| Signal | → Launch Type |
|--------|---------------|
| New product, pivot, major milestone | major |
| Significant new capability | feature |
| Improvements, fixes, small additions | update |

{% if launch_type == "major" %}
## Major Launch

### Timeline

| Phase | When | Focus |
|-------|------|-------|
| Foundation | -8 to -4 weeks | Messaging, assets, partnerships |
| Anticipation | -4 to -1 weeks | Waitlist, early access, FOMO |
| Launch Day | D-Day | Coordinated maximum impact |
| Momentum | +1 to +2 weeks | Convert attention to users |

### Channel Mix

{% if product_type == "b2b-saas" %}
**B2B SaaS Priority:**
1. Email list (highest conversion)
2. LinkedIn (decision makers)
3. Product Hunt (if tech audience)
4. Industry newsletters (borrowed)
{% elif product_type == "devtool" %}
**DevTool Priority:**
1. Hacker News (if genuinely novel)
2. Dev Twitter
3. GitHub (if open source)
4. Dev newsletters (borrowed)
{% elif product_type == "b2c-app" %}
**B2C App Priority:**
1. TikTok/Instagram (awareness)
2. App Store optimization
3. Influencer partnerships
4. PR for broad reach
{% elif product_type == "marketplace" %}
**Marketplace Priority:**
1. Supply side first (chicken-egg)
2. Local/niche communities
3. Referral mechanics
4. PR for demand side
{% endif %}

### Success Metrics

| Metric | Good | Great |
|--------|------|-------|
| Waitlist → Signup | 30% | 50%+ |
| Day 1 active users | 20% of signups | 40%+ |
| Week 1 retention | 30% | 50%+ |

{% elif launch_type == "feature" %}
## Feature Launch

### Timeline

| Phase | When | Action |
|-------|------|--------|
| Prep | -2 weeks | Assets, copy, early access |
| Soft launch | -1 week | Power users, feedback |
| Announce | D-Day | Blog + email + social |
| Follow-up | +3 days | User stories, tips |

### Channel Mix

1. Email to relevant segments (not full list)
2. In-app announcement
3. Blog post
4. Social (LinkedIn or Twitter based on audience)

### Success Metrics

| Metric | Good | Great |
|--------|------|-------|
| Feature adoption | 10% of users | 25%+ |
| Support tickets | <5% increase | No increase |
| Expansion revenue | Any | Measurable lift |

{% elif launch_type == "update" %}
## Update/Changelog

### Timeline

Same day: Write → Review → Publish → Share

### Channel Mix

1. Changelog entry
2. In-app notification (if relevant)
3. Single social post
4. Slack/Discord community

### Why It Matters

- Shows momentum (product is alive)
- Keeps users engaged
- SEO benefit (fresh content)
- Compounds over time

{% endif %}

---

## Product Hunt Decision

```
USE PRODUCT HUNT IF:
✓ Tech-savvy early adopter audience
✓ Product has visual appeal / demo-ability
✓ Can dedicate full day to engagement
✓ Have 500+ genuine supporters to mobilize

SKIP PRODUCT HUNT IF:
✗ Enterprise/non-technical audience
✗ Product requires lengthy explanation
✗ Can't monitor comments all day
✗ Main value is behind complex setup
```

{% if launch_type == "major" %}
### Product Hunt Execution

**Timing:** 12:01 AM PST (full 24 hours)

**Day Structure:**
```
Hours 0-2:   Team engagement, first email blast
Hours 2-8:   Respond to ALL comments <30 min
Hours 8-16:  Second push, momentum update
Hours 16-24: Final push, thank supporters
```

**What drives ranking:**
- Upvote count + upvoter karma
- Comment engagement (quality > quantity)
- Spread of upvotes (not burst)

**What gets you flagged:**
- Asking for upvotes directly
- Suspicious voting patterns
- Mass-adding voters
{% endif %}

---

## Audience Size Strategy

{% if audience_size == "none" %}
### No Existing Audience

**Reality check:** Launch to no one = no results

**Before launching:**
1. Build waitlist (minimum 500 emails)
2. Create content for 4-8 weeks
3. Engage in communities where audience lives
4. Line up borrowed channels (podcasts, newsletters)

**Best channels:**
- Borrowed > Rented > Owned (you have no owned)
- Focus on 1 community deeply
- Personal outreach to 100 target users

{% elif audience_size == "small" %}
### Small Audience (<5K)

**Leverage:**
- Email list for core conversion
- Personal asks to engaged followers
- 1-2 borrowed channels for reach

**Amplify:**
- Referral mechanics (waitlist with rewards)
- User-generated content from early users
- Strategic comments on larger accounts

{% elif audience_size == "medium" %}
### Medium Audience (5K-50K)

**Leverage:**
- Segmented email campaigns
- Multi-platform social push
- Community (Slack/Discord) for amplification

**Add:**
- Press outreach with angle
- Influencer partnerships
- Paid amplification of best content

{% elif audience_size == "large" %}
### Large Audience (50K+)

**Leverage:**
- Full email list with sequence
- All owned channels simultaneously
- Community as launch army

**Optimize for:**
- Conversion over awareness
- User stories and social proof
- Secondary launches (regions, segments)
{% endif %}

---

## Common Launch Failures

| Failure | Cause | Prevention |
|---------|-------|------------|
| No one shows up | Launched to no audience | Build waitlist first |
| Spike then flatline | No follow-up plan | Schedule week 2-4 content |
| Wrong audience | Product Hunt for enterprise | Match channel to audience |
| Overwhelmed | One person doing everything | Assign roles, prep templates |
| Bugs kill momentum | Launched before ready | Soft launch to 50 users first |

---

## When NOT to Launch

- **Friday-Sunday:** Weekend kills momentum
- **Major holidays:** Attention elsewhere
- **Competitor's launch day:** Unless strategic
- **Before product is stable:** First impressions matter
- **Without a follow-up plan:** Spike = wasted if no capture

---

## Launch Day Checklist

{% if launch_type == "major" %}
### Major Launch

**Before:**
- [ ] 500+ waitlist emails
- [ ] Assets ready (screenshots, video, GIFs)
- [ ] Blog post written
- [ ] Email sequences built
- [ ] Social posts scheduled
- [ ] Team roles assigned
- [ ] Response templates prepared
- [ ] Analytics configured

**During:**
- [ ] Email to waitlist
- [ ] Social posts live
- [ ] Blog published
- [ ] Team monitoring all channels
- [ ] Responding within 30 min
- [ ] Tracking metrics hourly

**After:**
- [ ] All inquiries answered
- [ ] Feedback categorized
- [ ] Week 2-4 content scheduled
- [ ] Retro completed
{% elif launch_type == "feature" %}
### Feature Launch

**Before:**
- [ ] Feature tested by power users
- [ ] Blog post / changelog ready
- [ ] Email to relevant segment drafted
- [ ] Social copy ready

**During:**
- [ ] Publish all simultaneously
- [ ] Monitor for issues
- [ ] Engage with responses

**After:**
- [ ] Track adoption metrics
- [ ] Collect feedback
- [ ] Plan tips/tutorial content
{% endif %}

---

## Related Skills

- **@include skill:email-sequence**: Launch email campaigns
- **@include skill:social-content**: Launch social content
- **@include skill:page-cro**: Optimize launch landing page
