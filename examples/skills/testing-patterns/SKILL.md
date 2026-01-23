---
name: testing-patterns
description: |
  Testing strategies and patterns for writing effective, maintainable tests.
  Use when writing unit tests, integration tests, or establishing testing
  conventions. Covers test structure, mocking, fixtures, and common patterns.
license: MIT
allowed-tools: Read Edit Bash
version: 1.0.0
tags: [testing, unit-tests, tdd, quality]
category: development/testing
variables:
  language:
    type: string
    description: Programming language
    enum: [python, javascript, typescript]
    default: python
  test_type:
    type: string
    description: Type of testing focus
    enum: [unit, integration, e2e, all]
    default: all
---

# Testing Patterns Guide

## Testing Philosophy

**Tests are specifications.** They document what your code should do.

> "Write tests that give you confidence to deploy on Friday afternoon."

### The Testing Pyramid

```
        /\
       /  \        E2E Tests (few)
      /────\       - Full system flows
     /      \      - Slow, expensive
    /────────\
   /          \    Integration Tests (some)
  /────────────\   - Component interactions
 /              \  - Medium speed
/────────────────\
      Unit Tests (many)
      - Single functions/classes
      - Fast, isolated
```

---

{% if test_type == "unit" or test_type == "all" %}
## Unit Testing

### Test Structure: Arrange-Act-Assert

{% if language == "python" %}
```python
def test_user_full_name():
    # Arrange - Set up test data
    user = User(first_name="John", last_name="Doe")

    # Act - Execute the behavior
    result = user.full_name

    # Assert - Verify the outcome
    assert result == "John Doe"
```
{% elif language == "javascript" or language == "typescript" %}
```typescript
test('user full name', () => {
  // Arrange
  const user = new User({ firstName: 'John', lastName: 'Doe' });

  // Act
  const result = user.fullName;

  // Assert
  expect(result).toBe('John Doe');
});
```
{% endif %}

### Naming Conventions

```
test_<unit>_<scenario>_<expected_result>

Examples:
test_calculate_total_with_discount_returns_reduced_price
test_validate_email_with_invalid_format_raises_error
test_user_authenticate_with_correct_password_returns_true
```

### One Assertion Per Test (Conceptually)

{% if language == "python" %}
```python
# BAD - Testing multiple behaviors
def test_user():
    user = User(name="John", email="john@example.com")
    assert user.name == "John"
    assert user.email == "john@example.com"
    assert user.is_valid()
    assert user.created_at is not None

# GOOD - Focused tests
def test_user_stores_name():
    user = User(name="John")
    assert user.name == "John"

def test_user_validates_with_required_fields():
    user = User(name="John", email="john@example.com")
    assert user.is_valid()

def test_user_sets_created_at_on_init():
    user = User(name="John")
    assert user.created_at is not None
```
{% elif language == "javascript" or language == "typescript" %}
```typescript
// BAD
test('user', () => {
  const user = new User({ name: 'John', email: 'john@example.com' });
  expect(user.name).toBe('John');
  expect(user.email).toBe('john@example.com');
  expect(user.isValid()).toBe(true);
  expect(user.createdAt).toBeDefined();
});

// GOOD
test('user stores name', () => {
  const user = new User({ name: 'John' });
  expect(user.name).toBe('John');
});

test('user validates with required fields', () => {
  const user = new User({ name: 'John', email: 'john@example.com' });
  expect(user.isValid()).toBe(true);
});
```
{% endif %}

### Testing Edge Cases

{% if language == "python" %}
```python
import pytest

class TestDivide:
    def test_divides_positive_numbers(self):
        assert divide(10, 2) == 5

    def test_divides_negative_numbers(self):
        assert divide(-10, 2) == -5

    def test_returns_float_for_non_integer_result(self):
        assert divide(5, 2) == 2.5

    def test_raises_error_for_zero_divisor(self):
        with pytest.raises(ZeroDivisionError):
            divide(10, 0)

    def test_handles_zero_dividend(self):
        assert divide(0, 5) == 0
```
{% elif language == "javascript" or language == "typescript" %}
```typescript
describe('divide', () => {
  test('divides positive numbers', () => {
    expect(divide(10, 2)).toBe(5);
  });

  test('divides negative numbers', () => {
    expect(divide(-10, 2)).toBe(-5);
  });

  test('throws for zero divisor', () => {
    expect(() => divide(10, 0)).toThrow('Division by zero');
  });

  test('handles zero dividend', () => {
    expect(divide(0, 5)).toBe(0);
  });
});
```
{% endif %}

