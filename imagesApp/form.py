from django import forms
from .models import UploadedImage


class UploadedImageForm(forms.ModelForm):
    class Meta:
        model = UploadedImage
        fields = ('image',)

    def save(self, commit=True, user=None):
        instance = super(UploadedImageForm, self).save(commit=False)
        if user:
            instance.user = user
        if commit:
            instance.save()
        return instance
