---
name: authentication-patterns
description: |
  Authentication and authorization patterns for web applications.
  Use when implementing user authentication, session management, OAuth flows,
  JWT tokens, or role-based access control (RBAC).
license: MIT
allowed-tools: Read Edit Bash Grep
version: 1.0.0
tags: [auth, security, jwt, oauth, session, rbac]
category: development/security
triggers:
  - authentication
  - authorization
  - login
  - logout
  - session
  - jwt
  - oauth
  - rbac
  - permissions
  - access control
  - password
  - token
variables:
  auth_type:
    type: string
    description: Authentication mechanism
    enum: [jwt, session, oauth2]
    default: jwt
  framework:
    type: string
    description: Web framework
    enum: [fastapi, express, nextjs]
    default: fastapi
---

# Authentication Patterns

## Authentication vs Authorization

```
Authentication (AuthN): WHO are you?
  → Verify identity (login, tokens, credentials)

Authorization (AuthZ): WHAT can you do?
  → Check permissions (roles, scopes, policies)
```

---

{% if auth_type == "jwt" %}
## JWT Authentication

### Token Structure

```
Header.Payload.Signature

eyJhbGciOiJIUzI1NiJ9.      ← Header (algorithm)
eyJzdWIiOiIxMjMiLCJleHAiOjE3MDQwNjcyMDB9.  ← Payload (claims)
SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c  ← Signature
```

### Token Payload (Claims)

```json
{
  "sub": "user_123",           // Subject (user ID)
  "iat": 1704067200,           // Issued at
  "exp": 1704153600,           // Expiration (24h later)
  "iss": "api.example.com",    // Issuer
  "aud": "app.example.com",    // Audience
  "scope": "read write",       // Permissions
  "role": "admin"              // Custom claims
}
```

{% if framework == "fastapi" %}
### FastAPI Implementation

```python
from datetime import datetime, timedelta
from typing import Optional
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

# Configuration
SECRET_KEY = "your-secret-key"  # Use env var in production!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE = timedelta(hours=1)
REFRESH_TOKEN_EXPIRE = timedelta(days=7)

security = HTTPBearer()

class TokenPayload(BaseModel):
    sub: str
    exp: datetime
    scope: str = ""
    role: str = "user"

def create_access_token(user_id: str, role: str = "user") -> str:
    """Create JWT access token."""
    payload = {
        "sub": user_id,
        "exp": datetime.utcnow() + ACCESS_TOKEN_EXPIRE,
        "iat": datetime.utcnow(),
        "scope": "read write",
        "role": role,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(user_id: str) -> str:
    """Create longer-lived refresh token."""
    payload = {
        "sub": user_id,
        "exp": datetime.utcnow() + REFRESH_TOKEN_EXPIRE,
        "type": "refresh",
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> TokenPayload:
    """Validate JWT and return user info."""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return TokenPayload(**payload)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Role-based access control
def require_role(required_role: str):
    """Dependency to check user role."""
    async def role_checker(user: TokenPayload = Depends(get_current_user)):
        if user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{required_role}' required"
            )
        return user
    return role_checker

# Usage in endpoints
@app.post("/login")
async def login(email: str, password: str):
    user = await authenticate_user(email, password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {
        "access_token": create_access_token(user.id, user.role),
        "refresh_token": create_refresh_token(user.id),
        "token_type": "bearer",
    }

@app.get("/me")
async def get_me(user: TokenPayload = Depends(get_current_user)):
    return {"user_id": user.sub, "role": user.role}

@app.get("/admin")
async def admin_only(user: TokenPayload = Depends(require_role("admin"))):
    return {"message": "Admin access granted"}

@app.post("/refresh")
async def refresh_token(refresh_token: str):
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        user_id = payload["sub"]
        user = await get_user(user_id)
        return {
            "access_token": create_access_token(user.id, user.role),
            "token_type": "bearer",
        }
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
```

{% elif framework == "express" %}
### Express.js Implementation