{% endif %}

---

{% if test_type == "integration" or test_type == "all" %}
## Integration Testing

### Database Integration

{% if language == "python" %}
```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture
def db_session():
    """Create a test database session."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    yield session

    session.rollback()
    session.close()

def test_user_repository_saves_user(db_session):
    # Arrange
    repo = UserRepository(db_session)
    user = User(name="John", email="john@example.com")

    # Act
    repo.save(user)

    # Assert
    saved_user = repo.find_by_email("john@example.com")
    assert saved_user is not None
    assert saved_user.name == "John"
```
{% elif language == "javascript" or language == "typescript" %}
```typescript
describe('UserRepository', () => {
  let db: Database;
  let repo: UserRepository;

  beforeEach(async () => {
    db = await createTestDatabase();
    repo = new UserRepository(db);
  });

  afterEach(async () => {
    await db.close();
  });

  test('saves user to database', async () => {
    const user = { name: 'John', email: 'john@example.com' };

    await repo.save(user);

    const savedUser = await repo.findByEmail('john@example.com');
    expect(savedUser).toMatchObject(user);
  });
});
```
{% endif %}

### API Integration

{% if language == "python" %}
```python
import pytest
from fastapi.testclient import TestClient

@pytest.fixture
def client():
    from myapp import app
    return TestClient(app)

def test_create_user_endpoint(client):
    # Arrange
    user_data = {"name": "John", "email": "john@example.com"}

    # Act
    response = client.post("/users", json=user_data)

    # Assert
    assert response.status_code == 201
    assert response.json()["name"] == "John"
    assert "id" in response.json()

def test_get_user_returns_404_for_unknown_id(client):
    response = client.get("/users/unknown-id")
    assert response.status_code == 404
```
{% elif language == "javascript" or language == "typescript" %}
```typescript
import request from 'supertest';
import { app } from '../src/app';

describe('User API', () => {
  test('POST /users creates user', async () => {
    const response = await request(app)
      .post('/users')
      .send({ name: 'John', email: 'john@example.com' });

    expect(response.status).toBe(201);
    expect(response.body.name).toBe('John');
    expect(response.body.id).toBeDefined();
  });

  test('GET /users/:id returns 404 for unknown id', async () => {
    const response = await request(app).get('/users/unknown-id');
    expect(response.status).toBe(404);
  });
});
```
{% endif %}

{% endif %}

---

## Mocking Strategies

### When to Mock

✅ **Mock:**
- External services (APIs, databases in unit tests)
- Time-dependent operations
- Non-deterministic behavior
- Slow operations

❌ **Don't mock:**
- The thing you're testing
- Simple value objects
- Pure functions

### Mocking Examples

{% if language == "python" %}
```python
from unittest.mock import Mock, patch, MagicMock

# Mock a dependency
def test_notification_service_sends_email():
    # Arrange
    email_client = Mock()
    service = NotificationService(email_client)

    # Act
    service.notify_user("user@example.com", "Hello")

    # Assert
    email_client.send.assert_called_once_with(
        to="user@example.com",
        body="Hello"
    )

# Patch a module
@patch('myapp.services.requests.get')
def test_fetches_data_from_api(mock_get):
    mock_get.return_value.json.return_value = {"data": "value"}

    result = fetch_data("http://api.example.com")

    assert result == {"data": "value"}
    mock_get.assert_called_once()

# Mock with side effects
def test_retry_on_failure():
    api = Mock()
    api.call.side_effect = [
        ConnectionError("Failed"),
        ConnectionError("Failed"),
        {"success": True}
    ]

    result = retry_call(api)

    assert result == {"success": True}
    assert api.call.call_count == 3
```
{% elif language == "javascript" or language == "typescript" %}
```typescript
// Mock a module
jest.mock('../services/emailService');

import { EmailService } from '../services/emailService';

test('notification service sends email', () => {
  const mockSend = jest.fn();
  (EmailService as jest.Mock).mockImplementation(() => ({
    send: mockSend
  }));

  const service = new NotificationService();
  service.notifyUser('user@example.com', 'Hello');

  expect(mockSend).toHaveBeenCalledWith({
    to: 'user@example.com',
    body: 'Hello'
  });
});

// Mock fetch
global.fetch = jest.fn(() =>
  Promise.resolve({
    json: () => Promise.resolve({ data: 'value' })
  })
) as jest.Mock;

test('fetches data from API', async () => {
  const result = await fetchData('http://api.example.com');

  expect(result).toEqual({ data: 'value' });
  expect(fetch).toHaveBeenCalledTimes(1);
});
```
{% endif %}

