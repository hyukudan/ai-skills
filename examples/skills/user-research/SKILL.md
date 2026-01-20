---
name: user-research
description: |
  User research methods and best practices. Covers interviews, surveys,
  usability testing, personas, journey mapping, and synthesizing insights
  into actionable product decisions.
version: 1.0.0
tags: [user-research, ux, interviews, usability, personas]
category: product/research
trigger_phrases:
  - "user research"
  - "user interview"
  - "usability test"
  - "persona"
  - "journey map"
  - "user feedback"
  - "customer discovery"
variables:
  phase:
    type: string
    description: Product phase
    enum: [discovery, validation, optimization]
    default: discovery
---

# User Research Guide

## Core Philosophy

**Research is about learning, not validating.** Seek to understand user needs and behaviors, not confirm your assumptions.

> "Fall in love with the problem, not the solution."

---

## Research Methods Overview

| Method | Best For | Time | Sample Size |
|--------|----------|------|-------------|
| **User Interviews** | Deep understanding, discovery | 45-60 min | 5-8 users |
| **Usability Testing** | Evaluating designs | 30-60 min | 5 users |
| **Surveys** | Quantifying behaviors | 5-10 min | 100+ users |
| **Diary Studies** | Long-term behaviors | 1-4 weeks | 10-15 users |
| **Card Sorting** | Information architecture | 20-30 min | 15-30 users |
| **A/B Testing** | Comparing solutions | Varies | 1000+ users |

---

## 1. User Interviews

### Interview Structure

```
1. INTRODUCTION (5 min)
   - Thank them, explain purpose
   - Get consent for recording
   - "There are no wrong answers"

2. WARM-UP (5 min)
   - Background questions
   - Build rapport

3. MAIN QUESTIONS (30-40 min)
   - Core research questions
   - Follow-up probes

4. WRAP-UP (5 min)
   - "Anything else?"
   - Thank them, explain next steps
```

### Interview Best Practices

**DO:**
- Ask open-ended questions ("Tell me about...")
- Ask about past behavior, not future intentions
- Follow up with "Why?" and "How?"
- Let silences happen (people will fill them)
- Take notes on emotions, not just words

**DON'T:**
- Ask leading questions ("Don't you think...")
- Ask hypothetical questions ("Would you use...")
- Interrupt or finish their sentences
- Show your prototype too early
- Try to sell or explain your solution

### Sample Interview Questions

{% if phase == "discovery" %}
**Discovery Phase:**
```
CONTEXT
- "Walk me through a typical day when you [do task]."
- "Tell me about the last time you [experienced problem]."
- "How do you currently handle [situation]?"

PROBLEMS
- "What's the hardest part about [task]?"
- "What frustrates you most about [current solution]?"
- "If you had a magic wand, what would you change?"

MOTIVATION
- "Why is solving this important to you?"
- "What would success look like?"
- "What happens if you don't solve this?"
```
{% endif %}

{% if phase == "validation" %}
**Validation Phase:**
```
SOLUTION FIT
- "How does this compare to what you currently use?"
- "What would make this not work for you?"
- "What's missing that you'd need?"

ADOPTION
- "What would need to be true for you to switch?"
- "Who else would need to be involved in this decision?"
- "What concerns would your [boss/team] have?"

VALUE
- "What would you pay for this?"
- "How much time would this save you?"
- "What would you give up to have this?"
```
{% endif %}

---

## 2. Usability Testing

### Test Plan Template

```markdown
## Usability Test Plan

**Objective:** Evaluate [feature] for [goal]

**Research Questions:**
1. Can users complete [task] without assistance?
2. Where do users get confused?
3. What do users expect vs. what happens?

**Participants:**
- Number: 5
- Criteria: [user characteristics]
- Recruitment: [method]

**Tasks:**
1. [Specific task with success criteria]
2. [Another task]
3. [Another task]

**Metrics:**
- Task completion rate
- Time on task
- Errors/confusion points
- Satisfaction rating (1-5)
```

