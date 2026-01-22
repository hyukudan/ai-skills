---
name: email-sequence
description: |
  Create email sequences and drip campaigns. Covers welcome, nurture, re-engagement,
  onboarding, and billing emails with templates and timing strategies.
version: 1.1.0
tags: [email, marketing, automation, drip-campaign, lifecycle, nurture]
category: marketing/content
variables:
  sequence_type:
    type: string
    description: Type of email sequence to create
    enum: [welcome, nurture, reengagement, onboarding, sales]
    default: welcome
  business_type:
    type: string
    description: Type of business
    enum: [saas, ecommerce, agency, content, general]
    default: saas
scope:
  triggers:
    - email sequence
    - drip campaign
    - nurture sequence
    - onboarding emails
    - welcome sequence
    - email automation
---

# Email Sequence Design

You create email sequences that nurture relationships and drive conversion.

## Core Principles

**One email, one job.** Single primary purpose, one main CTA.

**Value before ask.** Lead with usefulness, earn the right to sell.

**Relevance over volume.** Fewer, better emails win.

**Clear path forward.** Every email moves them somewhere.

---

## Email Anatomy

```
┌────────────────────────────────────────────────────────────┐
│  FROM: Name <email@company.com>                            │
│  SUBJECT: [Hook] + [Value Promise]                         │
│  PREVIEW: First 90 chars that expand on subject            │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  HOOK (Line 1)                                             │
│  ─────────────                                             │
│  Grab attention, create curiosity                          │
│                                                            │
│  CONTEXT (2-3 sentences)                                   │
│  ──────────────────────                                    │
│  Why this matters to them right now                        │
│                                                            │
│  VALUE (Main content)                                      │
│  ───────────────────                                       │
│  The useful thing they came for                            │
│                                                            │
│  CTA (Single, clear action)                                │
│  ─────────────────────────                                 │
│  [Button or link - one action]                             │
│                                                            │
│  P.S. (Optional hook)                                      │
│  ─────────────────────                                     │
│  Secondary point or urgency                                │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

---

## Sequence Parameters

| Sequence Type | Length | Spacing | Goal |
|--------------|--------|---------|------|
| Welcome | 5-7 emails | Day 0,1,3,5,7,10,14 | Activate & educate |
| Lead Nurture | 6-10 emails | Every 2-4 days | Build trust & convert |
| Onboarding | 5-8 emails | Day 0,1,3,5,7,14,21 | Drive to "aha moment" |
| Re-engagement | 3-5 emails | Day 0,3,7,14 | Win back or clean list |
| Sales | 4-6 emails | Day 0,2,4,6,8 | Close the deal |

---

{% if sequence_type == "welcome" %}
## Welcome Sequence

### Sequence Overview

```
Day 0: Immediate welcome + deliver promise
Day 1: Quick win / easy first step
Day 3: Your story or mission
Day 5: Social proof / case study
Day 7: Address main objection
Day 10: Core feature highlight
Day 14: Soft conversion ask
```

### Email 1: Welcome (Send Immediately)

**Goal:** Deliver what was promised, set expectations

**Subject Lines:**
- "Welcome to [Company] - here's your [thing]"
- "[Name], you're in! Here's what happens next"
- "Your [thing] is ready"

**Template:**
```
Hey [Name],

Welcome to [Company]! I'm [Your name], [role].

Here's what you signed up for:
[Deliver the lead magnet / access / promise]

👉 [CTA Button: Access Your [Thing]]

What to expect from us:
- [Frequency] emails about [topic]
- [Key benefit 1]
- [Key benefit 2]

One thing to do right now:
[Single, specific action that takes <2 minutes]

Talk soon,
[Name]

P.S. Reply to this email if you have any questions.
I read every response.
```

### Email 2: Quick Win (Day 1-2)

**Goal:** Get them a small success fast

**Subject Lines:**
- "Do this in 5 minutes (big impact)"
- "The fastest way to [desired outcome]"
- "Your first [result] starts here"

**Template:**
```
Hey [Name],

