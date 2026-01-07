---
name: ci-cd-pipelines
description: |
  Guide for building CI/CD pipelines for automated testing, building, and deployment.
  Use when setting up GitHub Actions, GitLab CI, or other CI/CD systems. Covers
  workflow design, caching, secrets management, and deployment strategies.
version: 1.0.0
tags: [ci-cd, github-actions, gitlab-ci, automation, devops, deployment]
category: devops/automation
trigger_phrases:
  - "github actions"
  - "CI/CD"
  - "pipeline"
  - "gitlab ci"
  - "workflow yaml"
  - "deploy automation"
  - "build pipeline"
  - "continuous integration"
  - "continuous deployment"
  - "ci workflow"
variables:
  platform:
    type: string
    description: CI/CD platform
    enum: [github-actions, gitlab-ci, jenkins, circleci]
    default: github-actions
  language:
    type: string
    description: Primary programming language
    enum: [python, javascript, typescript, go, rust, java]
    default: python
  deployment_target:
    type: string
    description: Where to deploy
    enum: [none, docker, kubernetes, serverless, static]
    default: docker
---

# CI/CD Pipeline Guide

## Pipeline Philosophy

**Pipelines are code.** Treat them with the same rigor as application code.

```
Principles:
1. Fast feedback   - Fail fast, run quick checks first
2. Reproducible    - Same commit = same result
3. Incremental     - Only build/test what changed
4. Secure          - Secrets never exposed, minimal permissions
```

---

{% if platform == "github-actions" %}
## GitHub Actions

### Basic Workflow Structure

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  # Global environment variables
  NODE_ENV: test

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run linter
        run: npm run lint

  test:
    runs-on: ubuntu-latest
    needs: lint  # Run after lint passes
    steps:
      - uses: actions/checkout@v4
      - name: Run tests
        run: npm test

  build:
    runs-on: ubuntu-latest
    needs: [lint, test]  # Run after both pass
    steps:
      - uses: actions/checkout@v4
      - name: Build
        run: npm run build
```

### Optimized Pipeline with Caching

{% if language == "python" %}
```yaml
name: Python CI

on:
  push:
    branches: [main]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.10', '3.11', '3.12']

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Cache pip dependencies
        uses: actions/cache@v4
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements*.txt') }}
          restore-keys: |
            ${{ runner.os }}-pip-

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install -r requirements-dev.txt

      - name: Lint with ruff
        run: ruff check .

      - name: Type check with mypy
        run: mypy src/

      - name: Test with pytest
        run: |
          pytest --cov=src --cov-report=xml --cov-report=html
        env:
          DATABASE_URL: ${{ secrets.TEST_DATABASE_URL }}

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          files: ./coverage.xml
          fail_ci_if_error: true
```

{% elif language == "javascript" or language == "typescript" %}
```yaml
name: Node.js CI

on:
  push:
    branches: [main]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        node-version: [18, 20, 22]

    steps:
      - uses: actions/checkout@v4

      - name: Use Node.js ${{ matrix.node-version }}
        uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Lint
        run: npm run lint

      - name: Type check
        run: npm run typecheck

      - name: Test
        run: npm test -- --coverage

      - name: Build
        run: npm run build

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        if: matrix.node-version == 20

{% elif language == "go" %}
```yaml
name: Go CI

on:
  push:
    branches: [main]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Go
        uses: actions/setup-go@v5
        with:
          go-version: '1.22'
          cache: true

      - name: Verify dependencies
        run: go mod verify

      - name: Lint
        uses: golangci/golangci-lint-action@v4
        with:
          version: latest

      - name: Test
        run: go test -race -coverprofile=coverage.out -covermode=atomic ./...

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          files: ./coverage.out
```
{% endif %}

### Secrets Management

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production  # Requires approval for this environment

    steps:
      - uses: actions/checkout@v4

      # Use secrets securely
      - name: Deploy
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        run: |
          # Secrets are masked in logs automatically
          aws s3 sync ./dist s3://my-bucket

      # OIDC authentication (preferred over long-lived secrets)
      - name: Configure AWS Credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789:role/github-actions
          aws-region: us-east-1
```

### Reusable Workflows

```yaml
# .github/workflows/reusable-deploy.yml
name: Reusable Deploy

