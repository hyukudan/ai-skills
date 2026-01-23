---
name: tailwind-patterns
description: |
  Tailwind CSS patterns and best practices. Covers utility-first approach,
  responsive design, dark mode, component patterns, custom configuration,
  and performance optimization.
license: MIT
allowed-tools: Read Edit Bash
version: 1.0.0
tags: [tailwind, css, styling, responsive, design-system]
category: development/css
trigger_phrases:
  - "Tailwind"
  - "Tailwind CSS"
  - "utility CSS"
  - "responsive design"
  - "dark mode"
  - "design system"
  - "CSS utilities"
variables:
  framework:
    type: string
    description: Frontend framework
    enum: [react, vue, vanilla]
    default: react
---

# Tailwind CSS Patterns Guide

## Core Philosophy

**Utility-first means composing styles at the component level.** Build custom designs without leaving your HTML.

> "The best CSS is the CSS that doesn't fight against you."

---

## 1. Essential Patterns

### Spacing and Layout

```html
<!-- Container with responsive padding -->
<div class="container mx-auto px-4 sm:px-6 lg:px-8">
  <!-- Content -->
</div>

<!-- Flexbox layout -->
<div class="flex items-center justify-between gap-4">
  <div class="flex-1">Left</div>
  <div class="flex-shrink-0">Right</div>
</div>

<!-- Grid layout -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
  <div>Item 1</div>
  <div>Item 2</div>
  <div>Item 3</div>
</div>

<!-- Auto-fit grid (responsive without breakpoints) -->
<div class="grid grid-cols-[repeat(auto-fit,minmax(250px,1fr))] gap-4">
  <!-- Cards auto-adjust -->
</div>
```

### Typography

```html
<!-- Heading hierarchy -->
<h1 class="text-4xl font-bold tracking-tight text-gray-900">
  Main Title
</h1>
<h2 class="text-2xl font-semibold text-gray-800">
  Section Header
</h2>
<p class="text-base text-gray-600 leading-relaxed">
  Body text with comfortable reading line height.
</p>

<!-- Text utilities -->
<p class="line-clamp-3">Long text truncated to 3 lines...</p>
<p class="truncate">Single line truncate...</p>
<p class="text-balance">Balanced text for headlines</p>
```

### Colors and Backgrounds

```html
<!-- Background with overlay -->
<div class="relative">
  <img src="bg.jpg" class="absolute inset-0 w-full h-full object-cover" />
  <div class="absolute inset-0 bg-black/50" />
  <div class="relative z-10 text-white">Content over image</div>
</div>

<!-- Gradient backgrounds -->
<div class="bg-gradient-to-r from-blue-500 to-purple-600">
  Horizontal gradient
</div>
<div class="bg-gradient-to-br from-gray-900 via-purple-900 to-violet-600">
  Diagonal multi-stop gradient
</div>
```

---

## 2. Component Patterns

### Buttons

```html
<!-- Primary button -->
<button class="
  inline-flex items-center justify-center
  px-4 py-2 rounded-lg
  bg-blue-600 text-white font-medium
  hover:bg-blue-700
  focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
  disabled:opacity-50 disabled:cursor-not-allowed
  transition-colors
">
  Primary Action
</button>

<!-- Secondary/Outline button -->
<button class="
  px-4 py-2 rounded-lg
  border border-gray-300 text-gray-700
  hover:bg-gray-50
  focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2
  transition-colors
">
  Secondary
</button>

<!-- Icon button -->
<button class="
  p-2 rounded-full
  text-gray-500 hover:text-gray-700 hover:bg-gray-100
  focus:outline-none focus:ring-2 focus:ring-gray-500
  transition-colors
">
  <svg class="w-5 h-5">...</svg>
</button>
```

### Cards

```html
<!-- Basic card -->
<div class="bg-white rounded-lg shadow-md overflow-hidden">
  <img src="..." class="w-full h-48 object-cover" />
  <div class="p-6">
    <h3 class="text-lg font-semibold text-gray-900">Card Title</h3>
    <p class="mt-2 text-gray-600">Card description...</p>
  </div>
</div>

<!-- Interactive card -->
<div class="
  bg-white rounded-lg shadow-sm
  border border-gray-200
  hover:shadow-md hover:border-gray-300
  transition-all duration-200
  cursor-pointer
">
  <div class="p-6">...</div>
</div>

<!-- Card with hover effect -->
<div class="
  group
  bg-white rounded-xl overflow-hidden
  shadow-lg hover:shadow-xl
  transform hover:-translate-y-1
  transition-all duration-300
">
  <img class="w-full h-48 object-cover group-hover:scale-105 transition-transform duration-300" />
  <div class="p-6">
    <h3 class="group-hover:text-blue-600 transition-colors">Title</h3>
  </div>
</div>
```

### Forms