Most [audience type] struggle with [common problem].

Here's the fastest fix:

Step 1: [Simple action]
Step 2: [Simple action]
Step 3: [Simple action]

That's it. Takes 5 minutes, saves hours.

👉 [CTA: Try it now]

[Name]

P.S. Tomorrow I'll share [teaser for next email].
```

### Email 3: Story/Why (Day 3-4)

**Goal:** Build connection through origin story

**Subject Lines:**
- "Why I started [Company]"
- "The problem that started everything"
- "We almost didn't build this"

**Template:**
```
Hey [Name],

[Number] years ago, I was [relatable situation].

The problem was [specific pain point].

I tried [common solutions that fail]:
- [Failed approach 1]
- [Failed approach 2]

Nothing worked until [breakthrough moment].

That's when I realized [key insight].

So I built [Company] to [mission statement].

Today, we've helped [number] [audience] [achieve result].

You're part of this now.

👉 [CTA: See how it works]

[Name]
```

### Email 4: Social Proof (Day 5-6)

**Goal:** Build trust through results

**Subject Lines:**
- "How [Customer] got [specific result]"
- "[Number]% improvement in [metric]"
- "From [before state] to [after state]"

**Template:**
```
Hey [Name],

Meet [Customer name], [role at Company].

Before: [Their struggle in their words]

