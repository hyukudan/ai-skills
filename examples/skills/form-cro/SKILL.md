---
name: form-cro
description: |
  Decision frameworks for form optimization. Which fields to ask, when to use
  multi-step, and how to balance data capture with conversion.
license: MIT
allowed-tools: Read WebFetch
version: 2.0.0
tags: [forms, lead-capture, conversion, cro, ux]
category: marketing/cro
variables:
  form_type:
    type: string
    description: Type of form to optimize
    enum: [lead-capture, contact, demo-request, quote, signup, checkout]
    default: lead-capture
  industry:
    type: string
    description: Industry context
    enum: [saas, ecommerce, agency, finance, healthcare, general]
    default: saas
scope:
  triggers:
    - form optimization
    - lead form
    - form friction
    - form completion
    - contact form
---

# Form Conversion Optimization

You decide which fields to ask and when, balancing data capture with conversion.

## Form Type Selection

```
FORM TYPE DECISION:

What's the goal?
├── Capture email for nurture → Lead capture (1-2 fields)
├── Enable contact/inquiry → Contact form (3-4 fields)
├── Qualify for sales call → Demo request (4-5 fields)
├── Custom pricing → Quote request (multi-step)
├── Create account → Signup (2-3 fields + social)
└── Complete purchase → Checkout (structured sections)

Conversion rate correlation:
├── 1-2 fields → 25%+ conversion
├── 3-4 fields → 15-20% conversion
├── 5-6 fields → 10-15% conversion
└── 7+ fields  → <10% conversion (use multi-step)
```

---

## Field Justification Framework

```
FOR EACH FIELD ASK:

1. Is this required BEFORE we can help?
   ├── Yes → Keep
   └── No → Remove or make optional

2. Can we get this later?
   ├── In the follow-up email → Remove
   ├── On the sales call → Remove
   └── From their behavior → Remove

3. Can we infer it?
   ├── Email domain → Company name
   ├── IP address → Location
   └── Clearbit/enrichment → Company size, industry
```

| Field | Usually Required | Often Removable |
|-------|-----------------|-----------------|
| Email | Yes (always first) | - |
| First name | If personalization matters | If email marketing only |
| Last name | If CRM integration | If nurture sequence |
| Company | If B2B qualification | If can enrich from domain |
| Phone | If outbound sales | If inbound/self-serve |
| Job title | If persona-based routing | If single ICP |
| Company size | If pricing tiers | If ask on call |
| Budget | Almost never | Ask on sales call |
| Timeline | Almost never | Ask on sales call |

---

{% if form_type == "lead-capture" %}
## Lead Capture Form

**Optimal:** Email only, or Email + First Name

| Decision | Recommendation |
|----------|----------------|
| Label | "Work email" qualifies leads, "Email" is generic |
| CTA | "Get [Thing]" > "Submit" > "Subscribe" |
| Trust | "No spam. Unsubscribe anytime." reduces anxiety |
| Placeholder | "you@company.com" reinforces work email |

**When to add First Name:**
- If email personalization significantly impacts open rates
- If immediate personalized confirmation page

**When to skip First Name:**
- Anonymous lead magnet (ebook, tool)
- Volume > quality priority

{% elif form_type == "contact" %}
## Contact Form

**Optimal:** Email, Name, Message

| Decision | Recommendation |
|----------|----------------|
| Name | Single field tests better than First/Last split |
| Subject | Skip dropdown, let them write freely |
| Message | "How can we help?" > "Message" |
| CTA | "Send Message" + response time expectation |

**Avoid:**
- Subject dropdown (reduces freedom, rarely used)
- Phone (unless callback is primary channel)
- Visible captcha (use invisible reCAPTCHA v3)

{% elif form_type == "demo-request" %}
## Demo Request Form

**Optimal:** Email, Name, Company, Company Size (optional)

| Decision | Recommendation |
|----------|----------------|
| Email | "Work email" - filters personal emails |
| Company size | Optional dropdown - for routing to sales tiers |
| Trust elements | "No credit card" + "15 min call" reduces commitment fear |

**Avoid asking (get on the call):**
- Budget range
- Timeline
- Specific pain points (open-ended takes time)

**Consider adding:**
- Calendar embed after submit (Calendly) - reduces scheduling friction
- Self-scheduling vs sales assignment based on company size

{% elif form_type == "quote" %}
## Quote Request (Multi-Step)

**When to use multi-step:**
- 6+ fields required
- Complex configuration
- Industry expectation (insurance, services)

```
MULTI-STEP STRUCTURE:

Step 1: Easy (email, name)
├── Lowest friction, captures lead even if abandon
└── "Let's start with the basics"

Step 2: Requirements (services, options)
├── Show relevance of questions
└── "What do you need?"

Step 3: Details (timeline, notes)
├── Almost done psychology
└── "Almost there!"
```

| Pattern | Why |
|---------|-----|
| Progress indicator | Shows completion, reduces perceived effort |
| Back buttons | Reduces fear of commitment |
| Save on each step | Enables recovery emails |
| Focus first field | Maintains momentum |

{% elif form_type == "signup" %}
## Signup Form

```
SIGNUP PATTERN DECISION:

Product type?
├── B2B SaaS → Email + Password (social optional)
├── Developer tool → GitHub/Google primary
├── Consumer → Social-first (Google, Apple)
└── High-security → Email + Password only

Progressive profile?
├── Yes → Email only, profile after activation
└── No → Email + Password minimum
```

| Decision | Recommendation |
|----------|----------------|
| Social login | Offer 2 max (most used by your audience) |
| Password | Show/hide toggle, strength indicator |
| Terms | "By signing up, you agree to Terms" (link, don't checkbox) |
| Verification | Email verification after, not during signup |

{% elif form_type == "checkout" %}
## Checkout Form

```
CHECKOUT STRUCTURE:

1. Email FIRST
   └── Enables cart recovery even if abandon

2. Shipping
   └── Use autocomplete heavily

3. Payment
   └── Trust badges visible

4. Review (optional)
   └── Only if complex order
```

| Decision | Recommendation |
|----------|----------------|
| Guest checkout | Always offer (account creation post-purchase) |
| Express payment | Apple Pay, Google Pay above fold |
| Address | Autocomplete (Google Places) |
| Promo code | Collapsed by default (reduces "let me find a code") |
| Order summary | Sticky on desktop, collapsed on mobile |

{% endif %}

---

{% if industry == "saas" %}
## SaaS-Specific Decisions

| Scenario | Recommendation |
|----------|----------------|
| Self-serve vs sales | Company size determines routing |
| Free trial vs demo | Trial: minimal fields. Demo: qualify |
| PLG motion | Start with email only, progressive profile |
| Integration questions | Ask post-signup, not in form |

{% elif industry == "ecommerce" %}
## E-commerce-Specific Decisions

| Scenario | Recommendation |
|----------|----------------|
| Guest checkout | Always offer, 30%+ abandon if forced account |
| Address | Google Places autocomplete mandatory |
| Express checkout | Apple Pay/Google Pay above fold |
| Account creation | Offer post-purchase with one click |

{% elif industry == "finance" %}
## Finance-Specific Decisions

| Scenario | Recommendation |
|----------|----------------|
| SSN, DOB | Progressive disclosure, explain why needed |
| Long applications | Save progress, email recovery |
| Compliance | GLBA notice, clear data usage |
| Trust | Security badges, encryption messaging |

{% elif industry == "healthcare" %}
## Healthcare-Specific Decisions

| Scenario | Recommendation |
|----------|----------------|
| HIPAA | Consent checkbox before sensitive questions |
| DOB | Date picker (not free text) for accuracy |
| Insurance | Autocomplete for provider names |
| Telehealth | Include timezone selection |

{% endif %}

---

## Validation Strategy

```
VALIDATION TIMING:

When to validate?
├── On blur (field exit) → Show errors
├── On input (typing) → Clear errors only
└── On submit → Focus first error

What to show?
├── Error → Red border + message below
├── Success → Green checkmark (optional)
└── Loading → Spinner on async validation
```

| Pattern | Why |
|---------|-----|
| Validate on blur | Typing validation is annoying |
| Clear on input | Give immediate feedback they're fixing it |
| Don't clear value | Never delete what user typed |
| Email typo detection | "Did you mean @gmail.com?" |
| Focus first error | User knows where to fix |

---

## Mobile-Specific Decisions

| Decision | Recommendation |
|----------|----------------|
| Font size | 16px minimum (prevents iOS zoom) |
| Touch targets | 44px minimum height |
| Input types | `type="email"`, `type="tel"` for correct keyboard |
| Autocomplete | Always set `autocomplete` attributes |
| Labels | Above input, not placeholder-only (accessibility + clarity) |

---

## A/B Test Priority

| Test | Expected Impact | Metric |
|------|-----------------|--------|
| Remove one field | High | Completion rate |
| Single step vs multi-step | High | Completion rate |
| CTA copy | Medium | Submit rate |
| Social login presence | Medium | Signup rate |
| Trust badges | Low-Medium | Conversion rate |
| Field order | Low | Completion rate |

---

## Checklist

### Field Decisions
- [ ] Each field has clear business justification
- [ ] Removed everything that can be asked later
- [ ] Removed everything that can be inferred/enriched
- [ ] Required vs optional is intentional

### UX
- [ ] Autocomplete attributes on all inputs
- [ ] Correct input types (email, tel, etc.)
- [ ] 16px+ font size (mobile)
- [ ] 44px+ touch targets
- [ ] Single column layout

### Validation
- [ ] Validate on blur, clear on input
- [ ] Error messages suggest fixes
- [ ] Never clear user input on error
- [ ] Focus management on errors

### Trust
- [ ] Privacy statement or link present
- [ ] Response time expectation set
- [ ] Security badges if collecting sensitive data

### Accessibility
- [ ] Labels properly linked (for/id)
- [ ] Error messages announced (aria-live)
- [ ] Focus states visible
- [ ] Full keyboard navigation

---

## Related Skills

- `popup-cro` - Forms in modals and overlays
- `email-sequence` - What happens after form submission
