---
name: react-native-patterns
description: |
  React Native patterns for cross-platform mobile development. Covers
  navigation, state management, native modules, performance optimization,
  and platform-specific code.
license: MIT
allowed-tools: Read Edit Bash
version: 1.0.0
tags: [react-native, mobile, ios, android, cross-platform]
category: mobile/react-native
trigger_phrases:
  - "React Native"
  - "mobile app"
  - "cross-platform"
  - "Expo"
  - "native module"
  - "mobile navigation"
variables:
  setup:
    type: string
    description: Project setup type
    enum: [expo, bare]
    default: expo
---

# React Native Patterns Guide

## Core Philosophy

**React Native is "learn once, write anywhere" not "write once, run anywhere."** Embrace platform differences while sharing logic.

> "The best cross-platform code respects each platform's conventions."

---

## Project Structure

```
src/
├── components/           # Shared UI components
│   ├── Button/
│   │   ├── Button.tsx
│   │   ├── Button.styles.ts
│   │   └── index.ts
│   └── ...
├── screens/             # Screen components
│   ├── HomeScreen/
│   └── ProfileScreen/
├── navigation/          # Navigation config
│   ├── RootNavigator.tsx
│   └── types.ts
├── hooks/               # Custom hooks
├── services/            # API, storage
├── store/               # State management
├── utils/               # Helpers
├── constants/           # Theme, config
└── types/               # TypeScript types
```

---

## 1. Navigation (React Navigation)

### Stack Navigator

```tsx
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { NavigationContainer } from '@react-navigation/native';

// Type-safe navigation
type RootStackParamList = {
  Home: undefined;
  Profile: { userId: string };
  Settings: undefined;
};

const Stack = createNativeStackNavigator<RootStackParamList>();

function RootNavigator() {
  return (
    <NavigationContainer>
      <Stack.Navigator
        initialRouteName="Home"
        screenOptions={{
          headerShown: true,
          headerBackTitleVisible: false,
        }}
      >
        <Stack.Screen
          name="Home"
          component={HomeScreen}
          options={{ title: 'Home' }}
        />
        <Stack.Screen
          name="Profile"
          component={ProfileScreen}
          options={({ route }) => ({
            title: `Profile: ${route.params.userId}`,
          })}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
```

### Tab Navigator

```tsx
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Ionicons } from '@expo/vector-icons';

const Tab = createBottomTabNavigator();

function TabNavigator() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          const icons: Record<string, string> = {
            Home: focused ? 'home' : 'home-outline',
            Search: focused ? 'search' : 'search-outline',
            Profile: focused ? 'person' : 'person-outline',
          };
          return <Ionicons name={icons[route.name]} size={size} color={color} />;
        },
        tabBarActiveTintColor: '#007AFF',
        tabBarInactiveTintColor: 'gray',
      })}
    >
      <Tab.Screen name="Home" component={HomeScreen} />
      <Tab.Screen name="Search" component={SearchScreen} />
      <Tab.Screen name="Profile" component={ProfileScreen} />
    </Tab.Navigator>
  );
}
```

### Navigation Hooks

```tsx
import { useNavigation, useRoute } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';

// Custom typed hook
export function useAppNavigation() {
  return useNavigation<NativeStackNavigationProp<RootStackParamList>>();
}

// Usage
function MyComponent() {
  const navigation = useAppNavigation();

  const goToProfile = (userId: string) => {
    navigation.navigate('Profile', { userId });
  };

  const goBack = () => {
    if (navigation.canGoBack()) {
      navigation.goBack();
    }
  };
}
```

### Deep Linking

```tsx
const linking = {
  prefixes: ['myapp://', 'https://myapp.com'],
  config: {
    screens: {
      Home: '',
      Profile: 'user/:userId',
      Settings: 'settings',
    },
  },
};

<NavigationContainer linking={linking}>
  {/* ... */}
</NavigationContainer>
```

---

## 2. State Management

### React Context + Hooks

