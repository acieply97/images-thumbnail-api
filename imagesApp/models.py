from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class AccountTier(models.Model):
    name = models.CharField(max_length=50, unique=True)
    thumbnail_sizes = models.JSONField()
    include_image = models.BooleanField(default=False)
    generate_expiring_links = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class UploadedImage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    token = models.CharField(max_length=32, unique=True)
    url = models.URLField(null=True)

    def __str__(self):
        return f'{self.image}'

    def get_image_url(self):
        return f'{self.token}'


class Thumbnail(models.Model):
    image = models.ForeignKey(UploadedImage, on_delete=models.CASCADE)
    size = models.CharField(max_length=20)
    url = models.URLField(null=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    thumbnail_image = models.ImageField(upload_to='thumbnails/', )
    token = models.CharField(max_length=255, unique=True, null=True)

    def __str__(self):
        return f'{self.image} - {self.size}'

    def token_expired(self):
        if self.expires_at:
            return self.expires_at < timezone.now()
        return False


class UserProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    account_tier = models.ForeignKey(AccountTier, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user} - {self.account_tier.name}'