```typescript
import jwt from 'jsonwebtoken';
import { Request, Response, NextFunction } from 'express';

const SECRET_KEY = process.env.JWT_SECRET!;
const ACCESS_TOKEN_EXPIRE = '1h';
const REFRESH_TOKEN_EXPIRE = '7d';

interface TokenPayload {
  sub: string;
  role: string;
  scope: string;
}

function createAccessToken(userId: string, role: string = 'user'): string {
  return jwt.sign(
    { sub: userId, role, scope: 'read write' },
    SECRET_KEY,
    { expiresIn: ACCESS_TOKEN_EXPIRE }
  );
}

function createRefreshToken(userId: string): string {
  return jwt.sign(
    { sub: userId, type: 'refresh' },
    SECRET_KEY,
    { expiresIn: REFRESH_TOKEN_EXPIRE }
  );
}

// Middleware
function authenticate(req: Request, res: Response, next: NextFunction) {
  const authHeader = req.headers.authorization;
  if (!authHeader?.startsWith('Bearer ')) {
    return res.status(401).json({ error: 'Missing token' });
  }

  const token = authHeader.split(' ')[1];
  try {
    const payload = jwt.verify(token, SECRET_KEY) as TokenPayload;
    req.user = payload;
    next();
  } catch (err) {
    if (err instanceof jwt.TokenExpiredError) {
      return res.status(401).json({ error: 'Token expired' });
    }
    return res.status(401).json({ error: 'Invalid token' });
  }
}

function requireRole(role: string) {
  return (req: Request, res: Response, next: NextFunction) => {
    if (req.user?.role !== role) {
      return res.status(403).json({ error: `Role '${role}' required` });
    }
    next();
  };
}

// Routes
app.post('/login', async (req, res) => {
  const { email, password } = req.body;
  const user = await authenticateUser(email, password);

  if (!user) {
    return res.status(401).json({ error: 'Invalid credentials' });
  }

  res.json({
    access_token: createAccessToken(user.id, user.role),
    refresh_token: createRefreshToken(user.id),
    token_type: 'bearer',
  });
});

app.get('/me', authenticate, (req, res) => {
  res.json({ user_id: req.user.sub, role: req.user.role });
});

app.get('/admin', authenticate, requireRole('admin'), (req, res) => {
  res.json({ message: 'Admin access granted' });
});
```

{% elif framework == "nextjs" %}
### Next.js Implementation

```typescript
// lib/auth.ts
import jwt from 'jsonwebtoken';
import { cookies } from 'next/headers';
import { NextRequest, NextResponse } from 'next/server';

const SECRET_KEY = process.env.JWT_SECRET!;

interface TokenPayload {
  sub: string;
  role: string;
  exp: number;
}

export function createToken(userId: string, role: string): string {
  return jwt.sign(
    { sub: userId, role },
    SECRET_KEY,
    { expiresIn: '1h' }
  );
}

export function verifyToken(token: string): TokenPayload | null {
  try {
    return jwt.verify(token, SECRET_KEY) as TokenPayload;
  } catch {
    return null;
  }
}

export async function getUser(): Promise<TokenPayload | null> {
  const cookieStore = cookies();
  const token = cookieStore.get('auth-token')?.value;
  if (!token) return null;
  return verifyToken(token);
}

// Middleware (middleware.ts)
export function middleware(request: NextRequest) {
  const token = request.cookies.get('auth-token')?.value;

  // Protected routes
  if (request.nextUrl.pathname.startsWith('/dashboard')) {
    if (!token || !verifyToken(token)) {
      return NextResponse.redirect(new URL('/login', request.url));
    }
  }

  // Admin routes
  if (request.nextUrl.pathname.startsWith('/admin')) {
    const payload = token ? verifyToken(token) : null;
    if (payload?.role !== 'admin') {
      return NextResponse.redirect(new URL('/unauthorized', request.url));
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/dashboard/:path*', '/admin/:path*'],
};

// app/api/login/route.ts
export async function POST(request: Request) {
  const { email, password } = await request.json();
  const user = await authenticateUser(email, password);

  if (!user) {
    return Response.json({ error: 'Invalid credentials' }, { status: 401 });
  }

  const token = createToken(user.id, user.role);

  const response = Response.json({ success: true });
  response.headers.set(
    'Set-Cookie',
    `auth-token=${token}; HttpOnly; Secure; SameSite=Strict; Path=/; Max-Age=3600`
  );

  return response;
}
```

{% endif %}

{% elif auth_type == "session" %}
## Session-Based Authentication

### How Sessions Work

```
1. User logs in with credentials
2. Server creates session, stores in Redis/DB
3. Server sends session ID in cookie
4. Browser sends cookie with every request
5. Server validates session on each request
```

{% if framework == "fastapi" %}
### FastAPI with Redis Sessions

