from django.shortcuts import render
from rest_framework import viewsets, permissions,filters
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

    #search and filter
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['title', 'description']
    filterset_fields = ['category', 'type', 'location']
    ordering_fields = ['date']


    def perform_create(self, serializer):
        # Automatically set owner to logged-in user
        serializer.save(owner=self.request.user)