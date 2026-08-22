# Backend Recommendations

This document captures recommended improvements for the Django and Django REST Framework backend. The recommendations are ordered roughly by risk and expected impact.

## Priority 1: Production Configuration

The current settings are development-oriented and should not be used in production.

In `backend/config/settings.py`:

- Move `SECRET_KEY` to an environment variable.
- Set `DEBUG` from the environment and keep it disabled in production.
- Replace `ALLOWED_HOSTS = ["*"]` with an explicit list of hosts.
- Configure PostgreSQL instead of SQLite for deployed environments.
- Configure secure cookies, HTTPS redirects, HSTS, and CSRF trusted origins as appropriate for the deployment.
- Configure structured logging and error reporting.
- Validate required environment variables at startup and strip and validate comma-separated values such as `ALLOWED_HOSTS`.
- Run Django's `check --deploy` as part of deployment validation or CI.
- Configure email with Django's `EMAIL_BACKEND` and related `EMAIL_*` settings. The current `MAILERS` setting is not used by Django.

Example environment-based configuration:

```python
import os

SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]
DEBUG = os.environ.get("DJANGO_DEBUG", "false").lower() == "true"
ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ["DJANGO_ALLOWED_HOSTS"].split(",")
    if host.strip()
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ["POSTGRES_DB"],
        "USER": os.environ["POSTGRES_USERNAME"],
        "PASSWORD": os.environ["POSTGRES_PASSWORD"],
        "HOST": os.environ.get("POSTGRES_HOST", "localhost"),
        "PORT": os.environ.get("POSTGRES_PORT", "5432"),
        "CONN_MAX_AGE": 60,
    }
}
```

Keep a separate local or test configuration so development can continue using SQLite when convenient.

## Priority 2: Separate Domain Modules

The current `products` Django app contains products, customers, and orders. These are separate business domains and should be split before adding more complex behavior such as payments, inventory, shipping, or authentication workflows.

A practical structure is:

```text
backend/
    products/
        models.py
        serializers.py
        views.py
        urls.py
    customers/
        models.py
        serializers.py
        views.py
        urls.py
    orders/
        models.py
        serializers.py
        views.py
        urls.py
```

Keep responsibilities within their owning app:

- `products`: catalog data, pricing, categories, and inventory.
- `customers`: customer identity, contact information, addresses, and privacy rules.
- `orders`: order creation, totals, status transitions, cancellations, and fulfillment.

Orders can reference products and customers, but historical orders should not depend entirely on their current state. Store values such as the product name, SKU, and unit price on the order when appropriate so that changes to a product do not alter historical records.

Splitting the apps introduces migration and import work, so it is not necessary for a small prototype. It is an architectural improvement, not a prerequisite for the immediate security and correctness fixes below. Complete the split before adding payments, inventory, or complex order behavior if the project is continuing to grow.

## Priority 3: Calculate Order Totals on the Server

`total_price` is currently accepted from the client. This allows a client to submit a total that does not match the product price and quantity.

In `backend/products/serializers.py`:

- Make `total_price` read-only.
- Make timestamps and generated identifiers read-only.
- Calculate the total from the product price and requested quantity.
- Reject zero or negative quantities.
- Decide whether a client-supplied total is rejected or ignored; rejecting it usually exposes integration errors earlier.
- Define a rounding, currency, tax, discount, and shipping policy before the order model expands.
- Create orders inside a transaction, especially once inventory or payment authorization is involved.

Example:

```python
from rest_framework import serializers


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"
        read_only_fields = ("total_price", "order_date")

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than zero.")
        return value

    def create(self, validated_data):
        product = validated_data["product"]
        quantity = validated_data["quantity"]
        validated_data["total_price"] = product.price * quantity
        return super().create(validated_data)
```

For stronger ecommerce data integrity, store the product's unit price on the order as a snapshot. This preserves the historical order value if the product price changes later.

## Priority 4: Add Customer Login and Order Ownership

Customers need authenticated accounts so they can manage their own orders and view their order history. The current `Customer` model stores profile information but does not provide credentials or an ownership boundary.

Use Django's authentication system rather than adding password fields directly to `Customer`:

- Use Django's built-in user model, or introduce a custom user model before the project has many migrations.
- Link each customer profile to one user with a one-to-one relationship.
- Use email as the login identifier if that matches the business requirement.
- Never store plaintext passwords or implement password hashing manually.
- Keep account credentials separate from customer profile data.

