from django.db import DatabaseError, connection
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Product, Customer, Order
from .serializers import ProductSerializer, CustomerSerializer, OrderSerializer

# Create your views here.
@api_view(["GET"])
def readiness_check(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
    except DatabaseError:
        return Response(
            {"status": "unready"}, status=status.HTTP_503_SERVICE_UNAVAILABLE
        )

    return Response({"status": "ready"})


class HealthCheckViewSet(viewsets.ViewSet):
    def list(self, request):
        return Response({"status": "ok"})

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer