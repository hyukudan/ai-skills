---
name: react-best-practices
description: |
  React patterns, best practices, and performance optimization techniques.
  Use when building React applications, optimizing components, managing state,
  or implementing common UI patterns. Covers hooks, context, and modern React.
license: MIT
allowed-tools: Read Edit Bash
version: 1.0.0
tags: [react, javascript, frontend, hooks, components, state-management]
category: development/react
variables:
  react_version:
    type: string
    description: React version being used
    enum: [react18, react19]
    default: react18
  state_management:
    type: string
    description: State management approach
    enum: [useState, useReducer, context, zustand, redux]
    default: useState
---

# React Best Practices & Patterns

## Philosophy

**Components should be small, focused, and composable.** A component should do one thing well.

```
Good Component Design:
┌─────────────────────────────────────────┐
│  Single Responsibility                  │
│  Props are the API                      │
│  State is internal                      │
│  Side effects are explicit              │
│  Composition over inheritance           │
└─────────────────────────────────────────┘
```

---

## Component Patterns

### Functional Components (Standard)

```jsx
// Props interface for TypeScript
interface UserCardProps {
  user: {
    id: string;
    name: string;
    avatar?: string;
  };
  onSelect?: (id: string) => void;
  className?: string;
}

// Clean functional component
function UserCard({ user, onSelect, className }: UserCardProps) {
  const handleClick = () => {
    onSelect?.(user.id);
  };

  return (
    <div className={`user-card ${className ?? ''}`} onClick={handleClick}>
      {user.avatar && <img src={user.avatar} alt={user.name} />}
      <span>{user.name}</span>
    </div>
  );
}

// Default export for lazy loading support
export default UserCard;
```

### Compound Components Pattern

```jsx
// Parent provides context, children consume it
const TabsContext = createContext(null);

function Tabs({ children, defaultTab }) {
  const [activeTab, setActiveTab] = useState(defaultTab);

  return (
    <TabsContext.Provider value={{ activeTab, setActiveTab }}>
      <div className="tabs">{children}</div>
    </TabsContext.Provider>
  );
}

function TabList({ children }) {
  return <div className="tab-list">{children}</div>;
}

function Tab({ id, children }) {
  const { activeTab, setActiveTab } = useContext(TabsContext);

  return (
    <button
      className={activeTab === id ? 'active' : ''}
      onClick={() => setActiveTab(id)}
    >
      {children}
    </button>
  );
}

function TabPanel({ id, children }) {
  const { activeTab } = useContext(TabsContext);
  return activeTab === id ? <div className="tab-panel">{children}</div> : null;
}

// Attach sub-components
Tabs.List = TabList;
Tabs.Tab = Tab;
Tabs.Panel = TabPanel;

// Usage - clean, declarative API
<Tabs defaultTab="profile">
  <Tabs.List>
    <Tabs.Tab id="profile">Profile</Tabs.Tab>
    <Tabs.Tab id="settings">Settings</Tabs.Tab>
  </Tabs.List>
  <Tabs.Panel id="profile">Profile content</Tabs.Panel>
  <Tabs.Panel id="settings">Settings content</Tabs.Panel>
</Tabs>
```

### Render Props Pattern

```jsx
// Flexible data fetching component
function DataFetcher({ url, children }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch(url)
      .then(res => res.json())
      .then(setData)
      .catch(setError)
      .finally(() => setLoading(false));
  }, [url]);

  return children({ data, loading, error });
}

// Usage
<DataFetcher url="/api/users">
  {({ data, loading, error }) => {
    if (loading) return <Spinner />;
    if (error) return <Error message={error.message} />;
    return <UserList users={data} />;
  }}
</DataFetcher>
```

---

## Hooks Best Practices

### useState

```jsx
// BAD: Multiple related states
const [firstName, setFirstName] = useState('');
const [lastName, setLastName] = useState('');
const [email, setEmail] = useState('');

// GOOD: Group related state
const [formData, setFormData] = useState({
  firstName: '',
  lastName: '',
  email: '',
});

// Update with spread
setFormData(prev => ({ ...prev, email: newEmail }));

// For complex state, prefer useReducer
```

### useEffect

```jsx
// BAD: Missing dependencies, no cleanup
useEffect(() => {
  const handler = () => console.log(value);
  window.addEventListener('resize', handler);
}); // Runs every render, never cleans up!

// GOOD: Complete dependencies, proper cleanup
useEffect(() => {
  const handler = () => console.log(value);
  window.addEventListener('resize', handler);

  return () => {
    window.removeEventListener('resize', handler);
  };
}, [value]); // Only re-runs when value changes
```

### Custom Hooks

```jsx
// Encapsulate reusable logic
function useLocalStorage<T>(key: string, initialValue: T) {
  const [value, setValue] = useState<T>(() => {
    try {
      const stored = localStorage.getItem(key);
      return stored ? JSON.parse(stored) : initialValue;
    } catch {
      return initialValue;
    }
  });

  useEffect(() => {
    localStorage.setItem(key, JSON.stringify(value));
  }, [key, value]);

  return [value, setValue] as const;
}

// Debounce hook
function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedValue(value), delay);
    return () => clearTimeout(timer);
  }, [value, delay]);

  return debouncedValue;
}

// Previous value hook
function usePrevious<T>(value: T): T | undefined {
  const ref = useRef<T>();

  useEffect(() => {
    ref.current = value;
  }, [value]);

  return ref.current;
}
```

---

{% if state_management == 'useReducer' %}
## useReducer Pattern

```jsx
// Define action types
type Action =
  | { type: 'SET_LOADING' }
  | { type: 'SET_DATA'; payload: User[] }
  | { type: 'SET_ERROR'; payload: string }
  | { type: 'ADD_USER'; payload: User }
  | { type: 'REMOVE_USER'; payload: string };

// Define state shape
interface State {
  users: User[];
  loading: boolean;
  error: string | null;
}

const initialState: State = {
  users: [],
  loading: false,
  error: null,
};

// Pure reducer function
function userReducer(state: State, action: Action): State {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, loading: true, error: null };
    case 'SET_DATA':
      return { ...state, loading: false, users: action.payload };
    case 'SET_ERROR':
      return { ...state, loading: false, error: action.payload };
    case 'ADD_USER':
      return { ...state, users: [...state.users, action.payload] };
    case 'REMOVE_USER':
      return {
        ...state,
        users: state.users.filter(u => u.id !== action.payload),
      };
    default:
      return state;
  }
}

// Usage in component
function UserManager() {
  const [state, dispatch] = useReducer(userReducer, initialState);

  const loadUsers = async () => {
    dispatch({ type: 'SET_LOADING' });
    try {
      const users = await fetchUsers();
      dispatch({ type: 'SET_DATA', payload: users });
    } catch (e) {
      dispatch({ type: 'SET_ERROR', payload: e.message });
    }
  };

  return (/* ... */);
}
```
{% endif %}

{% if state_management == 'context' %}
## Context Pattern

```jsx
// Create typed context
interface AuthContextType {
  user: User | null;
  login: (credentials: Credentials) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | null>(null);

// Custom hook for type-safe access
function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}

// Provider component
function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check for existing session
    checkAuth().then(setUser).finally(() => setIsLoading(false));
  }, []);

  const login = async (credentials: Credentials) => {
    setIsLoading(true);
    try {
      const user = await authService.login(credentials);
      setUser(user);
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    authService.logout();
    setUser(null);
  };

  // Memoize value to prevent unnecessary re-renders
  const value = useMemo(
    () => ({ user, login, logout, isLoading }),
    [user, isLoading]
  );

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

// Usage
function ProfilePage() {
  const { user, logout } = useAuth();

  if (!user) return <Navigate to="/login" />;

  return (
    <div>
      <h1>Welcome, {user.name}</h1>
      <button onClick={logout}>Logout</button>
    </div>
  );
}
```
{% endif %}

{% if state_management == 'zustand' %}
## Zustand State Management

