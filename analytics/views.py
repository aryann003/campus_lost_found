# analytics/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count
from django.db.models.functions import TruncMonth
from items.models import Item


class IsAdminUser(IsAuthenticated):
    """Only users with role='admin' can access analytics."""
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.role == 'admin'


class SummaryView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        total_lost     = Item.objects.filter(type='Lost').count()
        total_found    = Item.objects.filter(type='Found').count()
        total_resolved = Item.objects.filter(status='Claimed').count()
        total_items    = Item.objects.count()

        recovery_rate = (
            round((total_resolved / total_items) * 100, 2)
            if total_items > 0 else 0
        )

        return Response({
            'total_lost':     total_lost,
            'total_found':    total_found,
            'total_resolved': total_resolved,
            'total_items':    total_items,
            'recovery_rate':  f'{recovery_rate}%',
        })


class CategoryStatsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        # Group items by category name, count each group
        stats = (
            Item.objects
            .values('category__name')       # GROUP BY category name
            .annotate(count=Count('id'))    # COUNT items in each group
            .order_by('-count')             # most common first
        )

        return Response([
            {'category': s['category__name'], 'count': s['count']}
            for s in stats
        ])


class TrendsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        # Group Lost items by month
        lost_by_month = (
            Item.objects
            .filter(type='Lost')
            .annotate(month=TruncMonth('date'))   # truncate date to month
            .values('month')
            .annotate(count=Count('id'))
            .order_by('month')
        )

        # Group Found items by month
        found_by_month = (
            Item.objects
            .filter(type='Found')
            .annotate(month=TruncMonth('date'))
            .values('month')
            .annotate(count=Count('id'))
            .order_by('month')
        )

        # Merge into one dict keyed by month string
        trends = {}
        for entry in lost_by_month:
            month_str = entry['month'].strftime('%Y-%m')
            trends[month_str] = {'month': month_str, 'lost': entry['count'], 'found': 0}

        for entry in found_by_month:
            month_str = entry['month'].strftime('%Y-%m')
            if month_str in trends:
                trends[month_str]['found'] = entry['count']
            else:
                trends[month_str] = {'month': month_str, 'lost': 0, 'found': entry['count']}

        return Response(sorted(trends.values(), key=lambda x: x['month']))