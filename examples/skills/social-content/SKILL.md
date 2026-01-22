---
name: social-content
description: |
  Generate social media posts for LinkedIn, Twitter/X, Instagram, and TikTok.
  Provides decision frameworks for post type, hook generation, and tone adaptation.
version: 2.0.0
tags: [social-media, content, linkedin, twitter, instagram, tiktok, marketing]
category: marketing/content
variables:
  platform:
    type: string
    description: Target platform
    enum: [linkedin, twitter, instagram, tiktok]
    default: linkedin
  niche:
    type: string
    description: Content niche
    enum: [tech, saas, marketing, creator, ecommerce, general]
    default: saas
  goal:
    type: string
    description: Primary goal of the post
    enum: [awareness, engagement, conversion, authority]
    default: engagement
scope:
  triggers:
    - LinkedIn post
    - Twitter thread
    - social media
    - social content
    - generate post
---

# Social Content Generation

You generate social posts optimized for platform, audience, and goal.

## Decision Framework

```
GOAL → POST TYPE → STRUCTURE → HOOK → TONE

awareness   → story, hot take      → emotion-first
engagement  → question, poll       → curiosity-first
conversion  → case study, how-to   → value-first
authority   → insight, data        → credibility-first
```

---

## Platform Selection

| Platform | Best When | Avoid When |
|----------|-----------|------------|
| LinkedIn | B2B, thought leadership, hiring | Quick updates, memes |
| Twitter | Tech, real-time, building in public | Long explanations |
| Instagram | Visual products, lifestyle, personal brand | Text-heavy content |
| TikTok | Gen Z/Millennial, entertainment, trends | B2B enterprise |

---

{% if platform == "linkedin" %}
## LinkedIn Generation

### Post Type by Goal

| Goal | Post Type | Why |
|------|-----------|-----|
| awareness | Personal story | Algorithm favors vulnerability |
| engagement | Contrarian take + question | Drives comments |
| conversion | Case study with results | Proof sells |
| authority | Industry insight with data | Establishes expertise |

### Structure Formula

```
[HOOK] ← 125 chars max, must stop scroll
⠀
[PATTERN INTERRUPT] ← whitespace or emoji

[BODY] ← 3-7 short paragraphs, one idea each

[INSIGHT] ← The "aha" moment

[CTA] ← Question or action
```

### Hook Generation by Type

{% if goal == "awareness" %}
**Story Hooks:**
- "I {failed/almost quit/got fired} because of {specific thing}."
- "{Number} {time} ago, I was {relatable struggle}."
- "Nobody talks about the {dark side/real cost} of {topic}."
{% elif goal == "engagement" %}
**Engagement Hooks:**
- "Hot take: {common belief} is {wrong/outdated/overrated}."
- "{Audience}, what's your take on {controversial topic}?"
- "I {did something unexpected}. Here's why:"
{% elif goal == "conversion" %}
**Conversion Hooks:**
- "We went from {bad metric} to {good metric} in {time}."
- "Here's the exact {system/framework/template} that {result}:"
- "{Customer} was {struggling}. Now they're {winning}. Here's how:"
{% elif goal == "authority" %}
**Authority Hooks:**
- "I {analyzed/reviewed/studied} {number} {things}. Here's what I found:"
- "After {years/projects/clients}, here's what actually matters:"
- "The {industry} is changing. Here's what {audience} need to know:"
{% endif %}

### Tone by Niche

{% if niche == "tech" or niche == "saas" %}
- Direct, no fluff
- Data when possible
- Building in public resonates
- Avoid: corporate speak, buzzwords
{% elif niche == "marketing" %}
- Bold claims with proof
- Frameworks and acronyms work
- Contrarian takes perform well
- Avoid: vague "value" statements
{% elif niche == "creator" %}
- Personal, vulnerable
- Behind-the-scenes
- Numbers and milestones
- Avoid: preaching, lecturing
{% elif niche == "ecommerce" %}
- Customer stories
- Before/after transformations
- Social proof heavy
- Avoid: hard selling
{% else %}
- Adapt to audience expectations
- Test different tones
- Lead with value
{% endif %}

### Constraints

- 1,200-1,500 chars optimal
- No links in body (comment instead)
- First 125 chars = everything
- 3+ line breaks for readability

{% elif platform == "twitter" %}
## Twitter Generation

### Post Type by Goal

| Goal | Format | Why |
|------|--------|-----|
| awareness | Single tweet story | Shareability |
| engagement | Thread with question | Replies boost reach |
| conversion | Thread with CTA | Value → ask |
| authority | Data thread | Screenshots get saved |

### Single Tweet Formula

```
[HOOK - bold claim or question]

[SUPPORT - 2-3 bullet points or one-liner]

[KICKER - unexpected twist or CTA]
```

### Thread Formula

