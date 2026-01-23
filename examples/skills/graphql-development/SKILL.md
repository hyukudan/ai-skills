---
name: graphql-development
description: |
  GraphQL API design and implementation patterns. Covers schema design,
  resolvers, N+1 problem, subscriptions, error handling, and production
  best practices.
license: MIT
allowed-tools: Read Edit Bash
version: 1.0.0
tags: [graphql, api, schema, resolvers, apollo]
category: development/graphql
trigger_phrases:
  - "GraphQL"
  - "GraphQL schema"
  - "resolver"
  - "GraphQL mutation"
  - "GraphQL subscription"
  - "N+1 problem"
  - "Apollo"
variables:
  framework:
    type: string
    description: GraphQL framework
    enum: [apollo, strawberry, graphene, ariadne]
    default: apollo
---

# GraphQL Development Guide

## Core Philosophy

**GraphQL is a contract between client and server.** Design schemas for client needs, not database structure.

> "A well-designed GraphQL schema makes impossible states unrepresentable."

---

## 1. Schema Design

### Types and Fields

```graphql
type User {
  id: ID!
  email: String!
  name: String
  posts(first: Int = 10, after: String): PostConnection!
  createdAt: DateTime!
}

type Post {
  id: ID!
  title: String!
  content: String!
  author: User!
  comments: [Comment!]!
  publishedAt: DateTime
  status: PostStatus!
}

enum PostStatus {
  DRAFT
  PUBLISHED
  ARCHIVED
}

# Pagination with Relay-style connections
type PostConnection {
  edges: [PostEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
}

type PostEdge {
  node: Post!
  cursor: String!
}

type PageInfo {
  hasNextPage: Boolean!
  hasPreviousPage: Boolean!
  startCursor: String
  endCursor: String
}
```

### Input Types

```graphql
input CreatePostInput {
  title: String!
  content: String!
  status: PostStatus = DRAFT
}

input UpdatePostInput {
  title: String
  content: String
  status: PostStatus
}

input PostFilterInput {
  status: PostStatus
  authorId: ID
  searchTerm: String
  createdAfter: DateTime
}
```

### Queries and Mutations

```graphql
type Query {
  # Single resource
  user(id: ID!): User
  post(id: ID!): Post

  # Collections with filtering and pagination
  posts(
    filter: PostFilterInput
    first: Int = 10
    after: String
  ): PostConnection!

  # Authenticated user
  me: User
}

type Mutation {
  # Create
  createPost(input: CreatePostInput!): CreatePostPayload!

  # Update
  updatePost(id: ID!, input: UpdatePostInput!): UpdatePostPayload!

  # Delete
  deletePost(id: ID!): DeletePostPayload!
}

# Mutation payloads (for errors and metadata)
type CreatePostPayload {
  post: Post
  errors: [UserError!]!
}

type UserError {
  field: String
  message: String!
  code: ErrorCode!
}

enum ErrorCode {
  NOT_FOUND
  UNAUTHORIZED
  VALIDATION_ERROR
  INTERNAL_ERROR
}
```

---

## 2. Resolvers

### Basic Resolvers (Node.js/Apollo)

```typescript
const resolvers = {
  Query: {
    user: async (_, { id }, context) => {
      return context.dataSources.users.findById(id);
    },

    posts: async (_, { filter, first, after }, context) => {
      return context.dataSources.posts.findMany({
        filter,
        first,
        after,
      });
    },

    me: async (_, __, context) => {
      if (!context.user) return null;
      return context.dataSources.users.findById(context.user.id);
    },
  },

  Mutation: {
    createPost: async (_, { input }, context) => {
      if (!context.user) {
        return {
          post: null,
          errors: [{ message: 'Not authenticated', code: 'UNAUTHORIZED' }],
        };
      }

      try {
        const post = await context.dataSources.posts.create({
          ...input,
          authorId: context.user.id,
        });
        return { post, errors: [] };
      } catch (error) {
        return {
          post: null,
          errors: [{ message: error.message, code: 'VALIDATION_ERROR' }],
        };
      }
    },
  },

  // Field resolvers
  User: {
    posts: async (user, { first, after }, context) => {
      return context.dataSources.posts.findByAuthor(user.id, { first, after });
    },
  },

  Post: {
    author: async (post, _, context) => {
      return context.dataSources.users.findById(post.authorId);
    },
  },
};
```

### Python Resolvers (Strawberry)

```python
import strawberry
from typing import Optional, List

@strawberry.type
class User:
    id: strawberry.ID
    email: str
    name: Optional[str]

    @strawberry.field
    async def posts(self, info, first: int = 10) -> List["Post"]:
        loader = info.context.loaders.posts_by_author
        return await loader.load(self.id)

@strawberry.type
class Query:
    @strawberry.field
    async def user(self, info, id: strawberry.ID) -> Optional[User]:
        return await info.context.db.users.find_by_id(id)

    @strawberry.field
    async def me(self, info) -> Optional[User]:
        if not info.context.user:
            return None
        return await info.context.db.users.find_by_id(info.context.user.id)

@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_post(self, info, input: CreatePostInput) -> CreatePostPayload:
        if not info.context.user:
            return CreatePostPayload(
                post=None,
                errors=[UserError(message="Not authenticated", code="UNAUTHORIZED")]
            )

        post = await info.context.db.posts.create(
            title=input.title,
            content=input.content,
            author_id=info.context.user.id
        )
        return CreatePostPayload(post=post, errors=[])
```