For a React frontend, use an established authentication approach. Session authentication with secure, HTTP-only cookies is a good choice when the frontend and backend share a site. A short-lived JWT access token with refresh-token rotation is another option when the frontend and API are deployed independently. Do not store long-lived access tokens in `localStorage` without explicitly accepting the associated XSS risk.

Recommended customer capabilities:

- Register an account and create or connect a customer profile.
- Log in and log out.
- Change a password and request a password reset.
- View only the authenticated customer's orders.
- View order details and status.
- Cancel or update an order only when its status allows that operation.
- Update permitted profile fields without changing account ownership.

The order queryset should be scoped to the authenticated user, for example through the customer's one-to-one profile relationship. Do not rely on a customer ID supplied by the frontend, and do not expose an unrestricted customer list to normal users.

Administrative permissions should remain separate:

- Restrict product creation, updates, and deletion to staff users.
- Require staff permissions for customer support actions across accounts.
- Consider a read-only customer-facing product endpoint.
- Add throttling to limit abusive login and API requests.

Example DRF defaults:

```python
REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "60/minute",
        "user": "600/minute",
    },
}
```

Apply exceptions deliberately, such as allowing the health endpoint to remain public.

Authentication and order-history endpoints should also have explicit protections against account enumeration, excessive login attempts, insecure token handling, and unauthorized object access.

## Priority 5: Add Pagination

The list endpoints currently return every product, customer, or order in one response. This increases database work, response size, memory usage, and frontend latency as data grows.

Configure DRF pagination:

```python
REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": (
        "rest_framework.pagination.PageNumberPagination"
    ),
    "PAGE_SIZE": 25,
}
```

For large or frequently changing order histories, cursor pagination is often a better choice than page-number pagination.

Update API tests to assert the paginated response shape and include coverage for page size and page boundaries.

## Priority 6: Prevent N+1 Queries

Orders reference both customers and products. The current serializer returns only foreign-key IDs, so it does not appear to create an N+1 query today. If the serializer includes related object data, fetching a list of orders can result in one query for the list plus additional queries per order.

Use `select_related` in `backend/products/views.py`:

```python
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.select_related(
        "customer",
        "product",
    ).all()
    serializer_class = OrderSerializer
```

Use `prefetch_related` for many-to-many or reverse relationships added in the future.

Add query-count tests with Django's `assertNumQueries` after the response shape and queryset are finalized. Keep the assertion focused on the intended query path so harmless changes do not make the test brittle.

## Priority 7: Use Explicit Serializer Fields

The serializers currently use `fields = "__all__"`. That makes every future model field part of the public API automatically and may unintentionally make internal fields writable.

Prefer explicit fields and read-only declarations:

```python
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "description",
            "price",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")
```

Apply the same approach to customer and order serializers.

## Priority 8: Add Targeted Database Indexes

Foreign keys receive indexes by default, but indexes should reflect actual query patterns. A likely order-history pattern is sorting by newest order and filtering by customer or product.

A possible model configuration is:

```python
class Order(models.Model):
    # existing fields ...

    class Meta:
        indexes = [
            models.Index(fields=["-order_date"]),
            models.Index(fields=["customer", "-order_date"]),
            models.Index(fields=["product", "-order_date"]),
        ]
```

Before adding indexes broadly:

- Confirm the queries used by the API.
- Inspect PostgreSQL query plans with `EXPLAIN ANALYZE`.
- Measure write overhead and storage cost.
- Add indexes through migrations.

An index on `Product.created_at` may also help if products are commonly listed newest first.

## Priority 9: Protect Historical Orders

Both order foreign keys currently use `on_delete=models.CASCADE`. Deleting a customer or product can therefore delete historical orders.

For most ecommerce systems, `PROTECT` is safer:

```python
customer = models.ForeignKey(
    Customer,
    on_delete=models.PROTECT,
)
product = models.ForeignKey(
    Product,
    on_delete=models.PROTECT,
)
```

Another option is soft deletion for customers and products. Order records should retain the relevant historical product name, SKU, and unit price rather than depending entirely on mutable product records.

## Priority 10: Use a Production Application Server

`backend/Dockerfile` currently starts Django with `manage.py runserver`. That server is intended for development.

Use Gunicorn for WSGI deployments:

```dockerfile
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
```

For an ASGI deployment, use an ASGI server such as Uvicorn or Daphne with `config.asgi:application`.

The deployment process should also run migrations in a controlled step and expose a health check that verifies the application and database are available as required.

