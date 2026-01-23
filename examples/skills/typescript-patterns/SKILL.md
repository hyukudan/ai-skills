---
name: typescript-patterns
description: |
  TypeScript patterns, best practices, and advanced type techniques.
  Use when writing TypeScript code, designing type-safe APIs, or improving
  type safety in existing codebases. Covers utility types, generics, and patterns.
license: MIT
allowed-tools: Read Edit Bash
version: 1.0.0
tags: [typescript, types, generics, patterns, type-safety]
category: development/typescript
variables:
  strictness:
    type: string
    description: TypeScript strictness level
    enum: [strict, moderate, loose]
    default: strict
  use_case:
    type: string
    description: Primary use case
    enum: [general, api, react, library]
    default: general
---

# TypeScript Patterns & Best Practices

## Philosophy

**Types are documentation that the compiler verifies.** Good types make invalid states unrepresentable.

```typescript
// BAD: Valid TypeScript, but allows invalid states
interface User {
  name: string;
  email: string;
  isVerified: boolean;
  verifiedAt: Date | null; // Can be null even when isVerified is true!
}

// GOOD: Type system enforces consistency
type UnverifiedUser = {
  name: string;
  email: string;
  status: 'unverified';
};

type VerifiedUser = {
  name: string;
  email: string;
  status: 'verified';
  verifiedAt: Date;
};

type User = UnverifiedUser | VerifiedUser;
```

---

## Essential Utility Types

### Built-in Utility Types

```typescript
interface User {
  id: number;
  name: string;
  email: string;
  role: 'admin' | 'user';
}

// Partial - all properties optional
type UserUpdate = Partial<User>;
// { id?: number; name?: string; email?: string; role?: 'admin' | 'user'; }

// Required - all properties required
type CompleteUser = Required<User>;

// Pick - select specific properties
type UserCredentials = Pick<User, 'email' | 'role'>;
// { email: string; role: 'admin' | 'user'; }

// Omit - exclude specific properties
type PublicUser = Omit<User, 'email'>;
// { id: number; name: string; role: 'admin' | 'user'; }

// Readonly - immutable properties
type ImmutableUser = Readonly<User>;

// Record - typed object with specific keys
type UserRoles = Record<'admin' | 'user' | 'guest', string[]>;
// { admin: string[]; user: string[]; guest: string[]; }

// Extract - extract matching types from union
type AdminRole = Extract<User['role'], 'admin'>;
// 'admin'

// Exclude - remove matching types from union
type NonAdminRole = Exclude<User['role'], 'admin'>;
// 'user'

// NonNullable - remove null and undefined
type DefinitelyString = NonNullable<string | null | undefined>;
// string

// ReturnType - get function return type
function getUser() { return { id: 1, name: 'Alice' }; }
type UserResult = ReturnType<typeof getUser>;
// { id: number; name: string; }

// Parameters - get function parameters as tuple
function createUser(name: string, age: number) { }
type CreateUserParams = Parameters<typeof createUser>;
// [string, number]
```

### Custom Utility Types

```typescript
// DeepPartial - recursive partial
type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};

// DeepReadonly - recursive readonly
type DeepReadonly<T> = {
  readonly [P in keyof T]: T[P] extends object ? DeepReadonly<T[P]> : T[P];
};

// Nullable - add null to type
type Nullable<T> = T | null;

// ValueOf - get union of object values
type ValueOf<T> = T[keyof T];

// Example
interface Config {
  host: string;
  port: number;
}
type ConfigValue = ValueOf<Config>; // string | number
```

---

## Generics Patterns

### Basic Generics

```typescript
// Generic function
function identity<T>(value: T): T {
  return value;
}

// Generic with constraint
function getProperty<T, K extends keyof T>(obj: T, key: K): T[K] {
  return obj[key];
}

// Generic interface
interface Repository<T> {
  find(id: string): Promise<T | null>;
  findAll(): Promise<T[]>;
  create(item: Omit<T, 'id'>): Promise<T>;
  update(id: string, item: Partial<T>): Promise<T>;
  delete(id: string): Promise<void>;
}

// Generic class
class ApiClient<T> {
  constructor(private baseUrl: string) {}

  async get(id: string): Promise<T> {
    const response = await fetch(`${this.baseUrl}/${id}`);
    return response.json();
  }
}
```

### Advanced Generic Patterns

