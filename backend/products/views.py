from rest_framework import viewsets
from rest_framework.response import Response
from .models import Product, Customer, Order
from .serializers import ProductSerializer, CustomerSerializer, OrderSerializer

# Create your views here.
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