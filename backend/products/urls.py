from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, HealthCheckViewSet

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'health', HealthCheckViewSet, basename='health')

# configure your urls below
urlpatterns = [
    path('', include(router.urls)),
]