```typescript
// Conditional types
type IsString<T> = T extends string ? true : false;
type A = IsString<string>;  // true
type B = IsString<number>;  // false

// Infer keyword - extract types
type UnwrapPromise<T> = T extends Promise<infer U> ? U : T;
type Result = UnwrapPromise<Promise<string>>; // string

// Array element type
type ArrayElement<T> = T extends (infer E)[] ? E : never;
type Item = ArrayElement<string[]>; // string

// Function argument types
type FirstArgument<T> = T extends (arg: infer A, ...args: any[]) => any ? A : never;

// Mapped types with conditional
type NullableProperties<T> = {
  [K in keyof T]: T[K] extends object ? T[K] | null : T[K];
};
```

---

## Discriminated Unions

### Pattern: State Machines

```typescript
// API request states
type RequestState<T> =
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'success'; data: T }
  | { status: 'error'; error: Error };

function handleRequest<T>(state: RequestState<T>) {
  switch (state.status) {
    case 'idle':
      return 'Ready to fetch';
    case 'loading':
      return 'Loading...';
    case 'success':
      return `Data: ${JSON.stringify(state.data)}`; // TypeScript knows data exists
    case 'error':
      return `Error: ${state.error.message}`; // TypeScript knows error exists
  }
}
```

### Pattern: Event System

```typescript
type AppEvent =
  | { type: 'USER_LOGIN'; payload: { userId: string; timestamp: Date } }
  | { type: 'USER_LOGOUT'; payload: { userId: string } }
  | { type: 'PAGE_VIEW'; payload: { path: string; referrer?: string } }
  | { type: 'PURCHASE'; payload: { productId: string; amount: number } };

function trackEvent(event: AppEvent) {
  switch (event.type) {
    case 'USER_LOGIN':
      console.log(`User ${event.payload.userId} logged in at ${event.payload.timestamp}`);
      break;
    case 'PURCHASE':
      console.log(`Purchase: ${event.payload.productId} for $${event.payload.amount}`);
      break;
    // TypeScript ensures all cases are handled
  }
}

// Exhaustive check helper
function assertNever(x: never): never {
  throw new Error(`Unexpected value: ${x}`);
}
```

---

{% if use_case == 'api' %}
## API Type Patterns

### Typed API Client

```typescript
// Define API routes with types
interface ApiRoutes {
  '/users': {
    GET: { response: User[] };
    POST: { body: CreateUserDto; response: User };
  };
  '/users/:id': {
    GET: { response: User };
    PUT: { body: UpdateUserDto; response: User };
    DELETE: { response: void };
  };
}

// Type-safe fetch wrapper
type HttpMethod = 'GET' | 'POST' | 'PUT' | 'DELETE';

async function api<
  Path extends keyof ApiRoutes,
  Method extends keyof ApiRoutes[Path] & HttpMethod
>(
  path: Path,
  method: Method,
  options?: ApiRoutes[Path][Method] extends { body: infer B } ? { body: B } : never
): Promise<ApiRoutes[Path][Method] extends { response: infer R } ? R : never> {
  // Implementation
}

// Usage - fully typed!
const users = await api('/users', 'GET');           // User[]
const newUser = await api('/users', 'POST', { body: { name: 'Alice' } }); // User
```

### Zod Schema Integration

```typescript
import { z } from 'zod';

// Define schema
const UserSchema = z.object({
  id: z.string().uuid(),
  name: z.string().min(1),
  email: z.string().email(),
  role: z.enum(['admin', 'user']),
  createdAt: z.date(),
});

// Infer TypeScript type from schema
type User = z.infer<typeof UserSchema>;

// Validate at runtime, get typed result
function parseUser(data: unknown): User {
  return UserSchema.parse(data);
}
```
{% endif %}

{% if use_case == 'react' %}
## React TypeScript Patterns

### Typed Components

```typescript
// Props interface
interface ButtonProps {
  variant: 'primary' | 'secondary' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  onClick?: (event: React.MouseEvent<HTMLButtonElement>) => void;
  children: React.ReactNode;
}

// Function component with typed props
const Button: React.FC<ButtonProps> = ({
  variant,
  size = 'md',
  disabled = false,
  onClick,
  children,
}) => {
  return (
    <button
      className={`btn btn-${variant} btn-${size}`}
      disabled={disabled}
      onClick={onClick}
    >
      {children}
    </button>
  );
};

// Generic component
interface ListProps<T> {
  items: T[];
  renderItem: (item: T, index: number) => React.ReactNode;
  keyExtractor: (item: T) => string;
}

function List<T>({ items, renderItem, keyExtractor }: ListProps<T>) {
  return (
    <ul>
      {items.map((item, index) => (
        <li key={keyExtractor(item)}>{renderItem(item, index)}</li>
      ))}
    </ul>
  );
}
```

### Typed Hooks

