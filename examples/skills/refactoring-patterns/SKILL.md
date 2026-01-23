---
name: refactoring-patterns
description: |
  Code refactoring techniques and design patterns. Use when improving existing code,
  eliminating code smells, or restructuring for maintainability. Covers systematic
  refactoring approaches, common patterns, and safe transformation techniques.
license: MIT
allowed-tools: Read Edit Bash
version: 1.0.0
tags: [refactoring, patterns, clean-code, design-patterns, maintainability]
category: development/quality
variables:
  language:
    type: string
    description: Programming language
    enum: [python, javascript, typescript, java, go]
    default: python
  focus:
    type: string
    description: Refactoring focus area
    enum: [code-smells, design-patterns, simplification, performance]
    default: code-smells
---

# Refactoring Patterns Guide

## Refactoring Philosophy

**Refactoring is changing code structure without changing behavior.** Small, safe steps compound into significant improvements.

### Core Principles

1. **Tests first** - Never refactor without a safety net
2. **Small steps** - Each change should be reversible
3. **One thing at a time** - Don't mix refactoring with feature work
4. **Boy Scout Rule** - Leave code better than you found it

> "Any fool can write code that a computer can understand. Good programmers write code that humans can understand." — Martin Fowler

---

{% if focus == "code-smells" or focus == "simplification" %}
## Code Smells & Fixes

### Long Method

**Smell:** Method does too many things, hard to understand at a glance.

{% if language == "python" %}
```python
# BEFORE: Long method doing everything
def process_order(order):
    # Validate
    if not order.items:
        raise ValueError("Empty order")
    if not order.customer:
        raise ValueError("No customer")

    # Calculate totals
    subtotal = 0
    for item in order.items:
        subtotal += item.price * item.quantity
    tax = subtotal * 0.1
    shipping = 5.99 if subtotal < 50 else 0
    total = subtotal + tax + shipping

    # Save to database
    db.orders.insert({
        'customer_id': order.customer.id,
        'items': [i.to_dict() for i in order.items],
        'subtotal': subtotal,
        'tax': tax,
        'shipping': shipping,
        'total': total
    })

    # Send notification
    email.send(
        to=order.customer.email,
        subject="Order Confirmation",
        body=f"Your order total: ${total}"
    )

    return total

# AFTER: Extract methods
def process_order(order):
    validate_order(order)
    totals = calculate_totals(order)
    save_order(order, totals)
    notify_customer(order.customer, totals)
    return totals.total

def validate_order(order):
    if not order.items:
        raise ValueError("Empty order")
    if not order.customer:
        raise ValueError("No customer")

def calculate_totals(order):
    subtotal = sum(item.price * item.quantity for item in order.items)
    tax = subtotal * TAX_RATE
    shipping = 0 if subtotal >= FREE_SHIPPING_THRESHOLD else SHIPPING_COST
    return OrderTotals(subtotal=subtotal, tax=tax, shipping=shipping)

def save_order(order, totals):
    db.orders.insert(order.to_dict() | totals.to_dict())

def notify_customer(customer, totals):
    email.send_order_confirmation(customer.email, totals.total)
```
{% elif language == "javascript" or language == "typescript" %}
```typescript
// BEFORE: Long method
async function processOrder(order: Order): Promise<number> {
  // 50 lines of validation, calculation, saving, notification...
}

// AFTER: Extract methods
async function processOrder(order: Order): Promise<number> {
  validateOrder(order);
  const totals = calculateTotals(order);
  await saveOrder(order, totals);
  await notifyCustomer(order.customer, totals);
  return totals.total;
}

function validateOrder(order: Order): void {
  if (!order.items.length) throw new Error('Empty order');
  if (!order.customer) throw new Error('No customer');
}

function calculateTotals(order: Order): OrderTotals {
  const subtotal = order.items.reduce((sum, item) => sum + item.price * item.quantity, 0);
  const tax = subtotal * TAX_RATE;
  const shipping = subtotal >= FREE_SHIPPING_THRESHOLD ? 0 : SHIPPING_COST;
  return { subtotal, tax, shipping, total: subtotal + tax + shipping };
}
```
{% endif %}

---

### Feature Envy

**Smell:** Method uses more data from another class than its own.

{% if language == "python" %}
```python
# BEFORE: Order reaching into Customer
class Order:
    def get_shipping_address(self):
        return f"{self.customer.street}, {self.customer.city}, {self.customer.zip}"

# AFTER: Move method to where data lives
class Customer:
    def get_shipping_address(self):
        return f"{self.street}, {self.city}, {self.zip}"

class Order:
    def get_shipping_address(self):
        return self.customer.get_shipping_address()
```
{% elif language == "javascript" or language == "typescript" %}
```typescript
// BEFORE: Reaching into other object
class Order {
  getShippingAddress(): string {
    return `${this.customer.street}, ${this.customer.city}, ${this.customer.zip}`;
  }
}

// AFTER: Delegate to owner of data
class Customer {
  getShippingAddress(): string {
    return `${this.street}, ${this.city}, ${this.zip}`;
  }
}

class Order {
  getShippingAddress(): string {
    return this.customer.getShippingAddress();
  }
}
```
{% endif %}

