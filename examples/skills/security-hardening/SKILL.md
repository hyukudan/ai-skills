---
name: security-hardening
description: |
  Application security best practices and hardening techniques. Use when securing
  applications, reviewing code for vulnerabilities, implementing authentication,
  or handling sensitive data. Covers OWASP Top 10, secrets management, and defense in depth.
version: 1.0.0
tags: [security, owasp, authentication, encryption, vulnerabilities]
category: development/security
variables:
  language:
    type: string
    description: Primary programming language
    enum: [python, javascript, typescript, go, java]
    default: python
  app_type:
    type: string
    description: Type of application
    enum: [web, api, cli, library]
    default: api
  auth_type:
    type: string
    description: Authentication approach
    enum: [jwt, session, oauth2, api-key]
    default: jwt
---

# Security Hardening Guide

## Security Philosophy

**Security is a process, not a feature.** It must be built into every layer, not bolted on at the end.

### Defense in Depth

```
Layer 1: Network     → Firewalls, WAF, rate limiting
Layer 2: Transport   → TLS, certificate validation
Layer 3: Application → Input validation, auth, authz
Layer 4: Data        → Encryption at rest, access control
Layer 5: Monitoring  → Logging, alerting, incident response
```

> "A system is only as secure as its weakest link."

---

## OWASP Top 10 (2021)

### A01: Broken Access Control

**Problem:** Users can act outside their intended permissions.

{% if language == "python" %}
```python
# BAD: No authorization check
@app.get("/users/{user_id}/data")
async def get_user_data(user_id: int):
    return await db.get_user_data(user_id)  # Anyone can access any user!

# GOOD: Verify ownership
@app.get("/users/{user_id}/data")
async def get_user_data(user_id: int, current_user: User = Depends(get_current_user)):
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Access denied")
    return await db.get_user_data(user_id)
```
{% elif language == "javascript" or language == "typescript" %}
```typescript
// BAD: No authorization check
app.get('/users/:userId/data', async (req, res) => {
  const data = await db.getUserData(req.params.userId);  // Anyone can access!
  res.json(data);
});

// GOOD: Verify ownership
app.get('/users/:userId/data', authenticate, async (req, res) => {
  const { userId } = req.params;
  if (req.user.id !== userId && !req.user.isAdmin) {
    return res.status(403).json({ error: 'Access denied' });
  }
  const data = await db.getUserData(userId);
  res.json(data);
});
```
{% endif %}

**Checklist:**
- [ ] Deny by default, require explicit grants
- [ ] Check ownership on every request, not just UI
- [ ] Log access control failures
- [ ] Invalidate sessions on logout/password change

---

### A02: Cryptographic Failures

**Problem:** Sensitive data exposed due to weak/missing encryption.

{% if language == "python" %}
```python
# BAD: Storing passwords in plain text
user.password = request.password

# GOOD: Use strong hashing
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

user.password_hash = pwd_context.hash(request.password)

# Verification
def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)
```
{% elif language == "javascript" or language == "typescript" %}
```typescript
import bcrypt from 'bcrypt';

// BAD: Plain text password
user.password = request.body.password;

// GOOD: Hash with bcrypt
const SALT_ROUNDS = 12;
user.passwordHash = await bcrypt.hash(request.body.password, SALT_ROUNDS);

// Verification
async function verifyPassword(plain: string, hash: string): Promise<boolean> {
  return bcrypt.compare(plain, hash);
}
```
{% endif %}

**Checklist:**
- [ ] Use TLS 1.2+ everywhere (no exceptions)
- [ ] Hash passwords with Argon2id, bcrypt, or scrypt
- [ ] Encrypt sensitive data at rest (AES-256-GCM)
- [ ] Never commit secrets to version control
- [ ] Rotate keys and secrets regularly

---

### A03: Injection

**Problem:** Untrusted data sent to interpreter as command/query.

{% if language == "python" %}
```python
# BAD: SQL Injection
query = f"SELECT * FROM users WHERE email = '{email}'"
cursor.execute(query)

# GOOD: Parameterized queries
cursor.execute("SELECT * FROM users WHERE email = %s", (email,))

# BAD: Command injection
os.system(f"convert {filename} output.png")

# GOOD: Use subprocess with list
subprocess.run(["convert", filename, "output.png"], check=True)

# BAD: Template injection
template = Template(user_input)  # User controls template!

# GOOD: Never let users control templates
template = Template("Hello, {{ name }}")
template.render(name=user_input)
```
{% elif language == "javascript" or language == "typescript" %}
```typescript
// BAD: SQL Injection
const query = `SELECT * FROM users WHERE email = '${email}'`;

// GOOD: Parameterized query (using pg)
const result = await client.query(
  'SELECT * FROM users WHERE email = $1',
  [email]
);

// BAD: XSS via innerHTML
element.innerHTML = userInput;

// GOOD: Use textContent or sanitize
element.textContent = userInput;
// Or sanitize HTML
import DOMPurify from 'dompurify';
element.innerHTML = DOMPurify.sanitize(userInput);
```
{% endif %}