```typescript
// Typed useState
const [user, setUser] = useState<User | null>(null);

// Typed useReducer
type State = { count: number; error: string | null };
type Action =
  | { type: 'increment' }
  | { type: 'decrement' }
  | { type: 'error'; payload: string };

function reducer(state: State, action: Action): State {
  switch (action.type) {
    case 'increment':
      return { ...state, count: state.count + 1 };
    case 'decrement':
      return { ...state, count: state.count - 1 };
    case 'error':
      return { ...state, error: action.payload };
  }
}

// Custom hook with generics
function useFetch<T>(url: string): {
  data: T | null;
  loading: boolean;
  error: Error | null;
} {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    fetch(url)
      .then(res => res.json())
      .then(setData)
      .catch(setError)
      .finally(() => setLoading(false));
  }, [url]);

  return { data, loading, error };
}
```
{% endif %}

---

## Type Guards

### Custom Type Guards

```typescript
// Type predicate
function isString(value: unknown): value is string {
  return typeof value === 'string';
}

// Discriminated union guard
function isSuccessResponse<T>(
  response: RequestState<T>
): response is { status: 'success'; data: T } {
  return response.status === 'success';
}

// Array type guard
function isStringArray(value: unknown): value is string[] {
  return Array.isArray(value) && value.every(item => typeof item === 'string');
}

// Object shape guard
function isUser(value: unknown): value is User {
  return (
    typeof value === 'object' &&
    value !== null &&
    'id' in value &&
    'name' in value &&
    'email' in value
  );
}

// Usage
function processValue(value: unknown) {
  if (isString(value)) {
    console.log(value.toUpperCase()); // TypeScript knows it's a string
  }
}
```

### Assertion Functions

```typescript
// Assert function - throws if condition fails
function assertIsString(value: unknown): asserts value is string {
  if (typeof value !== 'string') {
    throw new Error(`Expected string, got ${typeof value}`);
  }
}

// Non-null assertion function
function assertDefined<T>(value: T | null | undefined): asserts value is T {
  if (value === null || value === undefined) {
    throw new Error('Value must be defined');
  }
}

// Usage
function processInput(input: unknown) {
  assertIsString(input);
  // TypeScript now knows input is string
  console.log(input.toLowerCase());
}
```

---

{% if strictness == 'strict' %}
## Strict Mode Best Practices

### tsconfig.json Strict Settings

```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true,
    "strictBindCallApply": true,
    "strictPropertyInitialization": true,
    "noImplicitThis": true,
    "alwaysStrict": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "noImplicitOverride": true
  }
}
```

### Handling Strict Null Checks

```typescript
// BAD: Assumes value exists
function getLength(str: string | null) {
  return str.length; // Error: str might be null
}

// GOOD: Handle null case
function getLength(str: string | null): number {
  if (str === null) return 0;
  return str.length;
}

// GOOD: Optional chaining + nullish coalescing
function getLength(str: string | null): number {
  return str?.length ?? 0;
}
```
{% endif %}

---

## Common Patterns

### Builder Pattern

```typescript
class QueryBuilder<T> {
  private query: Partial<T> = {};

  where<K extends keyof T>(key: K, value: T[K]): this {
    this.query[key] = value;
    return this;
  }

  build(): Partial<T> {
    return { ...this.query };
  }
}

// Usage
interface User { name: string; age: number; city: string; }

const query = new QueryBuilder<User>()
  .where('name', 'Alice')  // Type-safe: only User keys allowed
  .where('age', 30)        // Type-safe: value must match key's type
  .build();
```

### Factory Pattern

```typescript
interface Logger {
  log(message: string): void;
}

class ConsoleLogger implements Logger {
  log(message: string) { console.log(message); }
}

class FileLogger implements Logger {
  log(message: string) { /* write to file */ }
}

type LoggerType = 'console' | 'file';

function createLogger(type: LoggerType): Logger {
  const loggers: Record<LoggerType, () => Logger> = {
    console: () => new ConsoleLogger(),
    file: () => new FileLogger(),
  };
  return loggers[type]();
}
```

---

## TypeScript Checklist

### Types
- [ ] Avoid `any` - use `unknown` for truly unknown types
- [ ] Use discriminated unions for state
- [ ] Prefer interfaces for objects, types for unions
- [ ] Use `readonly` for immutable data

### Functions
- [ ] Explicit return types for public APIs
- [ ] Use generics to maintain type relationships
- [ ] Narrow types with guards, not assertions

### Configuration
- [ ] Enable strict mode
- [ ] Enable noUncheckedIndexedAccess
- [ ] Configure path aliases for clean imports
