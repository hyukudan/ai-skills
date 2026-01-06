---
name: docker-deployment
description: |
  Docker containerization and deployment best practices. Use when containerizing
  applications, creating Docker Compose setups, or optimizing images for production.
  Covers multi-stage builds, security hardening, and orchestration patterns.
version: 1.0.0
tags: [docker, containers, deployment, devops, ci-cd]
category: devops/containers
variables:
  language:
    type: string
    description: Application language/runtime
    enum: [python, node, go, java, rust]
    default: python
  environment:
    type: string
    description: Deployment environment
    enum: [development, staging, production]
    default: production
  orchestration:
    type: string
    description: Container orchestration platform
    enum: [compose, kubernetes, swarm, none]
    default: compose
---

# Docker Deployment Guide

## Philosophy

**Containers are immutable.** Build once, run anywhere. Configuration lives outside the image.

### Core Principles

1. **One process per container** - Containers should do one thing well
2. **Immutable infrastructure** - Never modify running containers
3. **Configuration as environment** - Secrets and config via env vars or mounts
4. **Minimal images** - Smaller = faster + more secure

---

## Dockerfile Best Practices

{% if language == "python" %}
### Python Multi-Stage Build

```dockerfile
# Stage 1: Build
FROM python:3.12-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# Stage 2: Production
FROM python:3.12-slim as production

# Create non-root user
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

WORKDIR /app

# Install only runtime dependencies
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache /wheels/*

# Copy application code
COPY --chown=appuser:appgroup . .

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Python with Poetry

```dockerfile
FROM python:3.12-slim as builder

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VENV_IN_PROJECT=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

RUN pip install poetry==1.7.0

COPY pyproject.toml poetry.lock ./
RUN --mount=type=cache,target=/tmp/poetry_cache poetry install --no-root --only main

FROM python:3.12-slim as production

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY . .

ENV PATH="/app/.venv/bin:$PATH"

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0"]
```

{% elif language == "node" %}
### Node.js Multi-Stage Build

```dockerfile
# Stage 1: Dependencies
FROM node:20-alpine as deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --only=production

# Stage 2: Build
FROM node:20-alpine as builder
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 3: Production
FROM node:20-alpine as production

RUN addgroup -g 1001 -S nodejs && adduser -S nextjs -u 1001

WORKDIR /app

COPY --from=deps /app/node_modules ./node_modules
COPY --from=builder --chown=nextjs:nodejs /app/dist ./dist
COPY --from=builder /app/package.json ./

USER nextjs

HEALTHCHECK --interval=30s --timeout=3s \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000/health || exit 1

EXPOSE 3000

CMD ["node", "dist/index.js"]
```

{% elif language == "go" %}
### Go Multi-Stage Build

```dockerfile
# Stage 1: Build
FROM golang:1.22-alpine as builder

WORKDIR /app

# Download dependencies first (cache layer)
COPY go.mod go.sum ./
RUN go mod download

# Build
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -ldflags="-w -s" -o /app/server ./cmd/server

# Stage 2: Production (scratch for minimal image)
FROM scratch as production

# Import CA certificates for HTTPS
COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/

# Copy binary
COPY --from=builder /app/server /server

# Non-root user (numeric for scratch)
USER 65534

EXPOSE 8080

ENTRYPOINT ["/server"]
```

{% elif language == "java" %}
### Java Multi-Stage Build

```dockerfile
# Stage 1: Build
FROM maven:3.9-eclipse-temurin-21 as builder

WORKDIR /app

# Cache dependencies
COPY pom.xml .
RUN mvn dependency:go-offline

# Build
COPY src ./src
RUN mvn package -DskipTests

# Stage 2: Production
FROM eclipse-temurin:21-jre-alpine as production

RUN addgroup -S spring && adduser -S spring -G spring

WORKDIR /app

