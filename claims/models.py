from django.db import models

# Create your models here.
from django.conf import settings
from items.models import Item

class Claim(models.Model):
    STATUS_CHPICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='claims')
    claimant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='claims')
    proof_description = models.TextField()
    proof_image = models.ImageField(upload_to='claim_proofs/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHPICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('item', 'claimant')  

    def __str__(self):
        return f"{self.claimant.username} -> {self.item.title} ({self.status})"
    

class Notification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )

    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.user.username} - {'Read' if self.is_read else 'Unread'}"