from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import ItemSerializer, CategorySerializer
from .models import Item, Category, UserProfile
from .permissions import IsOwnerOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from claims.models import Claim, Notification
from django.contrib.auth.models import User
from .notifications_helper import notify_claim_approved, notify_claim_rejected, notify_item_deleted


# ==================== TEMPLATE VIEWS ====================

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
    return render(request, 'registration/login.html')


def home(request):
    items = Item.objects.all()
    categories = Category.objects.all()

    q = request.GET.get('q', '').strip()
    if q:
        items = items.filter(Q(title__icontains=q) | Q(description__icontains=q))

    category_id = request.GET.get('category', '')
    selected_category_name = ''
    if category_id:
        items = items.filter(category__id=category_id)
        try:
            selected_category_name = Category.objects.get(id=category_id).name
        except Category.DoesNotExist:
            pass

    item_type = request.GET.get('type', '')
    if item_type in ['Lost', 'Found']:
        items = items.filter(type=item_type)

    context = {
        'items': items,
        'categories': categories,
        'selected_category_name': selected_category_name,
    }
    return render(request, 'home.html', context)


@login_required(login_url='login')
def post_item(request):
    if request.method == 'POST':
        try:
            item = Item.objects.create(
                title=request.POST['title'],
                description=request.POST['description'],
                category=Category.objects.get(id=request.POST['category']),
                type=request.POST['type'],
                location=request.POST['location'],
                date=request.POST['date'],
                owner=request.user
            )
            if 'image' in request.FILES:
                item.image = request.FILES['image']
                item.save()
            # Check for matches and notify
            from .notifications_helper import notify_item_match
            opposite_type = 'Found' if item.type == 'Lost' else 'Lost'
            matches = Item.objects.filter(
                category=item.category,
                type=opposite_type,
                status='Open'
            ).exclude(pk=item.pk)
            for match in matches[:3]:
                notify_item_match(item, match) if item.type == 'Lost' else notify_item_match(match, item)

            return render(request, 'post_item.html', {'success': True, 'categories': Category.objects.all()})
        except Exception as e:
            return render(request, 'post_item.html', {'error': str(e), 'categories': Category.objects.all()})
    categories = Category.objects.all()
    return render(request, 'post_item.html', {'categories': categories})


@login_required(login_url='login')
def my_claims(request):
    claims = Claim.objects.filter(claimant=request.user)
    return render(request, 'my_claims.html', {'claims': claims})


