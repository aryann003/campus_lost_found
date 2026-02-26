from rest_framework import viewsets, status,serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Claim
from .serializers import ClaimSerializer
from items.models import Item

class ClaimViewSet(viewsets.ModelViewSet):
    serializer_class = ClaimSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Regular users only see their own claims
        user = self.request.user
        if user.role == 'admin':
            return Claim.objects.all()
        return Claim.objects.filter(claimant=user)

    def perform_create(self, serializer):
        item = serializer.validated_data['item']

        # Prevent claiming your own item
        if item.owner == self.request.user:
            raise serializers.ValidationError("You cannot claim your own item.")

        # Prevent claiming an already-claimed item
        if item.status == 'Claimed':
            raise serializers.ValidationError("This item has already been claimed.")

        serializer.save(claimant=self.request.user)

    @action(detail=True, methods=['put'], url_path='approve')
    def approve(self, request, pk=None):
        claim = self.get_object()

        # Only the item owner can approve
        if claim.item.owner != request.user:
            return Response({'error': 'Only the item owner can approve claims.'}, status=403)

        # Only one claim can be approved — reject all others
        Claim.objects.filter(item=claim.item).exclude(pk=claim.pk).update(status='Rejected')

        claim.status = 'Approved'
        claim.save()

        # Auto-update item status
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