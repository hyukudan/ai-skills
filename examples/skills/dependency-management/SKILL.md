---
name: dependency-management
description: |
  Guide for managing project dependencies securely and effectively. Use when
  updating dependencies, handling security vulnerabilities, managing lockfiles,
  or setting up dependency policies. Covers security audits, update strategies,
  and supply chain security.
version: 1.0.0
tags: [dependencies, security, npm, pip, cargo, supply-chain]
category: development/dependencies
trigger_phrases:
  - "update dependencies"
  - "security vulnerability"
  - "npm audit"
  - "pip-audit"
  - "dependabot"
  - "renovate"
  - "lock file"
  - "package update"
  - "CVE fix"
  - "supply chain"
variables:
  language:
    type: string
    description: Primary programming language/ecosystem
    enum: [python, javascript, go, rust, java]
    default: python
  strategy:
    type: string
    description: Update strategy preference
    enum: [conservative, balanced, aggressive]
    default: balanced
  automation:
    type: string
    description: Level of automation desired
    enum: [manual, semi-auto, fully-auto]
    default: semi-auto
---

# Dependency Management Guide

## Dependency Philosophy

**Dependencies are a liability, not just an asset.** Every dependency you add:
- Increases attack surface
- Adds maintenance burden
- Creates potential for breaking changes
- Requires trust in maintainers

> "The best dependency is no dependency. The second best is one that's well-maintained, widely used, and actively developed."

---

## Evaluation Criteria

Before adding a dependency, check:

```
Security:
- [ ] No known vulnerabilities (check CVE databases)
- [ ] Maintained in last 6 months
- [ ] Multiple maintainers (bus factor > 1)
- [ ] Signed releases/commits

Quality:
- [ ] Test coverage visible
- [ ] Documentation exists
- [ ] Active issue response
- [ ] Semantic versioning followed

Necessity:
- [ ] Can't easily implement ourselves (< 100 lines)
- [ ] Significantly more robust than DIY
- [ ] Will be used in multiple places
- [ ] Doesn't pull in massive transitive deps
```

### Dependency Health Check

```bash
{% if language == "python" %}
# Check for vulnerabilities
pip-audit

# Check outdated packages
pip list --outdated

# Show dependency tree
pipdeptree

# Check package info
pip show <package>
{% elif language == "javascript" %}
# Check for vulnerabilities
npm audit

# Check outdated packages
npm outdated

# Show dependency tree
npm ls

# Check package info
npm info <package>
{% elif language == "go" %}
# Check for vulnerabilities
govulncheck ./...

# Check outdated packages
go list -u -m all

# Show dependency tree
go mod graph

# Tidy dependencies
go mod tidy
{% elif language == "rust" %}
# Check for vulnerabilities
cargo audit

# Check outdated packages
cargo outdated

# Show dependency tree
cargo tree

# Check package info
cargo info <crate>
{% endif %}
```

---

{% if language == "python" %}
## Python Dependency Management

### Project Setup with pyproject.toml

```toml
# pyproject.toml
[project]
name = "my-project"
version = "1.0.0"
requires-python = ">=3.10"

dependencies = [
    "fastapi>=0.100,<1.0",      # Pin major version
    "pydantic>=2.0,<3.0",
    "httpx>=0.24",              # Minimum version only
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "ruff>=0.1",
    "mypy>=1.0",
]

[tool.pip-tools]
generate-hashes = true          # Enable hash checking
```

### Managing Lock Files

```bash
# Using pip-tools (recommended)
pip install pip-tools

# Generate locked requirements from pyproject.toml
pip-compile pyproject.toml -o requirements.txt

# Generate with hashes for security
pip-compile --generate-hashes pyproject.toml -o requirements.txt

# Update a specific package
pip-compile --upgrade-package fastapi pyproject.toml

# Update all packages
pip-compile --upgrade pyproject.toml

# Install from lock file
pip-sync requirements.txt
```

### Using uv (Modern Alternative)

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment
uv venv

# Install dependencies
uv pip install -r requirements.txt

# Add new dependency
uv pip install fastapi

# Lock dependencies
uv pip compile pyproject.toml -o requirements.txt
```

### Security Scanning

```bash
# Using pip-audit
pip install pip-audit
pip-audit