---

## 3. N+1 Problem and DataLoader

### The Problem

```graphql
# This query causes N+1 database queries
query {
  posts(first: 10) {    # 1 query for posts
    title
    author {            # 10 queries for authors (1 per post)
      name
    }
  }
}
```

### Solution: DataLoader

```typescript
import DataLoader from 'dataloader';

// Create loaders per request
function createLoaders(db) {
  return {
    users: new DataLoader(async (ids) => {
      // Batch load: single query for all IDs
      const users = await db.users.findByIds(ids);
      // Return in same order as requested IDs
      return ids.map(id => users.find(u => u.id === id));
    }),

    postsByAuthor: new DataLoader(async (authorIds) => {
      const posts = await db.posts.findByAuthorIds(authorIds);
      // Group by author ID
      return authorIds.map(authorId =>
        posts.filter(p => p.authorId === authorId)
      );
    }),
  };
}

// In resolver
const resolvers = {
  Post: {
    author: (post, _, context) => {
      return context.loaders.users.load(post.authorId);
    },
  },
};
```

---

## 4. Error Handling

### Structured Errors

```graphql
interface Error {
  message: String!
  code: ErrorCode!
}

type ValidationError implements Error {
  message: String!
  code: ErrorCode!
  field: String!
}

type NotFoundError implements Error {
  message: String!
  code: ErrorCode!
  resourceType: String!
  resourceId: ID!
}

union CreatePostResult = Post | ValidationError | NotFoundError
```

### Error Handling in Resolvers

```typescript
import { ApolloError, AuthenticationError, ForbiddenError } from 'apollo-server';

const resolvers = {
  Mutation: {
    updatePost: async (_, { id, input }, context) => {
      // Check authentication
      if (!context.user) {
        throw new AuthenticationError('Must be logged in');
      }

      const post = await context.dataSources.posts.findById(id);

      // Check existence
      if (!post) {
        throw new ApolloError('Post not found', 'NOT_FOUND', { id });
      }

      // Check authorization
      if (post.authorId !== context.user.id) {
        throw new ForbiddenError('Cannot edit another user\'s post');
      }

      // Validate input
      const errors = validatePostInput(input);
      if (errors.length > 0) {
        return { post: null, errors };
      }

      const updated = await context.dataSources.posts.update(id, input);
      return { post: updated, errors: [] };
    },
  },
};
```

---

## 5. Subscriptions

```graphql
type Subscription {
  postCreated: Post!
  postUpdated(id: ID!): Post!
  commentAdded(postId: ID!): Comment!
}
```

```typescript
import { PubSub } from 'graphql-subscriptions';

const pubsub = new PubSub();

const resolvers = {
  Mutation: {
    createPost: async (_, { input }, context) => {
      const post = await context.dataSources.posts.create(input);

      // Publish event
      pubsub.publish('POST_CREATED', { postCreated: post });

      return { post, errors: [] };
    },
  },

  Subscription: {
    postCreated: {
      subscribe: () => pubsub.asyncIterator(['POST_CREATED']),
    },

    commentAdded: {
      subscribe: (_, { postId }) => {
        return pubsub.asyncIterator([`COMMENT_ADDED_${postId}`]);
      },
    },
  },
};
```

---

## 6. Performance & Security

### Query Complexity Limiting

```typescript
import { createComplexityLimitRule } from 'graphql-validation-complexity';

const complexityLimitRule = createComplexityLimitRule(1000, {
  scalarCost: 1,
  objectCost: 10,
  listFactor: 10,
});

const server = new ApolloServer({
  schema,
  validationRules: [complexityLimitRule],
});
```

### Query Depth Limiting

```typescript
import depthLimit from 'graphql-depth-limit';

const server = new ApolloServer({
  schema,
  validationRules: [depthLimit(7)],
});
```

### Persisted Queries

```typescript
// Client sends hash instead of full query
// query=abc123 instead of query={ user { name } }

const server = new ApolloServer({
  schema,
  persistedQueries: {
    cache: new RedisCache({ host: 'localhost' }),
  },
});
```

---

## Quick Reference

### Schema Design Checklist

- [ ] Use non-nullable (`!`) where appropriate
- [ ] Provide default values for optional arguments
- [ ] Use Relay-style connections for pagination
- [ ] Return payload types from mutations (not just the resource)
- [ ] Include error information in payloads
- [ ] Use enums for fixed sets of values
- [ ] Document with descriptions

### Common Patterns

| Pattern | When to Use |
|---------|-------------|
| Relay Connections | Paginated lists |
| Payload Types | Mutation results |
| DataLoader | Batching related queries |
| Interfaces | Shared fields across types |
| Unions | Multiple possible return types |

---

## Related Skills

- `api-design` - General API patterns
- `rest-vs-graphql` - When to use each
- `websocket-patterns` - Real-time alternatives
