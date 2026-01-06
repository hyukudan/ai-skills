---
name: frontend-design
description: |
  Create distinctive, production-grade frontend interfaces with high design quality.
  Use when building web components, pages, or applications. Covers framework-specific
  patterns, responsive design, accessibility, and modern CSS techniques. Generates
  creative, polished code that avoids generic AI aesthetics.
version: 1.0.0
tags: [frontend, design, ui, ux, css, responsive, accessibility]
category: development/frontend
variables:
  framework:
    type: string
    description: Frontend framework to use
    enum: [react, vue, vanilla, nextjs, svelte]
    default: react
  styling:
    type: string
    description: CSS approach
    enum: [tailwind, css-modules, styled-components, vanilla-css]
    default: tailwind
  accessibility_level:
    type: string
    description: WCAG compliance level
    enum: [basic, aa, aaa]
    default: aa
---

# Frontend Design Guide

## Design Philosophy

**Interfaces are experiences.** Every pixel, transition, and interaction shapes how users feel about your product.

### Core Principles

1. **Intentionality over defaults** - Every design choice should be deliberate
2. **Consistency builds trust** - Unified patterns reduce cognitive load
3. **Accessibility is not optional** - Design for everyone from the start
4. **Performance is a feature** - Fast interfaces feel premium

> "The best interface is one that disappears—users achieve their goals without thinking about the tool."

---

## Design Thinking Phase

Before writing code, answer these questions:

```
1. PURPOSE: What is the primary user goal?
2. AUDIENCE: Who are we designing for?
3. TONE: What emotion should this evoke?
   - Professional & trustworthy
   - Playful & energetic
   - Minimal & focused
   - Bold & innovative
4. CONSTRAINTS: Device targets, browser support, performance budget
5. DIFFERENTIATION: What makes this memorable?
```

---

## Visual Design System

### Typography

**Choose characterful fonts, not defaults:**

```css
/* AVOID - Generic AI aesthetics */
font-family: Inter, system-ui, sans-serif;

/* BETTER - Distinctive choices */
font-family: 'Space Grotesk', sans-serif;     /* Tech/Modern */
font-family: 'Playfair Display', serif;       /* Editorial/Luxury */
font-family: 'JetBrains Mono', monospace;     /* Developer tools */
```

**Type Scale (Golden Ratio):**

```css
--text-xs: 0.75rem;    /* 12px */
--text-sm: 0.875rem;   /* 14px */
--text-base: 1rem;     /* 16px */
--text-lg: 1.125rem;   /* 18px */
--text-xl: 1.25rem;    /* 20px */
--text-2xl: 1.618rem;  /* ~26px - Golden ratio */
--text-3xl: 2.618rem;  /* ~42px */
--text-4xl: 4.236rem;  /* ~68px */
```

### Color System

**Build a cohesive palette:**

```css
:root {
  /* Primary - Your brand color */
  --primary-50: #eff6ff;
  --primary-500: #3b82f6;
  --primary-900: #1e3a8a;

  /* Semantic colors */
  --success: #10b981;
  --warning: #f59e0b;
  --error: #ef4444;

  /* Neutrals - Never pure black/white */
  --gray-50: #fafafa;
  --gray-900: #18181b;

  /* Surfaces */
  --surface: var(--gray-50);
  --surface-elevated: white;
  --surface-overlay: rgba(0, 0, 0, 0.5);
}
```

### Spacing System

**Use consistent scale:**

```css
--space-1: 0.25rem;   /* 4px - Tight */
--space-2: 0.5rem;    /* 8px - Related elements */
--space-3: 0.75rem;   /* 12px */
--space-4: 1rem;      /* 16px - Default */
--space-6: 1.5rem;    /* 24px - Sections */
--space-8: 2rem;      /* 32px */
--space-12: 3rem;     /* 48px - Major sections */
--space-16: 4rem;     /* 64px - Page margins */
```

---

{% if framework == "react" or framework == "nextjs" %}
## React Component Patterns

### Component Structure

```tsx
// components/Button/Button.tsx
import { forwardRef } from 'react';
import { cn } from '@/lib/utils';
import styles from './Button.module.css';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'primary', size = 'md', loading, children, ...props }, ref) => {
    return (
      <button
        ref={ref}
        className={cn(
          styles.button,
          styles[variant],
          styles[size],
          loading && styles.loading,
          className
        )}
        disabled={loading || props.disabled}
        {...props}
      >
        {loading ? <Spinner /> : children}
      </button>
    );
  }
);

Button.displayName = 'Button';
```

### Composition Pattern

