---
name: security-best-practices
version: 1.0.0
description: |
  Application security best practices covering OWASP Top 10, secure coding patterns,
  authentication, input validation, and common vulnerability prevention. Use when
  reviewing code for security issues or implementing secure features.
tags:
  - security
  - owasp
  - authentication
  - validation
  - encryption
category: development/security
author: AI Skills Team
trigger_phrases:
  - security review
  - prevent injection
  - secure authentication
  - input validation
  - owasp vulnerabilities
  - xss prevention
  - sql injection
variables:
  language:
    type: string
    description: Programming language context
    enum:
      - python
      - javascript
      - go
      - java
      - general
    default: general
  focus:
    type: string
    description: Security focus area
    enum:
      - web
      - api
      - database
      - authentication
      - all
    default: all
---

# Security Best Practices

## Core Principles

1. **Defense in Depth** - Multiple layers of security
2. **Least Privilege** - Minimal permissions needed
3. **Fail Secure** - Default to denial on errors
4. **Input Validation** - Trust nothing from outside
5. **Secure by Default** - Security shouldn't be optional

---

## OWASP Top 10 (2021)

### 1. Broken Access Control

**Problem:** Users accessing data/functions they shouldn't.

{% if language == "python" %}
```python
# BAD - No authorization check
@app.route('/users/<user_id>/data')
def get_user_data(user_id):
    return db.get_user_data(user_id)  # Any user can access any data!

# GOOD - Verify ownership
@app.route('/users/<user_id>/data')
@login_required
def get_user_data(user_id):
    if current_user.id != user_id and not current_user.is_admin:
        abort(403)
    return db.get_user_data(user_id)
```
{% elif language == "javascript" %}
```javascript
// BAD - No authorization check
app.get('/users/:userId/data', (req, res) => {
  const data = db.getUserData(req.params.userId);
  res.json(data);  // Any user can access any data!
});

// GOOD - Verify ownership
app.get('/users/:userId/data', authenticate, (req, res) => {
  if (req.user.id !== req.params.userId && !req.user.isAdmin) {
    return res.status(403).json({ error: 'Forbidden' });
  }
  const data = db.getUserData(req.params.userId);
  res.json(data);
});
```
{% else %}
```
// Always verify:
1. User is authenticated
2. User is authorized for this resource
3. User is authorized for this action
4. Resource belongs to user (or user has elevated privileges)
```
{% endif %}

---

### 2. Cryptographic Failures

**Problem:** Sensitive data exposed through weak/missing encryption.

**Do:**
- Use TLS 1.3 for all connections
- Hash passwords with bcrypt/argon2 (never MD5/SHA1)
- Encrypt sensitive data at rest (AES-256-GCM)
- Use secure random for tokens

{% if language == "python" %}
```python
# Password hashing
from argon2 import PasswordHasher

ph = PasswordHasher()
hashed = ph.hash(password)
ph.verify(hashed, password)  # Raises on mismatch

# Secure tokens
import secrets
token = secrets.token_urlsafe(32)  # NOT random.random()!

# Encryption
from cryptography.fernet import Fernet
key = Fernet.generate_key()
cipher = Fernet(key)
encrypted = cipher.encrypt(b"sensitive data")
```
{% elif language == "javascript" %}
```javascript
// Password hashing
const bcrypt = require('bcrypt');
const hash = await bcrypt.hash(password, 12);
const valid = await bcrypt.compare(password, hash);

// Secure tokens
const crypto = require('crypto');
const token = crypto.randomBytes(32).toString('hex');

// Encryption
const { createCipheriv, createDecipheriv, randomBytes } = require('crypto');
const key = randomBytes(32);
const iv = randomBytes(16);
const cipher = createCipheriv('aes-256-gcm', key, iv);
```
{% endif %}

---

### 3. Injection

**Problem:** Untrusted data executed as code/queries.