They tried [what didn't work].

Then they [what they did with your product].

After [timeframe]:
✓ [Specific result with number]
✓ [Specific result with number]
✓ [Specific result with number]

"[Short testimonial quote]" — [Customer name]

👉 [CTA: Get similar results]

[Name]
```

### Email 5: Objection Handler (Day 7-8)

**Goal:** Address the main reason they haven't acted

**Subject Lines:**
- "The #1 reason people don't [action]"
- "I know what you're thinking..."
- "Is [common objection] holding you back?"

{% if business_type == "saas" %}
**Common SaaS Objections:**
- "It's too complicated to set up"
- "I don't have time to learn a new tool"
- "I'm not sure it will work for my use case"
- "The price is too high"
{% elif business_type == "ecommerce" %}
**Common E-commerce Objections:**
- "Shipping takes too long"
- "What if it doesn't fit/work?"
- "I can find it cheaper elsewhere"
- "I'm not sure about the quality"
{% elif business_type == "agency" %}
**Common Agency Objections:**
- "I've been burned by agencies before"
- "It's too expensive"
- "I can do it myself"
- "How do I know you'll understand my business?"
{% endif %}

**Template:**
```
Hey [Name],

I hear this a lot: "[Main objection]"

I get it. [Validate their concern].

Here's the truth: [Reframe the objection]

[Evidence that addresses the objection]:
- [Point 1]
- [Point 2]
- [Point 3]

Still not sure? [Low-risk offer or guarantee]

👉 [CTA: Give it a try]

[Name]

P.S. [Reinforce low-risk nature]
```

### Email 6: Core Feature (Day 10-11)

**Goal:** Highlight underused capability

**Template:**
```
Hey [Name],

Most [audience] miss this.

[Feature name] can [specific benefit].

Here's how it works:
[3-step explanation with specifics]

Real example:
[Before/after scenario]

👉 [CTA: Try [feature]]

[Name]
```

### Email 7: Conversion (Day 14)

**Goal:** Clear ask with urgency if appropriate

**Template:**
```
Hey [Name],

It's been [time] since you joined.

Quick question: Have you [taken key action] yet?

If not, here's why now is the time:
[Reason 1 - benefit reminder]
[Reason 2 - what they're missing]
[Reason 3 - urgency if genuine]

[Special offer if applicable]

👉 [CTA: Start now]

[Name]

P.S. [Specific deadline or consequence of waiting]
```

{% elif sequence_type == "nurture" %}
## Lead Nurture Sequence

### Sequence Overview

```
Email 1: Deliver lead magnet + introduce
Email 2: Expand on topic (value)
Email 3: Problem deep-dive (agitate)
Email 4: Solution framework (educate)
Email 5: Case study (prove)
Email 6: Differentiation (position)
Email 7: Objection handler (overcome)
Email 8: Direct offer (convert)
```

### Email 1: Deliver + Introduce (Immediate)

**Subject:** "Your [lead magnet] is ready"

**Template:**
```
Hey [Name],

Here's your [lead magnet]:

👉 [Download/Access link]

Inside, you'll learn:
- [Key takeaway 1]
- [Key takeaway 2]
- [Key takeaway 3]

Over the next [timeframe], I'll send you [what to expect].

Quick tip: Start with [specific section] first.
It's the fastest way to [quick result].

[Name]
[Company]
```

### Email 2: Expand on Topic (Day 2-3)

**Subject:** "What [lead magnet] didn't cover..."

**Template:**
```
Hey [Name],

Hope you got value from [lead magnet].

There's one thing I couldn't fit in:

[Valuable insight or technique]

Here's why this matters:
[Explanation with specifics]

How to apply this:
1. [Actionable step]
2. [Actionable step]
3. [Actionable step]

Tomorrow, I'll share [teaser].

[Name]
```

### Email 3: Problem Deep-Dive (Day 4-5)

**Subject:** "The hidden cost of [problem]"

**Template:**
```
Hey [Name],

Let's talk about [problem] honestly.

Most [audience] deal with:
- [Pain point 1]
- [Pain point 2]
- [Pain point 3]

The real cost? [Quantified impact]

I've seen [audience] waste [time/money] on [ineffective solutions].

Sound familiar?

Tomorrow, I'll share the framework that changes this.

[Name]
```

### Email 4: Solution Framework (Day 6-8)

**Subject:** "The [Name] Framework for [outcome]"

**Template:**
```
Hey [Name],

Yesterday I talked about [problem].

Here's the fix—the [Framework Name]:

[Letter/Step 1]: [Concept]
What it means: [Explanation]
How to do it: [Specific action]

[Letter/Step 2]: [Concept]
What it means: [Explanation]
How to do it: [Specific action]

[Letter/Step 3]: [Concept]
What it means: [Explanation]
How to do it: [Specific action]

This works because [reason].

👉 [CTA: See it in action]

[Name]
```

### Email 8: Direct Offer (Day 19-21)

**Subject:** "[Name], decision time"

**Template:**
```
Hey [Name],

Over the past [time], I've shared:
- [Key insight 1]
- [Key insight 2]
- [Key insight 3]

Now it's decision time.

You can:

A) Keep doing [what they're doing now]
   Result: [Same outcomes they have]

B) Try [your solution]
   Result: [Transformed outcomes]

Here's exactly what you get:
[Offer breakdown]

👉 [CTA: Get started now]

[Name]

P.S. [Urgency element if genuine]
```

{% elif sequence_type == "reengagement" %}
## Re-engagement Sequence

### Sequence Overview

```
Day 0: Soft check-in
Day 3: Value reminder
Day 7: Incentive (if appropriate)
Day 14: Last chance / list hygiene
```

### Email 1: Check-In (Day 0)

**Subject Lines:**
- "Is everything okay, [Name]?"
- "We miss you"
- "Quick check-in"

**Template:**
```
Hey [Name],

I noticed you haven't [opened emails / logged in / purchased] lately.

Just checking in—is everything okay?

If something's wrong, I'd love to fix it.
Hit reply and let me know.

If you're just busy, no worries.
Here's what you've missed:
- [Recent update 1]
- [Recent update 2]

👉 [CTA: Catch up here]

[Name]
```

### Email 2: Value Reminder (Day 3)

**Subject:** "Remember why you signed up?"

**Template:**
```
Hey [Name],

You joined [Company] because you wanted [original goal].

That goal is still achievable.

Here's the fastest path:
[3 simple steps]

Others who came back saw [specific results].

👉 [CTA: Pick up where you left off]

[Name]
```

### Email 3: Incentive (Day 7)

**Subject:** "[Offer] just for you"

**Template:**
```
Hey [Name],

I want you back.

So here's [offer]:
[Specific incentive details]

Valid until [date].

👉 [CTA: Claim your [offer]]

[Name]
```

### Email 4: Last Chance (Day 14)

**Subject:** "Should I remove you from the list?"

**Template:**
```
Hey [Name],

I haven't heard from you in a while.

I don't want to clutter your inbox
if you're no longer interested.

Click below to stay on the list:
👉 [CTA: Yes, keep me subscribed]

If I don't hear from you by [date],
I'll remove you automatically.

No hard feelings either way.

[Name]

P.S. If you stay, you'll get [what they'll miss].
```

{% elif sequence_type == "onboarding" %}
## Onboarding Sequence

### Sequence Overview

```
Day 0: Welcome + single first step
Day 1: Complete setup
Day 3: First milestone
Day 5: "Aha moment" trigger
Day 7: Best practices
Day 14: Advanced features
Day 21: Success check + upgrade path
```

{% if business_type == "saas" %}
### Email 1: Welcome + First Step (Immediate)

**Subject:** "Start here (2 minutes)"

**Template:**
```
Hey [Name],

Welcome to [Product]! 🎉

You're in. Now let's get you your first win.

Here's the ONE thing to do right now:
[Single, specific first action]

👉 [CTA: Do this now - takes 2 minutes]

That's it. Do that, and you'll be ready
for what comes tomorrow.

[Name]
[Product] Team

P.S. Stuck? Reply to this email—I'm here to help.
```

### Email 2: Complete Setup (Day 1)

**Subject:** "Finish your setup (you're 50% done)"

**Template:**
```
Hey [Name],

Nice work on [first action they took]!

You're halfway through setup.

Remaining steps:
☐ [Setup step 1] (~2 min)
☐ [Setup step 2] (~3 min)
☐ [Setup step 3] (~2 min)

Total: ~7 minutes.

👉 [CTA: Complete setup]

Once you're done, you can [key capability].

[Name]
```

### Email 3: First Milestone (Day 3)

**Subject:** "Your first [milestone]"

**Template:**
```
Hey [Name],

Time for your first [milestone].

People who hit this milestone in week 1
are [X]% more likely to [positive outcome].

Here's how:

Step 1: [Action]
Step 2: [Action]
Step 3: [Action]

👉 [CTA: Achieve your first [milestone]]

Need help? [Support link] or reply here.

[Name]
```

### Email 5: Aha Moment (Day 5-7)

**Subject:** "The moment everything clicks"

**Template:**
```
Hey [Name],

There's a moment with [Product] when it all makes sense.

For most users, it's when they [specific aha action].

You might not have reached it yet—but you're close.

Try this:
[Specific action that triggers aha moment]

When it works, you'll understand why
[number] [audience] rely on [Product].

👉 [CTA: Try it now]

[Name]
```
{% endif %}

{% elif sequence_type == "sales" %}
## Sales Sequence

### Sequence Overview

```
Email 1: Problem recognition + curiosity
Email 2: Agitate + solution preview
Email 3: Full pitch + offer
Email 4: Proof + objection handling
Email 5: Urgency + final push
Email 6: Last call
```

### Email 1: Problem Recognition (Day 0)

**Subject:** "The [problem] nobody talks about"

**Template:**
```
Hey [Name],

Let me ask you something:

How much time do you spend on [frustrating activity]?

For most [audience], it's [shocking amount].

That's [cost in money/time/opportunity].

What if you could [desired outcome] instead?

Tomorrow, I'll show you exactly how.

[Name]
```

### Email 3: Full Pitch (Day 4)

**Subject:** "Introducing [Product/Offer]"

**Template:**
```
Hey [Name],

Two days ago, I mentioned [problem].

Yesterday, I shared [solution concept].

Today: the full picture.

Introducing [Product/Offer]:

