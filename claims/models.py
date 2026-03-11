from django.db import models
from django.conf import settings
from items.models import Item


class Claim(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    item              = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='claims')
    claimant          = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='claims')
    proof_description = models.TextField()
    proof_image       = models.ImageField(upload_to='claim_proofs/', blank=True, null=True)
    status            = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at        = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('item', 'claimant')

    def __str__(self):
        return f"{self.claimant.username} -> {self.item.title} ({self.status})"


class Notification(models.Model):
    NOTIF_TYPES = [
        ('claim_received', 'Someone claimed your item'),
        ('claim_approved', 'Your claim was approved'),
        ('claim_rejected', 'Your claim was rejected'),
        ('item_match',     'A found item matches your lost report'),
        ('item_deleted',   'Your item was deleted by admin'),
    ]

    user       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    notif_type = models.CharField(max_length=30, choices=NOTIF_TYPES, default='claim_received')
    title      = models.CharField(max_length=200, default='Notification')
    message    = models.TextField()
    item       = models.ForeignKey(Item, on_delete=models.SET_NULL, null=True, blank=True)
    is_read    = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.notif_type}"