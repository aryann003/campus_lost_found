from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from items.views import ItemViewSet, CategoryViewSet, home, post_item, my_claims, item_detail, user_login, profile, admin_dashboard,notifications_view, mark_read, mark_all_read
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
    path('admin-panel/', admin_dashboard, name='admin_dashboard'),
    path('notifications/', notifications_view, name='notifications'),
    path('notifications/<int:notif_id>/read/', mark_read, name='mark_read'),
    path('notifications/mark-all-read/', mark_all_read, name='mark_all_read'),

    
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