```jsx
import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

// Define store with TypeScript
interface CartStore {
  items: CartItem[];
  total: number;
  addItem: (item: Product) => void;
  removeItem: (id: string) => void;
  clearCart: () => void;
}

const useCartStore = create<CartStore>()(
  devtools(
    persist(
      (set, get) => ({
        items: [],
        total: 0,

        addItem: (product) => set((state) => {
          const existing = state.items.find(i => i.id === product.id);
          if (existing) {
            return {
              items: state.items.map(i =>
                i.id === product.id
                  ? { ...i, quantity: i.quantity + 1 }
                  : i
              ),
              total: state.total + product.price,
            };
          }
          return {
            items: [...state.items, { ...product, quantity: 1 }],
            total: state.total + product.price,
          };
        }),

        removeItem: (id) => set((state) => {
          const item = state.items.find(i => i.id === id);
          if (!item) return state;
          return {
            items: state.items.filter(i => i.id !== id),
            total: state.total - (item.price * item.quantity),
          };
        }),

        clearCart: () => set({ items: [], total: 0 }),
      }),
      { name: 'cart-storage' }
    )
  )
);

// Usage - auto-subscribes to changes
function CartButton() {
  const itemCount = useCartStore((state) => state.items.length);
  return <button>Cart ({itemCount})</button>;
}

function CartTotal() {
  const total = useCartStore((state) => state.total);
  return <span>${total.toFixed(2)}</span>;
}
```
{% endif %}

---

## Performance Optimization

### Memoization

```jsx
// Memoize expensive components
const ExpensiveList = memo(function ExpensiveList({ items, onSelect }) {
  return (
    <ul>
      {items.map(item => (
        <li key={item.id} onClick={() => onSelect(item.id)}>
          {item.name}
        </li>
      ))}
    </ul>
  );
});

// Memoize callbacks passed to children
function Parent() {
  const [count, setCount] = useState(0);

  // Without useCallback, this creates new function every render
  const handleSelect = useCallback((id: string) => {
    console.log('Selected:', id);
  }, []); // Empty deps = stable reference

  return (
    <>
      <button onClick={() => setCount(c => c + 1)}>Count: {count}</button>
      <ExpensiveList items={items} onSelect={handleSelect} />
    </>
  );
}

// Memoize expensive calculations
function DataTable({ data, filter }) {
  const filteredData = useMemo(() => {
    // Expensive filtering/sorting
    return data
      .filter(item => item.name.includes(filter))
      .sort((a, b) => a.name.localeCompare(b.name));
  }, [data, filter]); // Only recalculate when these change

  return <Table data={filteredData} />;
}
```

### Code Splitting

```jsx
import { lazy, Suspense } from 'react';

// Lazy load heavy components
const Dashboard = lazy(() => import('./Dashboard'));
const Analytics = lazy(() => import('./Analytics'));
const Settings = lazy(() => import('./Settings'));

function App() {
  return (
    <Suspense fallback={<LoadingSpinner />}>
      <Routes>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/analytics" element={<Analytics />} />
        <Route path="/settings" element={<Settings />} />
      </Routes>
    </Suspense>
  );
}

// Named exports require different syntax
const UserProfile = lazy(() =>
  import('./UserModule').then(module => ({ default: module.UserProfile }))
);
```

### Virtualization for Large Lists

```jsx
import { useVirtualizer } from '@tanstack/react-virtual';

function VirtualList({ items }) {
  const parentRef = useRef(null);

  const virtualizer = useVirtualizer({
    count: items.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 50, // Estimated row height
  });

  return (
    <div ref={parentRef} style={{ height: '400px', overflow: 'auto' }}>
      <div style={{ height: virtualizer.getTotalSize() }}>
        {virtualizer.getVirtualItems().map((virtualItem) => (
          <div
            key={virtualItem.key}
            style={{
              position: 'absolute',
              top: 0,
              transform: `translateY(${virtualItem.start}px)`,
              height: `${virtualItem.size}px`,
            }}
          >
            {items[virtualItem.index].name}
          </div>
        ))}
      </div>
    </div>
  );
}
```

---

{% if react_version == 'react19' %}
## React 19 Features

### use() Hook

```jsx
// Suspense-native data fetching
function UserProfile({ userPromise }) {
  const user = use(userPromise); // Suspends until resolved
  return <div>{user.name}</div>;
}

// Read context conditionally
function ThemeButton({ showTheme }) {
  if (showTheme) {
    const theme = use(ThemeContext);
    return <button style={{ color: theme.primary }}>Themed</button>;
  }
  return <button>Default</button>;
}
```

### Actions and useActionState

