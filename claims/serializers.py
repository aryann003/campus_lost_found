from rest_framework import serializers
from .models import Claim

class ClaimSerializer(serializers.ModelSerializer):
    claimant = serializers.StringRelatedField(read_only=True)
    item_title = serializers.CharField(source='item.title', read_only=True)

    class Meta:
        model = Claim
        fields = ['id', 'item', 'item_title', 'claimant', 'proof_description', 'proof_image', 'status', 'created_at']
        read_only_fields = ['claimant', 'status', 'created_at']