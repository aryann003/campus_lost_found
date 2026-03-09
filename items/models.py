from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User

User = get_user_model()

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Item(models.Model):

    # Choices for type field
    TYPE_CHOICES = [
        ('Lost', 'Lost'),
        ('Found', 'Found'),
    ]

    # Choices for status field
    STATUS_CHOICES = [
        ('Open', 'Open'),
        ('Claimed', 'Claimed'),
        ('Resolved', 'Resolved'),
    ]

    title       = models.CharField(max_length=200)
    description = models.TextField()
    category    = models.ForeignKey(Category, on_delete=models.CASCADE)
    type        = models.CharField(max_length=10, choices=TYPE_CHOICES)
    image       = models.ImageField(upload_to='item_images/', blank=True, null=True)
    location    = models.CharField(max_length=200)
    date        = models.DateField(auto_now_add=True)
    status      = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Open')
    owner       = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title
    
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s profile"