```python
from fastapi import FastAPI, Request, Response, HTTPException, Depends
from fastapi.security import APIKeyCookie
import redis
import secrets
import json

app = FastAPI()
redis_client = redis.Redis()

SESSION_COOKIE = "session_id"
SESSION_EXPIRE = 3600 * 24  # 24 hours

cookie_scheme = APIKeyCookie(name=SESSION_COOKIE, auto_error=False)

def create_session(user_id: str, user_data: dict) -> str:
    """Create new session and return session ID."""
    session_id = secrets.token_urlsafe(32)
    session_data = {
        "user_id": user_id,
        **user_data
    }
    redis_client.setex(
        f"session:{session_id}",
        SESSION_EXPIRE,
        json.dumps(session_data)
    )
    return session_id

def get_session(session_id: str) -> dict | None:
    """Get session data from Redis."""
    data = redis_client.get(f"session:{session_id}")
    if data:
        # Refresh TTL on access (sliding session)
        redis_client.expire(f"session:{session_id}", SESSION_EXPIRE)
        return json.loads(data)
    return None

def delete_session(session_id: str):
    """Delete session (logout)."""
    redis_client.delete(f"session:{session_id}")

async def get_current_user(
    session_id: str = Depends(cookie_scheme)
) -> dict:
    """Get current user from session."""
    if not session_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=401, detail="Session expired")

    return session

@app.post("/login")
async def login(email: str, password: str, response: Response):
    user = await authenticate_user(email, password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    session_id = create_session(user.id, {"email": user.email, "role": user.role})

    response.set_cookie(
        key=SESSION_COOKIE,
        value=session_id,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=SESSION_EXPIRE
    )
    return {"message": "Logged in"}

@app.post("/logout")
async def logout(
    response: Response,
    session_id: str = Depends(cookie_scheme)
):
    if session_id:
        delete_session(session_id)
    response.delete_cookie(SESSION_COOKIE)
    return {"message": "Logged out"}

@app.get("/me")
async def get_me(user: dict = Depends(get_current_user)):
    return user
```

{% elif framework == "express" %}
### Express with express-session

```typescript
import session from 'express-session';
import RedisStore from 'connect-redis';
import { createClient } from 'redis';

const redisClient = createClient();
await redisClient.connect();

app.use(session({
  store: new RedisStore({ client: redisClient }),
  secret: process.env.SESSION_SECRET!,
  resave: false,
  saveUninitialized: false,
  cookie: {
    secure: process.env.NODE_ENV === 'production',
    httpOnly: true,
    sameSite: 'lax',
    maxAge: 24 * 60 * 60 * 1000, // 24 hours
  },
}));

// Middleware
function requireAuth(req: Request, res: Response, next: NextFunction) {
  if (!req.session.userId) {
    return res.status(401).json({ error: 'Not authenticated' });
  }
  next();
}

// Routes
app.post('/login', async (req, res) => {
  const { email, password } = req.body;
  const user = await authenticateUser(email, password);

  if (!user) {
    return res.status(401).json({ error: 'Invalid credentials' });
  }

  req.session.userId = user.id;
  req.session.role = user.role;

  res.json({ message: 'Logged in' });
});

app.post('/logout', (req, res) => {
  req.session.destroy((err) => {
    if (err) {
      return res.status(500).json({ error: 'Logout failed' });
    }
    res.clearCookie('connect.sid');
    res.json({ message: 'Logged out' });
  });
});

app.get('/me', requireAuth, (req, res) => {
  res.json({ userId: req.session.userId, role: req.session.role });
});
```

{% endif %}

{% elif auth_type == "oauth2" %}
## OAuth2 Authentication

### Flow Types

```
Authorization Code (web apps):
  User → Auth Server → Code → Your Server → Token

PKCE (mobile/SPA):
  Like Authorization Code + code_verifier/challenge

Client Credentials (server-to-server):
  Your Server → Auth Server → Token (no user)

Implicit (deprecated):
  User → Auth Server → Token directly (insecure)
```

{% if framework == "fastapi" %}
### FastAPI OAuth2 with Google

```python
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config

config = Config('.env')
oauth = OAuth(config)

oauth.register(
    name='google',
    client_id=config('GOOGLE_CLIENT_ID'),
    client_secret=config('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'},
)

@app.get("/login/google")
async def login_google(request: Request):
    redirect_uri = request.url_for('auth_callback')
    return await oauth.google.authorize_redirect(request, redirect_uri)

@app.get("/auth/callback")
async def auth_callback(request: Request):
    token = await oauth.google.authorize_access_token(request)
    user_info = token.get('userinfo')

    # Find or create user
    user = await get_or_create_user(
        email=user_info['email'],
        name=user_info['name'],
        provider='google'
    )

    # Create your own session/JWT
    access_token = create_access_token(user.id, user.role)

    response = RedirectResponse(url='/dashboard')
    response.set_cookie('access_token', access_token, httponly=True)
    return response
```