**Checklist:**
- [ ] Use parameterized queries/prepared statements
- [ ] Validate and sanitize all input
- [ ] Use ORM/ODM when possible
- [ ] Escape output based on context (HTML, JS, URL, CSS)

---

### A04: Insecure Design

**Problem:** Missing or ineffective security controls by design.

```
Security Design Principles:

1. Least Privilege
   - Users get minimum permissions needed
   - Services run with minimal access
   - Time-limited access tokens

2. Defense in Depth
   - Multiple security layers
   - Assume each layer can fail

3. Fail Secure
   - Errors should deny access, not grant it
   - Default to closed, not open

4. Separation of Duties
   - Different roles for different actions
   - No single point of compromise
```

**Checklist:**
- [ ] Threat model documented
- [ ] Security requirements in user stories
- [ ] Rate limiting on all endpoints
- [ ] Business logic tested for abuse cases

---

### A05: Security Misconfiguration

{% if app_type == "web" or app_type == "api" %}
**Security Headers (HTTP):**

```
# Essential headers
Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: default-src 'self'
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: geolocation=(), microphone=()

# Remove revealing headers
X-Powered-By: (remove)
Server: (remove or generic)
```

{% if language == "python" %}
```python
# FastAPI security headers middleware
from fastapi import FastAPI
from starlette.middleware import Middleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware

app = FastAPI()

@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response
```
{% elif language == "javascript" or language == "typescript" %}
```typescript
import helmet from 'helmet';

// Express.js
app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      scriptSrc: ["'self'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
    },
  },
  hsts: { maxAge: 31536000, includeSubDomains: true },
}));
```
{% endif %}
{% endif %}

**Checklist:**
- [ ] Remove default credentials
- [ ] Disable directory listing
- [ ] Remove unnecessary features/pages
- [ ] Keep dependencies updated
- [ ] Different configs for dev/staging/prod

---

## Authentication & Authorization

{% if auth_type == "jwt" %}
### JWT Implementation

{% if language == "python" %}
```python
from datetime import datetime, timedelta
from jose import jwt, JWTError
from pydantic import BaseModel

SECRET_KEY = os.environ["JWT_SECRET"]  # Never hardcode!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE = timedelta(minutes=15)
REFRESH_TOKEN_EXPIRE = timedelta(days=7)

class TokenPayload(BaseModel):
    sub: str        # Subject (user ID)
    exp: datetime   # Expiration
    iat: datetime   # Issued at
    type: str       # "access" or "refresh"

def create_access_token(user_id: str) -> str:
    payload = {
        "sub": user_id,
        "exp": datetime.utcnow() + ACCESS_TOKEN_EXPIRE,
        "iat": datetime.utcnow(),
        "type": "access"
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str) -> TokenPayload:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return TokenPayload(**payload)
    except JWTError as e:
        raise HTTPException(status_code=401, detail="Invalid token")
```
{% elif language == "javascript" or language == "typescript" %}
```typescript
import jwt from 'jsonwebtoken';

const SECRET = process.env.JWT_SECRET!;
const ACCESS_EXPIRE = '15m';
const REFRESH_EXPIRE = '7d';

interface TokenPayload {
  sub: string;
  type: 'access' | 'refresh';
}

export function createAccessToken(userId: string): string {
  return jwt.sign(
    { sub: userId, type: 'access' },
    SECRET,
    { expiresIn: ACCESS_EXPIRE }
  );
}

export function verifyToken(token: string): TokenPayload {
  try {
    return jwt.verify(token, SECRET) as TokenPayload;
  } catch (error) {
    throw new UnauthorizedError('Invalid token');
  }
}
```
{% endif %}

**JWT Security Checklist:**
- [ ] Short expiration (15-30 min for access tokens)
- [ ] Use refresh tokens for long sessions
- [ ] Store secret securely (env var, secrets manager)
- [ ] Validate all claims (exp, iss, aud)
- [ ] Use RS256 for distributed systems
{% endif %}

{% if auth_type == "session" %}
### Session Security

