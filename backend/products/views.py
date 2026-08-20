from rest_framework import viewsets
from rest_framework.response import Response
from .models import Product
from .serializers import ProductSerializer

# Create your views here.
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class HealthCheckViewSet(viewsets.ViewSet):
    def list(self, request):
        return Response({"status": "ok"})