{% elif framework == "nextjs" %}
### Next.js with NextAuth

```typescript
// app/api/auth/[...nextauth]/route.ts
import NextAuth from 'next-auth';
import GoogleProvider from 'next-auth/providers/google';
import GitHubProvider from 'next-auth/providers/github';

const handler = NextAuth({
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    }),
    GitHubProvider({
      clientId: process.env.GITHUB_ID!,
      clientSecret: process.env.GITHUB_SECRET!,
    }),
  ],
  callbacks: {
    async jwt({ token, user, account }) {
      if (user) {
        token.role = user.role || 'user';
      }
      return token;
    },
    async session({ session, token }) {
      session.user.role = token.role;
      return session;
    },
  },
});

export { handler as GET, handler as POST };

// Usage in components
import { useSession, signIn, signOut } from 'next-auth/react';

function LoginButton() {
  const { data: session } = useSession();

  if (session) {
    return (
      <div>
        <p>Signed in as {session.user.email}</p>
        <button onClick={() => signOut()}>Sign out</button>
      </div>
    );
  }

  return (
    <div>
      <button onClick={() => signIn('google')}>Sign in with Google</button>
      <button onClick={() => signIn('github')}>Sign in with GitHub</button>
    </div>
  );
}
```

{% endif %}
{% endif %}

---

## Password Security

### Hashing

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash password with bcrypt."""
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    """Verify password against hash."""
    return pwd_context.verify(plain, hashed)

# Usage
hashed = hash_password("user_password")
# "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN..."

is_valid = verify_password("user_password", hashed)
# True
```

### Password Requirements

```python
import re

def validate_password(password: str) -> list[str]:
    """Return list of validation errors."""
    errors = []

    if len(password) < 8:
        errors.append("Password must be at least 8 characters")
    if not re.search(r"[A-Z]", password):
        errors.append("Password must contain uppercase letter")
    if not re.search(r"[a-z]", password):
        errors.append("Password must contain lowercase letter")
    if not re.search(r"\d", password):
        errors.append("Password must contain digit")
    if not re.search(r"[!@#$%^&*]", password):
        errors.append("Password must contain special character")

    return errors
```

---

## Role-Based Access Control (RBAC)

### Permission Model

```python
from enum import Enum
from typing import Set

class Permission(str, Enum):
    READ_USERS = "users:read"
    WRITE_USERS = "users:write"
    DELETE_USERS = "users:delete"
    READ_POSTS = "posts:read"
    WRITE_POSTS = "posts:write"
    ADMIN = "admin:*"

ROLE_PERMISSIONS: dict[str, Set[Permission]] = {
    "viewer": {Permission.READ_USERS, Permission.READ_POSTS},
    "editor": {Permission.READ_USERS, Permission.READ_POSTS, Permission.WRITE_POSTS},
    "admin": {Permission.ADMIN},  # Wildcard
}

def has_permission(role: str, required: Permission) -> bool:
    """Check if role has required permission."""
    permissions = ROLE_PERMISSIONS.get(role, set())

    # Check for admin wildcard
    if Permission.ADMIN in permissions:
        return True

    return required in permissions

# Decorator
def require_permission(permission: Permission):
    async def checker(user = Depends(get_current_user)):
        if not has_permission(user.role, permission):
            raise HTTPException(status_code=403, detail="Permission denied")
        return user
    return Depends(checker)

# Usage
@app.delete("/users/{id}")
async def delete_user(
    id: str,
    user = require_permission(Permission.DELETE_USERS)
):
    await db.delete_user(id)
    return {"deleted": id}
```

---

## Security Best Practices

1. **Never store plain passwords** - Always hash with bcrypt/argon2
2. **Use HTTPS everywhere** - Encrypt all traffic
3. **Set secure cookie flags** - HttpOnly, Secure, SameSite
4. **Implement rate limiting** - Prevent brute force attacks
5. **Use short-lived access tokens** - 15min-1hr
6. **Rotate refresh tokens** - Issue new one on each use
7. **Validate all inputs** - Prevent injection attacks
8. **Log authentication events** - For audit and detection
9. **Implement account lockout** - After N failed attempts
10. **Use CSRF tokens** - For session-based auth
