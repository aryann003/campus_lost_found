# items/views.py

from django.shortcuts import render
from django.db.models import Q
from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import ItemSerializer, CategorySerializer
from .models import Item, Category
from .permissions import IsOwnerOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    # search and filter
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['title', 'description']
    filterset_fields = ['category', 'type', 'location']
    ordering_fields = ['date']

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['get'], url_path='matches')
    def matches(self, request, pk=None):
        item = self.get_object()

        # Opposite type: Lost → Found, Found → Lost
        opposite_type = 'Found' if item.type == 'Lost' else 'Lost'

        # Base queryset: same category, opposite type, not the item itself
        candidates = Item.objects.filter(
            category=item.category,
            type=opposite_type,
        ).exclude(pk=item.pk)

        # ── Score each candidate ──────────────────────────────────
        scored = []
        # Extract keywords from the source item (words of 4+ chars)
        keywords = [w for w in item.title.lower().split() if len(w) >= 4]
        keywords += [w for w in item.description.lower().split() if len(w) >= 4]

        for candidate in candidates:
            score = 0

            # +2 for each keyword match in title
            for kw in keywords:
                if kw in candidate.title.lower():
                    score += 2

            # +1 for each keyword match in description
            for kw in keywords:
                if kw in candidate.description.lower():
                    score += 1

            # +3 bonus for same location (case-insensitive)
            if item.location and candidate.location:
                if item.location.lower() == candidate.location.lower():
                    score += 3

            scored.append((score, candidate))

        # Sort by score descending, take top 5
        scored.sort(key=lambda x: x[0], reverse=True)
        top5 = [candidate for score, candidate in scored[:5]]

        serializer = ItemSerializer(top5, many=True, context={'request': request})
        return Response({
            'source_item': item.title,
            'looking_for': opposite_type,
            'matches_found': len(top5),
            'results': serializer.data
        })