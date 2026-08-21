from decimal import Decimal

import pytest

from products.models import Customer, Order, Product


@pytest.mark.django_db
def test_order_str_includes_order_id_and_customer_name():
    customer = Customer.objects.create(
        first_name="Alice",
        last_name="Johnson",
        email="alice.johnson@example.com",
    )
    product = Product.objects.create(
        name="Keyboard",
        description="Mechanical keyboard",
        price=Decimal("89.99"),
    )

    order = Order.objects.create(
        customer=customer,
        product=product,
        quantity=2,
        total_price=Decimal("179.98"),
    )

    assert str(order) == f"Order {order.id} by Alice Johnson"


@pytest.mark.django_db
def test_order_links_customer_and_product():
    customer = Customer.objects.create(
        first_name="Bob",
        last_name="Martin",
        email="bob.martin@example.com",
    )
    product = Product.objects.create(
        name="Monitor",
        description="27-inch display",
        price=Decimal("249.00"),
    )

    order = Order.objects.create(
        customer=customer,
        product=product,
        quantity=3,
        total_price=Decimal("747.00"),
    )

    assert order.customer == customer
    assert order.product == product
    assert order.quantity == 3
    assert str(order.total_price) == "747.00"
