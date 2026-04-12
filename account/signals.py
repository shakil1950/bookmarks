from django.contrib.auth.models import User
from django.db.models.signals import post_save
from .models import Profile
from django.dispatch import receiver
import requests
from django.core.files.base import ContentFile
from allauth.socialaccount.models import SocialAccount


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()



@receiver(post_save, sender=SocialAccount)
def save_google_avatar(sender, instance, created, **kwargs):
   
    if created and instance.provider == 'google':
        avater_url = instance.extra_data.get('picture')
        
        if avater_url:
         
            response = requests.get(avater_url)
            if response.status_code == 200:
                
                profile, _ = Profile.objects.get_or_create(user=instance.user)
                
             
                file_name = f'user_{instance.user.id}_avatar.jpg'
                
              
                profile.avater.save(file_name, ContentFile(response.content), save=True)