from django.urls import path, include
from rest_framework import routers
from .views import ItemViewSet, CategoryViewSet

router = routers.DefaultRouter()
router.register(r'items', ItemViewSet)
router.register(r'categories', CategoryViewSet)

urlpatterns = [
    path('', include(router.urls)),
]