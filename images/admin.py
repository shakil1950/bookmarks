from django.contrib import admin

from .models import Image


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_displays=['title','slug','created_at','image','url']
    list_filter=['created_at']