---
name: analytics-tracking
description: |
  Set up analytics tracking that informs decisions. Covers GA4 implementation,
  event design, UTM strategy, and tracking plans.
license: MIT
allowed-tools: Read WebFetch
version: 1.0.0
tags: [analytics, tracking, ga4, gtm, events, utm, measurement]
category: marketing/analytics
scope:
  triggers:
    - analytics tracking
    - GA4
    - Google Analytics
    - conversion tracking
    - event tracking
    - UTM parameters
    - tag manager
    - GTM
---

# Analytics Tracking

You help implement tracking that produces actionable data. Every event should inform a decision.

## Core Principles

1. **Track for decisions, not data** - Every event should inform an action
2. **Start with questions** - What do you need to know? Work backwards
3. **Name consistently** - Establish conventions before implementing
4. **Maintain quality** - Clean data > more data

---

## Event Naming

**Recommended format: object_action**
```
signup_completed
button_clicked
form_submitted
purchase_completed
```

**Best practices:**
- Lowercase with underscores
- Be specific: `cta_hero_clicked` vs `button_clicked`
- Context in properties, not event name
- Document everything

---

## Essential Events

### Marketing Site
```
page_view, scroll_depth
cta_clicked, form_submitted
signup_started, signup_completed
demo_requested
```

### Product/App
```
onboarding_step_completed, feature_used
trial_started, checkout_started
purchase_completed, subscription_cancelled
```

### E-commerce
```
product_viewed, product_added_to_cart
checkout_started, purchase_completed
```

---

## Event Properties

**Standard properties:**
- page_title, page_location
- user_id (if logged in), user_type
- source, medium, campaign (UTMs)
- product_id, price, quantity (e-commerce)

---

## GA4 Implementation

**Custom event (gtag):**
```javascript
gtag('event', 'signup_completed', {
  'method': 'email',
  'plan': 'free'
});
```

**Via GTM dataLayer:**
```javascript
dataLayer.push({
  'event': 'signup_completed',
  'method': 'email',
  'plan': 'free'
});
```

**Mark as conversion:** Admin > Events > Toggle conversion

---

## UTM Parameters

| Parameter | Purpose | Example |
|-----------|---------|---------|
| utm_source | Traffic origin | google, newsletter |
| utm_medium | Channel type | cpc, email, social |
| utm_campaign | Campaign name | spring_sale |
| utm_content | Differentiate versions | hero_cta |

**Conventions:**
- Lowercase everything
- Use underscores consistently
- Be specific: `blog_footer_cta` not `cta1`
- Document all UTMs in a central location

---

## Validation

**Testing tools:**
- GA4 DebugView (`?debug_mode=true`)
- GTM Preview Mode
- Browser extensions (Tag Assistant)

**Checklist:**
- [ ] Events fire on correct triggers
- [ ] Properties populate correctly
- [ ] No duplicate events
- [ ] Works on mobile
- [ ] No PII leaking

---

## Tracking Plan Template

```
# [Site] Tracking Plan

## Events

| Event Name | Description | Properties | Trigger |
|------------|-------------|------------|---------|
| signup_completed | User completes signup | method, plan | Success page |

## Conversions

| Conversion | Event | Google Ads Import |
|------------|-------|-------------------|
| Signup | signup_completed | Yes |

## UTM Convention
[Your guidelines]
```

---

## Related Skills

- **@include skill:ab-test-setup**: Experiment tracking
- **@include skill:page-cro**: Uses this data for optimization
