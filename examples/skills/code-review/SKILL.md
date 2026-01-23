---
name: code-review
description: |
  Systematic code review methodology for improving code quality, catching bugs,
  and sharing knowledge. Use when reviewing pull requests, conducting peer reviews,
  or evaluating code changes. Focuses on actionable feedback and collaborative improvement.
license: MIT
allowed-tools: Read Edit Bash
version: 1.0.0
tags: [code-review, quality, collaboration, best-practices]
category: development/quality
variables:
  language:
    type: string
    description: Primary programming language
    enum: [python, javascript, typescript, go, rust, java]
    default: python
  review_depth:
    type: string
    description: Level of review thoroughness
    enum: [quick, standard, thorough]
    default: standard
  focus_area:
    type: string
    description: Specific area to focus on
    enum: [all, security, performance, maintainability, testing]
    default: all
---

# Code Review Guide

## Review Philosophy

**Be kind, be specific, be constructive.**

Reviews are conversations, not judgments. The goal is better code AND better developers.

> "The best code review comment explains WHY, not just WHAT."

---

## Review Checklist

{% if review_depth == "quick" %}
### Quick Review (5-10 minutes)

Focus on high-impact issues only:

- [ ] **Does it work?** - Logic correctness, edge cases
- [ ] **Is it safe?** - No obvious security issues
- [ ] **Is it clear?** - Can you understand it in one read?
- [ ] **Tests pass?** - CI is green

{% elif review_depth == "standard" %}
### Standard Review (15-30 minutes)

#### 1. Correctness
- [ ] Logic handles all cases correctly
- [ ] Edge cases are considered
- [ ] Error handling is appropriate
- [ ] No obvious bugs or typos

#### 2. Security
- [ ] No hardcoded secrets
- [ ] Input validation present
- [ ] No injection vulnerabilities
- [ ] Proper authentication/authorization

#### 3. Design
- [ ] Single responsibility principle
- [ ] Appropriate abstraction level
- [ ] No unnecessary complexity
- [ ] Consistent with codebase patterns

#### 4. Quality
- [ ] Clear naming conventions
- [ ] Adequate comments for complex logic
- [ ] No dead code
- [ ] Reasonable function/file sizes

#### 5. Testing
- [ ] Tests cover new functionality
- [ ] Tests cover edge cases
- [ ] Tests are maintainable

{% else %}
### Thorough Review (30-60 minutes)

#### Phase 1: Context (5 min)
- [ ] Understand the PR description and linked issues
- [ ] Review the overall architecture impact
- [ ] Check if this is the right approach

#### Phase 2: High-Level Review (10 min)
- [ ] File structure makes sense
- [ ] Changes are cohesive (single purpose)
- [ ] No scope creep
- [ ] Breaking changes documented

#### Phase 3: Detailed Review (30 min)
- [ ] Line-by-line correctness
- [ ] Security implications
- [ ] Performance considerations
- [ ] Error handling completeness
- [ ] Logging and observability
- [ ] Backwards compatibility

#### Phase 4: Testing Review (10 min)
- [ ] Test coverage is adequate
- [ ] Tests are meaningful (not just coverage)
- [ ] Integration tests where needed
- [ ] Edge cases covered

#### Phase 5: Documentation (5 min)
- [ ] README updates if needed
- [ ] API documentation current
- [ ] Inline comments for complex logic
- [ ] CHANGELOG updated

{% endif %}

---

{% if focus_area == "security" or focus_area == "all" %}
## Security Review Focus

### Critical Checks

{% if language == "python" %}
```python
# CHECK: SQL Injection
# BAD
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")

# GOOD
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))

# CHECK: Command Injection
# BAD
os.system(f"echo {user_input}")

# GOOD
subprocess.run(["echo", user_input], shell=False)

# CHECK: Path Traversal
# BAD
open(f"/uploads/{filename}")

# GOOD
safe_path = Path("/uploads") / Path(filename).name
open(safe_path)
```
{% elif language == "javascript" or language == "typescript" %}
```javascript
// CHECK: XSS
// BAD
element.innerHTML = userInput;

// GOOD
element.textContent = userInput;

// CHECK: Prototype Pollution
// BAD
Object.assign(target, JSON.parse(userInput));

// GOOD
const safe = JSON.parse(userInput);
if (safe.__proto__ || safe.constructor) throw new Error('Invalid');

// CHECK: Path Traversal
// BAD
fs.readFile(`./uploads/${filename}`);

// GOOD
const safePath = path.join('./uploads', path.basename(filename));
```
{% endif %}

