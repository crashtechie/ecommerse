from decimal import Decimal

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from .models import Product, Customer, Order

# Create your tests here.
class ProductModelTests(TestCase):
    def test_product_string_representation(self):
        product = Product.objects.create(
            name="Test Product",
            description="This is a test product.",
            price=Decimal("9.99"),
        )

        self.assertEqual(str(product), "Test Product")

class CustomerModelTests(TestCase):
    def test_customer_string_representation(self):
        customer = Customer.objects.create(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
        )

        self.assertEqual(str(customer), "John Doe")

    def test_customer_email_uniqueness(self):
        Customer.objects.create(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
        )

        with self.assertRaises(Exception):
            Customer.objects.create(
                first_name="Jane",
                last_name="Doe",
                email="john.doe@example.com",
            )

class HealthCheckApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_health_check_endpoint(self):
        response = self.client.get("/api/health/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"status": "ok"})

class ProductApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.product = Product.objects.create(
            name="Test Product",
            description="This is a test product.",
            price=Decimal("9.99"),
        )

    def test_get_product_list(self):
        response = self.client.get("/api/products/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["name"], "Test Product")

    def test_get_product_detail(self):
        response = self.client.get(f"/api/products/{self.product.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["name"], "Test Product")

    def test_create_product(self):
        data = {
            "name": "New Product",
            "description": "This is a new product.",
            "price": "19.99",
        }
        response = self.client.post("/api/products/", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 2)
        self.assertEqual(response.json()["name"], "New Product")

    def test_update_product(self):
        response = self.client.patch(
            f"/api/products/{self.product.id}/",
            {"price": "29.99"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertEqual(str(self.product.price), "29.99")

    def test_delete_product(self):
        response = self.client.delete(f"/api/products/{self.product.id}/")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Product.objects.filter(id=self.product.id).exists())

class CustomerAndOrderApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.product = Product.objects.create(
            name="Test Product",
            description="This is a test product.",
            price=Decimal("9.99"),
        )
        self.customer = Customer.objects.create(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
        )

    def test_create_customer(self):
        data = {
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "jane.doe@example.com",
        }

        response = self.client.post("/api/customers/", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Customer.objects.count(), 2)
        self.assertEqual(response.json()["email"], "jane.doe@example.com")

    def test_create_order(self):
        data = {
            "customer": self.customer.id,
            "product": self.product.id,
            "quantity": 2,
            "total_price": "20.15",
        }
        response = self.client.post("/api/orders/", data, format="json")

        self. assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)

        order = Order.objects.get()
        self.assertEqual(order.customer, self.customer)
        self.assertEqual(order.product, self.product)
        self.assertEqual(order.quantity, 2)
        self.assertEqual(str(order.total_price), "20.15")

    def test_create_order_rejects_nonexistent_customer(self):
        data = {
            "customer": 99999,  # Non-existent customer ID
            "product": self.product.id,
            "quantity": 1,
            "total_price": "9.99",
        }

        response = self.client.post("/api/orders/", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Order.objects.count(), 0)



    