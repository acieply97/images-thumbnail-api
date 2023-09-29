from django.contrib import admin
from .models import UploadedImage, AccountTier, Thumbnail, UserProfile

admin.site.register(UploadedImage)
admin.site.register(AccountTier)
admin.site.register(UserProfile)
admin.site.register(Thumbnail)