---

### Primitive Obsession

**Smell:** Using primitives for domain concepts (email as string, money as float).

{% if language == "python" %}
```python
# BEFORE: Primitives everywhere
def create_user(email: str, phone: str) -> dict:
    if "@" not in email:
        raise ValueError("Invalid email")
    if len(phone) != 10:
        raise ValueError("Invalid phone")
    return {"email": email, "phone": phone}

# AFTER: Value objects
from dataclasses import dataclass
import re

@dataclass(frozen=True)
class Email:
    value: str

    def __post_init__(self):
        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', self.value):
            raise ValueError(f"Invalid email: {self.value}")

@dataclass(frozen=True)
class PhoneNumber:
    value: str

    def __post_init__(self):
        digits = re.sub(r'\D', '', self.value)
        if len(digits) != 10:
            raise ValueError(f"Invalid phone: {self.value}")
        object.__setattr__(self, 'value', digits)

    def formatted(self) -> str:
        return f"({self.value[:3]}) {self.value[3:6]}-{self.value[6:]}"

def create_user(email: Email, phone: PhoneNumber) -> User:
    return User(email=email, phone=phone)
```
{% elif language == "javascript" or language == "typescript" %}
```typescript
// BEFORE: Primitives
function createUser(email: string, phone: string): User { ... }

// AFTER: Value objects
class Email {
  private readonly value: string;

  constructor(value: string) {
    if (!this.isValid(value)) {
      throw new Error(`Invalid email: ${value}`);
    }
    this.value = value;
  }

  private isValid(email: string): boolean {
    return /^[\w.-]+@[\w.-]+\.\w+$/.test(email);
  }

  toString(): string {
    return this.value;
  }
}

function createUser(email: Email, phone: PhoneNumber): User { ... }
```
{% endif %}

---

### Duplicate Code

**Smell:** Same code structure in multiple places.

{% if language == "python" %}
```python
# BEFORE: Duplicate validation logic
class UserController:
    def create(self, data):
        if not data.get('email'):
            raise ValueError("Email required")
        if not data.get('name'):
            raise ValueError("Name required")
        # ... create user

    def update(self, data):
        if not data.get('email'):
            raise ValueError("Email required")
        if not data.get('name'):
            raise ValueError("Name required")
        # ... update user

# AFTER: Extract and reuse
def validate_user_data(data: dict, required: list[str]) -> None:
    missing = [f for f in required if not data.get(f)]
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")

class UserController:
    REQUIRED_FIELDS = ['email', 'name']

    def create(self, data):
        validate_user_data(data, self.REQUIRED_FIELDS)
        # ... create user

    def update(self, data):
        validate_user_data(data, self.REQUIRED_FIELDS)
        # ... update user
```
{% endif %}

---

### God Class

**Smell:** One class that knows/does too much.

```python
# BEFORE: God class
class OrderManager:
    def create_order(self): ...
    def validate_order(self): ...
    def calculate_tax(self): ...
    def calculate_shipping(self): ...
    def save_to_database(self): ...
    def send_email(self): ...
    def generate_pdf(self): ...
    def upload_to_s3(self): ...
    # ... 50 more methods

# AFTER: Single responsibility
class OrderService:
    def __init__(self, validator, calculator, repository, notifier):
        self.validator = validator
        self.calculator = calculator
        self.repository = repository
        self.notifier = notifier

    def create_order(self, order):
        self.validator.validate(order)
        order.totals = self.calculator.calculate(order)
        self.repository.save(order)
        self.notifier.send_confirmation(order)

class OrderValidator: ...
class OrderCalculator: ...
class OrderRepository: ...
class OrderNotifier: ...
```

{% endif %}

---

{% if focus == "design-patterns" or focus == "simplification" %}
## Design Pattern Refactorings

### Replace Conditional with Polymorphism

