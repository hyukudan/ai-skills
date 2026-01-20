---
name: competitor-alternatives
description: |
  Create competitor comparison and alternative pages. Covers four formats: singular
  alternative, plural alternatives, you vs competitor, and competitor vs competitor.
version: 1.0.0
tags: [seo, competitor, comparison, alternatives, sales-enablement]
category: marketing/seo
scope:
  triggers:
    - alternative page
    - vs page
    - competitor comparison
    - comparison page
---

# Competitor & Alternative Pages

You create comparison pages that rank, provide value, and position your product effectively.

## Principles

**1. Honesty builds trust** — Acknowledge competitor strengths, be accurate about limitations

**2. Depth over surface** — Beyond checklists. Explain why differences matter.

**3. Help them decide** — Be clear about who you're best for AND who competitor is best for

**4. Centralize data** — Single source of truth per competitor, updates propagate everywhere

---

## Page Formats

### Format 1: [Competitor] Alternative (Singular)
**Intent:** User actively looking to switch
**URL:** `/alternatives/[competitor]`
**Keywords:** "[Competitor] alternative", "switch from [Competitor]"

**Structure:**
1. Why people look for alternatives
2. You as the alternative (quick positioning)
3. Detailed comparison
4. Who should switch (and who shouldn't)
5. Migration path
6. Social proof from switchers
7. CTA

### Format 2: [Competitor] Alternatives (Plural)
**Intent:** Research phase, earlier in journey
**URL:** `/alternatives/[competitor]-alternatives`
**Keywords:** "[Competitor] alternatives", "tools like [Competitor]"

**Structure:**
1. Common pain points
2. What to look for in an alternative
3. List of alternatives (you first, but include real options)
4. Comparison table
5. Recommendation by use case
6. CTA

**Important:** Include 4-7 real alternatives. Being helpful builds trust.

### Format 3: You vs [Competitor]
**Intent:** Direct comparison between you and competitor
**URL:** `/vs/[competitor]`
**Keywords:** "[You] vs [Competitor]"

**Structure:**
1. TL;DR (key differences in 2-3 sentences)
2. At-a-glance comparison table
3. Detailed comparison by category
4. Who [You] is best for
5. Who [Competitor] is best for (be honest)
6. Migration support
7. CTA

### Format 4: [Competitor A] vs [Competitor B]
**Intent:** User comparing two competitors (not you)
**URL:** `/compare/[a]-vs-[b]`

**Structure:**
1. Overview of both products
2. Comparison by category
3. Who each is best for
4. The third option (introduce yourself)
5. CTA

---

## Comparison Tables

**Beyond checkmarks:**

| Feature | You | Competitor |
|---------|-----|-----------|
| Feature A | Full support with [detail] | Basic, [limitation] |

**Organize by category:** Core functionality, Collaboration, Integrations, Security, Support

---

## Section Templates

### TL;DR
```
[Competitor] excels at [strength] but struggles with [weakness].
[You] is built for [focus], offering [differentiator].
Choose [Competitor] if [their use case]. Choose [You] if [your use case].
```

### Feature Section
```
## [Feature Category]

**[Competitor]**: [2-3 sentences]
- Strengths: [specific]
- Limitations: [specific]

**[You]**: [2-3 sentences]
- Strengths: [specific]
- Limitations: [specific]

**Bottom line**: Choose [Competitor] if [scenario]. Choose [You] if [scenario].
```

### Migration Section
```
## Switching from [Competitor]

**What transfers:** [data type, how easily]
**What needs reconfiguration:** [thing, effort level]
**Support:** [free import tool, white-glove migration, timeline]
```

---

## Competitor Data File

```yaml
name: Notion
website: notion.so
tagline: "All-in-one workspace"
primary_use_case: "docs + light databases"

pricing_model: per-seat
starter_price: $8/user/month

strengths:
  - Extremely flexible
  - Beautiful interface

weaknesses:
  - Slow with large databases
  - Learning curve

best_for:
  - Documentation-first teams
  - All-in-one workspace seekers
```

---

## SEO

**Keywords by format:**
- Alternative (singular): [Competitor] alternative, switch from [Competitor]
- Alternatives (plural): [Competitor] alternatives, tools like [Competitor]
- You vs Competitor: [You] vs [Competitor]

**Internal linking:** Link between competitor pages, from features to comparisons, hub page to all

---

## Related Skills

- **@include skill:programmatic-seo**: Building competitor pages at scale
- **@include skill:copywriting**: Compelling comparison copy
- **@include skill:schema-markup**: FAQ schema for comparison pages