{% if language == "python" %}
```python
# SQL Injection - BAD
query = f"SELECT * FROM users WHERE id = {user_id}"

# SQL Injection - GOOD (parameterized)
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))

# Or use ORM
user = User.query.filter_by(id=user_id).first()

# Command Injection - BAD
os.system(f"ping {host}")

# Command Injection - GOOD
import subprocess
subprocess.run(["ping", "-c", "1", host], check=True)
```
{% elif language == "javascript" %}
```javascript
// SQL Injection - BAD
const query = `SELECT * FROM users WHERE id = ${userId}`;

// SQL Injection - GOOD (parameterized)
const [rows] = await db.query(
  'SELECT * FROM users WHERE id = ?',
  [userId]
);

// NoSQL Injection - BAD
db.users.find({ username: req.body.username });  // Can inject { $gt: "" }

// NoSQL Injection - GOOD
const username = String(req.body.username);
db.users.find({ username });
```
{% else %}
```
ALWAYS:
- Use parameterized queries/prepared statements
- Use ORM/query builders
- Validate and sanitize input
- Use allowlists, not blocklists
```
{% endif %}

---

### 4. Insecure Design

**Problem:** Missing security controls in architecture.

**Security Requirements Checklist:**
- [ ] Authentication for all sensitive endpoints
- [ ] Authorization checks at every layer
- [ ] Rate limiting on authentication endpoints
- [ ] Account lockout after failed attempts
- [ ] Secure session management
- [ ] Audit logging for security events
- [ ] Input validation on all boundaries

---

### 5. Security Misconfiguration

**Problem:** Insecure default configurations.

**Checklist:**
```yaml
# Headers to set
Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: default-src 'self'
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block

# Things to disable
- Directory listings
- Stack traces in errors
- Debug mode in production
- Default credentials
- Unnecessary HTTP methods
- Server version headers
```

{% if language == "python" %}
```python
# Flask security headers
from flask import Flask
from flask_talisman import Talisman

app = Flask(__name__)
Talisman(app,
    force_https=True,
    content_security_policy={
        'default-src': "'self'",
        'script-src': "'self'"
    }
)
```
{% elif language == "javascript" %}
```javascript
// Express security headers
const helmet = require('helmet');
app.use(helmet());
app.use(helmet.contentSecurityPolicy({
  directives: {
    defaultSrc: ["'self'"],
    scriptSrc: ["'self'"]
  }
}));
```
{% endif %}

---

### 6. Vulnerable Components

**Problem:** Using components with known vulnerabilities.

**Mitigation:**
```bash
# Python
pip install safety
safety check

# JavaScript
npm audit
npm audit fix

# Go
govulncheck ./...

# General
- Subscribe to security advisories
- Use Dependabot/Renovate
- Pin dependency versions
- Review dependencies before adding
```

---

### 7. Authentication Failures

{% if focus == "authentication" or focus == "all" %}

**Secure Authentication Checklist:**

- [ ] Strong password policy (12+ chars, complexity optional)
- [ ] Password breach checking (HaveIBeenPwned API)
- [ ] Multi-factor authentication
- [ ] Secure session management
- [ ] Rate limiting (5 attempts/minute)
- [ ] Account lockout (30 min after 10 failures)
- [ ] Secure password reset flow

{% if language == "python" %}
```python
# Rate limiting login attempts
from flask_limiter import Limiter

limiter = Limiter(app, key_func=get_remote_address)

@app.route('/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    # ... authentication logic
    pass

# Session security
app.config.update(
    SESSION_COOKIE_SECURE=True,      # HTTPS only
    SESSION_COOKIE_HTTPONLY=True,    # No JS access
    SESSION_COOKIE_SAMESITE='Lax',   # CSRF protection
    PERMANENT_SESSION_LIFETIME=3600  # 1 hour
)
```
{% elif language == "javascript" %}
```javascript
// Session configuration
app.use(session({
  secret: process.env.SESSION_SECRET,
  name: '__session',  // Non-default name
  cookie: {
    secure: true,     // HTTPS only
    httpOnly: true,   // No JS access
    sameSite: 'lax',  // CSRF protection
    maxAge: 3600000   // 1 hour
  },
  resave: false,
  saveUninitialized: false
}));
```
{% endif %}
{% endif %}

---

### 8. Software and Data Integrity

**Problem:** Assuming code/data integrity without verification.

**Mitigation:**
- Verify package signatures
- Use lockfiles (package-lock.json, Pipfile.lock)
- Implement CI/CD pipeline security
- Sign releases/commits
- Use Subresource Integrity for CDN scripts

```html
<!-- SRI for external scripts -->
<script src="https://cdn.example.com/lib.js"
  integrity="sha384-oqVuAfXRKap7fdgcCY5uykM6+R9GqQ8K/uxy9rx7HNQlGYl1kPzQho1wx4JwY8wC"
  crossorigin="anonymous"></script>
```

