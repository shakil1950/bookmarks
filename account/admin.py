from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Profile
from django.contrib.auth.models import User
# Register your models here.


class ProfileInline(admin.StackedInline):
    model=Profile
    can_delete=False
    verbose_name_plural='profile'

class AdminUser(UserAdmin):
    inlines=[ProfileInline]


admin.site.unregister(User)
admin.site.register(User,AdminUser)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
  
    list_display = ['user', 'dob', 'mob', 'avater_preview'] 
    
   
    fields = ['user', 'bio', 'avater', 'dob', 'mob']
    
   
    search_fields = ['user__username', 'mob']

    def avater_preview(self, obj):
        if obj.avater:
            return "Has Image"
        return "No Image"