```
Tweet 1: Hook + "Thread 🧵"
         Must work standalone

Tweet 2-7: One point per tweet
           Action → Result format

Tweet 8: Summary + CTA
         "If this helped: RT #1, Follow"
```

### Hook Generation

{% if goal == "awareness" %}
- "I {achieved thing} by doing the opposite of {common advice}."
- "Everyone's talking about {X}. Nobody's talking about {Y}."
{% elif goal == "engagement" %}
- "Unpopular opinion: {contrarian take}"
- "{Audience}, which do you prefer: {A} or {B}?"
{% elif goal == "conversion" %}
- "Here's the exact {thing} I use to {result}:"
- "Stop {common mistake}. Do this instead:"
{% elif goal == "authority" %}
- "I've {done impressive thing}. Here's what I learned:"
- "{Number} lessons from {experience}:"
{% endif %}

### Constraints

- <280 chars for single tweets
- Threads: 5-12 tweets optimal
- Under 100 chars = more engagement
- Quote tweet > plain retweet

{% elif platform == "instagram" %}
## Instagram Generation

### Post Type by Goal

| Goal | Format | Why |
|------|--------|-----|
| awareness | Reel | 2x reach of static |
| engagement | Carousel with question | Swipes + comments |
| conversion | Carousel tutorial | Saves = algorithm boost |
| authority | Behind-the-scenes Reel | Authenticity wins |

### Carousel Structure

```
Slide 1: Hook (large text, eye-catching)
         "X things that {outcome}"

Slides 2-8: One point per slide
            Headline + 2-3 lines

Slide 9: Summary
Slide 10: CTA + "Save for later"
```

### Reel Structure

```
0-3s:   Hook (text + voice)
3-15s:  Setup (why this matters)
15-45s: Content (3-5 points, quick cuts)
45-60s: CTA (follow, comment, save)
```

### Caption Formula

```
[Hook - first line is preview]

[Value - short paragraphs]

[CTA - question or action]

.
.
.

#hashtag1 #hashtag2 (5-10 relevant)
```

### Constraints

- Reels: 30-90 seconds
- Carousels: 5-10 slides
- Hashtags: 5-10 mid-size (10K-500K posts)
- Post to Stories to boost reach

{% elif platform == "tiktok" %}
## TikTok Generation

### Post Type by Goal

| Goal | Format | Why |
|------|--------|-----|
| awareness | Trend participation | Algorithm push |
| engagement | Stitch/Duet | Borrowed audience |
| conversion | Tutorial with results | Saves drive reach |
| authority | Story time | Watch time = reach |

### Video Structure

```
0-2s:   Hook (must stop scroll)
        Text on screen + voice

2-10s:  Setup (quick context)

10-25s: Content (pattern interrupts every 3-5s)

25-30s: CTA or loop setup
```

### Hook Templates

```
"Wait, you're still {common thing}?"
"POV: You just {achieved something}"
"The {thing} they don't want you to know"
"I was today years old when I learned..."
"{Number} {time} ago, I {did thing}. Here's what happened:"
```

### Constraints

- First 1-3 seconds = everything
- 30-60 seconds optimal
- Trending sounds boost reach
- Native/unpolished > produced
- Post 1-4x daily for growth

{% endif %}

---

## Hook Quality Check

A good hook has 2+ of these:

| Element | Example |
|---------|---------|
| **Curiosity gap** | "Here's what nobody tells you about..." |
| **Specific number** | "I made $47,000 from one tweet" |
| **Contrarian angle** | "Stop following this advice" |
| **Personal stake** | "I almost quit my job because..." |
| **Time element** | "In 30 days, I..." |

**Red flags:**
- Generic ("Here are some tips...")
- No stakes ("I want to share...")
- Too long (>2 lines)
- Clickbait without payoff

---

## Content Pillar Mix

| Pillar | % | Purpose |
|--------|---|---------|
| Educational | 30% | Teach something useful |
| Personal | 25% | Build connection |
| Industry | 25% | Show expertise |
| Behind-scenes | 15% | Authenticity |
| Promotional | 5% | Convert (earn the ask) |

---

## When NOT to Post

- **Don't:** Post about tragedy for engagement
- **Don't:** Jump on trends that don't fit your brand
- **Don't:** Cross-post identical content across platforms
- **Don't:** Post promotional content >10% of the time
- **Don't:** Engage with negativity publicly

---

## Quality Evaluation

Before posting, score 1-5:

| Criteria | Question |
|----------|----------|
| Hook | Would I stop scrolling? |
| Value | Does this teach, inspire, or entertain? |
| Clarity | Can someone skim and get it? |
| CTA | Is the next step obvious? |
| Platform fit | Does format match platform? |

**Post if:** Average ≥4

---

## Related Skills

- **@include skill:copywriting**: Long-form that feeds social
- **@include skill:launch-strategy**: Coordinating social with launches
