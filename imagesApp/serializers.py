from rest_framework import serializers
from .models import Thumbnail, UploadedImage, AccountTier, UserProfile


class UploadedImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedImage
        fields = ('image',)

    def __init__(self, *args, **kwargs):
        super(UploadedImageSerializer, self).__init__(*args, **kwargs)

        user = self.context['request'].user
        profile = UserProfile.objects.get(user_id=user.id)

        if user.is_authenticated and profile.account_tier.generate_expiring_links:
            self.fields['expire_link_value'] = serializers.IntegerField(
                required=False,
                allow_null=True,
                default=False,
                min_value=300,
                max_value=30000,
                help_text='Specify the link expiration time in seconds (between 300 and 3000 seconds)'
            )

    def create(self, validated_data):
        validated_data.pop('expire_link_value', None)
        instance = super(UploadedImageSerializer, self).create(validated_data)

        return instance


class ThumbnailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Thumbnail
        fields = ('url', 'expires_at')


class AccountTierSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountTier
        fields = '__all__'


class ThumbnailListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Thumbnail
        fields = ('token',)


class ImagelListSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedImage
        fields = ('url',)

    def to_representation(self, instance):
        data = super(ImagelListSerializer, self).to_representation(instance)

        thumbnails = self.context.get('thumbnails', [])

        data['thumbnails'] = thumbnails.get(instance.id, [])

        return data