### Running the Test

```
MODERATOR SCRIPT

"Thanks for helping us today. I'm going to ask you to complete
some tasks using [product]. I want to emphasize:

- We're testing the product, not you
- There are no wrong answers
- Please think out loud - tell me what you're looking at,
  what you're thinking, what you expect to happen
- I may not answer questions during the tasks because I want
  to see how the product works without help
- If you get stuck, that's valuable information for us

Do you have any questions before we start?"

DURING THE TEST
- "What are you thinking right now?"
- "What do you expect to happen?"
- "Is that what you expected?"
- "What would you do next?"

AFTER EACH TASK
- "On a scale of 1-5, how easy was that?"
- "What was confusing about that?"
```

### Analysis Framework

| Issue | Severity | Frequency | Recommendation |
|-------|----------|-----------|----------------|
| Users can't find X | High | 4/5 | Move to main nav |
| Confused by label | Medium | 3/5 | Rename to "..." |
| Slow loading | Low | 2/5 | Add loading state |

**Severity Ratings:**
- **Critical:** Prevents task completion
- **High:** Causes significant delay/frustration
- **Medium:** Noticeable but workaround exists
- **Low:** Minor annoyance

---

## 3. Surveys

### Survey Design Principles

```markdown
## Good Survey Questions

LENGTH
- Keep under 5 minutes (10-15 questions max)
- Put important questions first
- Use progress indicator

QUESTION TYPES
- Single choice: When options are mutually exclusive
- Multiple choice: When multiple options can apply
- Likert scale: For measuring attitudes (5 or 7 point)
- Open-ended: Use sparingly, at the end

WORDING
- One concept per question
- Avoid jargon and acronyms
- Include "Not applicable" option
- Randomize answer order when appropriate
```

### Sample Survey Structure

```
1. SCREENING (if needed)
   "Do you use [product category]?" Yes/No

2. BEHAVIOR
   "How often do you [action]?"
   - Daily
   - Weekly
   - Monthly
   - Rarely
   - Never

3. SATISFACTION
   "How satisfied are you with [aspect]?"
   1 - Very dissatisfied
   2 - Dissatisfied
   3 - Neutral
   4 - Satisfied
   5 - Very satisfied

4. IMPORTANCE
   "How important is [feature] to you?"
   1 - Not at all important
   5 - Extremely important

5. NPS
   "How likely are you to recommend [product]?"
   0-10 scale

6. OPEN-ENDED
   "What one thing would you improve?"
   [Text field]

7. DEMOGRAPHICS
   (Only if relevant to analysis)
```

---

## 4. Personas

### Persona Template

```markdown
# [Persona Name]
## [One-line description]

**Demographics:**
- Role: [Job title or life stage]
- Industry: [If B2B]
- Technical proficiency: [Low/Medium/High]

**Goals:**
- Primary: [Main goal related to your product]
- Secondary: [Supporting goals]

**Frustrations:**
- [Current pain point 1]
- [Current pain point 2]
- [Current pain point 3]

**Behaviors:**
- [How they currently solve the problem]
- [Tools they use]
- [Decision-making process]

**Quote:**
"[Representative quote from research]"

**Scenario:**
[Brief story of them using your product]
```

### Persona Do's and Don'ts

**DO:**
- Base on real research data
- Focus on behaviors and goals
- Include quotes from actual users
- Update as you learn more

**DON'T:**
- Make up demographics
- Include irrelevant details (hobbies, pets)
- Create too many personas (2-4 is ideal)
- Treat as static documents

---

## 5. Journey Mapping

### Journey Map Structure

