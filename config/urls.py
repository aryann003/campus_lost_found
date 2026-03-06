from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from items.views import ItemViewSet, CategoryViewSet
from claims.views import ClaimViewSet, NotificationViewSet
from users.views import RegisterView
router = DefaultRouter()
router.register(r'items', ItemViewSet, basename='item')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'claims', ClaimViewSet, basename='claim')
router.register(r'notifications', NotificationViewSet, basename='notification') 
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/users/', include('users.urls')),
    path('api-auth/', include('rest_framework.urls')),
    path('api/analytics/', include('analytics.urls'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)