```tsx
import React, { createContext, useContext, useReducer, ReactNode } from 'react';

// Types
interface User {
  id: string;
  name: string;
}

interface AuthState {
  user: User | null;
  isLoading: boolean;
}

type AuthAction =
  | { type: 'SET_USER'; payload: User }
  | { type: 'LOGOUT' }
  | { type: 'SET_LOADING'; payload: boolean };

// Reducer
function authReducer(state: AuthState, action: AuthAction): AuthState {
  switch (action.type) {
    case 'SET_USER':
      return { ...state, user: action.payload, isLoading: false };
    case 'LOGOUT':
      return { ...state, user: null };
    case 'SET_LOADING':
      return { ...state, isLoading: action.payload };
    default:
      return state;
  }
}

// Context
const AuthContext = createContext<{
  state: AuthState;
  dispatch: React.Dispatch<AuthAction>;
} | null>(null);

// Provider
export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(authReducer, {
    user: null,
    isLoading: true,
  });

  return (
    <AuthContext.Provider value={{ state, dispatch }}>
      {children}
    </AuthContext.Provider>
  );
}

// Hook
export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}
```

### Zustand (Recommended)

```tsx
import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import AsyncStorage from '@react-native-async-storage/async-storage';

interface AuthStore {
  user: User | null;
  token: string | null;
  setUser: (user: User) => void;
  setToken: (token: string) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthStore>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      setUser: (user) => set({ user }),
      setToken: (token) => set({ token }),
      logout: () => set({ user: null, token: null }),
    }),
    {
      name: 'auth-storage',
      storage: createJSONStorage(() => AsyncStorage),
    }
  )
);

// Usage
function ProfileScreen() {
  const user = useAuthStore((state) => state.user);
  const logout = useAuthStore((state) => state.logout);

  return (
    <View>
      <Text>{user?.name}</Text>
      <Button onPress={logout} title="Logout" />
    </View>
  );
}
```

---

## 3. API and Data Fetching

### React Query Setup

```tsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      retry: 2,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <RootNavigator />
    </QueryClientProvider>
  );
}
```

### API Hooks

```tsx
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

// Fetch hook
export function useUser(userId: string) {
  return useQuery({
    queryKey: ['user', userId],
    queryFn: () => api.getUser(userId),
    enabled: !!userId,
  });
}

// Mutation hook
export function useUpdateProfile() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: UpdateProfileInput) => api.updateProfile(data),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['user'] });
    },
  });
}

// Usage
function ProfileScreen() {
  const { data: user, isLoading, error } = useUser('123');
  const updateProfile = useUpdateProfile();

  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorMessage error={error} />;

  return (
    <ProfileForm
      user={user}
      onSubmit={(data) => updateProfile.mutate(data)}
      isSubmitting={updateProfile.isPending}
    />
  );
}
```

### API Client

```tsx
const API_URL = 'https://api.myapp.com';

class ApiClient {
  private token: string | null = null;

  setToken(token: string | null) {
    this.token = token;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...(this.token && { Authorization: `Bearer ${this.token}` }),
      ...options.headers,
    };

    const response = await fetch(`${API_URL}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new ApiError(response.status, error.message);
    }

    return response.json();
  }

  getUser(id: string) {
    return this.request<User>(`/users/${id}`);
  }

  updateProfile(data: UpdateProfileInput) {
    return this.request<User>('/profile', {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }
}

export const api = new ApiClient();
```

---

## 4. Styling Patterns

### StyleSheet

```tsx
import { StyleSheet, View, Text } from 'react-native';

function Card({ title, children }: CardProps) {
  return (
    <View style={styles.card}>
      <Text style={styles.title}>{title}</Text>
      {children}
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3, // Android shadow
  },
  title: {
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 8,
  },
});
```

### Theme System

```tsx
// constants/theme.ts
export const theme = {
  colors: {
    primary: '#007AFF',
    secondary: '#5856D6',
    success: '#34C759',
    error: '#FF3B30',
    background: '#F2F2F7',
    surface: '#FFFFFF',
    text: '#000000',
    textSecondary: '#8E8E93',
  },
  spacing: {
    xs: 4,
    sm: 8,
    md: 16,
    lg: 24,
    xl: 32,
  },
  borderRadius: {
    sm: 4,
    md: 8,
    lg: 12,
    full: 9999,
  },
  typography: {
    h1: { fontSize: 32, fontWeight: '700' as const },
    h2: { fontSize: 24, fontWeight: '600' as const },
    body: { fontSize: 16, fontWeight: '400' as const },
    caption: { fontSize: 12, fontWeight: '400' as const },
  },
};

// Typed theme hook
export type Theme = typeof theme;

// Usage
const styles = StyleSheet.create({
  container: {
    padding: theme.spacing.md,
    backgroundColor: theme.colors.background,
  },
});
```

---

## 5. Platform-Specific Code

### Platform Module

```tsx
import { Platform } from 'react-native';