```tsx
// Card with slots for flexible composition
interface CardProps {
  children: React.ReactNode;
}

export function Card({ children }: CardProps) {
  return <div className="card">{children}</div>;
}

Card.Header = function CardHeader({ children }: { children: React.ReactNode }) {
  return <div className="card-header">{children}</div>;
};

Card.Body = function CardBody({ children }: { children: React.ReactNode }) {
  return <div className="card-body">{children}</div>;
};

Card.Footer = function CardFooter({ children }: { children: React.ReactNode }) {
  return <div className="card-footer">{children}</div>;
};

// Usage
<Card>
  <Card.Header>Title</Card.Header>
  <Card.Body>Content</Card.Body>
  <Card.Footer>Actions</Card.Footer>
</Card>
```

{% elif framework == "vue" %}
## Vue Component Patterns

### Component Structure

```vue
<!-- components/Button.vue -->
<script setup lang="ts">
interface Props {
  variant?: 'primary' | 'secondary' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'primary',
  size: 'md',
  loading: false,
});

const emit = defineEmits<{
  click: [event: MouseEvent];
}>();
</script>

<template>
  <button
    :class="[
      'button',
      `button--${variant}`,
      `button--${size}`,
      { 'button--loading': loading }
    ]"
    :disabled="loading"
    @click="emit('click', $event)"
  >
    <Spinner v-if="loading" />
    <slot v-else />
  </button>
</template>

<style scoped>
.button {
  /* Base styles */
}
</style>
```

### Composables Pattern

```typescript
// composables/useToggle.ts
import { ref, computed } from 'vue';

export function useToggle(initialValue = false) {
  const state = ref(initialValue);

  const toggle = () => { state.value = !state.value };
  const setTrue = () => { state.value = true };
  const setFalse = () => { state.value = false };

  return { state, toggle, setTrue, setFalse };
}
```

{% elif framework == "vanilla" %}
## Vanilla JavaScript Patterns

### Web Components

```javascript
class CustomButton extends HTMLElement {
  static observedAttributes = ['variant', 'loading'];

  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }

  connectedCallback() {
    this.render();
  }

  attributeChangedCallback() {
    this.render();
  }

  render() {
    const variant = this.getAttribute('variant') || 'primary';
    const loading = this.hasAttribute('loading');

    this.shadowRoot.innerHTML = `
      <style>
        :host { display: inline-block; }
        button {
          padding: 0.5rem 1rem;
          border: none;
          border-radius: 0.375rem;
          cursor: pointer;
          transition: all 0.2s;
        }
        .primary { background: var(--primary-500); color: white; }
        .secondary { background: var(--gray-200); color: var(--gray-900); }
      </style>
      <button class="${variant}" ${loading ? 'disabled' : ''}>
        ${loading ? '<span class="spinner"></span>' : '<slot></slot>'}
      </button>
    `;
  }
}

customElements.define('custom-button', CustomButton);
```

{% endif %}

---

{% if styling == "tailwind" %}
## Tailwind CSS Patterns

### Custom Configuration

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#eff6ff',
          500: '#3b82f6',
          900: '#1e3a8a',
        },
      },
      fontFamily: {
        display: ['Space Grotesk', 'sans-serif'],
        body: ['Inter', 'sans-serif'],
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-out',
        'slide-up': 'slideUp 0.3s ease-out',
      },
    },
  },
};
```

### Component Classes Pattern

```tsx
// Avoid long class strings in JSX
const buttonVariants = {
  primary: 'bg-brand-500 text-white hover:bg-brand-600',
  secondary: 'bg-gray-100 text-gray-900 hover:bg-gray-200',
  ghost: 'bg-transparent hover:bg-gray-100',
};

const buttonSizes = {
  sm: 'px-3 py-1.5 text-sm',
  md: 'px-4 py-2 text-base',
  lg: 'px-6 py-3 text-lg',
};

function Button({ variant = 'primary', size = 'md', className, ...props }) {
  return (
    <button
      className={cn(
        'rounded-lg font-medium transition-colors',
        buttonVariants[variant],
        buttonSizes[size],
        className
      )}
      {...props}
    />
  );
}
```

{% elif styling == "css-modules" %}
## CSS Modules Patterns

```css
/* Button.module.css */
.button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.375rem;
  font-weight: 500;
  transition: all 0.2s ease;
}

.primary {
  background: var(--primary-500);
  color: white;
}

.primary:hover {
  background: var(--primary-600);
}

.sm { padding: 0.375rem 0.75rem; font-size: 0.875rem; }
.md { padding: 0.5rem 1rem; font-size: 1rem; }
.lg { padding: 0.75rem 1.5rem; font-size: 1.125rem; }
```

{% endif %}

---

## Responsive Design

### Mobile-First Breakpoints

```css
/* Base styles: Mobile (320px+) */
.container { padding: 1rem; }