```html
<!-- Input with label -->
<div>
  <label for="email" class="block text-sm font-medium text-gray-700 mb-1">
    Email
  </label>
  <input
    type="email"
    id="email"
    class="
      w-full px-3 py-2 rounded-lg
      border border-gray-300
      focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
      placeholder:text-gray-400
    "
    placeholder="you@example.com"
  />
</div>

<!-- Input with error -->
<div>
  <input class="
    w-full px-3 py-2 rounded-lg
    border border-red-500
    focus:outline-none focus:ring-2 focus:ring-red-500
  " />
  <p class="mt-1 text-sm text-red-600">Please enter a valid email</p>
</div>

<!-- Checkbox -->
<label class="flex items-center gap-2 cursor-pointer">
  <input type="checkbox" class="
    w-4 h-4 rounded
    border-gray-300
    text-blue-600
    focus:ring-blue-500
  " />
  <span class="text-sm text-gray-700">Remember me</span>
</label>
```

### Navigation

```html
<!-- Navbar -->
<nav class="bg-white shadow-sm border-b border-gray-200">
  <div class="container mx-auto px-4">
    <div class="flex items-center justify-between h-16">
      <!-- Logo -->
      <a href="/" class="text-xl font-bold text-gray-900">Logo</a>

      <!-- Desktop nav -->
      <div class="hidden md:flex items-center gap-6">
        <a href="#" class="text-gray-600 hover:text-gray-900 transition-colors">
          Features
        </a>
        <a href="#" class="text-gray-600 hover:text-gray-900 transition-colors">
          Pricing
        </a>
        <button class="px-4 py-2 bg-blue-600 text-white rounded-lg">
          Get Started
        </button>
      </div>

      <!-- Mobile menu button -->
      <button class="md:hidden p-2">
        <svg class="w-6 h-6">...</svg>
      </button>
    </div>
  </div>
</nav>
```

---

## 3. Responsive Design

### Breakpoint Strategy

```html
<!-- Mobile-first approach -->
<div class="
  text-sm      /* Mobile (default) */
  sm:text-base /* >= 640px */
  md:text-lg   /* >= 768px */
  lg:text-xl   /* >= 1024px */
  xl:text-2xl  /* >= 1280px */
  2xl:text-3xl /* >= 1536px */
">
  Responsive text
</div>

<!-- Hide/show at breakpoints -->
<div class="block md:hidden">Mobile only</div>
<div class="hidden md:block">Desktop only</div>

<!-- Responsive grid -->
<div class="
  grid
  grid-cols-1
  sm:grid-cols-2
  lg:grid-cols-3
  xl:grid-cols-4
  gap-4 sm:gap-6
">
  <!-- Cards -->
</div>
```

### Container Queries

```html
<!-- Enable container queries -->
<div class="@container">
  <div class="@md:flex @md:items-center">
    <!-- Responds to container width, not viewport -->
  </div>
</div>
```

---

## 4. Dark Mode

### Basic Dark Mode

```html
<!-- Toggle with class strategy -->
<html class="dark">
  <body class="bg-white dark:bg-gray-900 text-gray-900 dark:text-white">
    <div class="bg-gray-100 dark:bg-gray-800 p-6 rounded-lg">
      <h2 class="text-gray-900 dark:text-white">Title</h2>
      <p class="text-gray-600 dark:text-gray-400">Description</p>
    </div>
  </body>
</html>
```

### Dark Mode Toggle (React)

```tsx
{% if framework == "react" %}
import { useState, useEffect } from 'react';

function useDarkMode() {
  const [isDark, setIsDark] = useState(() => {
    if (typeof window === 'undefined') return false;
    return localStorage.theme === 'dark' ||
      (!('theme' in localStorage) &&
       window.matchMedia('(prefers-color-scheme: dark)').matches);
  });

  useEffect(() => {
    const root = document.documentElement;
    if (isDark) {
      root.classList.add('dark');
      localStorage.theme = 'dark';
    } else {
      root.classList.remove('dark');
      localStorage.theme = 'light';
    }
  }, [isDark]);

  return [isDark, setIsDark] as const;
}

function ThemeToggle() {
  const [isDark, setIsDark] = useDarkMode();

  return (
    <button
      onClick={() => setIsDark(!isDark)}
      class="p-2 rounded-lg bg-gray-200 dark:bg-gray-700"
    >
      {isDark ? '☀️' : '🌙'}
    </button>
  );
}
{% endif %}
```

### Dark Mode Colors Pattern

```html
<!-- Semantic color classes -->
<div class="
  bg-surface
  text-content
  border-border
">
  <!-- In tailwind.config.js, define these as CSS variables -->
</div>
```

```js
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        surface: 'var(--color-surface)',
        content: 'var(--color-content)',
        border: 'var(--color-border)',
      }
    }
  }
}
```

```css
/* globals.css */
:root {
  --color-surface: theme('colors.white');
  --color-content: theme('colors.gray.900');
  --color-border: theme('colors.gray.200');
}

.dark {
  --color-surface: theme('colors.gray.900');
  --color-content: theme('colors.gray.100');
  --color-border: theme('colors.gray.700');
}
```

