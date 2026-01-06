from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AccessLogViewSet

# Router 
router = DefaultRouter()
router.register(r'logs', AccessLogViewSet, basename='accesslog')

urlpatterns = [
    path('', include(router.urls)),
]