def item_detail(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    return render(request, 'item_detail.html', {'item': item})


@login_required(login_url='login')
def profile(request):
    user = request.user
    context = {
        'posted_items': Item.objects.filter(owner=user).order_by('-date'),
        'total_items': Item.objects.filter(owner=user).count(),
        'lost_items': Item.objects.filter(owner=user, type='Lost').count(),
        'found_items': Item.objects.filter(owner=user, type='Found').count(),
        'total_claims': Claim.objects.filter(claimant=user).count(),
    }

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'avatar':
            if 'avatar' in request.FILES:
                profile_obj, _ = UserProfile.objects.get_or_create(user=user)
                profile_obj.avatar = request.FILES['avatar']
                profile_obj.save()
            return redirect('profile')

        elif action == 'profile':
            user.first_name = request.POST.get('first_name', '').strip()
            user.last_name = request.POST.get('last_name', '').strip()
            user.email = request.POST.get('email', '').strip()
            user.save()
            context['profile_success'] = True

        elif action == 'password':
            current = request.POST.get('current_password')
            new_pw = request.POST.get('new_password')
            confirm = request.POST.get('confirm_password')
            if not user.check_password(current):
                context['password_error'] = 'Current password is incorrect.'
            elif new_pw != confirm:
                context['password_error'] = 'New passwords do not match.'
            elif len(new_pw) < 6:
                context['password_error'] = 'Password must be at least 6 characters.'
            else:
                user.set_password(new_pw)
                user.save()
                from django.contrib.auth import update_session_auth_hash
                update_session_auth_hash(request, user)
                context['password_success'] = True

    UserProfile.objects.get_or_create(user=user)
    return render(request, 'profile.html', context)


# ==================== ADMIN ====================

def admin_required(view_func):
    from functools import wraps
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.is_superuser or getattr(request.user, 'role', None) == 'admin':
            return view_func(request, *args, **kwargs)
        return redirect('home')
    return wrapper


@admin_required
def admin_dashboard(request):
    message = None

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'delete_item':
            item_id = request.POST.get('item_id')
            item = Item.objects.get(id=item_id)
            notify_item_deleted(item.owner, item.title)
            item.delete()
            message = 'Item deleted successfully.'

        elif action == 'toggle_item_status':
            item_id = request.POST.get('item_id')
            item = Item.objects.get(id=item_id)
            item.status = 'Claimed' if item.status == 'Open' else 'Open'
            item.save()
            message = f'Item status updated to {item.status}.'

        elif action == 'approve_claim':
            claim_id = request.POST.get('claim_id')
            claim = Claim.objects.get(id=claim_id)
            claim.status = 'Approved'
            claim.save()
            claim.item.status = 'Claimed'
            claim.item.save()
            notify_claim_approved(claim)
            message = 'Claim approved.'

        elif action == 'reject_claim':
            claim_id = request.POST.get('claim_id')
            claim = Claim.objects.get(id=claim_id)
            claim.status = 'Rejected'
            claim.save()
            notify_claim_rejected(claim)
            message = 'Claim rejected.'

        elif action == 'toggle_user':
            user_id = request.POST.get('user_id')
            u = User.objects.get(id=user_id)
            u.is_active = not u.is_active
            u.save()
            message = f'User {"activated" if u.is_active else "deactivated"}.'

    context = {
        'total_items': Item.objects.count(),
        'lost_items': Item.objects.filter(type='Lost').count(),
        'found_items': Item.objects.filter(type='Found').count(),
        'total_claims': Claim.objects.count(),
        'pending_claims': Claim.objects.filter(status='Pending').count(),
        'total_users': User.objects.count(),
        'all_items': Item.objects.select_related('owner', 'category').order_by('-date'),
        'all_claims': Claim.objects.select_related('item', 'claimant').order_by('-created_at'),
        'all_users': User.objects.order_by('-date_joined'),
        'message': message,
    }
    return render(request, 'admin_dashboard.html', context)


# ==================== NOTIFICATIONS ====================

@login_required(login_url='login')
def notifications_view(request):
    notifications = Notification.objects.filter(user=request.user)
    unread_count = notifications.filter(is_read=False).count()
    return render(request, 'notifications.html', {
        'notifications': notifications,
        'unread_count': unread_count,
    })


@login_required(login_url='login')
def mark_read(request, notif_id):
    notif = get_object_or_404(Notification, id=notif_id, user=request.user)
    notif.is_read = True
    notif.save()
    next_url = request.GET.get('next', '/')
    return redirect(next_url)


@login_required(login_url='login')
def mark_all_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return redirect('notifications')


# ==================== API VIEWSETS ====================

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['title', 'description']
    filterset_fields = ['category', 'type', 'location']
    ordering_fields = ['date']

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['get'], url_path='matches')
    def matches(self, request, pk=None):
        item = self.get_object()
        opposite_type = 'Found' if item.type == 'Lost' else 'Lost'

        candidates = Item.objects.filter(
            category=item.category,
            type=opposite_type,
        ).exclude(pk=item.pk)

        scored = []
        keywords = [w for w in item.title.lower().split() if len(w) >= 4]
        keywords += [w for w in item.description.lower().split() if len(w) >= 4]

        for candidate in candidates:
            score = 0
            for kw in keywords:
                if kw in candidate.title.lower():
                    score += 2
            for kw in keywords:
                if kw in candidate.description.lower():
                    score += 1
            if item.location and candidate.location:
                if item.location.lower() == candidate.location.lower():
                    score += 3
            scored.append((score, candidate))

        scored.sort(key=lambda x: x[0], reverse=True)
        top5 = [candidate for score, candidate in scored[:5]]

        serializer = ItemSerializer(top5, many=True, context={'request': request})
        return Response({
            'source_item': item.title,
            'looking_for': opposite_type,
            'matches_found': len(top5),
            'results': serializer.data
        })