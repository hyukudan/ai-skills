---
name: ab-test-setup
description: |
  Design and run A/B tests that produce valid, actionable results. Covers
  hypothesis design, sample size, metrics selection, and analysis.
version: 1.0.0
tags: [ab-test, experimentation, split-test, cro, optimization]
category: marketing/analytics
scope:
  triggers:
    - A/B test
    - split test
    - experiment
    - test this change
    - multivariate test
    - hypothesis
---

# A/B Testing

You help design experiments that produce statistically valid, actionable results.

## Core Principles

1. **Start with a hypothesis** - Not "let's see what happens"
2. **Test one thing** - Single variable per test
3. **Statistical rigor** - Pre-determine sample size, don't peek
4. **Measure what matters** - Primary metric tied to business value

---

## Hypothesis Framework

```
Because [observation/data],
we believe [change]
will cause [expected outcome]
for [audience].
We'll measure [metric].
```

**Example:**
"Because heatmaps show users miss the CTA, we believe making it larger and higher-contrast will increase clicks by 15%+ for new visitors. We'll measure CTA click-through rate."

---

## Sample Size

| Baseline Rate | 10% Lift | 20% Lift |
|---------------|----------|----------|
| 1% | 150k/variant | 39k/variant |
| 3% | 47k/variant | 12k/variant |
| 5% | 27k/variant | 7k/variant |
| 10% | 12k/variant | 3k/variant |

**Calculator:** evanmiller.org/ab-testing/sample-size.html

**Duration:** Minimum 1-2 business cycles (usually 1-2 weeks)

---

## Metrics Selection

**Primary:** Single metric that matters most, directly tied to hypothesis

**Secondary:** Support interpretation, explain why/how

**Guardrails:** Things that shouldn't get worse (revenue, retention)

**Example - CTA test:**
- Primary: CTA click-through rate
- Secondary: Time to click, scroll depth
- Guardrail: Downstream conversion

---

## Test Types

**A/B:** Two versions, single change (most common)

**A/B/n:** Multiple variants (needs more traffic)

**Multivariate:** Multiple changes in combinations (needs much more traffic)

---

## Running the Test

### Do:
- Monitor for technical issues
- Check segment quality
- Document external factors

### Don't:
- Peek and stop early
- Change variants mid-test
- End early because you "know"

**The peeking problem:** Looking at results before sample size and stopping at significance leads to false positives.

---

## Analyzing Results

1. Did you reach sample size?
2. Is it statistically significant? (p < 0.05)
3. Is the effect size meaningful?
4. Are secondary metrics consistent?
5. Any guardrail concerns?
6. Segment differences?

| Result | Action |
|--------|--------|
| Significant winner | Implement |
| Significant loser | Keep control, learn why |
| No difference | Need more traffic or bolder test |

---

## Documentation

```
Test: [Name]
Dates: [Start] - [End]

Hypothesis: [Full statement]

Variants:
- Control: [Description]
- Variant: [Description + changes]

Results:
- Sample: [achieved vs target]
- Primary: [control] vs [variant] ([% change], [confidence])

Decision: [Winner/Loser/Inconclusive]
Learnings: [What we learned]
```

---

## Common Mistakes

**Design:** Testing too small a change, testing too many things, no hypothesis

**Execution:** Stopping early, changing mid-test, not checking implementation

**Analysis:** Ignoring confidence intervals, cherry-picking segments

---

## Related Skills

- **@include skill:page-cro**: Generate test ideas
- **@include skill:analytics-tracking**: Set up test measurement
- **@include skill:copywriting**: Create variant copy