# Using safety
pip install safety
safety check

# In CI/CD
pip-audit --require-hashes -r requirements.txt --strict
```

{% elif language == "javascript" %}
## JavaScript/Node.js Dependency Management

### Package.json Best Practices

```json
{
  "name": "my-project",
  "version": "1.0.0",
  "engines": {
    "node": ">=18.0.0"
  },
  "dependencies": {
    "express": "^4.18.0",
    "lodash": "^4.17.21"
  },
  "devDependencies": {
    "jest": "^29.0.0",
    "eslint": "^8.0.0"
  },
  "overrides": {
    "vulnerable-package": "^2.0.0"
  }
}
```

### Lock File Management

```bash
# npm (package-lock.json)
npm ci                    # Install from lock file (CI)
npm install               # Update lock file
npm update                # Update within semver range
npm update lodash         # Update specific package

# pnpm (pnpm-lock.yaml)
pnpm install --frozen-lockfile  # CI install
pnpm update                     # Update packages
pnpm update lodash              # Update specific

# yarn (yarn.lock)
yarn install --immutable        # CI install
yarn up                         # Update packages
yarn up lodash                  # Update specific
```

### Security Scanning

```bash
# npm built-in audit
npm audit
npm audit fix              # Auto-fix vulnerabilities
npm audit fix --force      # Force major updates (careful!)

# Show detailed info
npm audit --json

# In CI - fail on vulnerabilities
npm audit --audit-level=high
```

### Handling Vulnerabilities

```json
// package.json - Override transitive dependency
{
  "overrides": {
    "vulnerable-transitive-dep": "^2.0.0"
  }
}

// Or in npm v8.3+
{
  "overrides": {
    "some-package": {
      "vulnerable-dep": "^2.0.0"
    }
  }
}
```

{% elif language == "go" %}
## Go Dependency Management

### go.mod Best Practices

```go
// go.mod
module github.com/myorg/myproject

go 1.22

require (
    github.com/gin-gonic/gin v1.9.1
    github.com/jackc/pgx/v5 v5.5.0
)

// Replace for local development or forks
replace github.com/broken/pkg => github.com/myorg/pkg-fork v1.0.0

// Exclude vulnerable versions
exclude github.com/vulnerable/pkg v1.0.0
```

### Managing Dependencies

```bash
# Add dependency
go get github.com/gin-gonic/gin@v1.9.1

# Update dependency
go get -u github.com/gin-gonic/gin

# Update all dependencies
go get -u ./...

# Update to specific version
go get github.com/gin-gonic/gin@v1.9.0

# Remove unused dependencies
go mod tidy

# Verify dependencies
go mod verify

# Download dependencies
go mod download
```

### Security Scanning

```bash
# Install govulncheck
go install golang.org/x/vuln/cmd/govulncheck@latest

# Scan for vulnerabilities
govulncheck ./...

# Scan specific binary
govulncheck -mode=binary ./myapp
```

{% elif language == "rust" %}
## Rust Dependency Management

### Cargo.toml Best Practices

```toml
[package]
name = "my-project"
version = "1.0.0"
edition = "2021"
rust-version = "1.70"

[dependencies]
serde = { version = "1.0", features = ["derive"] }
tokio = { version = "1", features = ["full"] }
# Exact version for critical deps
openssl = "=0.10.60"

[dev-dependencies]
criterion = "0.5"

[patch.crates-io]
# Patch vulnerable crate
vulnerable-crate = { git = "https://github.com/org/vulnerable-crate", branch = "fix" }
```

### Managing Dependencies

```bash
# Add dependency
cargo add serde --features derive

# Update dependencies
cargo update

# Update specific crate
cargo update -p serde

# Check outdated
cargo install cargo-outdated
cargo outdated

# Show dependency tree
cargo tree
cargo tree -d  # Show duplicates
```

### Security Scanning

```bash
# Install cargo-audit
cargo install cargo-audit

# Scan for vulnerabilities
cargo audit

# Fix vulnerabilities (when possible)
cargo audit fix

# Deny specific advisories in CI
cargo audit --deny warnings
```

{% endif %}

---

## Update Strategies

{% if strategy == "conservative" %}
### Conservative Strategy

**Principle**: Only update for security fixes or critical bugs.

```yaml
Approach:
  security_updates: immediate
  bug_fixes: monthly review
  minor_versions: quarterly review
  major_versions: annual review or when EOL

