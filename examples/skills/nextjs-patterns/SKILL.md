---
name: nextjs-patterns
description: |
  Next.js App Router patterns and best practices. Covers Server Components,
  data fetching, caching, route handlers, middleware, and performance
  optimization for production applications.
license: MIT
allowed-tools: Read Edit Bash
version: 1.0.0
tags: [nextjs, react, ssr, app-router, server-components]
category: development/nextjs
trigger_phrases:
  - "Next.js"
  - "App Router"
  - "Server Components"
  - "RSC"
  - "Next.js caching"
  - "route handlers"
  - "server actions"
variables:
  version:
    type: string
    description: Next.js version context
    enum: [14, 15]
    default: 14
---

# Next.js Patterns Guide

## Core Philosophy

**Server Components by default, Client Components when needed.** Start with RSC and add interactivity selectively.

> "The best JavaScript is the JavaScript you don't ship to the browser."

---

## App Router Structure

```
app/
├── layout.tsx           # Root layout
├── page.tsx             # Home page (/)
├── loading.tsx          # Loading UI
├── error.tsx            # Error UI
├── not-found.tsx        # 404 page
├── globals.css
├── (auth)/              # Route group (no URL impact)
│   ├── login/page.tsx   # /login
│   └── signup/page.tsx  # /signup
├── dashboard/
│   ├── layout.tsx       # Nested layout
│   ├── page.tsx         # /dashboard
│   └── [id]/            # Dynamic segment
│       └── page.tsx     # /dashboard/123
├── api/
│   └── users/
│       └── route.ts     # API route /api/users
└── @modal/              # Parallel route (for modals)
    └── (.)photo/[id]/
        └── page.tsx     # Intercepted route
```

---

## 1. Server Components

### Default Behavior (Server Component)

```tsx
// app/users/page.tsx
// This is a Server Component by default

async function UsersPage() {
  // Direct database access - no API needed!
  const users = await db.user.findMany();

  return (
    <div>
      <h1>Users</h1>
      <ul>
        {users.map(user => (
          <li key={user.id}>{user.name}</li>
        ))}
      </ul>
    </div>
  );
}

export default UsersPage;
```

### Client Components

```tsx
'use client';  // Required at top of file

import { useState } from 'react';

export function Counter() {
  const [count, setCount] = useState(0);

  return (
    <button onClick={() => setCount(c => c + 1)}>
      Count: {count}
    </button>
  );
}
```

### Mixing Server and Client

```tsx
// app/dashboard/page.tsx (Server Component)
import { Counter } from './Counter';  // Client Component
import { UserList } from './UserList';  // Server Component

async function DashboardPage() {
  const data = await fetchDashboardData();

  return (
    <div>
      <h1>Dashboard</h1>
      {/* Server Component */}
      <UserList users={data.users} />
      {/* Client Component */}
      <Counter />
    </div>
  );
}
```

---

## 2. Data Fetching

### Fetch with Caching

```tsx
// Cached by default (equivalent to force-cache)
async function getUser(id: string) {
  const res = await fetch(`https://api.example.com/users/${id}`);
  return res.json();
}

// Revalidate every 60 seconds
async function getPosts() {
  const res = await fetch('https://api.example.com/posts', {
    next: { revalidate: 60 }
  });
  return res.json();
}

// No caching (always fresh)
async function getComments() {
  const res = await fetch('https://api.example.com/comments', {
    cache: 'no-store'
  });
  return res.json();
}

// With tags for on-demand revalidation
async function getProduct(id: string) {
  const res = await fetch(`https://api.example.com/products/${id}`, {
    next: { tags: [`product-${id}`] }
  });
  return res.json();
}
```

### Parallel Data Fetching

```tsx
async function Page() {
  // BAD: Sequential (slow)
  const user = await getUser();
  const posts = await getPosts();

  // GOOD: Parallel (fast)
  const [user, posts] = await Promise.all([
    getUser(),
    getPosts()
  ]);

  return <div>...</div>;
}
```

### With Suspense

```tsx
import { Suspense } from 'react';

async function UserProfile({ userId }: { userId: string }) {
  const user = await getUser(userId);
  return <div>{user.name}</div>;
}

function Page({ params }: { params: { id: string } }) {
  return (
    <div>
      <h1>Profile</h1>
      <Suspense fallback={<div>Loading profile...</div>}>
        <UserProfile userId={params.id} />
      </Suspense>
    </div>
  );
}
```

---

## 3. Server Actions

```tsx
// app/actions.ts
'use server';

import { revalidatePath, revalidateTag } from 'next/cache';
import { redirect } from 'next/navigation';

export async function createPost(formData: FormData) {
  const title = formData.get('title') as string;
  const content = formData.get('content') as string;

  // Validate
  if (!title || title.length < 3) {
    return { error: 'Title must be at least 3 characters' };
  }

  // Create in database
  const post = await db.post.create({
    data: { title, content }
  });

  // Revalidate cache
  revalidatePath('/posts');
  revalidateTag('posts');

  // Redirect
  redirect(`/posts/${post.id}`);
}

export async function deletePost(id: string) {
  await db.post.delete({ where: { id } });
  revalidatePath('/posts');
}
```

### Using Server Actions

```tsx
// In a Server Component
import { createPost } from './actions';