const styles = StyleSheet.create({
  shadow: Platform.select({
    ios: {
      shadowColor: '#000',
      shadowOffset: { width: 0, height: 2 },
      shadowOpacity: 0.1,
      shadowRadius: 4,
    },
    android: {
      elevation: 4,
    },
  }),
});

// Conditional rendering
{Platform.OS === 'ios' && <StatusBar barStyle="dark-content" />}

// Platform version check
if (Platform.OS === 'android' && Platform.Version >= 31) {
  // Android 12+ specific code
}
```

### Platform-Specific Files

```
components/
├── Button/
│   ├── Button.tsx         # Shared logic
│   ├── Button.ios.tsx     # iOS-specific
│   └── Button.android.tsx # Android-specific
```

---

## 6. Lists and Performance

### FlatList Optimization

```tsx
import { FlatList, View, Text } from 'react-native';
import { useCallback, memo } from 'react';

interface Item {
  id: string;
  title: string;
}

// Memoized item component
const ListItem = memo(({ item }: { item: Item }) => (
  <View style={styles.item}>
    <Text>{item.title}</Text>
  </View>
));

function OptimizedList({ data }: { data: Item[] }) {
  // Stable key extractor
  const keyExtractor = useCallback((item: Item) => item.id, []);

  // Memoized render function
  const renderItem = useCallback(
    ({ item }: { item: Item }) => <ListItem item={item} />,
    []
  );

  // Item layout for fixed height items
  const getItemLayout = useCallback(
    (_: any, index: number) => ({
      length: ITEM_HEIGHT,
      offset: ITEM_HEIGHT * index,
      index,
    }),
    []
  );

  return (
    <FlatList
      data={data}
      keyExtractor={keyExtractor}
      renderItem={renderItem}
      getItemLayout={getItemLayout}
      // Performance props
      removeClippedSubviews={true}
      maxToRenderPerBatch={10}
      windowSize={5}
      initialNumToRender={10}
      // Pull to refresh
      onRefresh={handleRefresh}
      refreshing={isRefreshing}
      // Load more
      onEndReached={handleLoadMore}
      onEndReachedThreshold={0.5}
      ListFooterComponent={isLoadingMore ? <Spinner /> : null}
    />
  );
}
```

### FlashList (Better Performance)

```tsx
import { FlashList } from '@shopify/flash-list';

function HighPerformanceList({ data }: { data: Item[] }) {
  return (
    <FlashList
      data={data}
      renderItem={({ item }) => <ListItem item={item} />}
      estimatedItemSize={80}
      keyExtractor={(item) => item.id}
    />
  );
}
```

---

## 7. Common Patterns

### Safe Area Handling

```tsx
import { SafeAreaProvider, useSafeAreaInsets } from 'react-native-safe-area-context';

function App() {
  return (
    <SafeAreaProvider>
      <RootNavigator />
    </SafeAreaProvider>
  );
}

function ScreenWithSafeArea() {
  const insets = useSafeAreaInsets();

  return (
    <View style={{ paddingTop: insets.top, paddingBottom: insets.bottom }}>
      {/* Content */}
    </View>
  );
}
```

### Keyboard Handling

```tsx
import { KeyboardAvoidingView, Platform } from 'react-native';

function FormScreen() {
  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      style={{ flex: 1 }}
    >
      <ScrollView keyboardShouldPersistTaps="handled">
        {/* Form inputs */}
      </ScrollView>
    </KeyboardAvoidingView>
  );
}
```

### Error Boundaries

```tsx
import React, { Component, ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
}

class ErrorBoundary extends Component<Props, State> {
  state = { hasError: false };

  static getDerivedStateFromError(): State {
    return { hasError: true };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    // Log to error reporting service
    console.error('Error caught:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || <ErrorFallback />;
    }
    return this.props.children;
  }
}
```

---

## Quick Reference

### Common Libraries

| Purpose | Library |
|---------|---------|
| Navigation | @react-navigation/native |
| State | zustand, @tanstack/react-query |
| Forms | react-hook-form |
| Icons | @expo/vector-icons |
| Storage | @react-native-async-storage/async-storage |
| Lists | @shopify/flash-list |

### Performance Checklist

- [ ] Use `memo()` for list items
- [ ] Memoize callbacks with `useCallback()`
- [ ] Use `getItemLayout` for fixed-height lists
- [ ] Enable `removeClippedSubviews`
- [ ] Avoid inline styles/objects in render
- [ ] Use FlashList for long lists

---

## Related Skills

- `mobile-performance` - Deep performance optimization
- `react-patterns` - React fundamentals
- `typescript-patterns` - TypeScript patterns