---

### 9. Logging and Monitoring Failures

**Problem:** Unable to detect or respond to attacks.

**What to Log:**
```
- Authentication events (login, logout, failed attempts)
- Authorization failures
- Input validation failures
- Application errors
- Admin actions
- Data access patterns
```

{% if language == "python" %}
```python
import logging
import structlog

logger = structlog.get_logger()

@app.route('/login', methods=['POST'])
def login():
    user = authenticate(request.form['username'], request.form['password'])
    if user:
        logger.info("login_success", user_id=user.id, ip=request.remote_addr)
    else:
        logger.warning("login_failed",
            username=request.form['username'],
            ip=request.remote_addr
        )
```
{% endif %}

---

### 10. Server-Side Request Forgery (SSRF)

**Problem:** Server makes requests to attacker-controlled URLs.

{% if language == "python" %}
```python
# BAD - User controls URL
@app.route('/fetch')
def fetch_url():
    url = request.args.get('url')
    return requests.get(url).content  # Can hit internal services!

# GOOD - Validate and restrict
import ipaddress
from urllib.parse import urlparse

ALLOWED_HOSTS = {'api.example.com', 'cdn.example.com'}

def is_safe_url(url):
    parsed = urlparse(url)

    # Only allow specific hosts
    if parsed.hostname not in ALLOWED_HOSTS:
        return False

    # Block internal IPs
    try:
        ip = ipaddress.ip_address(parsed.hostname)
        if ip.is_private or ip.is_loopback:
            return False
    except ValueError:
        pass  # Not an IP, it's a hostname

    return True

@app.route('/fetch')
def fetch_url():
    url = request.args.get('url')
    if not is_safe_url(url):
        abort(400, "Invalid URL")
    return requests.get(url, timeout=5).content
```
{% endif %}

---

{% if focus == "web" or focus == "all" %}
## XSS Prevention

### Output Encoding

{% if language == "javascript" %}
```javascript
// React - Safe by default (escapes HTML)
return <div>{userInput}</div>;

// Dangerous - only when absolutely necessary
return <div dangerouslySetInnerHTML={{__html: sanitizedHtml}} />;

// Sanitize if you must render HTML
import DOMPurify from 'dompurify';
const clean = DOMPurify.sanitize(dirty);
```
{% elif language == "python" %}
```python
# Jinja2 - Safe by default
{{ user_input }}  # Auto-escaped

# Mark as safe only for trusted content
{{ trusted_html | safe }}

# Manual escaping
from markupsafe import escape
escaped = escape(user_input)
```
{% endif %}

### Content Security Policy

```
Content-Security-Policy:
  default-src 'self';
  script-src 'self' 'nonce-abc123';
  style-src 'self' 'unsafe-inline';
  img-src 'self' data: https:;
  connect-src 'self' https://api.example.com;
  frame-ancestors 'none';
```
{% endif %}

---

{% if focus == "api" or focus == "all" %}
## API Security

### Authentication
- Use OAuth 2.0 / OpenID Connect for user auth
- Use API keys for service-to-service
- Never expose secrets in URLs

### Authorization
- Implement RBAC or ABAC
- Check permissions on every request
- Use scopes for API tokens

### Input Validation
```python
from pydantic import BaseModel, validator, constr

class UserCreate(BaseModel):
    email: constr(max_length=254)
    name: constr(min_length=1, max_length=100)
    age: int

    @validator('email')
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('Invalid email')
        return v.lower()

    @validator('age')
    def validate_age(cls, v):
        if not 0 < v < 150:
            raise ValueError('Invalid age')
        return v
```

### Rate Limiting
```
- Global: 1000 requests/minute
- Authentication: 5 attempts/minute
- Sensitive operations: 10/hour
- Return 429 with Retry-After header
```
{% endif %}

---

## Security Checklist

### Before Deployment
- [ ] All secrets in environment variables
- [ ] Debug mode disabled
- [ ] HTTPS enforced everywhere
- [ ] Security headers configured
- [ ] Dependencies audited
- [ ] Error messages don't leak info
- [ ] Logs don't contain sensitive data
- [ ] Rate limiting enabled
- [ ] Input validation on all endpoints
- [ ] Output encoding for all user content