/* Tablet (768px+) */
@media (min-width: 768px) {
  .container { padding: 2rem; }
}

/* Desktop (1024px+) */
@media (min-width: 1024px) {
  .container { padding: 4rem; max-width: 1280px; margin: 0 auto; }
}
```

### Responsive Patterns

```css
/* Fluid typography */
.heading {
  font-size: clamp(1.5rem, 5vw, 3rem);
}

/* Responsive grid */
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
}

/* Container queries (modern) */
@container (min-width: 400px) {
  .card { flex-direction: row; }
}
```

---

{% if accessibility_level == "aa" or accessibility_level == "aaa" %}
## Accessibility (WCAG {{ accessibility_level | upper }})

### Color Contrast

```
WCAG AA Requirements:
- Normal text: 4.5:1 contrast ratio
- Large text (18px+ bold, 24px+ regular): 3:1
- UI components: 3:1

WCAG AAA Requirements:
- Normal text: 7:1 contrast ratio
- Large text: 4.5:1
```

### Focus Management

```css
/* Visible focus indicators */
:focus-visible {
  outline: 2px solid var(--primary-500);
  outline-offset: 2px;
}

/* Skip link */
.skip-link {
  position: absolute;
  top: -100%;
  left: 0;
  z-index: 100;
}

.skip-link:focus {
  top: 0;
}
```

### ARIA Patterns

```html
<!-- Accessible button with loading state -->
<button
  aria-busy="true"
  aria-label="Submitting form, please wait"
>
  <span aria-hidden="true">⏳</span>
  Submitting...
</button>

<!-- Accessible modal -->
<div
  role="dialog"
  aria-modal="true"
  aria-labelledby="modal-title"
>
  <h2 id="modal-title">Confirm Action</h2>
  <!-- content -->
</div>

<!-- Live region for dynamic updates -->
<div aria-live="polite" aria-atomic="true">
  Form submitted successfully!
</div>
```

### Keyboard Navigation

```javascript
// Focus trap for modals
function trapFocus(element) {
  const focusableElements = element.querySelectorAll(
    'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
  );
  const firstElement = focusableElements[0];
  const lastElement = focusableElements[focusableElements.length - 1];

  element.addEventListener('keydown', (e) => {
    if (e.key === 'Tab') {
      if (e.shiftKey && document.activeElement === firstElement) {
        e.preventDefault();
        lastElement.focus();
      } else if (!e.shiftKey && document.activeElement === lastElement) {
        e.preventDefault();
        firstElement.focus();
      }
    }
  });
}
```

{% endif %}

---

## Animation & Motion

### Meaningful Transitions

```css
/* Micro-interactions */
.button {
  transition: transform 0.1s ease, box-shadow 0.2s ease;
}

.button:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.button:active {
  transform: translateY(0);
}

/* Page transitions */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.page-enter {
  animation: fadeIn 0.3s ease-out;
}

/* Staggered reveals */
.list-item {
  animation: fadeIn 0.4s ease-out backwards;
}

.list-item:nth-child(1) { animation-delay: 0ms; }
.list-item:nth-child(2) { animation-delay: 50ms; }
.list-item:nth-child(3) { animation-delay: 100ms; }
```

### Respect User Preferences

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## Anti-Patterns to Avoid

### Generic AI Aesthetics

```
❌ AVOID:
- Default Inter/system fonts everywhere
- Purple-to-blue gradients on everything
- Rounded corners on absolutely everything
- Generic hero with "Welcome to [Product]"
- Stock illustrations with floating people

✅ INSTEAD:
- Choose fonts that match the brand personality
- Use color intentionally, not decoratively
- Vary border-radius based on context
- Lead with value proposition
- Custom illustrations or real photography
```

### Common Mistakes

```css
/* BAD: Magic numbers */
.card { margin-top: 37px; padding: 13px; }

/* GOOD: Use design tokens */
.card { margin-top: var(--space-8); padding: var(--space-4); }

/* BAD: Color values everywhere */
.button { background: #3b82f6; }
.link { color: #3b82f6; }

/* GOOD: Semantic variables */
.button { background: var(--primary-500); }
.link { color: var(--primary-500); }
```

---

## Performance Checklist

- [ ] Images optimized (WebP, proper sizing, lazy loading)
- [ ] Fonts subset and preloaded
- [ ] CSS critical path inlined
- [ ] No layout shifts (CLS < 0.1)
- [ ] First paint < 1.5s
- [ ] Bundle size monitored
