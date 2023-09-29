from io import BytesIO
from PIL import Image

from django.core.files.storage import default_storage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import HttpResponse, HttpResponseForbidden
from django.utils.crypto import get_random_string
from django.utils import timezone
from datetime import timedelta

from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework import generics, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from .models import UploadedImage, Thumbnail, AccountTier, UserProfile
from .serializers import UploadedImageSerializer, ThumbnailSerializer, AccountTierSerializer, ImagelListSerializer
from .validators import IsOwnerOrAdminImage, IsOwnerOrAdminThumbnail


class CustomAuthToken(ObtainAuthToken):
    """
        Generate token for created user
    """
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'user_id': user.id})


class ThumbnailView(generics.RetrieveAPIView):
    """
        Create thumbnail response, if the token is active
    """

    permission_classes = [IsAuthenticated, IsOwnerOrAdminThumbnail]
    queryset = Thumbnail.objects.all()
    serializer_class = ThumbnailSerializer
    lookup_field = 'token'

    def get(self, request, *args, **kwargs):
        thumbnail = self.get_object()

        if thumbnail.token_expired():
            return HttpResponseForbidden("Token expired")

        with default_storage.open(thumbnail.thumbnail_image.name, "rb") as file:
            thumbnail_data = file.read()

        return HttpResponse(thumbnail_data, content_type="image/jpeg")


class ImageView(generics.RetrieveAPIView):
    """
        Create image response
    """
    permission_classes = [IsAuthenticated, IsOwnerOrAdminImage]
    queryset = UploadedImage.objects.all()
    serializer_class = UploadedImageSerializer
    lookup_field = 'token'

    def get(self, request, *args, **kwargs):
        image = self.get_object()

        with default_storage.open(image.image.name, "rb") as file:
            image_data = file.read()

        return HttpResponse(image_data, content_type="image/jpeg")


class UploadImageView(generics.CreateAPIView):
    """
        is responsible for downloading the photo to the server,
        creating a thumbnail depending on the tier of the account,
        validating the data. Saving to the database. Generate respond
    """
    queryset = UploadedImage.objects.all()
    serializer_class = UploadedImageSerializer
    parser_classes = (MultiPartParser, FormParser)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = self.request.user
        token = self.set_image_token()

        self.set_image_url(serializer, token)

        instance = serializer.save(user=user, token=token)
        headers = self.get_success_headers(serializer.data)

        user_tier = self.get_account_tier()

        expire_time = serializer.validated_data.get('expire_link_value')
        print(expire_time, 'befire ebntering if')

        response = {}
        response = self._create_thumbnails(response, instance, user_tier, expire_time)
        response = self.check_include_image(response, serializer.validated_data.get('url'), user_tier)

        return Response(
            response,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    def set_image_token(self):
        return get_random_string(length=32)

    def set_expire_at_time(self, expire_time):
        return timezone.now() + timedelta(seconds=expire_time)

    def set_image_url(self, instance, token):
        host = self.request.get_host()
        url = f'{host}/image/{token}'
        instance.validated_data['url'] = url

    def _create_thumbnails(self, response, image_instance, tier, expire_time):
        thumbnails = [self.create_thumbnail(image_instance, size, expire_time) for size in tier.thumbnail_sizes]
        response['thumbnails'] = thumbnails
        return response

    def check_include_image(self, response, image_url, tier):
        if tier.include_image:
            response['image'] = image_url
        return response

    def create_thumbnail(self, image_instance, size, expire_time):
        image = Image.open(image_instance.image)
        image.thumbnail((size['x'], size['y']))

        thumb_io = BytesIO()
        image.save(thumb_io, 'JPEG')

        thumb_name = image_instance.image.name
        thumb_name = f'thumbnails/{thumb_name}'

        thumbnail = SimpleUploadedFile(
            thumb_name,
            thumb_io.getvalue(),
            content_type="image/jpeg"
        )

        token = get_random_string(length=32)
        host = self.request.get_host()
        thumbnail_url = f'{host}/thumbnail/{token}'

        thumbnail_db = Thumbnail(
            image=image_instance,
            size=size,
            token=token,
            thumbnail_image=thumbnail,
            url=thumbnail_url,
        )
        profile = UserProfile.objects.get(user_id=self.request.user.id)

        if profile.account_tier.generate_expiring_links and expire_time:
            self.validate_expire_link_value(expire_time)
            thumbnail_db.expires_at = self.set_expire_at_time(expire_time)

        thumbnail_db.save()
        thumbnail_serializer = ThumbnailSerializer(thumbnail_db)

        thumbnail_respond = thumbnail_serializer.data
        thumbnail_respond['size'] = f"{size['x']}x{size['y']}"

        return thumbnail_respond

    def get_account_tier(self):
        try:
            user_profile = UserProfile.objects.get(user_id=self.request.user.id)
            account_tier = user_profile.account_tier
            return account_tier

        except UserProfile.DoesNotExist:
            return None

    def validate_expire_link_value(self, value):
        if value and (value < 300 or value > 30000):
            raise ValidationError("expire_link_value must be between 300 and 30000 seconds.")
        return value


class AccountTierListCreateView(generics.ListCreateAPIView):
    queryset = AccountTier.objects.all()
    serializer_class = AccountTierSerializer
    permission_classes = [IsAdminUser]


class UserImagesAPIView(generics.ListAPIView):
    """
        Generate view for all images and their thumbnails for specific user
    """
    serializer_class = ImagelListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return UploadedImage.objects.filter(user=user)

    def get_serializer_context(self):
        context = super(UserImagesAPIView, self).get_serializer_context()
        context['thumbnails'] = self.get_thumbnails()
        return context

    def get_thumbnails(self):
        user = self.request.user
        image_ids = UploadedImage.objects.filter(user=user).values_list('id', flat=True)
        thumbnails = Thumbnail.objects.filter(image__in=image_ids)

        thumbnail_dict = {}
        for thumbnail in thumbnails:
            if thumbnail.image_id not in thumbnail_dict:
                thumbnail_dict[thumbnail.image_id] = []
            thumbnail_dict[thumbnail.image_id].append({
                'url': thumbnail.url,
                'expires_at': thumbnail.expires_at
            })

        return thumbnail_dict