```python
# Session configuration
SESSION_CONFIG = {
    "secret_key": os.environ["SESSION_SECRET"],
    "cookie_name": "__session",
    "cookie_secure": True,      # HTTPS only
    "cookie_httponly": True,    # No JavaScript access
    "cookie_samesite": "lax",   # CSRF protection
    "max_age": 3600,            # 1 hour
}

# Regenerate session ID after login (prevent fixation)
def login_user(session, user):
    session.regenerate()
    session["user_id"] = user.id
    session["logged_in_at"] = datetime.utcnow().isoformat()
```

**Session Checklist:**
- [ ] Regenerate session ID on privilege change
- [ ] Set Secure, HttpOnly, SameSite flags
- [ ] Implement session timeout
- [ ] Store sessions server-side (Redis, DB)
{% endif %}

---

## Secrets Management

### Environment Variables

```bash
# .env (NEVER commit this file)
DATABASE_URL=postgresql://user:pass@localhost/db
JWT_SECRET=your-256-bit-secret
API_KEY=sk_live_...

# .env.example (commit this)
DATABASE_URL=postgresql://user:pass@localhost/db
JWT_SECRET=generate-a-secure-secret
API_KEY=your-api-key
```

{% if language == "python" %}
```python
# Load secrets from environment
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    jwt_secret: str
    api_key: str

    class Config:
        env_file = ".env"

settings = Settings()

# Access secrets
db_url = settings.database_url  # Never print/log secrets!
```
{% elif language == "javascript" or language == "typescript" %}
```typescript
// Load from environment
import dotenv from 'dotenv';
dotenv.config();

const config = {
  databaseUrl: process.env.DATABASE_URL!,
  jwtSecret: process.env.JWT_SECRET!,
  apiKey: process.env.API_KEY!,
};

// Validate required secrets at startup
const required = ['DATABASE_URL', 'JWT_SECRET', 'API_KEY'];
for (const key of required) {
  if (!process.env[key]) {
    throw new Error(`Missing required env var: ${key}`);
  }
}
```
{% endif %}

### Secrets Checklist

```
✅ DO:
- Use environment variables or secrets manager
- Rotate secrets regularly
- Use different secrets per environment
- Encrypt secrets in CI/CD
- Audit secret access

❌ DON'T:
- Commit secrets to git (even in "private" repos)
- Log secrets (even accidentally)
- Share secrets via Slack/email
- Use the same secret for multiple purposes
- Hardcode secrets in code
```

---

## Input Validation

{% if language == "python" %}
```python
from pydantic import BaseModel, EmailStr, Field, validator
import re

class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=50, pattern=r'^[a-zA-Z0-9_]+$')
    password: str = Field(min_length=12)

    @validator('password')
    def password_strength(cls, v):
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain uppercase')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain lowercase')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain digit')
        return v

# File upload validation
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def validate_upload(file: UploadFile):
    # Check extension
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"File type {ext} not allowed")

    # Check magic bytes (not just extension)
    header = file.file.read(8)
    file.file.seek(0)
    if not is_valid_image(header):
        raise HTTPException(400, "Invalid file content")

    # Check size
    file.file.seek(0, 2)  # Seek to end
    size = file.file.tell()
    file.file.seek(0)
    if size > MAX_FILE_SIZE:
        raise HTTPException(400, f"File too large (max {MAX_FILE_SIZE} bytes)")
```
{% elif language == "javascript" or language == "typescript" %}
```typescript
import { z } from 'zod';

const UserCreateSchema = z.object({
  email: z.string().email(),
  username: z.string().min(3).max(50).regex(/^[a-zA-Z0-9_]+$/),
  password: z.string().min(12).refine(
    (val) => /[A-Z]/.test(val) && /[a-z]/.test(val) && /\d/.test(val),
    { message: 'Password must contain uppercase, lowercase, and digit' }
  ),
});

// Validate input
function validateUser(input: unknown) {
  const result = UserCreateSchema.safeParse(input);
  if (!result.success) {
    throw new ValidationError(result.error.format());
  }
  return result.data;
}
```
{% endif %}

---

## Security Checklist

### Before Deployment

```
Authentication & Authorization:
- [ ] Passwords hashed with Argon2id/bcrypt
- [ ] Rate limiting on login endpoints
- [ ] Account lockout after failed attempts
- [ ] Secure password reset flow
- [ ] MFA available for sensitive accounts

Data Protection:
- [ ] TLS 1.2+ for all connections
- [ ] Sensitive data encrypted at rest
- [ ] No secrets in code or logs
- [ ] PII handling documented

Input/Output:
- [ ] All input validated server-side
- [ ] Output encoded for context
- [ ] File uploads validated (type, size, content)
- [ ] SQL injection prevented

Infrastructure:
- [ ] Security headers configured
- [ ] CORS properly restricted
- [ ] Dependencies up to date
- [ ] Error messages don't leak info
- [ ] Logging captures security events
```