---

## Test Fixtures

### Fixture Patterns

{% if language == "python" %}
```python
import pytest
from datetime import datetime

# Simple fixture
@pytest.fixture
def user():
    return User(name="John", email="john@example.com")

# Fixture with cleanup
@pytest.fixture
def temp_file(tmp_path):
    file_path = tmp_path / "test.txt"
    file_path.write_text("test content")
    yield file_path
    # Cleanup happens automatically with tmp_path

# Parametrized fixture
@pytest.fixture(params=["admin", "user", "guest"])
def role(request):
    return request.param

def test_permissions_for_role(role):
    # Runs 3 times, once for each role
    permissions = get_permissions(role)
    assert permissions is not None

# Factory fixture
@pytest.fixture
def create_user():
    created_users = []

    def _create_user(**kwargs):
        defaults = {"name": "Test", "email": "test@example.com"}
        user = User(**{**defaults, **kwargs})
        created_users.append(user)
        return user

    yield _create_user

    # Cleanup
    for user in created_users:
        user.delete()

def test_user_with_custom_data(create_user):
    user = create_user(name="Custom", role="admin")
    assert user.name == "Custom"
```
{% elif language == "javascript" or language == "typescript" %}
```typescript
// Setup and teardown
describe('UserService', () => {
  let db: Database;
  let service: UserService;

  beforeAll(async () => {
    db = await Database.connect();
  });

  afterAll(async () => {
    await db.disconnect();
  });

  beforeEach(async () => {
    await db.clear();
    service = new UserService(db);
  });

  test('creates user', async () => {
    const user = await service.create({ name: 'John' });
    expect(user.id).toBeDefined();
  });
});

// Factory pattern
const createUser = (overrides = {}) => ({
  id: 'user-123',
  name: 'John',
  email: 'john@example.com',
  createdAt: new Date(),
  ...overrides
});

test('user display name', () => {
  const user = createUser({ name: 'Jane' });
  expect(getDisplayName(user)).toBe('Jane');
});
```
{% endif %}

---

## Testing Anti-Patterns

### Tests That Always Pass

```python
# BAD - No assertion!
def test_user_creation():
    user = User(name="John")
    # Missing assert!

# BAD - Assertion on wrong thing
def test_api_response():
    response = api.get("/users")
    assert response is not None  # Doesn't verify content!
```

### Flaky Tests

```python
# BAD - Depends on timing
def test_cache_expiration():
    cache.set("key", "value", ttl=1)
    time.sleep(1.1)  # Flaky!
    assert cache.get("key") is None

# GOOD - Mock time
def test_cache_expiration(mock_time):
    cache.set("key", "value", ttl=1)
    mock_time.advance(2)
    assert cache.get("key") is None
```

### Over-Mocking

```python
# BAD - Testing mocks, not code
def test_user_service():
    repo = Mock()
    repo.save.return_value = User(id=1)
    service = UserService(repo)

    result = service.create({"name": "John"})

    # We're just testing that Mock works!
    assert result.id == 1
```

### Test Interdependence

```python
# BAD - Tests depend on order
class TestUserFlow:
    user_id = None

    def test_1_create_user(self):
        user = create_user()
        TestUserFlow.user_id = user.id  # Shared state!

    def test_2_get_user(self):
        user = get_user(TestUserFlow.user_id)  # Depends on test_1!

# GOOD - Independent tests
def test_get_user():
    user = create_user()  # Each test creates its own data
    result = get_user(user.id)
    assert result == user
```

---

## Test Organization

```
tests/
├── conftest.py           # Shared fixtures
├── unit/
│   ├── test_models.py
│   ├── test_services.py
│   └── test_utils.py
├── integration/
│   ├── test_api.py
│   └── test_database.py
└── e2e/
    └── test_workflows.py
```

### Running Tests

{% if language == "python" %}
```bash
# All tests
pytest

# With coverage
pytest --cov=myapp --cov-report=html

# Specific file/test
pytest tests/unit/test_models.py::test_user_creation

# By marker
pytest -m "not slow"

# Parallel execution
pytest -n auto
```
{% elif language == "javascript" or language == "typescript" %}
```bash
# All tests
npm test

# With coverage
npm test -- --coverage

# Watch mode
npm test -- --watch

# Specific file
npm test -- tests/user.test.ts
```
{% endif %}
