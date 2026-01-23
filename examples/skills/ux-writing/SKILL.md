---
name: ux-writing
description: |
  UX writing patterns for clear, helpful interface copy. Covers microcopy,
  error messages, empty states, onboarding, CTAs, and voice/tone guidelines
  for user-centered communication.
license: MIT
allowed-tools: Read WebFetch WebSearch
version: 1.0.0
tags: [ux-writing, microcopy, content-design, copywriting, user-experience]
category: product/ux
trigger_phrases:
  - "UX writing"
  - "microcopy"
  - "error message"
  - "empty state"
  - "button text"
  - "onboarding copy"
  - "interface copy"
variables:
  tone:
    type: string
    description: Brand tone
    enum: [professional, friendly, playful]
    default: friendly
---

# UX Writing Guide

## Core Philosophy

**Words are interface.** Every word in your product is a design decision that affects user experience.

> "The best UX writing is invisible - users accomplish their goal without noticing the words that helped them."

---

## UX Writing Principles

### The 4 Cs

```
CLEAR
- Use simple, familiar words
- One idea per sentence
- Avoid jargon

CONCISE
- Cut unnecessary words
- Front-load important info
- Respect user's time

CONSISTENT
- Same terms for same things
- Predictable patterns
- Unified voice

CONVERSATIONAL
- Write like you talk
- Use "you" and "we"
- Be human, not robotic
```

---

## 1. Buttons and CTAs

### Button Copy Guidelines

```
USE VERBS
✗ "Submission"
✓ "Submit"

BE SPECIFIC
✗ "Click here"
✓ "Download report"

SHOW VALUE
✗ "Next"
✓ "See pricing"

MATCH USER INTENT
✗ "Submit" (for newsletter)
✓ "Subscribe"
```

### Button Patterns

| Context | Weak | Strong |
|---------|------|--------|
| Sign up | Submit | Create account |
| Purchase | Buy | Add to cart |
| Newsletter | Submit | Get updates |
| Download | Click here | Download PDF |
| Save | OK | Save changes |
| Delete | Yes | Delete project |

### Primary vs Secondary Actions

```
DESTRUCTIVE ACTION
┌─────────────────────────────────────────────┐
│  Delete this project?                       │
│                                             │
│  This will permanently remove all files.    │
│                                             │
│        [Cancel]  [Delete project]           │
│         ghost      danger/red               │
└─────────────────────────────────────────────┘

CONFIRMATION
┌─────────────────────────────────────────────┐
│  Save changes before leaving?               │
│                                             │
│  [Don't save]  [Cancel]  [Save]             │
│    tertiary     ghost    primary            │
└─────────────────────────────────────────────┘
```

---

## 2. Error Messages

### Error Message Formula

```
WHAT happened + WHY it happened + HOW to fix it

BAD:
"Error 404"
"Invalid input"
"Something went wrong"

GOOD:
"We couldn't find that page. It may have been moved or deleted.
Try searching or go back to the homepage."

"That email address isn't valid. Please check for typos."

"We couldn't save your changes. Check your internet connection
and try again."
```

### Error Message Patterns

{% if tone == "professional" %}
**Professional Tone:**
```
FORM VALIDATION
"Please enter a valid email address."
"Password must be at least 8 characters."
"This field is required."

SYSTEM ERRORS
"Unable to complete your request. Please try again."
"Your session has expired. Please sign in again."
"This service is temporarily unavailable."
```
{% endif %}

{% if tone == "friendly" %}
**Friendly Tone:**
```
FORM VALIDATION
"That email doesn't look quite right. Mind checking it?"
"Your password needs at least 8 characters to be secure."
"We need this info to continue."

SYSTEM ERRORS
"Something went wrong on our end. Give it another try?"
"You've been signed out. Sign back in to pick up where you left off."
"We're doing some maintenance. Back in a few minutes!"
```
{% endif %}

{% if tone == "playful" %}
**Playful Tone:**
```
FORM VALIDATION
"Hmm, that email looks a bit off. Double-check?"
"8+ characters, please! Your password needs to hit the gym."
"This one's important - we can't move on without it."

SYSTEM ERRORS
"Oops! Something broke. Our team is on it."
"Looks like you got logged out. Welcome back!"
"We're sprucing things up. Check back shortly!"
```
{% endif %}

### Error Message Don'ts

```
DON'T BLAME THE USER
✗ "You entered an invalid password"
✓ "That password doesn't match our records"

DON'T USE TECHNICAL JARGON
✗ "Error 500: Internal server exception"
✓ "Something went wrong. Please try again."

DON'T BE VAGUE
✗ "Invalid input"
✓ "Enter a number between 1 and 100"

DON'T USE ALL CAPS
✗ "ERROR! PAYMENT FAILED!"
✓ "Payment unsuccessful"
```

---

## 3. Empty States

### Empty State Formula

```
ACKNOWLEDGE the empty state
+ EXPLAIN why it's empty
+ GUIDE toward action

STRUCTURE:
┌─────────────────────────────────────────────┐
│           [Illustration/Icon]               │
│                                             │
│           Primary message                   │
│         Secondary explanation               │
│                                             │
│           [Call to action]                  │
└─────────────────────────────────────────────┘
```

### Empty State Examples

