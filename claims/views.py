# claims/views.py

from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Claim, Notification
from .serializers import ClaimSerializer, NotificationSerializer
from items.models import Item


class ClaimViewSet(viewsets.ModelViewSet):
    serializer_class = ClaimSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Claim.objects.all()
        return Claim.objects.filter(claimant=user) | Claim.objects.filter(item__owner=user)  # ← FIXED

    def perform_create(self, serializer):
        item = serializer.validated_data['item']

        if item.owner == self.request.user:
            raise serializers.ValidationError("You cannot claim your own item.")

        if item.status == 'Claimed':
            raise serializers.ValidationError("This item has already been claimed.")

        serializer.save(claimant=self.request.user)

    @action(detail=True, methods=['put'], url_path='approve')
    def approve(self, request, pk=None):
        claim = self.get_object()

        if claim.item.owner != request.user:
            return Response({'error': 'Only the item owner can approve claims.'}, status=403)

        Claim.objects.filter(item=claim.item).exclude(pk=claim.pk).update(status='Rejected')

        claim.status = 'Approved'
        claim.save()

        claim.item.status = 'Claimed'
        claim.item.save()

        return Response({'message': 'Claim approved. Item marked as Claimed.'})

    @action(detail=True, methods=['put'], url_path='reject')
    def reject(self, request, pk=None):
        claim = self.get_object()

        if claim.item.owner != request.user:
            return Response({'error': 'Only the item owner can reject claims.'}, status=403)

        claim.status = 'Rejected'
        claim.save()

        return Response({'message': 'Claim rejected.'})


class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'patch', 'head', 'options']

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    @action(detail=True, methods=['patch'], url_path='read')
    def mark_as_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save(update_fields=['is_read'])
        return Response({'status': 'marked as read'}, status=status.HTTP_200_OK)