## Priority 11: Expand Test Coverage

The current tests cover basic endpoint behavior, but the highest-risk contracts need explicit tests.

Add tests for:

- Server-calculated order totals.
- Rejection of zero and negative quantities.
- Mismatched client-supplied totals being ignored or rejected.
- Pagination and page boundaries.
- Authentication and permission boundaries.
- Customer registration, login, logout, password reset, and password-change flows.
- A customer can view their own order history but cannot view another customer's orders.
- A customer cannot change an order's customer, total, or other protected fields.
- Order cancellation and updates are rejected after the relevant status transition.
- Customer and product deletion with existing orders.
- Query counts for order list endpoints.
- Invalid or missing required fields.
- Database constraints such as unique customer email addresses.

## Deployment and Container Wiring

The current Compose file defines PostgreSQL but does not define or start a backend service, and the backend Dockerfile uses Django's development server. Document the complete deployment path rather than changing the Dockerfile in isolation:

- Add a backend service that builds `backend/Dockerfile`, passes the Django and database environment variables, and exposes the API port.
- Make the backend depend on the database health check rather than only on container startup order.
- Run migrations in a controlled deployment step before serving traffic.
- Keep development and production Compose configurations separate where their commands, volumes, and secrets differ.
- Add a backend readiness check that verifies the application and, when appropriate, database connectivity. Keep liveness checks lightweight.
- Use Gunicorn for WSGI or Uvicorn/Daphne for ASGI, and run the application as a non-root user.
- Use a minimal, reproducible image and scan dependencies and the image during CI.

## Data Integrity and Order Lifecycle

Server-side validation should be backed by database constraints so invalid data cannot be inserted through the admin, scripts, or another code path:

- Add a `CheckConstraint` requiring `quantity > 0`.
- Enforce non-negative monetary values and define the decimal precision policy.
- Store an immutable unit-price snapshot, and usually product name and SKU snapshots, on each order.
- Make order ownership, timestamps, totals, and generated identifiers read-only through the API.
- Add an explicit order status and enforce allowed transitions such as pending, paid, cancelled, fulfilled, and refunded.
- Reject cancellation or updates after the relevant status transition.
- Add an idempotency key with a uniqueness constraint so retried order submissions cannot create duplicate orders.

Choose a historical-data policy deliberately. `PROTECT` prevents deletion of referenced products and customers, but it does not preserve their mutable values. Alternatives are soft deletion or nullable foreign keys with `SET_NULL` combined with immutable order snapshots. Add tests for the selected policy.

## API Contract and Query Controls

Document the public API with OpenAPI and consider versioning routes such as `/api/v1/` before authentication and pagination change response contracts. Define validation error formats, authentication behavior, and deprecation policy.

For list endpoints:

- Impose a stable default ordering and a maximum page size.
- Allow filtering and ordering only through an explicit allowlist.
- Use page-number pagination for simple administrative lists and consider cursor pagination for frequently changing order histories.
- Update existing tests and frontend clients because pagination changes a raw list response into an object containing `count`, `next`, `previous`, and `results`.

## Operations and CI

Add deployment and maintenance checks alongside application tests:

- Run migrations checks, tests, formatting, Bandit, `manage.py check --deploy`, and dependency vulnerability scans in CI.
- Configure structured request and error logging with correlation or request IDs.
- Add PostgreSQL backup, restore-test, and migration-rollback guidance.
- Monitor latency, error rates, database connections, slow queries, and authentication failures.
- Test password-reset email delivery using the correct Django `EMAIL_*` configuration in a non-production environment.

## Recommended Implementation Order

1. Separate production and development settings.
2. Restrict endpoint permissions and implement customer/order ownership.
3. Calculate order totals server-side and validate quantities.
4. Add database constraints, historical-order policy, and explicit order status transitions.
5. Add focused tests for security, totals, constraints, and ownership.
6. Replace broad serializers with explicit fields.
7. Add pagination and update API consumers for the new response shape.
8. Wire the backend service, migrations, readiness checks, and production application server.
9. Add `select_related` and query-count tests when related response data requires them.
10. Add measured indexes through migrations.
11. Split the product, customer, and order domain modules before adding complex business workflows.

The most immediate performance risk is unbounded list responses. The most immediate correctness and security risks are development settings in deployment, unrestricted CRUD endpoints, and client-controlled order totals. N+1 queries become a performance risk when nested related data is added to serializers.