```
STAGES: Awareness → Consideration → Purchase → Onboarding → Usage → Advocacy

FOR EACH STAGE:
┌─────────────────────────────────────────────────────────┐
│ STAGE: [Name]                                          │
├─────────────────────────────────────────────────────────┤
│ Actions: What the user does                            │
│ Touchpoints: Where they interact with us               │
│ Thoughts: What they're thinking                        │
│ Emotions: How they feel (use emoji scale)              │
│ Pain Points: Frustrations and obstacles                │
│ Opportunities: How we can improve                      │
└─────────────────────────────────────────────────────────┘
```

### Sample Journey Map

```
┌────────────────┬────────────────┬────────────────┐
│   AWARENESS    │  CONSIDERATION │    SIGNUP      │
├────────────────┼────────────────┼────────────────┤
│ Actions:       │ Actions:       │ Actions:       │
│ - Hears about  │ - Visits site  │ - Creates acct │
│   from friend  │ - Reads docs   │ - Enters info  │
│                │ - Compares     │                │
├────────────────┼────────────────┼────────────────┤
│ Thinking:      │ Thinking:      │ Thinking:      │
│ "Is this for   │ "How does it   │ "Why do they   │
│  me?"          │  compare to X?"│  need this?"   │
├────────────────┼────────────────┼────────────────┤
│ Emotion: 😐    │ Emotion: 🤔    │ Emotion: 😤    │
├────────────────┼────────────────┼────────────────┤
│ Pain Points:   │ Pain Points:   │ Pain Points:   │
│ - Unclear what │ - Pricing not  │ - Too many     │
│   it does      │   obvious      │   form fields  │
├────────────────┼────────────────┼────────────────┤
│ Opportunities: │ Opportunities: │ Opportunities: │
│ - Clearer      │ - Add pricing  │ - Social login │
│   messaging    │   page         │ - Fewer fields │
└────────────────┴────────────────┴────────────────┘
```

---

## 6. Synthesizing Research

### Affinity Mapping Process

```
1. GATHER
   - Print/write each observation on sticky note
   - One insight per note
   - Include quotes and observations

2. CLUSTER
   - Group similar notes together
   - Don't overthink - go with gut
   - Allow "outliers" group

3. LABEL
   - Name each cluster
   - Use participant language when possible

4. PRIORITIZE
   - Which themes appear most often?
   - Which have highest impact?

5. INSIGHTS
   - "We observed [behavior]"
   - "We believe this is because [hypothesis]"
   - "This means we should [implication]"
```

### Research Report Template

```markdown
# Research Findings: [Study Name]

## Executive Summary
[3-4 sentence overview of key findings]

## Research Questions
1. [Question 1]
2. [Question 2]

## Methodology
- **Method:** [Interviews/Surveys/etc.]
- **Participants:** [Number and criteria]
- **Duration:** [Dates]

## Key Findings

### Finding 1: [Title]
**Observation:** [What we saw/heard]
**Evidence:** [Quotes, data]
**Implication:** [What this means for the product]

### Finding 2: [Title]
[Same structure]

## Recommendations
1. [Prioritized recommendation]
2. [Another recommendation]

## Next Steps
- [Planned follow-up research]
- [Teams to share with]
```

---

## Quick Reference

### Research Planning Checklist

- [ ] Define research questions
- [ ] Choose appropriate method
- [ ] Create screener/recruit participants
- [ ] Prepare discussion guide/test plan
- [ ] Set up recording/note-taking
- [ ] Conduct sessions
- [ ] Synthesize findings
- [ ] Share with stakeholders

### Sample Size Guidelines

| Method | Minimum | Ideal | Notes |
|--------|---------|-------|-------|
| Interviews | 5 | 8-12 | Until saturation |
| Usability | 5 | 5-8 | 5 finds 85% of issues |
| Surveys | 100 | 300+ | For statistical significance |
| Card Sorts | 15 | 30 | For clear patterns |

---

## Related Skills

- `product-metrics` - Quantitative analysis
- `ux-writing` - Communication design
- `feature-prioritization` - Using research in decisions
