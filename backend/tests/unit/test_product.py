from decimal import Decimal

import pytest

from products.models import Product


@pytest.mark.django_db
def test_product_str_returns_name():
    product = Product.objects.create(
        name="Laptop",
        description="Gaming laptop",
        price=Decimal("1299.99"),
    )

    assert str(product) == "Laptop"


@pytest.mark.django_db
def test_product_can_be_created_with_expected_fields():
    product = Product.objects.create(
        name="Mouse",
        description="Wireless optical mouse",
        price=Decimal("49.50"),
    )

    assert product.name == "Mouse"
    assert product.description == "Wireless optical mouse"
    assert str(product.price) == "49.50"
    assert product.pk is not None


@pytest.mark.django_db
def test_product_requires_a_price():
    with pytest.raises(Exception):
        Product.objects.create(
            name="Missing Price",
            description="This product has no price",
        )