on:
  workflow_call:
    inputs:
      environment:
        required: true
        type: string
      version:
        required: true
        type: string
    secrets:
      DEPLOY_KEY:
        required: true

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: ${{ inputs.environment }}
    steps:
      - name: Deploy version ${{ inputs.version }}
        run: ./deploy.sh ${{ inputs.version }}
        env:
          DEPLOY_KEY: ${{ secrets.DEPLOY_KEY }}

# Usage in another workflow:
# jobs:
#   call-deploy:
#     uses: ./.github/workflows/reusable-deploy.yml
#     with:
#       environment: production
#       version: v1.2.3
#     secrets:
#       DEPLOY_KEY: ${{ secrets.DEPLOY_KEY }}
```

{% elif platform == "gitlab-ci" %}
## GitLab CI/CD

### Basic Pipeline Structure

```yaml
# .gitlab-ci.yml
stages:
  - lint
  - test
  - build
  - deploy

variables:
  # Global variables
  DOCKER_DRIVER: overlay2

# Template for common setup
.setup-python:
  image: python:3.11
  before_script:
    - pip install -r requirements.txt

lint:
  stage: lint
  extends: .setup-python
  script:
    - ruff check .
    - mypy src/

test:
  stage: test
  extends: .setup-python
  script:
    - pytest --cov=src --cov-report=xml
  coverage: '/TOTAL.+ ([0-9]{1,3}%)/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml

build:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
  only:
    - main

deploy-staging:
  stage: deploy
  environment:
    name: staging
    url: https://staging.example.com
  script:
    - ./deploy.sh staging
  only:
    - main

deploy-production:
  stage: deploy
  environment:
    name: production
    url: https://example.com
  script:
    - ./deploy.sh production
  when: manual  # Requires manual approval
  only:
    - main
```

### Caching in GitLab CI

```yaml
{% if language == "python" %}
test:
  image: python:3.11
  cache:
    key: ${CI_COMMIT_REF_SLUG}
    paths:
      - .cache/pip
      - venv/
  variables:
    PIP_CACHE_DIR: "$CI_PROJECT_DIR/.cache/pip"
  before_script:
    - python -m venv venv
    - source venv/bin/activate
    - pip install -r requirements.txt
  script:
    - pytest
{% elif language == "javascript" or language == "typescript" %}
test:
  image: node:20
  cache:
    key: ${CI_COMMIT_REF_SLUG}
    paths:
      - node_modules/
  before_script:
    - npm ci
  script:
    - npm test
{% endif %}
```

### Merge Request Pipelines

```yaml
# Only run on merge requests
workflow:
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH

test:
  stage: test
  script:
    - pytest
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
      changes:
        - "**/*.py"
        - requirements*.txt
```

{% endif %}

---

{% if deployment_target == "docker" %}
## Docker Deployment Pipeline

### Build and Push

{% if platform == "github-actions" %}
```yaml
name: Docker Build and Push

on:
  push:
    branches: [main]
    tags: ['v*']

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to Container Registry
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
            type=ref,event=pr
            type=semver,pattern={{version}}
            type=sha

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

      - name: Deploy to staging
        if: github.ref == 'refs/heads/main'
        run: |
          # Trigger deployment via webhook or kubectl
          curl -X POST ${{ secrets.DEPLOY_WEBHOOK_URL }}
```
{% endif %}

### Multi-Stage Dockerfile

```dockerfile
# Build stage
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# Production stage
FROM python:3.11-slim as production

WORKDIR /app

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
USER app

