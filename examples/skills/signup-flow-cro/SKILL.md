---
name: signup-flow-cro
description: |
  Optimize signup and registration flows for higher completion rates.
  Covers field optimization, single vs multi-step, social auth, and mobile.
license: MIT
allowed-tools: Read WebFetch
version: 1.0.0
tags: [cro, signup, registration, conversion, onboarding]
category: marketing/cro
scope:
  triggers:
    - signup conversions
    - registration friction
    - signup form
    - reduce signup dropoff
---

# Signup Flow Optimization

You optimize signup flows to reduce friction and increase completion.

## Core Principles

1. **Minimize fields** - Every field reduces conversion. Defer what you can.
2. **Show value first** - Let them experience before requiring signup
3. **Reduce perceived effort** - Progress bars, smart defaults, pre-fill
4. **Remove uncertainty** - "Takes 30 seconds", show what happens next

---

## Field Priority

**Essential:** Email, Password

**Usually needed:** Name

**Defer if possible:** Company, Role, Team size, Phone

---

## Field Optimization

**Email:** Single field, inline validation, typo correction

**Password:** Show/hide toggle, requirements upfront, allow paste, strength meter

**Social auth:** Place prominently, most relevant options for audience (B2C: Google/Apple, B2B: Google/Microsoft)

---

## Single vs Multi-Step

**Single-step:** 3 or fewer fields, simple products, high-intent visitors

**Multi-step:** 4+ fields, complex B2B, need segmentation
- Show progress
- Easy questions first
- Save progress
- Allow back navigation

---

## Trust Elements

- "No credit card required"
- Privacy note near email field
- Testimonial near form
- Security badges if relevant

---

## Mobile

- Large touch targets (44px+)
- Appropriate keyboard types
- Autofill support
- Single column layout

---

## Related Skills

- **@include skill:onboarding-cro**: Post-signup optimization
- **@include skill:form-cro**: Non-signup forms
- **@include skill:page-cro**: Landing page leading to signup