Automation:
  - Auto-merge: security patches only
  - Auto-PR: all updates for review
  - Breaking changes: manual review required
```

**Best for**: Production systems, regulated industries, risk-averse teams.

{% elif strategy == "balanced" %}
### Balanced Strategy

**Principle**: Stay reasonably current while minimizing risk.

```yaml
Approach:
  security_updates: immediate (auto-merge if tests pass)
  patch_versions: weekly (auto-merge if tests pass)
  minor_versions: bi-weekly review
  major_versions: quarterly planning

Automation:
  - Auto-merge: security + patch updates
  - Auto-PR: minor updates grouped weekly
  - Breaking changes: scheduled upgrade sprints
```

**Best for**: Most production applications, balanced teams.

{% else %}
### Aggressive Strategy

**Principle**: Stay on latest versions to avoid technical debt.

```yaml
Approach:
  security_updates: immediate
  all_updates: daily/weekly
  major_versions: as soon as stable

Automation:
  - Auto-merge: all updates if tests pass
  - Continuous: Dependabot/Renovate running daily
  - Breaking changes: embrace and adapt quickly
```

**Best for**: Greenfield projects, fast-moving teams, libraries.

{% endif %}

---

{% if automation == "semi-auto" or automation == "fully-auto" %}
## Automated Dependency Updates

### Dependabot Configuration

```yaml
# .github/dependabot.yml
version: 2
updates:
{% if language == "python" %}
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
    open-pull-requests-limit: 10
    groups:
      development-dependencies:
        dependency-type: "development"
      production-dependencies:
        dependency-type: "production"
        update-types:
          - "minor"
          - "patch"
    ignore:
      - dependency-name: "aws-*"
        update-types: ["version-update:semver-major"]
{% elif language == "javascript" %}
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
    groups:
      dev-dependencies:
        dependency-type: "development"
      eslint:
        patterns:
          - "eslint*"
          - "@typescript-eslint/*"
    ignore:
      - dependency-name: "typescript"
        update-types: ["version-update:semver-major"]
{% elif language == "go" %}
  - package-ecosystem: "gomod"
    directory: "/"
    schedule:
      interval: "weekly"
    groups:
      aws-sdk:
        patterns:
          - "github.com/aws/aws-sdk-go-v2/*"
{% endif %}

  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
```

### Renovate Configuration

```json
// renovate.json
{
  "$schema": "https://docs.renovatebot.com/renovate-schema.json",
  "extends": [
    "config:recommended",
    "group:recommended",
    ":separateMajorReleases",
    ":combinePatchMinorReleases"
  ],
  "schedule": ["before 7am on Monday"],
  "prHourlyLimit": 5,
  "prConcurrentLimit": 10,
  "packageRules": [
    {
      "matchPackagePatterns": ["*"],
      "matchUpdateTypes": ["minor", "patch"],
      "groupName": "all non-major dependencies",
      "groupSlug": "all-minor-patch",
      "automerge": true
    },
    {
      "matchPackagePatterns": ["*"],
      "matchUpdateTypes": ["major"],
      "dependencyDashboardApproval": true
    },
    {
      "matchDepTypes": ["devDependencies"],
      "automerge": true
    }
  ],
  "vulnerabilityAlerts": {
    "enabled": true,
    "labels": ["security"]
  }
}
```

{% if automation == "fully-auto" %}
### Auto-Merge Configuration

```yaml
# .github/workflows/auto-merge.yml
name: Auto Merge Dependabot

on:
  pull_request:

permissions:
  contents: write
  pull-requests: write

