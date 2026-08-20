from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, HealthCheckViewSet, CustomerViewSet, OrderViewSet

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'health', HealthCheckViewSet, basename='health')
router.register(r'customers', CustomerViewSet, basename='customer')
router.register(r'orders', OrderViewSet, basename='order')

# configure your urls below
urlpatterns = [
    path('', include(router.urls)),
]