```
NEW USER / FIRST USE
┌─────────────────────────────────────────────┐
│              📝                              │
│                                             │
│        No projects yet                      │
│   Create your first project to get started │
│                                             │
│        [Create project]                     │
└─────────────────────────────────────────────┘

SEARCH WITH NO RESULTS
┌─────────────────────────────────────────────┐
│              🔍                              │
│                                             │
│   No results for "xyz"                      │
│   Try different keywords or check spelling │
│                                             │
│        [Clear search]                       │
└─────────────────────────────────────────────┘

FILTERED TO EMPTY
┌─────────────────────────────────────────────┐
│              📋                              │
│                                             │
│    No completed tasks                       │
│    Tasks will appear here once finished    │
│                                             │
│        [View all tasks]                     │
└─────────────────────────────────────────────┘

SUCCESS EMPTY
┌─────────────────────────────────────────────┐
│              ✓                              │
│                                             │
│        All caught up!                       │
│    No new notifications right now          │
│                                             │
└─────────────────────────────────────────────┘
```

---

## 4. Onboarding Copy

### Welcome Messages

```
FIRST-TIME USER
"Welcome to [Product]! Let's get you set up."
"You're in! Here's a quick tour to get started."
"Hey there! Ready to [achieve goal]?"

RETURNING USER
"Welcome back, [Name]!"
"Good to see you again."
"Pick up where you left off."
```

### Onboarding Flow Copy

```
STEP INDICATORS
"Step 1 of 3: Create your profile"
"Almost there! One more step."
"Last step: Invite your team"

PROGRESS ENCOURAGEMENT
"Great start! Let's keep going."
"You're halfway there!"
"One more thing and you're all set."

SKIP OPTIONS
"Skip for now" (not "Skip")
"I'll do this later"
"Remind me tomorrow"
```

### Tooltip/Coach Mark Copy

```
STRUCTURE:
[Feature name] (optional)
What it does + Why it's useful

EXAMPLES:
"Quick actions
Access your most-used tools with one click."

"Drag to reorder
Move items by dragging them to a new position."

"@mention teammates
Type @ to notify someone about this item."
```

---

## 5. Forms and Labels

### Form Labels

```
LABELS
- Clear and concise
- Sentence case (not Title Case)
- No colons at end

✓ "Email address"
✓ "Full name"
✓ "Phone number (optional)"

✗ "Email:"
✗ "Enter Your Email Address"
✗ "E-mail"
```

### Placeholder Text

```
USE FOR:
- Examples of valid input
- Format hints

"jane@example.com"
"(555) 123-4567"
"MM/DD/YYYY"

DON'T USE FOR:
- Labels (disappears on input)
- Instructions
- Required field indicators
```

### Helper Text

```
WHEN TO USE:
- Format requirements
- Additional context
- Recommendations

EXAMPLES:
"Use 8+ characters with a mix of letters and numbers."
"We'll only use this for account recovery."
"This will be visible on your public profile."
```

### Validation Messages

```
INLINE VALIDATION (shown immediately)
✓ "Looks good!"
✗ "Must be at least 8 characters"

REAL-TIME FEEDBACK
Password strength: Weak → Fair → Strong

FIELD-SPECIFIC ERRORS
"Enter a valid email (e.g., name@example.com)"
"Choose a username with only letters and numbers"
```

---

## 6. Notifications and Alerts

### Notification Types

```
SUCCESS
"Changes saved"
"Email sent to [address]"
"[Item] added to cart"

WARNING
"Your trial ends in 3 days"
"Low storage - 90% used"
"Session expires in 5 minutes"

ERROR
"Couldn't save changes. Please try again."
"Payment failed - update payment method"

INFO
"New feature: Try dark mode"
"Scheduled maintenance tonight 2-4am"
```

### Notification Patterns

```
TOAST (temporary, auto-dismiss)
- Confirmations: "Saved"
- Quick status: "Copied to clipboard"

BANNER (persistent until dismissed)
- Warnings: "Your account is past due"
- Announcements: "We've updated our terms"

MODAL (requires action)
- Destructive confirmations
- Important decisions
```

---

## 7. Voice and Tone

### Voice (Consistent)

```
Our product voice is:
- Helpful, not pushy
- Confident, not arrogant
- Professional, not stuffy
- Friendly, not silly
```

### Tone (Varies by Context)

```
CONTEXT → TONE ADJUSTMENT

Success → Celebratory, warm
"You did it! Your account is ready."

Error → Empathetic, helpful
"That didn't work. Here's what to try..."

Warning → Clear, urgent but calm
"Your subscription ends tomorrow."

Onboarding → Encouraging, patient
"Great start! Just a few more steps."

Upgrade → Helpful, not salesy
"Need more storage? See your options."
```

### Word Choice Guidelines

| Instead of | Use |
|------------|-----|
| Click | Select, Choose |
| Abort | Cancel |
| Invalid | Incorrect, Not valid |
| Terminate | End, Close |
| Execute | Run, Start |
| Utilize | Use |
| Functionality | Feature |
| Oops! | (context-dependent) |

---

## Quick Reference

### UX Writing Checklist

- [ ] Is it clear what action to take?
- [ ] Can it be shorter without losing meaning?
- [ ] Is it consistent with similar patterns?
- [ ] Does the tone match the context?
- [ ] Is it specific enough to be actionable?
- [ ] Does it avoid blame and jargon?

### Content Audit Questions

For each piece of copy, ask:
1. What does the user need to know?
2. What do we want them to do?
3. What are they feeling right now?
4. What's the simplest way to say this?

---

## Related Skills

- `user-research` - Understanding users
- `product-metrics` - Measuring copy effectiveness
- `accessibility` - Inclusive writing