What you get:
✓ [Feature 1] → [Benefit]
✓ [Feature 2] → [Benefit]
✓ [Feature 3] → [Benefit]

[Bonus 1]: [Value]
[Bonus 2]: [Value]

Price: [Amount]
Guarantee: [Risk reversal]

👉 [CTA: Get [Product] now]

[Name]

P.S. [Scarcity or bonus deadline if genuine]
```

### Email 5: Urgency (Day 8)

**Subject:** "[Hours/Days] left"

**Template:**
```
Hey [Name],

Quick reminder: [Offer] closes in [time].

After that:
- [What changes - price goes up/bonus disappears]

If you're on the fence:
[Address final objection]

[Testimonial or quick proof point]

👉 [CTA: Don't miss this]

[Name]
```

{% endif %}

---

## Subject Line Formulas

### By Type

| Type | Formula | Example |
|------|---------|---------|
| Curiosity | "The [thing] nobody talks about" | "The metric nobody talks about" |
| Question | "[Name], still [struggling/wanting]?" | "Sarah, still chasing leads?" |
| How-to | "How to [outcome] in [timeframe]" | "How to double conversions in 7 days" |
| Number | "[X] ways to [benefit]" | "5 ways to cut churn" |
| Direct | "Your [thing] is ready" | "Your free template is ready" |
| Story | "The [adjective] way I [outcome]" | "The accidental way I got 10k subscribers" |

### Patterns That Work

```
✓ Short (under 50 chars) for mobile
✓ First name when appropriate
✓ Lowercase can feel personal
✓ Questions drive opens
✓ Numbers grab attention
✓ Avoid spam words: free, urgent, limited time (in subject)
```

---

## Email Copy Patterns

### Opening Hooks

```
Story: "Last week, something weird happened..."
Question: "Quick question for you:"
Bold claim: "Everything you know about [topic] is wrong."
Empathy: "I know what you're going through."
Direct: "Let's skip the small talk."
```

### Transitions

```
"Here's the thing..."
"But wait, there's more to it."
"Here's where it gets interesting:"
"The truth is..."
"What most people miss:"
```

### Closing CTAs

{% if business_type == "saas" %}
```
"Start your free trial"
"See it in action"
"Book a demo"
"Try it free for 14 days"
"Get started in 2 minutes"
```
{% elif business_type == "ecommerce" %}
```
"Shop now"
"Get yours"
"Claim your [discount]"
"Add to cart"
"See the collection"
```
{% elif business_type == "agency" %}
```
"Book a strategy call"
"Get your free audit"
"Let's talk"
"See our work"
"Request a proposal"
```
{% endif %}

---

## HTML Email Structure

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Email Subject Here</title>
</head>
<body style="margin: 0; padding: 0; background-color: #f4f4f4;">

  <!-- Email Container -->
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
    <tr>
      <td align="center" style="padding: 40px 20px;">

        <!-- Content Area -->
        <table role="presentation" width="600" cellpadding="0" cellspacing="0"
               style="background-color: #ffffff; border-radius: 8px;">
          <tr>
            <td style="padding: 40px 40px 20px;">

              <!-- Logo -->
              <img src="logo.png" alt="Company" width="120"
                   style="margin-bottom: 30px;">

              <!-- Main Content -->
              <p style="font-family: -apple-system, BlinkMacSystemFont,
                 'Segoe UI', Roboto, sans-serif; font-size: 16px;
                 line-height: 1.6; color: #333333; margin: 0 0 20px;">
                Hey [Name],
              </p>

              <p style="font-family: -apple-system, BlinkMacSystemFont,
                 'Segoe UI', Roboto, sans-serif; font-size: 16px;
                 line-height: 1.6; color: #333333; margin: 0 0 20px;">
                [Email body content here]
              </p>

              <!-- CTA Button -->
              <table role="presentation" cellpadding="0" cellspacing="0"
                     style="margin: 30px 0;">
                <tr>
                  <td style="background-color: #007bff; border-radius: 6px;">
                    <a href="[CTA_URL]"
                       style="display: inline-block; padding: 14px 28px;
                       font-family: -apple-system, BlinkMacSystemFont,
                       'Segoe UI', Roboto, sans-serif; font-size: 16px;
                       font-weight: 600; color: #ffffff;
                       text-decoration: none;">
                      [CTA Text]
                    </a>
                  </td>
                </tr>
              </table>

              <!-- Signature -->
              <p style="font-family: -apple-system, BlinkMacSystemFont,
                 'Segoe UI', Roboto, sans-serif; font-size: 16px;
                 line-height: 1.6; color: #333333; margin: 20px 0 0;">
                [Name]<br>
                <span style="color: #666666; font-size: 14px;">
                  [Title], [Company]
                </span>
              </p>

            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="padding: 20px 40px; border-top: 1px solid #eeeeee;">
              <p style="font-family: -apple-system, BlinkMacSystemFont,
                 'Segoe UI', Roboto, sans-serif; font-size: 12px;
                 color: #999999; margin: 0; text-align: center;">
                [Company Name] · [Address]<br>
                <a href="[UNSUBSCRIBE_URL]" style="color: #999999;">
                  Unsubscribe
                </a> ·
                <a href="[PREFERENCES_URL]" style="color: #999999;">
                  Email preferences
                </a>
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>

</body>
</html>
```

---

## Deliverability

### Technical Setup

| Record | Purpose | Example |
|--------|---------|---------|
| SPF | Authorize sending servers | `v=spf1 include:_spf.google.com ~all` |
| DKIM | Verify email integrity | Domain key signature |
| DMARC | Policy for failures | `v=DMARC1; p=none; rua=mailto:dmarc@company.com` |

### Best Practices

```
✓ Use a subdomain for marketing (mail.company.com)
✓ Warm up new domains slowly (50/day, increase 50% weekly)
✓ Keep bounce rate under 2%
✓ Maintain unsubscribe rate under 0.5%
✓ Remove unengaged subscribers (no opens in 90 days)
✓ Use double opt-in for quality
✓ Include physical address (CAN-SPAM)
✓ Make unsubscribe easy (one click)
```

---

## Metrics & Benchmarks

| Metric | Good | Great | Action if Low |
|--------|------|-------|---------------|
| Open Rate | 20% | 35%+ | Fix subject lines, sender name |
| Click Rate | 2% | 5%+ | Improve CTA, reduce friction |
| Unsubscribe | <0.5% | <0.2% | Send less, better targeting |
| Bounce | <2% | <0.5% | Clean list, verify emails |
| Reply Rate | 1% | 3%+ | Add questions, personality |

---

## Checklist

### Before Sending

- [ ] Subject line under 50 characters
- [ ] Preview text set (not default)
- [ ] One clear CTA
- [ ] Mobile preview checked
- [ ] Links tested and working
- [ ] Unsubscribe link present
- [ ] Personalization tokens work
- [ ] Send time optimized (Tue-Thu, 10am-2pm)

### Sequence Setup

- [ ] Entry trigger defined
- [ ] Exit conditions set
- [ ] Wait times configured
- [ ] Goals/conversion tracking
- [ ] Branch logic if needed
- [ ] Suppression lists applied

{% if business_type == "saas" %}
### SaaS-Specific

- [ ] Trial expiration reminders
- [ ] Feature adoption emails
- [ ] Usage-based triggers
- [ ] Upgrade prompts based on behavior
{% elif business_type == "ecommerce" %}
### E-commerce-Specific

- [ ] Cart abandonment sequence
- [ ] Browse abandonment
- [ ] Post-purchase thank you
- [ ] Review request timing
- [ ] Replenishment reminders
{% endif %}

---

## Related Skills

- **@include skill:copywriting**: Writing compelling email copy
- **@include skill:popup-cro**: Email capture optimization
- **@include skill:form-cro**: Signup form best practices