---

## 5. Custom Configuration

### tailwind.config.js

```js
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx}',
  ],
  darkMode: 'class', // or 'media'
  theme: {
    extend: {
      // Custom colors
      colors: {
        brand: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          500: '#0ea5e9',
          600: '#0284c7',
          700: '#0369a1',
        },
      },
      // Custom fonts
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        display: ['Cal Sans', 'Inter', 'sans-serif'],
      },
      // Custom spacing
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
      },
      // Custom animations
      animation: {
        'fade-in': 'fadeIn 0.5s ease-out',
        'slide-up': 'slideUp 0.3s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
    require('@tailwindcss/aspect-ratio'),
  ],
}
```

### Custom Utilities

```js
// tailwind.config.js
const plugin = require('tailwindcss/plugin');

module.exports = {
  plugins: [
    plugin(function({ addUtilities, addComponents, theme }) {
      // Add utilities
      addUtilities({
        '.text-balance': {
          'text-wrap': 'balance',
        },
        '.scrollbar-hide': {
          '-ms-overflow-style': 'none',
          'scrollbar-width': 'none',
          '&::-webkit-scrollbar': {
            display: 'none',
          },
        },
      });

      // Add component classes
      addComponents({
        '.btn': {
          padding: theme('spacing.2') + ' ' + theme('spacing.4'),
          borderRadius: theme('borderRadius.lg'),
          fontWeight: theme('fontWeight.medium'),
        },
        '.btn-primary': {
          backgroundColor: theme('colors.blue.600'),
          color: theme('colors.white'),
          '&:hover': {
            backgroundColor: theme('colors.blue.700'),
          },
        },
      });
    }),
  ],
};
```

---

## 6. Performance Optimization

### Purging Unused CSS

```js
// tailwind.config.js
module.exports = {
  content: [
    './src/**/*.{js,ts,jsx,tsx}',
    // Include any files that use Tailwind classes
  ],
  // Safelist classes that might be dynamic
  safelist: [
    'bg-red-500',
    'bg-green-500',
    'bg-blue-500',
    { pattern: /^bg-(red|green|blue)-(100|500|900)$/ },
  ],
}
```

### Optimizing for Production

```html
<!-- Avoid dynamic class names -->
<!-- BAD -->
<div class={`text-${color}-500`}>...</div>

<!-- GOOD -->
<div class={color === 'red' ? 'text-red-500' : 'text-blue-500'}>...</div>

<!-- Or use complete class names in an object -->
const colorClasses = {
  red: 'text-red-500 bg-red-100',
  blue: 'text-blue-500 bg-blue-100',
};
<div class={colorClasses[color]}>...</div>
```

---

## 7. Common Patterns

### Aspect Ratio

```html
<!-- Fixed aspect ratio -->
<div class="aspect-video">
  <img src="..." class="w-full h-full object-cover" />
</div>

<div class="aspect-square">
  <img src="..." class="w-full h-full object-cover" />
</div>
```

### Centering

```html
<!-- Absolute centering -->
<div class="absolute inset-0 flex items-center justify-center">
  Centered content
</div>

<!-- Grid centering -->
<div class="grid place-items-center min-h-screen">
  Centered content
</div>
```

### Sticky Elements

```html
<!-- Sticky header -->
<header class="sticky top-0 z-50 bg-white/80 backdrop-blur-sm border-b">
  Navigation
</header>

<!-- Sticky sidebar -->
<aside class="sticky top-20 h-fit">
  Sidebar content
</aside>
```

### Skeleton Loading

```html
<div class="animate-pulse">
  <div class="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
  <div class="h-4 bg-gray-200 rounded w-1/2 mb-4"></div>
  <div class="h-32 bg-gray-200 rounded"></div>
</div>
```

---

## Quick Reference

### Spacing Scale

| Class | Value |
|-------|-------|
| `p-1` | 0.25rem (4px) |
| `p-2` | 0.5rem (8px) |
| `p-4` | 1rem (16px) |
| `p-6` | 1.5rem (24px) |
| `p-8` | 2rem (32px) |

### Breakpoints

| Prefix | Min Width |
|--------|-----------|
| `sm:` | 640px |
| `md:` | 768px |
| `lg:` | 1024px |
| `xl:` | 1280px |
| `2xl:` | 1536px |

### Useful Class Combinations

```html
<!-- Full-bleed image -->
<img class="w-full h-full object-cover" />

<!-- Truncate text -->
<p class="truncate" />
<p class="line-clamp-2" />

<!-- Flex center -->
<div class="flex items-center justify-center" />

<!-- Absolute fill -->
<div class="absolute inset-0" />

<!-- Ring focus -->
<button class="focus:outline-none focus:ring-2 focus:ring-offset-2" />
```

---

## Related Skills

- `css-architecture` - CSS organization patterns
- `design-systems` - Building component libraries
- `accessibility` - WCAG compliance
