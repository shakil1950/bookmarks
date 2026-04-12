import requests
from django import forms
from .models import Image
from django.core.files.base import ContentFile
from django.utils.text import slugify


class ImageCreateForm(forms.ModelForm):
    class Meta:
        model=Image
        fields=['title','description','url']

        widgets={
            'url':forms.HiddenInput
        }
    def clean_url(self):
        url = self.cleaned_data['url']
        # valid_extensions = ['jpg', 'jpeg', 'png']
        # extension = url.rsplit('.', 1)[1].lower()
        # if extension not in valid_extensions:
        #     raise forms.ValidationError(
        #     'The given URL does not match valid image extensions.')
        return url
    
class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['title', 'image']
    
    