```jsx
// Form actions with built-in pending state
function ContactForm() {
  const [state, formAction, isPending] = useActionState(
    async (prevState, formData) => {
      const email = formData.get('email');
      const message = formData.get('message');

      try {
        await submitContact({ email, message });
        return { success: true };
      } catch (error) {
        return { error: error.message };
      }
    },
    { success: false, error: null }
  );

  return (
    <form action={formAction}>
      <input name="email" type="email" required />
      <textarea name="message" required />
      <button type="submit" disabled={isPending}>
        {isPending ? 'Sending...' : 'Send'}
      </button>
      {state.error && <p className="error">{state.error}</p>}
      {state.success && <p className="success">Message sent!</p>}
    </form>
  );
}
```

### useOptimistic

```jsx
function TodoList({ todos, addTodo }) {
  const [optimisticTodos, addOptimisticTodo] = useOptimistic(
    todos,
    (state, newTodo) => [...state, { ...newTodo, pending: true }]
  );

  const handleAdd = async (formData) => {
    const title = formData.get('title');
    const optimisticTodo = { id: crypto.randomUUID(), title };

    addOptimisticTodo(optimisticTodo);
    await addTodo(optimisticTodo); // Server request
  };

  return (
    <>
      <form action={handleAdd}>
        <input name="title" />
        <button>Add</button>
      </form>
      <ul>
        {optimisticTodos.map(todo => (
          <li key={todo.id} style={{ opacity: todo.pending ? 0.5 : 1 }}>
            {todo.title}
          </li>
        ))}
      </ul>
    </>
  );
}
```
{% endif %}

---

## Error Handling

### Error Boundaries

```jsx
import { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false };

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error('Error boundary caught:', error, info);
    // Log to error reporting service
    errorReporter.log(error, info.componentStack);
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback ?? (
        <div className="error-fallback">
          <h2>Something went wrong</h2>
          <button onClick={() => this.setState({ hasError: false })}>
            Try again
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

// Usage
<ErrorBoundary fallback={<ErrorPage />}>
  <Dashboard />
</ErrorBoundary>
```

---

## Testing Patterns

### Component Testing

```jsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

describe('LoginForm', () => {
  it('submits form with valid data', async () => {
    const onSubmit = vi.fn();
    render(<LoginForm onSubmit={onSubmit} />);

    // Use userEvent for realistic interactions
    await userEvent.type(screen.getByLabelText(/email/i), 'test@example.com');
    await userEvent.type(screen.getByLabelText(/password/i), 'password123');
    await userEvent.click(screen.getByRole('button', { name: /sign in/i }));

    await waitFor(() => {
      expect(onSubmit).toHaveBeenCalledWith({
        email: 'test@example.com',
        password: 'password123',
      });
    });
  });

  it('shows validation errors', async () => {
    render(<LoginForm onSubmit={vi.fn()} />);

    await userEvent.click(screen.getByRole('button', { name: /sign in/i }));

    expect(screen.getByText(/email is required/i)).toBeInTheDocument();
  });
});
```

### Hook Testing

```jsx
import { renderHook, act } from '@testing-library/react';

describe('useCounter', () => {
  it('increments counter', () => {
    const { result } = renderHook(() => useCounter(0));

    act(() => {
      result.current.increment();
    });

    expect(result.current.count).toBe(1);
  });

  it('resets to initial value', () => {
    const { result } = renderHook(() => useCounter(5));

    act(() => {
      result.current.increment();
      result.current.reset();
    });

    expect(result.current.count).toBe(5);
  });
});
```

---

## React Checklist

### Component Design
- [ ] Single responsibility - one component, one job
- [ ] Props are the public API, well-typed
- [ ] State is minimal and derived when possible
- [ ] Side effects are in useEffect with proper cleanup

### Performance
- [ ] Heavy components wrapped in memo()
- [ ] Callbacks memoized with useCallback
- [ ] Expensive calculations use useMemo
- [ ] Large lists are virtualized
- [ ] Routes are lazy-loaded

### State Management
- [ ] Local state for UI-only state
- [ ] Context for cross-cutting concerns (auth, theme)
- [ ] External store for complex/shared state
- [ ] Server state with React Query/SWR

### Accessibility
- [ ] Semantic HTML elements
- [ ] ARIA attributes where needed
- [ ] Keyboard navigation works
- [ ] Focus management on route changes
