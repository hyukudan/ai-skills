---
name: seo-audit
description: |
  Audit websites for SEO issues. Covers crawlability, indexation, technical SEO,
  on-page optimization, Core Web Vitals, and content quality with prioritized fixes.
version: 1.0.0
tags: [seo, audit, technical-seo, on-page, organic-search]
category: marketing/seo
scope:
  triggers:
    - SEO audit
    - technical SEO
    - why am I not ranking
    - SEO issues
    - on-page SEO
---

# SEO Audit

You identify SEO issues and provide prioritized recommendations.

## Audit Priority Order

1. **Crawlability & Indexation** — Can Google find and index it?
2. **Technical Foundations** — Is the site fast and functional?
3. **On-Page Optimization** — Is content optimized?
4. **Content Quality** — Does it deserve to rank?
5. **Authority & Links** — Does it have credibility?

---

## Technical SEO

### Crawlability

**Robots.txt:** No unintentional blocks, sitemap referenced

**XML Sitemap:** Exists, submitted to Search Console, canonical URLs only, updated regularly

**Architecture:** Important pages within 3 clicks, logical hierarchy, no orphan pages

### Indexation

**Check:** `site:domain.com`, Search Console coverage

**Issues:** Noindex on important pages, wrong canonicals, redirect chains, soft 404s, duplicates

**Canonicalization:** All pages have canonical, self-referencing on unique pages, HTTP→HTTPS, www consistency

### Core Web Vitals

- **LCP** (Largest Contentful Paint): < 2.5s
- **INP** (Interaction to Next Paint): < 200ms
- **CLS** (Cumulative Layout Shift): < 0.1

**Speed factors:** Server response, image optimization, JS execution, CSS delivery, caching, CDN

### Mobile

- Responsive design (not m. subdomain)
- Tap targets 44px+
- Viewport configured
- Same content as desktop

### Security

- HTTPS everywhere
- Valid SSL
- No mixed content
- HTTP → HTTPS redirects

---

## On-Page SEO

### Title Tags

- Unique per page
- Primary keyword near beginning
- 50-60 characters
- Compelling, click-worthy

**Issues:** Duplicates, too long/short, keyword stuffing, missing

### Meta Descriptions

- Unique per page
- 150-160 characters
- Includes keyword
- Clear value proposition

### Headings

- One H1 per page with keyword
- Logical hierarchy (H1 → H2 → H3)
- Describes content, not just styling

### Content

- Keyword in first 100 words
- Related keywords naturally used
- Sufficient depth for topic
- Answers search intent
- Better than competitors

### Images

- Descriptive filenames
- Alt text on all images
- Compressed, modern formats (WebP)
- Lazy loading, responsive

### Internal Links

- Important pages well-linked
- Descriptive anchor text
- No broken links
- No orphan pages

---

## Content Quality (E-E-A-T)

**Experience:** First-hand, original insights, real examples

**Expertise:** Author credentials, accurate information, properly sourced

**Authoritativeness:** Recognized in space, cited by others

**Trustworthiness:** Accurate, transparent, contact info, privacy policy, HTTPS

---

## Common Issues by Site Type

**SaaS:** Product pages lack depth, blog not integrated, missing comparison pages

**E-commerce:** Thin category pages, duplicate descriptions, missing product schema

**Content/Blog:** Outdated content, keyword cannibalization, poor internal linking

**Local:** Inconsistent NAP, missing local schema, no Google Business optimization

---

## Report Format

**Executive Summary:**
- Overall health
- Top 3-5 priority issues
- Quick wins

**For each issue:**
- Issue + Evidence
- Impact (High/Medium/Low)
- Fix + Priority

**Action Plan:**
1. Critical (blocking indexation)
2. High-impact improvements
3. Quick wins
4. Long-term recommendations

---

## Tools

**Free:** Google Search Console, PageSpeed Insights, Rich Results Test, Mobile-Friendly Test

**Paid:** Screaming Frog, Ahrefs/Semrush, Sitebulb

---

## Related Skills

- **@include skill:programmatic-seo**: Building SEO pages at scale
- **@include skill:schema-markup**: Implementing structured data
- **@include skill:page-cro**: Converting traffic, not just ranking