function NewPostForm() {
  return (
    <form action={createPost}>
      <input name="title" placeholder="Title" required />
      <textarea name="content" placeholder="Content" />
      <button type="submit">Create Post</button>
    </form>
  );
}

// In a Client Component with pending state
'use client';

import { useFormStatus } from 'react-dom';
import { createPost } from './actions';

function SubmitButton() {
  const { pending } = useFormStatus();
  return (
    <button type="submit" disabled={pending}>
      {pending ? 'Creating...' : 'Create Post'}
    </button>
  );
}

function NewPostForm() {
  return (
    <form action={createPost}>
      <input name="title" placeholder="Title" required />
      <SubmitButton />
    </form>
  );
}
```

---

## 4. Route Handlers (API Routes)

```tsx
// app/api/users/route.ts
import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const page = searchParams.get('page') || '1';

  const users = await db.user.findMany({
    skip: (parseInt(page) - 1) * 10,
    take: 10,
  });

  return NextResponse.json(users);
}

export async function POST(request: NextRequest) {
  const body = await request.json();

  const user = await db.user.create({
    data: body,
  });

  return NextResponse.json(user, { status: 201 });
}

// app/api/users/[id]/route.ts
export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  const user = await db.user.findUnique({
    where: { id: params.id },
  });

  if (!user) {
    return NextResponse.json({ error: 'Not found' }, { status: 404 });
  }

  return NextResponse.json(user);
}
```

---

## 5. Middleware

```tsx
// middleware.ts (at root level)
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  // Check auth
  const token = request.cookies.get('token');

  if (!token && request.nextUrl.pathname.startsWith('/dashboard')) {
    return NextResponse.redirect(new URL('/login', request.url));
  }

  // Add headers
  const response = NextResponse.next();
  response.headers.set('x-request-id', crypto.randomUUID());

  return response;
}

export const config = {
  matcher: [
    // Match all paths except static files
    '/((?!_next/static|_next/image|favicon.ico).*)',
  ],
};
```

---

## 6. Loading and Error States

### Loading UI

```tsx
// app/dashboard/loading.tsx
export default function Loading() {
  return (
    <div className="animate-pulse">
      <div className="h-8 bg-gray-200 rounded w-1/4 mb-4" />
      <div className="h-4 bg-gray-200 rounded w-full mb-2" />
      <div className="h-4 bg-gray-200 rounded w-3/4" />
    </div>
  );
}
```

### Error Handling

```tsx
// app/dashboard/error.tsx
'use client';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div className="p-4 bg-red-50 rounded">
      <h2 className="text-red-800 font-bold">Something went wrong!</h2>
      <p className="text-red-600">{error.message}</p>
      <button
        onClick={reset}
        className="mt-2 px-4 py-2 bg-red-600 text-white rounded"
      >
        Try again
      </button>
    </div>
  );
}
```

---

## 7. Metadata and SEO

```tsx
// app/layout.tsx
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: {
    template: '%s | My App',
    default: 'My App',
  },
  description: 'My awesome app',
  openGraph: {
    title: 'My App',
    description: 'My awesome app',
    images: ['/og-image.png'],
  },
};

// app/posts/[id]/page.tsx
export async function generateMetadata({
  params,
}: {
  params: { id: string };
}): Promise<Metadata> {
  const post = await getPost(params.id);

  return {
    title: post.title,
    description: post.excerpt,
    openGraph: {
      title: post.title,
      images: [post.image],
    },
  };
}
```

---

## 8. Performance Patterns

### Static Generation

```tsx
// Generate static pages at build time
export async function generateStaticParams() {
  const posts = await getPosts();

  return posts.map((post) => ({
    id: post.id,
  }));
}

// Page will be statically generated for each ID
export default async function PostPage({
  params,
}: {
  params: { id: string };
}) {
  const post = await getPost(params.id);
  return <PostContent post={post} />;
}
```

### Image Optimization

```tsx
import Image from 'next/image';

function Avatar({ src, name }: { src: string; name: string }) {
  return (
    <Image
      src={src}
      alt={name}
      width={100}
      height={100}
      placeholder="blur"
      blurDataURL="data:image/jpeg;base64,..."
      priority={false}  // true for above-the-fold images
    />
  );
}
```

---

## Quick Reference

### File Conventions

| File | Purpose |
|------|---------|
| `page.tsx` | Route UI |
| `layout.tsx` | Shared layout |
| `loading.tsx` | Loading state |
| `error.tsx` | Error boundary |
| `not-found.tsx` | 404 page |
| `route.ts` | API endpoint |
| `template.tsx` | Re-rendered layout |

### Data Fetching Patterns

| Pattern | Cache | Use Case |
|---------|-------|----------|
| Default fetch | Cached forever | Static data |
| `revalidate: 60` | Revalidate every 60s | Semi-static |
| `cache: 'no-store'` | Never cached | Dynamic data |
| `tags` | On-demand revalidation | User actions |

---

## Related Skills

- `react-patterns` - React fundamentals
- `tailwind-patterns` - Styling with Tailwind
- `vercel-deployment` - Deploying Next.js
