---
name: git-workflow
description: |
  Best practices for Git version control workflows. Use when managing branches,
  writing commits, creating pull requests, or establishing team Git conventions.
  Covers branching strategies, commit hygiene, and collaborative workflows.
license: MIT
allowed-tools: Read Edit Bash
version: 1.0.0
tags: [git, version-control, workflow, collaboration]
category: development/tooling
variables:
  branching_strategy:
    type: string
    description: Team's branching model
    enum: [github-flow, gitflow, trunk-based]
    default: github-flow
  team_size:
    type: string
    description: Size of the development team
    enum: [solo, small, large]
    default: small
---

# Git Workflow Guide

## Core Principles

1. **Commit early, commit often** - Small, focused commits are easier to review and revert
2. **Write for humans** - Commit messages are documentation for your future self
3. **Keep history clean** - A readable history is a valuable debugging tool
4. **Branch for isolation** - Never commit directly to main/master

---

{% if branching_strategy == "github-flow" %}
## GitHub Flow

Simple, effective for continuous deployment.

```
main ─────●─────●─────●─────●─────●─────→
           \         /
feature     ●───●───●
```

### Workflow

1. **Create branch** from `main`
   ```bash
   git checkout main
   git pull origin main
   git checkout -b feature/user-authentication
   ```

2. **Make commits** with clear messages
   ```bash
   git add -p  # Stage interactively
   git commit -m "Add login form component"
   ```

3. **Push and create PR**
   ```bash
   git push -u origin feature/user-authentication
   gh pr create --fill
   ```

4. **Review, approve, merge**
   - Squash merge for clean history
   - Delete branch after merge

### Branch Naming

```
feature/   - New functionality
fix/       - Bug fixes
docs/      - Documentation only
refactor/  - Code restructuring
test/      - Test additions/changes
```

{% elif branching_strategy == "gitflow" %}
## Git Flow

Structured model for scheduled releases.

```
main     ───●───────────────────●───────→
            │                   │
release     │     ●─────●───────┤
            │    /             \│
develop  ───●───●───●───●───●───●───●───→
               /   \   /
feature       ●─────●─●
```

### Long-lived Branches

- `main` - Production-ready code only
- `develop` - Integration branch for features

### Short-lived Branches

- `feature/*` - New features (from develop)
- `release/*` - Release preparation (from develop)
- `hotfix/*` - Production fixes (from main)

### Workflow

```bash
# Start feature
git checkout develop
git checkout -b feature/new-dashboard

# Complete feature
git checkout develop
git merge --no-ff feature/new-dashboard
git branch -d feature/new-dashboard

# Start release
git checkout develop
git checkout -b release/1.2.0

# Complete release
git checkout main
git merge --no-ff release/1.2.0
git tag -a v1.2.0 -m "Release 1.2.0"
git checkout develop
git merge --no-ff release/1.2.0
```

{% elif branching_strategy == "trunk-based" %}
## Trunk-Based Development

Optimized for continuous integration.

```
main ───●───●───●───●───●───●───●───●───→
         \─●─/   \─●─/
      short-lived branches
```

### Principles

- **Main is always deployable**
- **Branches live < 1 day**
- **Feature flags for incomplete work**
- **Frequent integration (multiple times/day)**

### Workflow

```bash
# Start work (branch is optional for small changes)
git checkout main
git pull
git checkout -b quick-fix

# Make small, complete change
git add .
git commit -m "Fix null pointer in user service"

# Integrate immediately
git checkout main
git pull
git merge quick-fix
git push
git branch -d quick-fix
```

### Feature Flags

```python
# For incomplete features
if feature_flags.is_enabled('new_checkout'):
    return new_checkout_flow(cart)
else:
    return legacy_checkout(cart)
```

{% endif %}

---

## Commit Message Standards

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `style` | Formatting, no code change |
| `refactor` | Code change, no feature/fix |
| `perf` | Performance improvement |
| `test` | Adding/updating tests |
| `chore` | Build, tooling, etc. |

### Examples

**Good commits:**
```
feat(auth): add OAuth2 login with Google

Implement Google OAuth2 flow using passport.js.
Users can now sign in with their Google accounts.

Closes #123
```

```
fix(api): handle null response from payment provider

The payment API occasionally returns null instead of
an error object. Added defensive check to prevent
crash in checkout flow.

Fixes #456
```

**Bad commits:**
```
# Too vague
fix bug

# No context
update code

# Multiple unrelated changes
fix login and update styles and add tests
```

---

## Common Operations

### Undo Last Commit (Keep Changes)

```bash
git reset --soft HEAD~1
```

### Undo Last Commit (Discard Changes)

```bash
git reset --hard HEAD~1
```

### Fix Last Commit Message

```bash
git commit --amend -m "New message"
```

### Add to Last Commit

```bash
git add forgotten_file.py
git commit --amend --no-edit
```

### Interactive Rebase (Clean History)

```bash
# Rebase last 3 commits
git rebase -i HEAD~3

# In editor:
# pick   abc1234 First commit
# squash def5678 Fix typo
# squash ghi9012 More fixes
```

### Cherry-Pick Specific Commit

```bash
git cherry-pick abc1234
```

### Stash Work in Progress

```bash
git stash save "WIP: user dashboard"
git stash list
git stash pop
```

---

{% if team_size == "large" %}
## Large Team Conventions

### Protected Branches

```yaml
# Branch protection rules
main:
  - Require pull request reviews (2+)
  - Require status checks to pass
  - Require signed commits
  - No force pushes
  - No deletions
```

### Code Owners

```
# CODEOWNERS file
/src/auth/       @security-team
/src/payments/   @payments-team
/docs/           @docs-team
*.sql            @dba-team
```

### Merge Strategy

- **Squash merge** for feature branches (clean history)
- **Merge commit** for release branches (preserve context)
- **Rebase** prohibited on shared branches

{% elif team_size == "small" %}
## Small Team Conventions

### Simplified Rules

- 1 reviewer minimum for PRs
- Squash merge by default
- Branch protection on main only
- Trust-based workflow

### Communication

```bash
# Mention in commit when relevant
git commit -m "fix(api): rate limiting

Discussed with @teammate - using token bucket algorithm.
See Slack thread: #backend-2024-01-15"
```

{% else %}
## Solo Developer Workflow

### Still Use Branches

Even solo, branches help:
- Experiment safely
- Keep main deployable
- Track feature progress

### Commit Discipline

Write messages for future you:
```bash
# Bad - you won't remember
git commit -m "fix"

# Good - context preserved
git commit -m "fix(export): handle UTF-8 in CSV export

Excel was showing garbled characters for non-ASCII names.
Added BOM and explicit UTF-8 encoding."
```

{% endif %}

---

## Troubleshooting

### Accidentally Committed to Wrong Branch

```bash
# Move commit to correct branch
git checkout correct-branch
git cherry-pick abc1234
git checkout wrong-branch
git reset --hard HEAD~1
```

### Merge Conflicts

```bash
# See conflicting files
git status

# After resolving conflicts
git add resolved_file.py
git commit  # Completes the merge
```

### Recover Deleted Branch

```bash
# Find the commit
git reflog

# Recreate branch
git checkout -b recovered-branch abc1234
```

### Reset Remote to Match Local

```bash
# DANGER: Only if you're sure!
git push --force-with-lease origin branch-name
```

---

## Git Aliases

Add to `~/.gitconfig`:

```ini
[alias]
    st = status -sb
    co = checkout
    br = branch
    ci = commit
    lg = log --oneline --graph --decorate -20
    unstage = reset HEAD --
    last = log -1 HEAD
    undo = reset --soft HEAD~1
```