jobs:
  auto-merge:
    runs-on: ubuntu-latest
    if: github.actor == 'dependabot[bot]'
    steps:
      - name: Fetch Dependabot metadata
        id: metadata
        uses: dependabot/fetch-metadata@v2
        with:
          github-token: "${{ secrets.GITHUB_TOKEN }}"

      - name: Auto-merge patch and minor updates
        if: steps.metadata.outputs.update-type == 'version-update:semver-patch' || steps.metadata.outputs.update-type == 'version-update:semver-minor'
        run: gh pr merge --auto --squash "$PR_URL"
        env:
          PR_URL: ${{ github.event.pull_request.html_url }}
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      - name: Auto-merge security updates
        if: steps.metadata.outputs.dependency-type == 'direct:production' && steps.metadata.outputs.update-type == 'version-update:semver-patch'
        run: gh pr merge --auto --squash "$PR_URL"
        env:
          PR_URL: ${{ github.event.pull_request.html_url }}
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```
{% endif %}

{% endif %}

---

## Supply Chain Security

### SLSA Framework

```
SLSA Levels:
Level 1: Documentation of build process
Level 2: Tamper resistance of build service
Level 3: Hardened build platform
Level 4: Two-person review of all changes

Actions:
- [ ] Use lock files with hashes
- [ ] Pin dependencies to exact versions for production
- [ ] Verify signatures on packages
- [ ] Use private registry/mirror for critical deps
- [ ] Generate and verify SBOMs
```

### SBOM Generation

```bash
{% if language == "python" %}
# Using cyclonedx
pip install cyclonedx-bom
cyclonedx-py --format json -o sbom.json

# Using syft
syft . -o cyclonedx-json > sbom.json
{% elif language == "javascript" %}
# Using cyclonedx
npx @cyclonedx/cyclonedx-npm --output-file sbom.json

# Using syft
syft . -o cyclonedx-json > sbom.json
{% elif language == "go" %}
# Using cyclonedx
go install github.com/CycloneDX/cyclonedx-gomod/cmd/cyclonedx-gomod@latest
cyclonedx-gomod mod -json -output sbom.json

# Using syft
syft . -o cyclonedx-json > sbom.json
{% endif %}
```

### Security Policies

```yaml
# Example: dependency security policy
policies:
  allowed_licenses:
    - MIT
    - Apache-2.0
    - BSD-2-Clause
    - BSD-3-Clause
    - ISC

  blocked_packages:
    - event-stream  # Known malicious
    - colors@>1.4.0  # Sabotaged version

  vulnerability_thresholds:
    block: critical
    warn: high

  required_checks:
    - signature_verification
    - hash_verification
    - license_compliance
```

---

## Handling Vulnerabilities

### Response Playbook

```
1. ASSESS
   - What's the severity? (CVSS score)
   - Are we actually affected? (Check if vulnerable code path is used)
   - Is there an exploit in the wild?

2. PRIORITIZE
   Critical + Exploited: Immediate action
   Critical + No exploit: Within 24 hours
   High: Within 1 week
   Medium: Within 1 month
   Low: Next scheduled update

3. REMEDIATE
   Option A: Update to patched version
   Option B: Apply workaround if no patch
   Option C: Remove dependency if not critical
   Option D: Accept risk (documented decision)

4. VERIFY
   - Run security scan to confirm fix
   - Test that application still works
   - Deploy to production
```

### When Updates Break Things

```bash
# Scenario: Security update breaks your code

# 1. Check what changed
{% if language == "python" %}
pip show <package>  # Check version
# Read CHANGELOG for breaking changes
{% elif language == "javascript" %}
npm info <package>
npm diff <package>@<old> <package>@<new>
{% endif %}

# 2. Options:
# A) Fix your code to work with new version
# B) Pin to last working version (temporary!)
# C) Fork and patch the package
# D) Find alternative package

# 3. If pinning, create a ticket to revisit
# Never leave vulnerable versions pinned indefinitely
```

---

## Dependency Review Checklist

### Before Adding

```
- [ ] Is this dependency necessary?
- [ ] What's the maintenance status?
- [ ] How many transitive dependencies?
- [ ] License compatible?
- [ ] No known vulnerabilities?
- [ ] Reasonable bundle size? (frontend)
- [ ] Trusted maintainers?
```

### Regular Audit

```
Monthly:
- [ ] Run vulnerability scan
- [ ] Review and merge pending updates
- [ ] Check for deprecated packages

Quarterly:
- [ ] Full dependency audit
- [ ] Review for unused dependencies
- [ ] Check license compliance
- [ ] Update major versions if needed

Annually:
- [ ] Evaluate alternatives for major deps
- [ ] Review dependency policy
- [ ] Plan major version upgrades
```
