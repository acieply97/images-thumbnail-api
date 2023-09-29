from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from .views import *

urlpatterns = [
    path('api-token-auth/', CustomAuthToken.as_view(), name='api_token_auth'),
    path('thumbnail/<str:token>/', ThumbnailView.as_view(), name='thumbnail-view'),
    path('image/<str:token>/', ImageView.as_view(), name='image-view'),
    path('upload/', UploadImageView.as_view(), name='upload-image'),
    path('account-tiers/', AccountTierListCreateView.as_view(), name='account-tier-list-create'),
    path('user-images/', UserImagesAPIView.as_view(), name='user-images-view'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)