{% if language == "python" %}
```python
# BEFORE: Switch on type
def calculate_shipping(order):
    if order.shipping_type == "standard":
        return 5.99
    elif order.shipping_type == "express":
        return 15.99
    elif order.shipping_type == "overnight":
        return 29.99
    else:
        raise ValueError(f"Unknown shipping: {order.shipping_type}")

# AFTER: Polymorphism
from abc import ABC, abstractmethod

class ShippingStrategy(ABC):
    @abstractmethod
    def calculate(self, order) -> float: ...

class StandardShipping(ShippingStrategy):
    def calculate(self, order) -> float:
        return 5.99

class ExpressShipping(ShippingStrategy):
    def calculate(self, order) -> float:
        return 15.99

class OvernightShipping(ShippingStrategy):
    def calculate(self, order) -> float:
        return 29.99

# Usage
SHIPPING_STRATEGIES = {
    "standard": StandardShipping(),
    "express": ExpressShipping(),
    "overnight": OvernightShipping(),
}

def calculate_shipping(order):
    strategy = SHIPPING_STRATEGIES.get(order.shipping_type)
    if not strategy:
        raise ValueError(f"Unknown shipping: {order.shipping_type}")
    return strategy.calculate(order)
```
{% elif language == "javascript" or language == "typescript" %}
```typescript
// BEFORE: Switch statement
function calculateShipping(order: Order): number {
  switch (order.shippingType) {
    case 'standard': return 5.99;
    case 'express': return 15.99;
    case 'overnight': return 29.99;
    default: throw new Error(`Unknown shipping: ${order.shippingType}`);
  }
}

// AFTER: Strategy pattern
interface ShippingStrategy {
  calculate(order: Order): number;
}

const shippingStrategies: Record<string, ShippingStrategy> = {
  standard: { calculate: () => 5.99 },
  express: { calculate: () => 15.99 },
  overnight: { calculate: () => 29.99 },
};

function calculateShipping(order: Order): number {
  const strategy = shippingStrategies[order.shippingType];
  if (!strategy) throw new Error(`Unknown shipping: ${order.shippingType}`);
  return strategy.calculate(order);
}
```
{% endif %}

---

### Extract Interface

```python
# BEFORE: Concrete dependency
class OrderService:
    def __init__(self):
        self.db = PostgresDatabase()  # Hard-coded dependency

    def save(self, order):
        self.db.insert("orders", order.to_dict())

# AFTER: Depend on abstraction
from abc import ABC, abstractmethod

class OrderRepository(ABC):
    @abstractmethod
    def save(self, order: Order) -> None: ...

class PostgresOrderRepository(OrderRepository):
    def save(self, order: Order) -> None:
        self.db.insert("orders", order.to_dict())

class InMemoryOrderRepository(OrderRepository):  # For testing!
    def __init__(self):
        self.orders = []

    def save(self, order: Order) -> None:
        self.orders.append(order)

class OrderService:
    def __init__(self, repository: OrderRepository):
        self.repository = repository

    def create(self, order):
        # ... business logic
        self.repository.save(order)
```

---

### Introduce Parameter Object

```python
# BEFORE: Long parameter list
def search_products(
    category: str,
    min_price: float,
    max_price: float,
    in_stock: bool,
    sort_by: str,
    sort_order: str,
    page: int,
    page_size: int
) -> list[Product]:
    ...

# AFTER: Parameter object
@dataclass
class ProductSearchCriteria:
    category: str | None = None
    min_price: float | None = None
    max_price: float | None = None
    in_stock: bool | None = None

@dataclass
class SortOptions:
    field: str = "name"
    order: str = "asc"

@dataclass
class Pagination:
    page: int = 1
    page_size: int = 20

def search_products(
    criteria: ProductSearchCriteria,
    sort: SortOptions = SortOptions(),
    pagination: Pagination = Pagination()
) -> list[Product]:
    ...

# Usage becomes clearer
results = search_products(
    criteria=ProductSearchCriteria(category="electronics", in_stock=True),
    sort=SortOptions(field="price", order="desc"),
    pagination=Pagination(page=2)
)
```

{% endif %}

---

## Safe Refactoring Steps

### The Refactoring Process

```
1. Ensure tests pass (green)
2. Make one small change
3. Run tests (must stay green)
4. Commit
5. Repeat
```

### Common Refactoring Sequences

**Rename (safest):**
```
1. Rename variable/function/class
2. Update all references (IDE helps)
3. Run tests
```

**Extract Method:**
```
1. Identify code to extract
2. Create new method with meaningful name
3. Copy code to new method
4. Identify parameters needed
5. Replace original code with method call
6. Run tests
```

**Move Method:**
```
1. Declare method in target class
2. Copy body, adjust for new home
3. Update original to delegate
4. Run tests
5. Update all callers to use new location
6. Remove original method
7. Run tests
```

**Inline (reverse of extract):**
```
1. Ensure method isn't overridden
2. Replace all calls with method body
3. Delete the method
4. Run tests
```

---

## Refactoring Checklist

### Before Starting
- [ ] Tests exist and pass
- [ ] Code is under version control
- [ ] Understand current behavior
- [ ] Have a clear goal

### During Refactoring
- [ ] One change at a time
- [ ] Run tests after each change
- [ ] Commit frequently
- [ ] No new features

### Warning Signs to Stop
- [ ] Tests are failing
- [ ] Change is getting too big
- [ ] Discovering bugs (fix separately)
- [ ] Unclear on next step

---

## Anti-Patterns to Avoid

### Big Bang Refactoring

```
❌ "Let's rewrite this whole module over the weekend"
✅ "Let's improve this one function today"
```

### Refactoring Without Tests

```
❌ "The code is simple enough, we don't need tests"
✅ "Let me add characterization tests first"
```

### Mixing Refactoring with Features

```
❌ "While I'm here, let me also add this new feature"
✅ "I'll refactor first, commit, then add the feature"
```

### Premature Abstraction

```
❌ "We might need this to be configurable someday"
✅ "YAGNI - We'll abstract when we have a second use case"
```
