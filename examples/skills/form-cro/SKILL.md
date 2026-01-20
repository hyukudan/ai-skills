---
name: form-cro
description: |
  Optimize lead capture, contact, and request forms for higher completion rates.
  Covers field strategy, layout, validation, and mobile optimization.
version: 1.0.0
tags: [forms, lead-capture, conversion, cro, ux, marketing]
category: marketing/cro
scope:
  triggers:
    - form optimization
    - lead form
    - form friction
    - form completion
    - contact form
    - demo request form
---

# Form Conversion Optimization

You maximize form completion while capturing essential data.

## Field Economics

Each field costs conversions:
- 3 fields: Baseline
- 4-6 fields: -10-25%
- 7+ fields: -25-50%

**For each field ask:**
- Is this required before we can help?
- Can we get this later or elsewhere?
- Can we infer it (email domain → company)?

---

## Field-Specific Guidance

**Email:** Single field, inline validation, typo detection, mobile keyboard

**Name:** Test single vs. First/Last (single = less friction)

**Phone:** Optional if possible, explain why if required, auto-format

**Company:** Auto-suggest, enrich post-submission (Clearbit), infer from domain

**Dropdowns:** Placeholder "Select one...", searchable if many, radio if <5 options

**Free text:** Optional, expand on focus, reasonable guidance

---

## Layout Principles

**Field order:**
1. Easy fields first (name, email)
2. Build commitment
3. Sensitive last (phone, company size)

**Labels:** Always visible (not placeholder-only)

**Placeholders:** Examples, not labels

**Single column** > multi-column (higher completion, mobile-friendly)

---

## Multi-Step Forms

**Use when:** 5+ fields, distinct sections, conditional logic

**Rules:**
- Progress indicator (step X of Y)
- Easy before sensitive
- One topic per step
- Allow back navigation
- Save progress

**Progressive commitment:**
1. Just email
2. Name, company
3. Qualifying questions
4. Contact preferences

---

## Validation & Errors

**Inline validation:** On blur (not while typing), clear indicators

**Error messages:**
- Specific to problem
- Suggest fix
- Near the field
- Don't clear input

Good: "Please enter a valid email (e.g., name@company.com)"
Bad: "Invalid input"

---

## Submit Button

**Copy formula:** [Action] + [What they get]
- "Get My Free Quote"
- "Download the Guide"
- "Request Demo"

**Not:** "Submit", "Send"

**States:** Loading (disable + spinner), success (clear next steps), error (focus on issue)

---

## Trust Elements

**Near form:**
- "We'll never share your info"
- Security badges if sensitive data
- Expected response time

**Reducing perceived effort:**
- "Takes 30 seconds"
- Field count indicator
- White space

---

## By Form Type

**Lead Capture:** Minimum fields (often just email), clear value, test email-only vs. +name

**Contact:** Email + Name + Message, phone optional, set response expectations

**Demo Request:** Name, Email, Company required; calendar embed increases show rate

**Quote Request:** Multi-step works well, start easy, technical details later

---

## Mobile

- Touch targets 44px+
- Appropriate keyboard types
- Autofill support
- Single column only
- Sticky submit button

---

## Measurement

**Track:**
- Form start rate (page → started)
- Completion rate (started → submitted)
- Field drop-off
- Error rate by field
- Mobile vs. desktop completion

---

## Psychology

**Foot-in-the-door:** Small ask first, then more

**Loss aversion:** Frame around what they'll miss

**Social proof:** "Join 10,000+ marketers" near form

---

## Related Skills

- **@include skill:signup-flow-cro**: Account creation forms
- **@include skill:popup-cro**: Forms inside modals
- **@include skill:page-cro**: Page containing the form