COPY --from=builder /app/target/*.jar app.jar

USER spring

HEALTHCHECK --interval=30s --timeout=3s \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8080/actuator/health || exit 1

EXPOSE 8080

ENTRYPOINT ["java", "-XX:+UseContainerSupport", "-XX:MaxRAMPercentage=75.0", "-jar", "app.jar"]
```

{% endif %}

---

## Image Optimization

### Layer Caching

```dockerfile
# BAD: Busts cache on any code change
COPY . .
RUN pip install -r requirements.txt

# GOOD: Dependencies cached separately
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
```

### Minimize Image Size

```dockerfile
# Use slim/alpine base images
FROM python:3.12-slim     # ~150MB vs ~1GB for full
FROM node:20-alpine       # ~180MB vs ~1GB for full
FROM golang:1.22-alpine   # Go can use scratch (~0MB)

# Clean up in same layer
RUN apt-get update && apt-get install -y \
    build-essential \
    && pip install -r requirements.txt \
    && apt-get purge -y build-essential \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

# Use .dockerignore
```

### .dockerignore

```
# Version control
.git
.gitignore

# Dependencies (rebuild in container)
node_modules
__pycache__
*.pyc
.venv
venv

# Build artifacts
dist
build
*.egg-info

# IDE
.vscode
.idea
*.swp

# Tests
tests
*_test.go
*.test.js

# Documentation
docs
*.md
!README.md

# Docker files
Dockerfile*
docker-compose*
.dockerignore

# Environment
.env
.env.*
!.env.example
```

---

{% if orchestration == "compose" %}
## Docker Compose

### Development Setup

```yaml
# docker-compose.yml
services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
      target: development  # Multi-stage target
    volumes:
      - .:/app             # Live reload
      - /app/node_modules  # Preserve container modules
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=development
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/app
    depends_on:
      db:
        condition: service_healthy

  db:
    image: postgres:16-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=app
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5

volumes:
  postgres_data:
  redis_data:
```

{% if environment == "production" %}
### Production Setup

```yaml
# docker-compose.prod.yml
services:
  app:
    image: ${REGISTRY}/myapp:${VERSION:-latest}
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '1'
          memory: 512M
        reservations:
          cpus: '0.5'
          memory: 256M
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
    environment:
      - NODE_ENV=production
      - DATABASE_URL=${DATABASE_URL}  # From .env or secrets
    secrets:
      - db_password
      - jwt_secret
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./certs:/etc/nginx/certs:ro
    depends_on:
      - app

secrets:
  db_password:
    external: true
  jwt_secret:
    external: true
```
{% endif %}

### Useful Commands

```bash
# Start services
docker compose up -d

# View logs
docker compose logs -f app

# Execute command in container
docker compose exec app bash

# Rebuild single service
docker compose up -d --build app

# Scale service
docker compose up -d --scale app=3

# Stop and remove
docker compose down -v  # -v removes volumes
```

{% endif %}

---

## Security Hardening

### Run as Non-Root

```dockerfile
# Create user in Dockerfile
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

# Copy files with correct ownership
COPY --chown=appuser:appgroup . .

# Switch user before CMD
USER appuser
```

### Read-Only Filesystem

```yaml
# docker-compose.yml
services:
  app:
    read_only: true
    tmpfs:
      - /tmp
      - /var/run
    volumes:
      - app_data:/app/data  # Only writable mount
```

### Security Scanning

```bash
# Scan image for vulnerabilities
docker scout cves myapp:latest

# Using Trivy
trivy image myapp:latest

# Using Snyk
snyk container test myapp:latest
```

### Minimal Capabilities

```yaml
services:
  app:
    cap_drop:
      - ALL           # Drop all capabilities
    cap_add:
      - NET_BIND_SERVICE  # Only add what's needed
    security_opt:
      - no-new-privileges:true
```

---

## CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/docker.yml
name: Build and Push

on:
  push:
    branches: [main]
    tags: ['v*']

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=semver,pattern={{version}}
            type=sha,prefix=

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

---

## Health Checks

```dockerfile
# HTTP health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# TCP health check
HEALTHCHECK --interval=30s --timeout=3s \
    CMD nc -z localhost 8000 || exit 1

# Custom script
HEALTHCHECK --interval=30s --timeout=10s \
    CMD /app/healthcheck.sh || exit 1
```

```python
# Health endpoint example
@app.get("/health")
async def health_check():
    checks = {
        "database": await check_database(),
        "redis": await check_redis(),
        "disk": check_disk_space(),
    }

    healthy = all(checks.values())
    status_code = 200 if healthy else 503

    return JSONResponse(
        content={"status": "healthy" if healthy else "unhealthy", "checks": checks},
        status_code=status_code
    )
```

---

## Debugging

```bash
# Interactive shell in running container
docker exec -it container_name /bin/sh

# Run with debug options
docker run -it --rm \
    -v $(pwd):/app \
    -p 8000:8000 \
    myapp:latest \
    /bin/sh

# View container logs
docker logs -f --tail 100 container_name

# Inspect container
docker inspect container_name

# Resource usage
docker stats

# Build with verbose output
docker build --progress=plain -t myapp .
```

---

## Common Issues

### Container Exits Immediately

```bash
# Check logs
docker logs container_name

# Common causes:
# 1. Process runs in background (use foreground)
# 2. Missing environment variables
# 3. Permission issues (check USER directive)
# 4. Health check failing too quickly (increase start_period)
```

### Permission Denied

```dockerfile
# Ensure correct ownership
COPY --chown=appuser:appgroup . .

# Or fix at runtime
RUN chown -R appuser:appgroup /app
```

### Out of Memory

```yaml
# Set memory limits
services:
  app:
    deploy:
      resources:
        limits:
          memory: 512M
    # For JVM apps
    environment:
      - JAVA_OPTS=-XX:MaxRAMPercentage=75.0
```