# Copy wheels from builder
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache-dir /wheels/*

# Copy application
COPY --chown=app:app . .

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

{% elif deployment_target == "kubernetes" %}
## Kubernetes Deployment Pipeline

### GitOps with ArgoCD

{% if platform == "github-actions" %}
```yaml
name: Deploy to Kubernetes

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    outputs:
      image-tag: ${{ steps.meta.outputs.version }}

    steps:
      - uses: actions/checkout@v4

      - name: Build and push image
        id: meta
        # ... (same as Docker build above)

  update-manifests:
    needs: build
    runs-on: ubuntu-latest

    steps:
      - name: Checkout manifests repo
        uses: actions/checkout@v4
        with:
          repository: myorg/k8s-manifests
          token: ${{ secrets.MANIFEST_REPO_TOKEN }}

      - name: Update image tag
        run: |
          cd apps/my-app/overlays/staging
          kustomize edit set image my-app=ghcr.io/myorg/my-app:${{ needs.build.outputs.image-tag }}

      - name: Commit and push
        run: |
          git config user.name "GitHub Actions"
          git config user.email "actions@github.com"
          git add .
          git commit -m "Update my-app to ${{ needs.build.outputs.image-tag }}"
          git push
```
{% endif %}

### Kubernetes Manifests

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-app
  template:
    metadata:
      labels:
        app: my-app
    spec:
      containers:
        - name: my-app
          image: ghcr.io/myorg/my-app:latest
          ports:
            - containerPort: 8000
          resources:
            requests:
              memory: "128Mi"
              cpu: "100m"
            limits:
              memory: "256Mi"
              cpu: "500m"
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 10
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /ready
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 5
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: my-app-secrets
                  key: database-url
```

{% elif deployment_target == "serverless" %}
## Serverless Deployment

### AWS Lambda with SAM

{% if platform == "github-actions" %}
```yaml
name: Deploy to AWS Lambda

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    permissions:
      id-token: write
      contents: read

    steps:
      - uses: actions/checkout@v4

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789:role/github-actions
          aws-region: us-east-1

      - name: Setup SAM
        uses: aws-actions/setup-sam@v2

      - name: Build
        run: sam build

      - name: Deploy to staging
        run: |
          sam deploy \
            --stack-name my-app-staging \
            --parameter-overrides Environment=staging \
            --no-confirm-changeset \
            --no-fail-on-empty-changeset

      - name: Integration tests
        run: npm run test:integration
        env:
          API_URL: ${{ steps.deploy.outputs.api-url }}

      - name: Deploy to production
        if: success()
        run: |
          sam deploy \
            --stack-name my-app-production \
            --parameter-overrides Environment=production \
            --no-confirm-changeset
```
{% endif %}

{% elif deployment_target == "static" %}
## Static Site Deployment

### Deploy to Cloudflare Pages / Vercel / Netlify

{% if platform == "github-actions" %}
```yaml
name: Deploy Static Site

on:
  push:
    branches: [main]
  pull_request:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm

      - name: Install dependencies
        run: npm ci

      - name: Build
        run: npm run build

      - name: Deploy to Cloudflare Pages
        uses: cloudflare/pages-action@v1
        with:
          apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          accountId: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
          projectName: my-site
          directory: dist
          gitHubToken: ${{ secrets.GITHUB_TOKEN }}

      # Or deploy to Vercel
      - name: Deploy to Vercel
        uses: vercel/actions@v1
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
```
{% endif %}

{% endif %}

---

## Pipeline Best Practices

### 1. Fail Fast

```yaml
# Run quick checks first
jobs:
  quick-checks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Lint commit messages
        run: npx commitlint --from HEAD~1
      - name: Check formatting
        run: npm run format:check

  test:
    needs: quick-checks  # Only run if quick checks pass
    # ...
```

### 2. Parallel Execution

```yaml
jobs:
  lint:
    runs-on: ubuntu-latest
    # ...

  unit-test:
    runs-on: ubuntu-latest
    # Runs in parallel with lint

  integration-test:
    runs-on: ubuntu-latest
    # Runs in parallel with lint and unit-test

  build:
    needs: [lint, unit-test, integration-test]
    # Only runs after all above complete
```

### 3. Matrix Builds

```yaml
jobs:
  test:
    strategy:
      fail-fast: false  # Don't cancel other jobs if one fails
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        node: [18, 20]
        exclude:
          - os: windows-latest
            node: 18
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node }}
```

### 4. Conditional Execution

```yaml
jobs:
  deploy:
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'

    steps:
      - name: Deploy to staging
        run: ./deploy.sh staging

      - name: Run smoke tests
        run: npm run test:smoke

      - name: Deploy to production
        if: success()  # Only if smoke tests pass
        run: ./deploy.sh production
```

---

## Security Checklist

```
Secrets:
- [ ] Use OIDC instead of long-lived credentials
- [ ] Secrets are scoped to environments
- [ ] No secrets in logs (auto-masked)
- [ ] Rotate secrets regularly

Permissions:
- [ ] Minimal permissions (read-only where possible)
- [ ] Branch protection on main
- [ ] Required reviews for deployments
- [ ] Environment protection rules

Supply Chain:
- [ ] Pin action versions with SHA
- [ ] Dependabot enabled
- [ ] SBOM generated
- [ ] Container images scanned
```
