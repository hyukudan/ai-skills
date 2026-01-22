---
name: popup-cro
description: |
  Decision frameworks for when and how to use popups. Covers trigger selection,
  timing optimization, and when popups hurt more than help.
version: 2.0.0
tags: [popups, modals, conversion, lead-capture, cro]
category: marketing/cro
variables:
  popup_type:
    type: string
    description: Type of popup to create
    enum: [email-capture, exit-intent, slide-in, banner]
    default: email-capture
  site_type:
    type: string
    description: Type of website
    enum: [ecommerce, saas, blog, landing-page]
    default: saas
scope:
  triggers:
    - exit intent
    - popup
    - modal
    - lead capture
    - overlay
---

# Popup Optimization

You decide when popups help conversion and when they hurt.

## Should You Use a Popup?

```
POPUP DECISION:

Is the offer valuable enough to interrupt?
├── No → Don't use popup, use inline or sticky element
└── Yes ↓

Can user discover the offer otherwise?
├── Yes, easily → Don't use popup
└── No/unlikely → Popup may be justified ↓

Will it annoy more users than it converts?
├── Probably → Use less intrusive format (slide-in, banner)
└── No → Modal popup acceptable
```

---

## When NOT to Use Popups

| Situation | Why | Alternative |
|-----------|-----|-------------|
| Mobile traffic >60% | Google penalizes, UX poor | Sticky footer bar |
| High-intent pages (checkout, pricing) | Interrupts conversion flow | None, let them convert |
| Bounce rate already >70% | Popup won't help, may hurt | Fix page content first |
| No clear value exchange | Feels like spam | Build value prop first |
| Under 500 monthly visitors | Not enough data to optimize | Focus on traffic first |
| Repeat visitors (logged in) | Already converted | Personalized inline |

---

## Popup Type Selection

```
TYPE DECISION:

What are you offering?
├── Discount/coupon → Exit-intent (last chance) or banner (sitewide)
├── Lead magnet/content → Scroll-triggered modal (proven interest)
├── Newsletter → Slide-in (less intrusive)
└── Help/chat → Slide-in bottom-right (always)

How intrusive can you be?
├── Low tolerance (enterprise, professional) → Slide-in or banner only
├── Medium (general SaaS) → Scroll-triggered modal
└── Higher tolerance (e-commerce, deals) → Exit-intent acceptable
```

{% if popup_type == "email-capture" %}
## Email Capture Popup

**Best trigger:** Scroll 50% (proven engagement) or 30-60 seconds on page

**Conversion drivers:**
- Specific value prop ("Get our pricing guide" > "Subscribe")
- Social proof ("Join 50,000+")
- Immediate value (10% off, free resource)

**Copy formula:**
```
Headline: [Specific benefit] + [For whom]
Subhead: [Social proof] or [Overcome objection]
CTA: [Get/Claim/Download] + [The thing]
Dismiss: [Soft decline that implies loss]
```

{% elif popup_type == "exit-intent" %}
## Exit Intent Popup

**Detection:** `mouseleave` event with `clientY <= 0` (cursor leaving viewport top)

**When exit-intent works:**
- E-commerce with cart abandonment
- Price-sensitive audience (discount offer)
- Content sites (lead magnet)

**When to skip:**
- Mobile (no reliable detection)
- B2B enterprise (feels desperate)
- Already showed another popup

**Copy approach:** Urgency + last-chance framing
- "Wait! Before you go..."
- "Don't miss out on..."
- Offer should be better than earlier popup

{% elif popup_type == "slide-in" %}
## Slide-In Popup

**Position:** Bottom-right (standard), bottom-left (less common)

**When to use:**
- Want visibility without interruption
- Longer session engagement
- Chat/help prompts
- Secondary offers

**Advantages over modal:**
- Doesn't block content
- Lower bounce impact
- Better mobile UX
- Can persist across pages

{% elif popup_type == "banner" %}
## Banner Popup

**Position:** Top (most common), bottom (sticky footer)

**When to use:**
- Sitewide announcements
- Time-limited offers
- Shipping thresholds
- Cookie consent (required)

**Key rule:** Account for banner height in CSS (`body { padding-top }`)

{% endif %}

---

## Trigger Selection

| Trigger | Conversion Rate | User Perception | Best For |
|---------|----------------|-----------------|----------|
| Immediate (0-5s) | Low | Negative (interruption) | Almost never |
| Time-based (30-60s) | Medium | Neutral | General offers |
| Scroll % (25-50%) | Higher | Positive (earned) | Content sites |
| Exit intent | Medium-high | Mixed | Last-chance offers |
| Click-triggered | Highest | Positive | Lead magnets, demos |
| Page count (2-3) | Medium | Positive | Return visitors |

**Rule of thumb:** Later trigger = better reception, slightly lower volume

---

## Frequency Capping Strategy

```
FREQUENCY DECISION:

User dismissed popup:
├── Soft dismiss (X button) → Show again in 7 days
├── Hard dismiss (decline CTA) → Show again in 30 days
└── Converted → Never show that popup again

User hasn't converted:
├── First visit → Show after trigger met
├── Return visit (same day) → Don't show
└── Return visit (next day+) → Check frequency cap
```

**Storage key pattern:** `popup_{id}_dismissed` with ISO timestamp

---

## Mobile Considerations

```
MOBILE POPUP RULES:

Google interstitial penalty applies if:
- Full-screen popup before main content
- Popup covers >30% of screen
- Not a legal requirement (cookie, age gate)

Safe on mobile:
- Top/bottom banners (<15% screen)
- Slide-ins (<30% screen)
- Exit-intent (doesn't work anyway)
- Click-triggered modals
```

---

## Metrics & Benchmarks

| Metric | Good | Great | Investigate |
|--------|------|-------|-------------|
| View-to-submit | 3-5% | 5-10% | <2% = offer/timing issue |
| Close rate <5s | <30% | <20% | >40% = too early/aggressive |
| Bounce increase | <5% | <2% | >10% = damaging UX |

**A/B test priority:**
1. Trigger timing (biggest impact)
2. Headline copy
3. Offer value
4. Design/layout

---

## Accessibility Requirements

| Requirement | Implementation |
|-------------|----------------|
| Focus trap | Tab cycles within popup |
| Escape close | `keydown` handler for Esc |
| Screen reader | `role="dialog"`, `aria-modal="true"`, `aria-labelledby` |
| Focus restore | Return focus to trigger element on close |

---

## Compliance Checklist

| Regulation | Requirement |
|------------|-------------|
| GDPR | Consent checkbox unchecked by default, privacy link |
| Google SEO | No full-screen mobile interstitials |
| WCAG 2.1 | Keyboard navigable, screen reader compatible |
| CAN-SPAM | Unsubscribe option in all emails collected |

---

## Related Skills

- **@include skill:form-cro**: Optimize form inside popup
- **@include skill:email-sequence**: Nurture after capture
