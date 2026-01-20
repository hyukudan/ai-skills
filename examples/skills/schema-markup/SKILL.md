---
name: schema-markup
description: |
  Implement schema.org structured data for rich search results. Covers Organization,
  Article, Product, FAQ, HowTo, BreadcrumbList, LocalBusiness with JSON-LD examples.
version: 1.0.0
tags: [seo, schema, structured-data, json-ld, rich-snippets]
category: marketing/seo
scope:
  triggers:
    - schema markup
    - structured data
    - JSON-LD
    - rich snippets
    - FAQ schema
    - product schema
---

# Schema Markup

You implement structured data that enables rich search results.

## Principles

1. **Accuracy first** — Schema must match page content exactly
2. **Use JSON-LD** — Google's recommended format, place in `<head>`
3. **Follow Google guidelines** — Only use markup Google supports
4. **Validate everything** — Test before deploying

---

## Common Schema Types

### Organization
**Use for:** Homepage, about page
```json
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "Example Company",
  "url": "https://example.com",
  "logo": "https://example.com/logo.png",
  "sameAs": ["https://twitter.com/example", "https://linkedin.com/company/example"]
}
```

### Article / BlogPosting
**Use for:** Blog posts, news
**Required:** headline, image, datePublished, author
```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "How to Implement Schema",
  "image": "https://example.com/image.jpg",
  "datePublished": "2024-01-15T08:00:00+00:00",
  "author": {"@type": "Person", "name": "Jane Doe"}
}
```

### Product
**Use for:** Product pages
**Required:** name, image, offers (price, availability)
```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "Premium Widget",
  "image": "https://example.com/widget.jpg",
  "offers": {
    "@type": "Offer",
    "price": "99.99",
    "priceCurrency": "USD",
    "availability": "https://schema.org/InStock"
  }
}
```

### FAQPage
**Use for:** FAQ sections
```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [{
    "@type": "Question",
    "name": "What is schema markup?",
    "acceptedAnswer": {
      "@type": "Answer",
      "text": "Schema markup is structured data that helps search engines understand content..."
    }
  }]
}
```

### HowTo
**Use for:** Tutorials, instructions
```json
{
  "@context": "https://schema.org",
  "@type": "HowTo",
  "name": "How to Add Schema Markup",
  "step": [
    {"@type": "HowToStep", "name": "Choose schema type", "text": "Identify appropriate type..."},
    {"@type": "HowToStep", "name": "Write JSON-LD", "text": "Create the markup..."}
  ]
}
```

### BreadcrumbList
**Use for:** Any page with breadcrumb navigation
```json
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://example.com"},
    {"@type": "ListItem", "position": 2, "name": "Blog", "item": "https://example.com/blog"}
  ]
}
```

### LocalBusiness
**Use for:** Local business pages
```json
{
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  "name": "Example Coffee",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "123 Main St",
    "addressLocality": "San Francisco",
    "addressRegion": "CA"
  },
  "telephone": "+1-555-555-5555"
}
```

---

## Multiple Types

Use `@graph` for multiple schema types on one page:
```json
{
  "@context": "https://schema.org",
  "@graph": [
    {"@type": "Organization", ...},
    {"@type": "WebSite", ...},
    {"@type": "BreadcrumbList", ...}
  ]
}
```

---

## Validation

**Tools:**
- [Google Rich Results Test](https://search.google.com/test/rich-results)
- [Schema.org Validator](https://validator.schema.org/)
- Search Console Enhancements

**Common errors:**
- Missing required properties
- Dates not in ISO 8601 format
- URLs not fully qualified
- Schema doesn't match visible content

---

## Implementation

**Static sites:** Add JSON-LD directly in template

**Dynamic (React/Next.js):**
```jsx
<script
  type="application/ld+json"
  dangerouslySetInnerHTML={{ __html: JSON.stringify(schema) }}
/>
```

**WordPress:** Yoast, Rank Math, or Schema Pro plugins

---

## Checklist

- [ ] Validates in Rich Results Test
- [ ] No errors or warnings
- [ ] Matches page content exactly
- [ ] All required properties included

---

## Related Skills

- **@include skill:seo-audit**: Overall SEO including schema review
- **@include skill:programmatic-seo**: Templated schema at scale
