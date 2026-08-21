import pytest
from django.db import IntegrityError

from products.models import Customer


@pytest.mark.django_db
def test_customer_str_returns_full_name():
    customer = Customer.objects.create(
        first_name="Jane",
        last_name="Smith",
        email="jane.smith@example.com",
    )

    assert str(customer) == "Jane Smith"


@pytest.mark.django_db
def test_customer_email_must_be_unique():
    Customer.objects.create(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
    )

    with pytest.raises(IntegrityError):
        Customer.objects.create(
            first_name="Johnny",
            last_name="Doe",
            email="john.doe@example.com",
        )


@pytest.mark.django_db
def test_customer_can_be_created_with_valid_fields():
    customer = Customer.objects.create(
        first_name="Emma",
        last_name="Brown",
        email="emma.brown@example.com",
    )

    assert customer.first_name == "Emma"
    assert customer.last_name == "Brown"
    assert customer.email == "emma.brown@example.com"
    assert customer.pk is not None


@pytest.mark.django_db
def test_customer_duplicate_email_is_rejected_by_database():
    Customer.objects.create(
        first_name="First",
        last_name="User",
        email="duplicate@example.com",
    )

    with pytest.raises(Exception):
        Customer.objects.create(
            first_name="Second",
            last_name="User",
            email="duplicate@example.com",
        )
