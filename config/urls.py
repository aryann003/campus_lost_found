from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from items.views import ItemViewSet, CategoryViewSet, home, post_item, my_claims, item_detail, user_login, profile
from claims.views import ClaimViewSet, NotificationViewSet
from users.views import RegisterView

router = DefaultRouter()
router.register(r'items', ItemViewSet, basename='item')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'claims', ClaimViewSet, basename='claim')
router.register(r'notifications', NotificationViewSet, basename='notification') 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('profile/', profile, name = 'profile'),
    
    # Authentication
    path('login/', user_login, name='login'),
    path('accounts/', include('django.contrib.auth.urls')),
    
    # Template Routes
    path('', home, name='home'),
    path('post/', post_item, name='post_item'),
    path('claims/', my_claims, name='my_claims'),
    path('item/<int:item_id>/', item_detail, name='item_detail'),
    
    # API Routes
    path('api/', include(router.urls)),
    path('api/users/', include('users.urls')),
    path('api-auth/', include('rest_framework.urls')),
    path('api/analytics/', include('analytics.urls'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)