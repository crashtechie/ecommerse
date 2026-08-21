from decimal import Decimal

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from products.models import Customer, Order, Product


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
def test_health_check_endpoint(api_client):
    response = api_client.get("/api/health/")

    assert response.status_code == status.HTTP_200_OK
    assert response.data == {"status": "ok"}


@pytest.mark.django_db
def test_get_product_list_returns_created_products(api_client):
    Product.objects.create(
        name="Laptop",
        description="Gaming laptop",
        price=Decimal("1299.99"),
    )

    response = api_client.get("/api/products/")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Laptop"


@pytest.mark.django_db
def test_create_product_endpoint(api_client):
    payload = {
        "name": "Mouse",
        "description": "Wireless mouse",
        "price": "49.50",
    }

    response = api_client.post("/api/products/", payload, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert Product.objects.count() == 1
    assert response.json()["name"] == "Mouse"
    assert str(response.json()["price"]) == "49.50"


@pytest.mark.django_db
def test_create_customer_endpoint(api_client):
    payload = {
        "first_name": "Jane",
        "last_name": "Doe",
        "email": "jane.doe@example.com",
    }

    response = api_client.post("/api/customers/", payload, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert Customer.objects.count() == 1
    assert response.json()["email"] == "jane.doe@example.com"


@pytest.mark.django_db
def test_create_order_endpoint(api_client):
    customer = Customer.objects.create(
        first_name="John",
        last_name="Smith",
        email="john.smith@example.com",
    )
    product = Product.objects.create(
        name="Keyboard",
        description="Mechanical keyboard",
        price=Decimal("89.99"),
    )

    payload = {
        "customer": customer.id,
        "product": product.id,
        "quantity": 2,
        "total_price": "179.98",
    }

    response = api_client.post("/api/orders/", payload, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert Order.objects.count() == 1
    order = Order.objects.get()
    assert order.customer == customer
    assert order.product == product
    assert order.quantity == 2
    assert str(order.total_price) == "179.98"


@pytest.mark.django_db
def test_create_order_rejects_unknown_customer(api_client):
    product = Product.objects.create(
        name="Monitor",
        description="27-inch display",
        price=Decimal("249.00"),
    )

    payload = {
        "customer": 99999,
        "product": product.id,
        "quantity": 1,
        "total_price": "249.00",
    }

    response = api_client.post("/api/orders/", payload, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert Order.objects.count() == 0