### Security Questions
1. Is user input validated/sanitized at entry points?
2. Are secrets properly managed (not in code)?
3. Is authentication/authorization checked?
4. Are error messages safe (no sensitive info leakage)?
5. Is data encrypted in transit and at rest?

{% endif %}

{% if focus_area == "performance" or focus_area == "all" %}
## Performance Review Focus

### Common Issues

{% if language == "python" %}
```python
# N+1 Query Problem
# BAD
for user in users:
    orders = db.query(Order).filter(Order.user_id == user.id).all()

# GOOD
orders = db.query(Order).filter(Order.user_id.in_([u.id for u in users])).all()

# Unnecessary Iteration
# BAD
result = []
for item in items:
    result.append(transform(item))

# GOOD
result = [transform(item) for item in items]

# Memory Issues
# BAD
data = file.read()  # Loads entire file

# GOOD
for line in file:  # Streams line by line
    process(line)
```
{% elif language == "javascript" or language == "typescript" %}
```javascript
// Blocking the Event Loop
// BAD
const result = heavyComputation(data);

// GOOD
const result = await runInWorker(heavyComputation, data);

// Memory Leaks
// BAD
element.addEventListener('click', handler);
// Never removed!

// GOOD
const controller = new AbortController();
element.addEventListener('click', handler, { signal: controller.signal });
// Later: controller.abort();
```
{% endif %}

### Performance Questions
1. Are there O(n²) or worse algorithms that could be optimized?
2. Is caching used appropriately?
3. Are database queries efficient (indexes, batching)?
4. Is pagination implemented for large datasets?
5. Are there potential memory leaks?

{% endif %}

{% if focus_area == "maintainability" or focus_area == "all" %}
## Maintainability Review Focus

### Code Clarity

```
Ask yourself: "Will someone understand this in 6 months?"
```

**Naming Quality:**
- Variables describe their content
- Functions describe their action
- Classes describe their responsibility
- No abbreviations without context

**Structure Quality:**
- Functions do one thing
- Files have clear purposes
- Modules have minimal coupling
- Dependencies are explicit

### Maintainability Questions
1. Is the code self-documenting?
2. Are magic numbers/strings extracted as constants?
3. Is error handling consistent with the codebase?
4. Are there any "clever" solutions that should be simplified?
5. Would a new team member understand this?

{% endif %}

---

## Writing Good Review Comments

### Comment Templates

**Suggestion:**
```
Consider using X instead of Y here because [reason].
This would [benefit].
```

**Question:**
```
I'm curious about the choice to do X.
Was Y considered? I ask because [context].
```

**Issue:**
```
This could cause [problem] when [condition].
Suggested fix: [solution]
```

**Praise:**
```
Nice approach here! The [specific thing]
makes this really clear/efficient/elegant.
```

### Severity Levels

Use prefixes to indicate importance:

- `[BLOCKER]` - Must fix before merge
- `[IMPORTANT]` - Should fix, but can discuss
- `[NIT]` - Minor suggestion, optional
- `[QUESTION]` - Seeking understanding

---

## Anti-Patterns to Avoid

### As a Reviewer

❌ **Bikeshedding** - Spending time on trivial style issues
❌ **Gatekeeping** - Blocking for non-essential preferences
❌ **Drive-by comments** - Criticizing without explaining
❌ **Scope creep** - Requesting unrelated changes
❌ **Ego battles** - Making it personal

### As an Author

❌ **Defensive responses** - Taking feedback personally
❌ **Giant PRs** - Changes too large to review properly
❌ **No context** - Missing description of what/why
❌ **Ignoring feedback** - Dismissing without discussion

---

## Review Workflow

1. **Author prepares**
   - Self-review before requesting
   - Clear PR description
   - Link to relevant issues
   - Highlight areas needing attention

2. **Reviewer examines**
   - Understand context first
   - Review systematically
   - Comment constructively
   - Approve or request changes

3. **Discussion**
   - Author responds to comments
   - Discuss disagreements
   - Reach consensus

4. **Resolution**
   - Author addresses feedback
   - Reviewer re-reviews changes
   - Merge when approved
